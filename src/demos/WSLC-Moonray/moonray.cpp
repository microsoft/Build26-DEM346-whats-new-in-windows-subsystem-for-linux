// WSLC-Moonray
//
// A Windows executable that wraps the Linux "moonray" renderer using the WSL
// Container SDK.  All command-line arguments are forwarded into the container,
// so "moonray.exe -in scene.rdla -out render.exr" behaves just like running
// moonray on Linux.
//
// Windows paths passed via -in and -out are automatically mapped into the
// container as bind mounts so the renderer can access input scenes and write
// output images.

#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <objbase.h>
#include <string>
#include <vector>
#include "wslcsdk.h"

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "wslcsdk.lib")

static const char* IMAGE_NAME = "openmoonray:latest";

// Resolve IMAGE_TAR at runtime relative to the .exe location,
// matching the WslcImage TarLocation: $(OutDir)\Containerfiles\moonray.tar
static std::wstring GetImageTarPath()
{
    wchar_t exePath[MAX_PATH];
    GetModuleFileNameW(nullptr, exePath, MAX_PATH);
    std::wstring dir(exePath);
    size_t pos = dir.find_last_of(L"\\/");
    if (pos != std::wstring::npos)
        dir = dir.substr(0, pos);
    return dir + L"\\Containerfiles\\moonray.tar";
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static void PrintError(const wchar_t* context, HRESULT hr, PWSTR error)
{
    fwprintf(stderr, L"[moonray] Error: %s (0x%08X)", context, hr);
    if (error) {
        fwprintf(stderr, L": %s", error);
        CoTaskMemFree(error);
    }
    fwprintf(stderr, L"\n");
}

// Forward container stdout/stderr directly to the Windows console.
static void CALLBACK OnStdIO(
    WslcProcessIOHandle ioHandle,
    _In_reads_bytes_(dataSize) const BYTE* data,
    uint32_t dataSize,
    _In_opt_ PVOID /*context*/)
{
    HANDLE hOutput = (ioHandle == WSLC_PROCESS_IO_HANDLE_STDOUT)
        ? GetStdHandle(STD_OUTPUT_HANDLE)
        : GetStdHandle(STD_ERROR_HANDLE);
    DWORD written;
    WriteFile(hOutput, data, dataSize, &written, nullptr);
}

// Store the process exit code and signal completion.
static void CALLBACK OnProcessExit(INT32 exitCode, _In_opt_ PVOID context)
{
    auto* ctx = static_cast<std::pair<HANDLE, INT32>*>(context);
    ctx->second = exitCode;
    SetEvent(ctx->first);
}

// Image load progress callback
static HRESULT CALLBACK OnImageProgress(
    const WslcImageProgressMessage* message,
    _In_opt_ PVOID /*context*/)
{
    if (message) {
        fwprintf(stderr, L"[moonray]   layer %hs: status=%d  %llu / %llu bytes\n",
            message->id ? message->id : "(null)",
            (int)message->status,
            message->detail.currentBytes,
            message->detail.totalBytes);
    }
    return S_OK;
}

// Convert a wide string to UTF-8.
static std::string WideToUtf8(const wchar_t* wide)
{
    int len = WideCharToMultiByte(CP_UTF8, 0, wide, -1, nullptr, 0, nullptr, nullptr);
    std::string s(len - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wide, -1, &s[0], len, nullptr, nullptr);
    return s;
}

// Get the full path of a file, resolving relative paths.
static std::wstring ResolveFullPath(const wchar_t* path)
{
    wchar_t buf[MAX_PATH];
    DWORD len = GetFullPathNameW(path, MAX_PATH, buf, nullptr);
    if (len == 0 || len >= MAX_PATH) return path;
    return buf;
}

// Get the directory portion of a path.
static std::wstring GetDirPart(const std::wstring& path)
{
    size_t pos = path.find_last_of(L"\\/");
    if (pos == std::wstring::npos) return L".";
    return path.substr(0, pos);
}

// Get the filename portion of a path.
static std::wstring GetFilePart(const std::wstring& path)
{
    size_t pos = path.find_last_of(L"\\/");
    if (pos == std::wstring::npos) return path;
    return path.substr(pos + 1);
}

// Check if an argument looks like a Windows file path.
static bool LooksLikeWindowsPath(const std::wstring& arg)
{
    if (arg.length() >= 2 && arg[1] == L':') return true;
    if (arg.find(L'\\') != std::wstring::npos) return true;
    return false;
}

// A bind mount mapping: Windows dir -> Linux mount point.
struct BindMount {
    std::wstring windowsPath;
    std::string linuxPath;
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int wmain(int argc, wchar_t* argv[])
{
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);

    HRESULT hr;
    PWSTR error = nullptr;
    int result = 1;

    // Resources — declared up front so the single cleanup block can release them.
    WslcSession session = nullptr;
    WslcContainer container = nullptr;
    WslcProcess execProc = nullptr;
    HANDLE exitEvent = CreateEvent(nullptr, TRUE, FALSE, nullptr);
    std::pair<HANDLE, INT32> exitContext = { exitEvent, -1 };

    // Scan arguments: detect Windows paths after -in/-out and set up bind mounts.
    std::vector<BindMount> mounts;
    std::vector<std::string> argStrings;

    // argv[0] is replaced with the entrypoint wrapper then moonray
    argStrings.push_back("/entrypoint.sh");
    argStrings.push_back("moonray");

    for (int i = 1; i < argc; i++) {
        std::wstring arg = argv[i];

        // Check if this arg follows -in or -out (file path args)
        bool isPrevPathFlag = false;
        if (i > 1) {
            std::wstring prev = argv[i - 1];
            isPrevPathFlag = (prev == L"-in" || prev == L"-out" ||
                              prev == L"--in" || prev == L"--out");
        }

        if (isPrevPathFlag && (LooksLikeWindowsPath(arg) ||
            GetFileAttributesW(arg.c_str()) != INVALID_FILE_ATTRIBUTES)) {
            std::wstring fullPath = ResolveFullPath(arg.c_str());
            std::wstring dir = GetDirPart(fullPath);
            std::wstring filename = GetFilePart(fullPath);

            // Find or create mount for this directory
            std::string linuxDir;
            bool found = false;
            for (auto& m : mounts) {
                if (_wcsicmp(m.windowsPath.c_str(), dir.c_str()) == 0) {
                    linuxDir = m.linuxPath;
                    found = true;
                    break;
                }
            }

            if (!found) {
                char mp[64];
                sprintf_s(mp, "/mnt/bind%zu", mounts.size());
                BindMount bm;
                bm.windowsPath = dir;
                bm.linuxPath = mp;
                mounts.push_back(bm);
                linuxDir = mp;
            }

            std::string linuxFile = linuxDir + "/" + WideToUtf8(filename.c_str());
            argStrings.push_back(linuxFile);
        } else {
            argStrings.push_back(WideToUtf8(argv[i]));
        }
    }

    std::vector<PCSTR> execArgv;
    for (auto& s : argStrings)
        execArgv.push_back(s.c_str());

    // ---- Session ----
    fwprintf(stderr, L"[moonray] Creating session...\n");
    {
        WslcSessionSettings settings;
        hr = WslcInitSessionSettings(L"WSLCMoonray", L"C:\\WslcStorage\\moonray", &settings);
        if (FAILED(hr)) { PrintError(L"Init session settings", hr, nullptr); goto cleanup; }

        // Use all CPUs and at least 8 GB RAM for rendering
        SYSTEM_INFO sysInfo;
        GetSystemInfo(&sysInfo);
        WslcSetSessionSettingsCpuCount(&settings, sysInfo.dwNumberOfProcessors);
        WslcSetSessionSettingsMemory(&settings, 8192);

        // The image is ~8.5 GB, so we need a large session VHD
        WslcVhdRequirements vhdReqs = {};
        vhdReqs.sizeBytes = 20ULL * 1024 * 1024 * 1024; // 20 GB
        vhdReqs.type = WSLC_VHD_TYPE_DYNAMIC;
        WslcSetSessionSettingsVhd(&settings, &vhdReqs);

        fwprintf(stderr, L"[moonray]   CPUs: %lu  Memory: 8192 MB  VHD: 20 GB\n",
            sysInfo.dwNumberOfProcessors);

        hr = WslcCreateSession(&settings, &session, &error);
        if (FAILED(hr)) { PrintError(L"Create session", hr, error); goto cleanup; }
    }

    // ---- Ensure image is available ----
    {
        std::wstring imageTar = GetImageTarPath();

        // Check if the image is already cached in the session VHD
        WslcImageInfo* images = nullptr;
        uint32_t imgCount = 0;
        bool imageFound = false;

        hr = WslcListSessionImages(session, &images, &imgCount);
        if (SUCCEEDED(hr)) {
            for (uint32_t i = 0; i < imgCount; i++) {
                if (strcmp(images[i].name, IMAGE_NAME) == 0) {
                    imageFound = true;
                    break;
                }
            }
            if (images) CoTaskMemFree(images);
        }

        if (imageFound) {
            fwprintf(stderr, L"[moonray] Image '%hs' already cached in session.\n", IMAGE_NAME);
        } else {
            fwprintf(stderr, L"[moonray] Loading image from '%s'...\n", imageTar.c_str());

            WslcLoadImageOptions loadOpts = {};
            loadOpts.progressCallback = OnImageProgress;
            loadOpts.progressCallbackContext = nullptr;

            hr = WslcLoadSessionImageFromFile(session, imageTar.c_str(), &loadOpts, &error);
            if (FAILED(hr)) {
                PrintError(L"LoadSessionImageFromFile", hr, error);
                goto cleanup;
            }

            // Verify it loaded
            images = nullptr;
            imgCount = 0;
            WslcListSessionImages(session, &images, &imgCount);
            if (imgCount > 0) {
                fwprintf(stderr, L"[moonray] Loaded image: %hs\n", images[0].name);
                CoTaskMemFree(images);
            } else {
                fwprintf(stderr, L"[moonray] Error: No images after load.\n");
                if (images) CoTaskMemFree(images);
                goto cleanup;
            }
        }
    }

    // ---- Create & start container ----
    fwprintf(stderr, L"[moonray] Starting container...\n");
    {
        // The init process keeps the container alive while we exec moonray.
        WslcProcessSettings initProc;
        WslcInitProcessSettings(&initProc);
        PCSTR initArgv[] = { "/bin/sleep", "3600" };
        WslcSetProcessSettingsCmdLine(&initProc, initArgv, 2);

        WslcContainerSettings cSettings;
        WslcInitContainerSettings(IMAGE_NAME, &cSettings);
        WslcSetContainerSettingsName(&cSettings, "wslc-moonray");
        WslcSetContainerSettingsInitProcess(&cSettings, &initProc);
        WslcSetContainerSettingsFlags(&cSettings, WSLC_CONTAINER_FLAG_AUTO_REMOVE);

        // Add bind mounts for input/output paths
        std::vector<WslcContainerVolume> volumes;
        for (auto& m : mounts) {
            WslcContainerVolume vol = {};
            vol.windowsPath = m.windowsPath.c_str();
            vol.containerPath = m.linuxPath.c_str();
            vol.readOnly = FALSE;
            volumes.push_back(vol);
            fwprintf(stderr, L"[moonray] Mount: %s -> %hs\n",
                m.windowsPath.c_str(), m.linuxPath.c_str());
        }

        if (!volumes.empty()) {
            hr = WslcSetContainerSettingsVolumes(&cSettings, volumes.data(),
                static_cast<uint32_t>(volumes.size()));
            if (FAILED(hr)) { PrintError(L"Set volumes", hr, nullptr); goto cleanup; }
        }

        hr = WslcCreateContainer(session, &cSettings, &container, &error);
        if (FAILED(hr)) { PrintError(L"Create container", hr, error); goto cleanup; }

        hr = WslcStartContainer(container, WSLC_CONTAINER_START_FLAG_NONE, &error);
        if (FAILED(hr)) { PrintError(L"Start container", hr, error); goto cleanup; }
    }

    // ---- Exec moonray ----
    fwprintf(stderr, L"[moonray] Running moonray...\n");
    {
        WslcProcessSettings pSettings;
        WslcInitProcessSettings(&pSettings);
        WslcSetProcessSettingsCmdLine(&pSettings, execArgv.data(),
            static_cast<uint32_t>(execArgv.size()));

        WslcProcessCallbacks callbacks = {};
        callbacks.onStdOut = OnStdIO;
        callbacks.onStdErr = OnStdIO;
        callbacks.onExit = OnProcessExit;
        WslcSetProcessSettingsCallbacks(&pSettings, &callbacks, &exitContext);

        hr = WslcCreateContainerProcess(container, &pSettings, &execProc, &error);
        if (FAILED(hr)) { PrintError(L"Exec moonray", hr, error); goto cleanup; }

        // Wait indefinitely — renders can take a long time
        WaitForSingleObject(exitEvent, INFINITE);
        result = exitContext.second;
    }

    // ---- Cleanup (single path for both success and failure) ----
cleanup:
    fwprintf(stderr, L"[moonray] Shutting down...\n");

    if (execProc)  WslcReleaseProcess(execProc);
    if (exitEvent) CloseHandle(exitEvent);
    if (container) { WslcStopContainer(container, WSLC_SIGNAL_SIGTERM, 5, nullptr); WslcReleaseContainer(container); }
    if (session)   { WslcTerminateSession(session); WslcReleaseSession(session); }

    fwprintf(stderr, L"[moonray] Done.\n");
    CoUninitialize();
    return result;
}

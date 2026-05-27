using System.Diagnostics;
using System.Text;
using Microsoft.WSL.Containers;
using WslcProcess = Microsoft.WSL.Containers.Process;

namespace HerbertStockTrader.Services;

/// <summary>
/// Manages the WSL Container session, container, and process lifecycle
/// using the Microsoft.WSL.Containers C# SDK (2.8.5).
/// </summary>
public sealed class ContainerService
{
    public event Action<string>? OutputReceived;
    public event Action<string>? StatusChanged;

    private Session? _session;
    private Container? _container;
    private WslcProcess? _execProcess;

    private volatile bool _running;
    private volatile bool _shutdownCalled;

    private StreamWriter? _logFile;
    private readonly object _logLock = new();

    private const string SessionName = "HerbertStockTrader";
    private const string ImageName = "herbert:latest";
    private const string ContainerNamePrefix = "herbert-trader";

    private static readonly string BaseDir = AppContext.BaseDirectory;
    private static readonly string StoragePath = Path.Combine(BaseDir, "WslcStorage");
    private static readonly string DebugDir = Path.Combine(BaseDir, "logs");
    private static readonly string DebugLogPath = Path.Combine(DebugDir, "debug.log");
    private static readonly string ImageTarPath = Path.Combine(BaseDir, "herbert.tar");

    public ContainerService()
    {
        Directory.CreateDirectory(DebugDir);

        try
        {
            _logFile = new StreamWriter(DebugLogPath, append: false) { AutoFlush = true };
        }
        catch { /* ignore */ }

        DebugLog("ContainerService created");
    }

    public bool IsRunning => _running;

    public void StartContainer()
    {
        if (_running) return;

        EmitStatus("Initializing WSL Container session...");

        Directory.CreateDirectory(StoragePath);
        Directory.CreateDirectory(DebugDir);
        Directory.CreateDirectory(@"C:\temp\Herbert");

        // --- 1. Session setup ---
        DebugLog("Step 1: Creating session settings...");
        SessionSettings sessionSettings;
        try
        {
            sessionSettings = new SessionSettings(SessionName, StoragePath)
            {
                CpuCount = 4,
                MemoryMB = 4096,
                VhdRequirements = new VhdOptions("default", 40UL * 1024 * 1024 * 1024, VhdType.Dynamic)
            };
            DebugLog("SessionSettings created OK");
        }
        catch (Exception ex)
        {
            DebugLog($"SessionSettings FAILED: {ex.GetType().Name}: 0x{ex.HResult:X8} {ex.Message}");
            throw;
        }

        DebugLog("Step 2: Creating session...");
        try
        {
            _session = new Session(sessionSettings);
            DebugLog("Session object created, calling Start()...");
            _session.Start();
            DebugLog("Session created and started successfully");
        }
        catch (Exception ex)
        {
            DebugLog($"Session creation/start FAILED: {ex.GetType().Name}: 0x{ex.HResult:X8} {ex.Message}");
            DebugLog($"  StackTrace: {ex.StackTrace}");
            if (ex.InnerException != null)
                DebugLog($"  Inner: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}");
            throw;
        }
        EmitStatus("Session created. Checking for Herbert image...");

        // --- 2. Load image if not already in session ---
        DebugLog("Step 3: Checking for existing image...");
        bool imageFound = false;
        try
        {
            var images = _session.Images;
            foreach (var img in images)
            {
                DebugLog($"  Found image: {img.Name}");
                if (string.Equals(img.Name, ImageName, StringComparison.OrdinalIgnoreCase))
                {
                    imageFound = true;
                    break;
                }
            }
        }
        catch (Exception ex)
        {
            DebugLog($"Failed to list images: {ex.Message}");
        }

        if (imageFound)
        {
            DebugLog("Image already loaded in session, skipping import");
        }
        else
        {
            DebugLog("Image not found, loading from tar file...");
            EmitStatus("Loading image (this may take a moment)...");
            try
            {
                var loadOp = _session.LoadImageAsync(ImageTarPath);
                loadOp.AsTask().GetAwaiter().GetResult();
                DebugLog("Image loaded successfully from tar");
            }
            catch (Exception ex)
            {
                DebugLog($"LoadImageAsync failed: {ex.Message}");
            }
        }
        EmitStatus("Image ready. Configuring container...");

        // --- 3. Container settings ---
        DebugLog("Step 4: Configuring container settings...");

        var initProcess = new ProcessSettings { CmdLine = ["/bin/sleep", "infinity"] };

        var containerName = $"{ContainerNamePrefix}-{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";

        var containerSettings = new ContainerSettings(ImageName)
        {
            Name = containerName,
            InitProcess = initProcess,
            NetworkingMode = ContainerNetworkingMode.Bridged,
            HostName = "herbert",
            Flags = ContainerFlags.AutoRemove,
            PortMappings =
            [
                new ContainerPortMapping(6080, 6080, PortProtocol.TCP),
                new ContainerPortMapping(8765, 8765, PortProtocol.TCP)
            ],
            Volumes =
            [
                new ContainerVolume(@"C:\temp\Herbert", "/mnt/herbert", readOnly: false)
            ]
        };

        // --- 4. Create container ---
        DebugLog("Step 5: Creating container...");
        _container = _session.CreateContainer(containerSettings);
        DebugLog("Container created successfully");
        EmitStatus("Container created. Starting...");

        // --- 5. Start container ---
        DebugLog("Step 6: Starting container...");
        _container.Start();
        DebugLog("Container started successfully!");
        EmitStatus("Container running. Launching Herbert...");

        // --- 6. Exec /start.sh ---
        DebugLog("Step 7: Launching exec process (/start.sh)...");
        var execSettings = new ProcessSettings { CmdLine = ["/start.sh"], OutputMode = ProcessOutputMode.Event };

        _execProcess = _container.CreateProcess(execSettings);

        // Wire up output/error/exit events
        _execProcess.OutputReceived += OnProcessOutput;
        _execProcess.ErrorReceived += OnProcessOutput;
        _execProcess.Exited += OnProcessExit;

        _execProcess.Start();

        _running = true;
        DebugLog("Herbert trading agent launched successfully!");
        EmitStatus("Herbert is running!");
    }

    private void OnProcessOutput(byte[] data)
    {
        if (data.Length == 0) return;

        var text = Encoding.UTF8.GetString(data);
        DebugLog($"IO: {data.Length} bytes");
        EmitOutput(text);
    }

    private void OnProcessExit(int exitCode)
    {
        DebugLog($"Exec process exited with code {exitCode}");
        EmitStatus($"Herbert process exited with code {exitCode}");
        _running = false;
    }

    public void Shutdown()
    {
        if (_shutdownCalled) return;
        _shutdownCalled = true;

        DebugLog("Shutdown started...");
        _running = false;

        if (_execProcess != null)
        {
            DebugLog("Signalling exec process...");
            try { _execProcess.Signal(Signal.SIGTERM); }
            catch { /* ignore */ }
            _execProcess = null;
        }

        if (_container != null)
        {
            DebugLog("Stopping container...");
            try { _container.Stop(Signal.SIGTERM, TimeSpan.FromSeconds(5)); }
            catch { /* ignore */ }

            DebugLog("Deleting container...");
            try { _container.Delete(DeleteContainerFlags.Force); }
            catch { /* ignore */ }
            _container = null;
        }

        if (_session != null)
        {
            DebugLog("Terminating session...");
            try { _session.Terminate(); }
            catch { /* ignore */ }
            _session = null;
        }

        DebugLog("Shutdown complete");

        lock (_logLock)
        {
            _logFile?.Dispose();
            _logFile = null;
        }
    }

    private void EmitOutput(string text)
    {
        OutputReceived?.Invoke(text);
    }

    private void EmitStatus(string text)
    {
        DebugLog($"STATUS: {text}");
        StatusChanged?.Invoke(text);
    }

    private void DebugLog(string message)
    {
        var timestamp = DateTime.Now.ToString("HH:mm:ss");
        var line = $"[{timestamp}] {message}";

        Debug.WriteLine($"[Herbert] {line}");

        lock (_logLock)
        {
            try { _logFile?.WriteLine(line); }
            catch { /* ignore */ }
        }
    }
}

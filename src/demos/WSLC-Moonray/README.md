# WSLC-Moonray sample code

A sample that uses the [WSL Container SDK](https://aka.ms/wslc) to package the
Linux **MoonRay** renderer as a native Windows executable.  Running `moonray.exe`
on Windows creates a WSLC session, loads the MoonRay container image from a
saved tar, and executes the renderer — all via the SDK (no `wslc.exe` CLI needed
at runtime).

All command-line arguments are forwarded, and Windows file paths passed to
`-in` and `-out` are automatically mapped into the container as bind mounts.

## Prerequisites

1. Install wslc: `wsl.2.8.4.0.x64.msi` (from the `binaries/` folder)
2. Build the `openmoonray` container image (see the `Containerfile` in the repo root):
   ```
   wslc build -t openmoonray:latest -f Containerfile .
   ```
3. Save the image as a tar:
   ```
   wslc save openmoonray -o C:\cDev\moonray-test\output\openmoonray.tar
   ```

## Building

Open `WSLCMoonray.sln` in Visual Studio, or build from the command line:
```
msbuild WSLCMoonray.sln /p:Configuration=Debug /p:Platform=x64
```

## Running

```
x64\Debug\moonray.exe -in C:\scenes\coffee_maker\scene.rdla ^
                      -in C:\scenes\coffee_maker\scene.rdlb ^
                      -out C:\output\render.jpg
```

Progress messages are printed to stderr so they won't interfere if you pipe stdout.

## How it works

1. Creates a WSLC session with all available CPUs, 8 GB RAM, and a 20 GB VHD
2. Loads the `openmoonray:latest` image from the saved tar via `WslcLoadSessionImageFromFile`
3. Scans `-in` / `-out` arguments for Windows paths and sets up bind mounts
4. Starts a container and executes `moonray` with the rewritten arguments
5. Streams stdout/stderr back to the Windows console via SDK callbacks
6. Returns moonray's exit code

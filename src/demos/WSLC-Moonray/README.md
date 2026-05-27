# WSLC-Moonray sample code

A sample that uses the [WSL Container SDK](https://aka.ms/wslc) to package the
Linux **MoonRay** renderer as a native Windows executable.  Running `moonray.exe`
on Windows creates a WSLC session, loads the MoonRay container image from a
saved tar, and executes the renderer — all via the SDK (no `wslc.exe` CLI needed
at runtime).

All command-line arguments are forwarded, and Windows file paths passed to
`-in` and `-out` are automatically mapped into the container as bind mounts.

## Prerequisites

1. Install wslc (version 2.8.7 or later)
2. Place the `Microsoft.WSL.Containers` NuGet package in `C:\cDev\nuget`

## Building

Open `WSLCMoonray.sln` in Visual Studio, or build from the command line:
```
msbuild WSLCMoonray.sln /p:Configuration=Debug /p:Platform=x64
```

The build automatically creates the MoonRay container image (via the `WslcImage`
item in the project file) and places the `.tar` alongside the executable.

## Running

Render the included coffee maker sample scene:
```
x64\Debug\moonray.exe -in samples\coffee_maker\scene.rdla -in samples\coffee_maker\scene.rdlb -out samples\coffee_maker\render_output.jpg -res 4.0
```

By default moonray uses all available threads. Use `-res` to control the
resolution divisor (higher value = lower resolution = faster render).

Progress messages are printed to stderr so they won't interfere if you pipe stdout.

## How it works

1. Creates a WSLC session with all available CPUs, 8 GB RAM, and a 20 GB VHD
2. Loads the `moonray:latest` image from the auto-built tar (next to the `.exe`)
3. Scans `-in` / `-out` arguments for Windows paths and sets up bind mounts
4. Starts a container and executes `moonray` with the rewritten arguments
5. Streams stdout/stderr back to the Windows console via SDK callbacks
6. Returns moonray's exit code

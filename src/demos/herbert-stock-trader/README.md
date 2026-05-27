# Herbert Stock Trader 👻📈

A WinUI 3 desktop app that runs a ghost-powered stock trading terminal inside a WSL Container. Herbert (a cute animated ghost) lives in a containerized Linux desktop — launching terminals, browsing files, and generating fake trades — all streamed live to the Windows app.

## Prerequisites

- **Windows 11** (build 26100+)
- **.NET 8 SDK** (x64)
- **WSL Containers** (`wslc.exe` — ships with WSL 2.8+)
- **WebView2 Runtime** (usually pre-installed on Windows 11)

## Build & Run

```powershell
# 1. Build the container image
cd Container
wslc.exe build -t herbert:latest -f Containerfile .

# 2. Export the image to a tar (required by the app at runtime)
wslc.exe image save herbert:latest -o herbert.tar

# 3. Build the app
cd ..
dotnet build -p:Platform=x64

# 4. Run
dotnet run -p:Platform=x64
```

## Architecture

```
┌──────────────────────────────────────────┐
│  WinUI 3 App (Windows)                   │
│  ├─ Trading Dashboard (WebSocket feed)   │
│  ├─ File Browser (C:\temp\Herbert\)      │
│  └─ Herbert's Desktop (noVNC WebView2)   │
├──────────────────────────────────────────┤
│  WSL Container (Ubuntu 22.04)            │
│  ├─ XFCE4 + Xvfb → x11vnc → noVNC:6080 │
│  ├─ Ghost (Python/GTK3 overlay)          │
│  └─ WebSocket trade feed on :8765        │
└──────────────────────────────────────────┘
```

## Configuration

Edit `Container/ghost/config.py` to change ghost speed, processes launched, file names, screen resolution, and ghost appearance.

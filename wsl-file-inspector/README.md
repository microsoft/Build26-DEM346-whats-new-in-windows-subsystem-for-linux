# 🐧 WSL File Inspector

Upload any file and Linux tools will reveal its secrets — file type, metadata, hex dump, strings, checksums, and more.

A Flask web app that runs inside a container on **WSL** using `wslc`.

## Prerequisites

- **Windows 11** with [WSL 2](https://learn.microsoft.com/windows/wsl/install) enabled
- **wslc** (WSL Container Tools) installed via the Microsoft Store or your WSL distribution

Verify both are available:

```sh
wsl --version
wslc --version
```

## Build the container image

From the project root (in PowerShell, Command Prompt, or a WSL shell):

```sh
wslc build -t wsl-file-inspector -f Containerfile .
```

## Run the container

```sh
wslc run -d -p 5000:5000 --name file-inspector wsl-file-inspector
```

Then open **http://localhost:5000** in your browser.

## Usage

1. Click **Browse** and select any file (up to 50 MB).
2. Click **🔍 Inspect File**.
3. View results from these Linux tools:

| Tool | What it shows |
|------|---------------|
| `file` | File type identification |
| `stat` | Metadata & permissions |
| `exiftool` | EXIF & embedded metadata |
| `strings` | Readable text strings (first 40 lines) |
| `hexdump` | Raw hex view (first 32 lines) |
| `wc` | Byte count |
| `sha256sum` | SHA-256 checksum |

## Stop and clean up

```sh
wslc stop file-inspector
wslc rm file-inspector
```

To also remove the image:

```sh
wslc rmi wsl-file-inspector
```

## Project structure

```
├── Containerfile      # Container image definition
├── app.py             # Flask application
├── requirements.txt   # Python dependencies
└── README.md
```

## License

This project is provided as-is for demonstration purposes.

<a name="start-building"></a>
<br>
<p align="center">
<img src="img/banner-build-26.png" alt="Microsoft Build 2026" width="1200"/>
</p>

# [Microsoft Build 2026](https://build.microsoft.com)

## 🔥 DEM346: What's New in Windows Subsystem for Linux

### Session Description

Discover the latest features in Windows Subsystem for Linux, including WSL Containers — a new way to run containerized Linux workloads directly on Windows. See how to package Linux apps as native Windows executables, run GPU-accelerated machine learning workloads, and build containerized web apps, all powered by WSL.

### 🚀 Getting started

If you'd like to explore the demos from this presentation on your own:

- Clone this repository
- Install [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/install) (WSL 2.8+) with WSL Container support (`wslc`)
- Browse the demos in [`src/demos/`](src/demos/) — each has its own README with build and run instructions:
  - [**WSLC-Moonray**](src/demos/WSLC-Moonray/) — Package a Linux renderer as a native Windows executable using the WSL Container SDK
  - [**Herbert Stock Trader**](src/demos/herbert-stock-trader/) — A WinUI 3 app streaming a containerized Linux desktop to Windows
  - [**Kernel Vision (Triton Build Demo)**](src/demos/triton-build-demo/) — Visualize neural network optimization inside a WSL Container with GPU support
  - [**WSL File Inspector**](src/demos/wsl-file-inspector/) — A Flask web app running Linux file analysis tools in a container

### 🧠 Learning Outcomes

By the end of this demo, you will be able to:

- Understand what WSL Containers are and how they enable running containerized Linux workloads directly on Windows
- Use the WSL Container SDK and CLI to build, run, and package Linux container images as native Windows applications
- Explore real-world scenarios for WSL Containers including GPU-accelerated ML workloads, desktop app integration, and containerized web services

### 💬 Keep Learning with Copilot

Try these prompts with GitHub Copilot to explore the topics from this demo. Open Copilot Chat in Visual Studio Code (`Ctrl+Alt+I` on Windows/Linux, `Cmd+Shift+I` on Mac), paste a prompt, and see what you learn. Try connecting the [Microsoft Learn MCP Server](#-microsoft-learn-mcp-server) for the latest official documentation.

Use these as a starting point — or write your own!

1. Understand the basics:

```
Explain what WSL Containers are, how they differ from traditional WSL distributions, and what scenarios they're best suited for
```

2. Go deeper:

```
Using the Microsoft Learn MCP Server, find the latest documentation on the WSL Container SDK and walk me through how to package a Linux application as a native Windows executable
```

3. Build something:

```
Help me create a simple containerized Python web app that runs on Windows using wslc. I want to build a container image from a Containerfile, run it with port forwarding, and access it from my Windows browser
```

### 💻 Technologies Used

1. [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/windows/wsl/) — Run Linux distributions natively on Windows
1. [WSL Containers (wslc)](https://aka.ms/wslc) — Build and run OCI container images directly on Windows via WSL
1. [WinUI 3](https://learn.microsoft.com/windows/apps/winui/winui3/) — Modern native UI framework for Windows desktop apps
1. [.NET 8](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-8/) — Cross-platform framework used by the Herbert Stock Trader demo
1. [Python](https://www.python.org/) — Used in the WSL File Inspector and Triton demos
1. [PyTorch](https://pytorch.org/) — Machine learning framework used in the Kernel Vision demo

### 📚 Resources and Next Steps

| Resource | Description |
|:---------|:------------|
| [Windows Subsystem for Linux Documentation](https://learn.microsoft.com/windows/wsl/) | Official WSL documentation on Microsoft Learn |
| [WSL Containers](https://aka.ms/wslc) | Learn about WSL Containers and the WSL Container SDK |
| [Install WSL](https://learn.microsoft.com/windows/wsl/install) | Step-by-step guide to installing WSL on Windows |
| [GPU Support in WSL](https://learn.microsoft.com/windows/wsl/tutorials/gpu-compute) | Set up GPU-accelerated workloads in WSL |
| [WinUI 3 Documentation](https://learn.microsoft.com/windows/apps/winui/winui3/) | Build modern Windows desktop apps with WinUI |
| [Explore Microsoft Build 2026 Labs and Sessions](https://aka.ms/build26-next-steps) | Explore lab and session repos to further your learning from Microsoft Build |
| [Watch the session recording](https://aka.ms/build26/DEM346/youtube) | Watch the recorded Microsoft Build session. |


### 🌟 Microsoft Learn MCP Server

The Microsoft Learn MCP Server gives your AI agent direct access to Microsoft's official documentation — grounded, up-to-date answers about the products and services covered in this demo.

**Visual Studio Code** — One click installation: 

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Microsoft_Learn_MCP-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=microsoft-learn&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Flearn.microsoft.com%2Fapi%2Fmcp%22%7D)


**GitHub Copilot CLI** — Run this to install the Learn MCP Server as a plugin:
```
/plugin install microsoftdocs/mcp
```

For more info, other clients, and to post questions, visit the [Learn MCP Server repo](https://aka.ms/learnmcp).

## Content Owners

<table>
<tr>
    <td align="center"><a href="https://github.com/craigloewen-msft">
        <img src="https://github.com/craigloewen-msft.png" width="100px;" alt="Craig Loewen"/><br />
        <sub><b>Craig Loewen</b></sub></a><br />
            <a href="https://github.com/craigloewen-msft" title="talk">📢</a>
    </td>
    <td align="center"><a href="https://github.com/ptrivedi">
        <img src="https://github.com/ptrivedi.png" width="100px;" alt="Pooja Trivedi"/><br />
        <sub><b>Pooja Trivedi</b></sub></a><br />
            <a href="https://github.com/ptrivedi" title="talk">📢</a>
    </td>
</tr></table>

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

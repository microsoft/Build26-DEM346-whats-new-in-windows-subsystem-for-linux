# WSL Containers — BUILD 2026
## Slide Deck Outline

---

### Slide 1: Title / Splash

**Title:** WSL Containers

**Subtitle:** Running Linux Containers Natively on Windows

**Footer:** BUILD 2026 · Craig Loewen

**Visual guidance:** Full-bleed hero image — a stylized container ship or shipping containers blended with the Windows and Linux (Tux) logos. Deep blue / purple gradient background. Minimal text, bold modern typography.

---

### Slide 2: Overview — What Are WSL Containers?

**Headline:** Linux containers, built into Windows

**Key points (keep as short icon-paired phrases):**

- 🐧 Run Linux containers locally — no third-party runtime required
- 📦 Build, run, and manage containers with a first-party CLI
- 🔌 Embed Linux containers inside Windows apps with a native API
- 🏢 Enterprise-ready — Intune & MDE integration out of the box

**Visual guidance:** Split layout — left side has the four icon+phrase pairs, right side has a simple diagram showing "Windows → WSL VM → Container" stacked layers. Clean, airy whitespace.

---

### Slide 3: Demo — WSL Containers in Action

**Headline:** Demo

**Subtext:** Building and running a Linux container on Windows

**Visual guidance:** Large "DEMO" text centered on screen with a subtle terminal/code motif in the background (e.g., faint monospace code lines). Keep this slide nearly empty so audience attention goes to the live demo.

---

### Slide 4: Two Surfaces, One Runtime

**Headline:** CLI & API — Different doors, same engine

**Left column — Linux Container CLI:**

- Developer-facing command-line tool
- Familiar container workflow: `build`, `run`, `push`
- Volumes, port forwarding, interactive shells
- Think: *"built-in container CLI for Windows"*

**Right column — WSL Container API (WSLA):**

- Windows SDK for app developers
- Embed containers as app logic — invisible to end users
- Session-based lifecycle, image ingestion, file transfer
- Think: *"containers as a Windows platform capability"*

**Shared footer:** Both powered by containerd running inside a WSL-managed VM

**Visual guidance:** Two-column layout with a shared "engine" graphic at the bottom connecting both columns (e.g., a containerd/WSL gear icon). Use contrasting accent colors for CLI (terminal green) vs. API (Windows blue).

---

### Slide 5: Use Cases

**Headline:** Who is this for?

**Three cards/tiles:**

1. **🧑‍💻 Developers**
   - Built-in Linux container CLI on Windows
   - GPU, filesystem mounts, networking — all integrated

2. **🏗️ App Builders (ISVs)**
   - Ship Linux-powered features inside Windows apps
   - AI/ML models, backend services, dev environments
   - Parity with Apple's containerization APIs

3. **🏢 Enterprise IT**
   - Managed container workflows with Intune & MDE
   - Policy enforcement and compliance visibility
   - No opaque third-party VMs

**Visual guidance:** Three equal-width cards side by side, each with an icon, a bold title, and 2–3 short bullet phrases. Light background, colorful card headers.

---

### Slide 6: Demo — WSL Container API

**Headline:** Demo

**Subtext:** Embedding a Linux container inside a Windows app

**Visual guidance:** Same style as Slide 3 — large centered "DEMO" with a subtle Windows app wireframe + container icon motif in the background. Minimal text.

---

### Slide 7: Architecture (Placeholder)

**Headline:** Architecture

**Body:** *(To be added)*

**Visual guidance:** Reserve space for a full-slide architecture diagram. Suggested layout: layered diagram showing Windows Host → WSL VM → containerd → Containers, with callouts for networking (9P mounts, Hyper-V sockets) and management (Intune/MDE hooks).

---

### Slide 8: Thank You & Q&A

**Headline:** Thank you!

**Subtext:** Questions?

**Contact / links (small footer):**

- 📧 Craig Loewen
- 🔗 aka.ms/wsl

**Visual guidance:** Clean closing slide matching the title slide's color scheme. Large "Thank you!" with a smaller "Questions?" underneath. Optional: subtle reprise of the container/Windows/Linux graphic from the splash slide.

---

*Style notes for the entire deck:*

- *Aim for ≤ 20 words of body text per slide (excluding headlines)*
- *Use icons, diagrams, and whitespace instead of bullet walls*
- *Color palette: deep blues/purples with accent green (Linux/terminal) and Windows blue*
- *Font: modern sans-serif (Segoe UI, Inter, or similar)*
- *All demo slides should be visually sparse — they are transition cues, not content slides*

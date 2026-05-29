# GPU Galaxy Collision Demo

Real-time N-body galaxy collision simulation powered by **CUDA** on an NVIDIA GPU,
running inside a Linux container via **wslc**.

Two spiral galaxies — each with thousands of gravitationally-bound stars — collide
and merge in real time. The simulation runs entirely on the GPU using a custom CUDA
kernel, and streams the results to your browser over WebSocket.

![Architecture: wslc → Linux container → CUDA N-body → WebSocket → Browser](https://img.shields.io/badge/GPU-CUDA%20Accelerated-76b900?style=for-the-badge&logo=nvidia)

## Quick Start

**Build the container image:**

```powershell
wslc build -t gpu-nbody-demo .
```

**Run the demo:**

```powershell
wslc run --gpus all -p 8080:8080 --rm gpu-nbody-demo
```

**Open your browser to:**

```
http://localhost:8080
```

## Controls

| Control | Description |
|---------|-------------|
| **Particle selector** | Choose 5K / 10K / 20K / 30K / 50K particles |
| **⟳ Reset** | Restart the simulation |
| **🎥 Auto Camera** | Toggle cinematic orbit camera |
| **✨ Trails** | Toggle particle motion trails |
| **Mouse drag** | Rotate view (when auto camera is off) |
| **Scroll wheel** | Zoom in/out |

## How It Works

1. **CUDA Kernel** — A shared-memory tiled all-pairs gravitational force kernel runs on the GPU,
   computing O(n²) particle interactions with Plummer softening
2. **Leapfrog Integration** — Symplectic velocity-Verlet integration preserves energy and keeps
   the simulation stable over long runs
3. **Binary WebSocket** — Particle positions and velocities stream as packed Float32Arrays
   at ~30fps to the browser
4. **WebGL Rendering** — Three.js renders particles with additive blending, velocity-based
   coloring (blue → cyan → white → yellow → red), and motion trail persistence

## Requirements

- NVIDIA GPU with CUDA support
- `wslc` with `--gpus` support
- A web browser

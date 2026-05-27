# Kernel Vision: Inside Neural Network Optimization

Dissect a model → Watch it learn → See the compiler optimize it.

Five visual stages:
1. **3D Weight Landscape** — Q-projection kernel weights rendered as 3D surfaces across layers
2. **Attention Optics** — 16-panel heatmap grid showing how each attention head "sees" tokens
3. **Live Surgery** — Real-time 4-panel dashboard (weight Δ, gradient flow, loss curve, attention drift) during fine-tuning
4. **Kernel Fusion X-Ray** — Conceptual before/after computational graph showing how `torch.compile` fuses ops
5. **The Showdown** — Animated head-to-head race: compiled vs eager mode with dramatic speedup reveal

## Run

```powershell
cd build-demo
wslc.exe volume create hf-cache
wslc.exe build -t kernel-vision -f Containerfile .
wslc.exe run -it --rm -p 8888:8888 -v hf-cache:/root/.cache/huggingface kernel-vision
```

Open http://localhost:8888 and run all cells.

## GPU mode

```powershell
wslc.exe run -it --rm --gpus all -p 8888:8888 -v hf-cache:/root/.cache/huggingface kernel-vision
```

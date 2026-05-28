<template>
  <div
    class="slide arch-slide"
    :class="[{ active: isActive, 'exit-left': isExitLeft }, `storage-phase-${phase}`]"
    id="slide-arch-storage"
  >
    <span class="tag fade-up" style="background:rgba(124,58,237,0.1);color:#6d28d9;border:1px solid rgba(124,58,237,0.25);">Deep Dive</span>
    <h2 class="fade-up" style="font-size:2rem; margin-bottom:0.2rem;">Architecture Details — Storage</h2>

    <div class="arch-diagram fade-up" ref="diagramRef">

      <!-- SVG connection arrows -->
      <svg v-if="arrows.length" class="arch-arrow-overlay">
        <defs>
          <marker id="ahs-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed" />
          </marker>
          <marker id="ahs-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0891b2" />
          </marker>
          <marker id="ahs-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#059669" />
          </marker>
          <marker id="ahs-amber" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#d97706" />
          </marker>
        </defs>
        <template v-for="(a, i) in arrows" :key="i">
          <path :d="a.path" fill="none"
            :stroke="a.color" :stroke-width="a.strokeWidth + 6" stroke-linecap="round"
            opacity="0.08" />
          <path :d="a.path" fill="none"
            stroke="rgba(255,255,255,0.8)" :stroke-width="a.strokeWidth + 2" stroke-linecap="round" />
          <path :d="a.path" fill="none"
            :stroke="a.color" :stroke-width="a.strokeWidth" :marker-end="a.marker"
            :stroke-dasharray="a.dashed ? '8 5' : 'none'" stroke-linecap="round" />
          <rect v-if="a.label"
            :x="a.labelX - a.label.length * 4.3 - 5" :y="a.labelY - 8"
            :width="a.label.length * 8.6 + 10" height="20"
            rx="4" fill="rgba(255,255,255,0.9)" />
          <text v-if="a.label" :x="a.labelX" :y="a.labelY"
            :fill="a.labelColor" :font-size="a.labelSize || 13" font-weight="700"
            text-anchor="middle" dominant-baseline="middle"
            font-family="'Segoe UI', system-ui, sans-serif"
            letter-spacing="0.06em">
            {{ a.label }}
          </text>
        </template>
      </svg>

      <!-- ═══ Your Machine ═══ -->
      <div class="arch-machine">
        <div class="arch-machine-label">Your Machine</div>

        <div class="arch-machine-content">

          <!-- ── Windows OS ── -->
          <div class="arch-zone arch-zone-win">
            <div class="arch-zone-label win-label">Windows OS</div>

            <div class="arch-win-grid">
              <!-- Windows Application -->
              <div class="arch-win-app-box">
                <div class="arch-box-title">Windows Application</div>
                <div class="arch-app-flow">
                  <span class="arch-chip chip-blue">Executable</span>
                  <span class="arch-connector">
                    <span class="arch-connector-line"></span>
                    <span class="arch-connector-label">LoadLibrary()</span>
                    <span class="arch-connector-arrow">▸</span>
                  </span>
                  <span class="arch-chip chip-purple" ref="dllRef">wslcsdk.dll</span>
                </div>
                <div class="arch-vhd-pos arch-reveal">
                  <div class="arch-storage-card storage-win" ref="vhdRef">Storage VHD</div>
                </div>
              </div>

              <!-- wslservice.exe -->
              <div class="arch-service-pos">
                <span class="arch-chip chip-pink" ref="serviceRef">wslservice.exe</span>
              </div>

              <!-- WSL Containers CLI -->
              <div class="arch-wslc-pos">
                <div class="arch-win-cli-box">
                  <div class="arch-box-title cli-title">WSL Containers CLI</div>
                  <span class="arch-chip chip-blue" ref="wslcRef">wslc.exe</span>
                  <div class="arch-vhdx-pos arch-reveal">
                    <div class="arch-storage-card storage-win" ref="vhdxRef">%localappdata%\wsla\storage.vhdx</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ── Linux Virtual Machine ── -->
          <div class="arch-zone arch-zone-linux">
            <div class="arch-zone-label linux-label">Linux Virtual Machine</div>

            <div class="arch-linux-layout">
              <div class="arch-moby-pos">
                <span class="arch-chip chip-green" ref="mobyRef">container runtime (moby)</span>
              </div>
              <div class="arch-docker-pos arch-reveal" :style="{ transform: `translateY(${dockerOffset}px)` }">
                <div class="arch-storage-card storage-linux" ref="dockerRef">/var/lib/&lt;container-storage&gt;</div>
              </div>
            </div>
          </div>

          <!-- ── Hypervisor ── -->
          <div class="arch-layer arch-hypervisor">Hypervisor</div>

        </div>
      </div>

      <!-- ── Hardware ── -->
      <div class="arch-layer arch-hardware">Hardware</div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
  phase: { type: Number, default: 1 },
})

const diagramRef = ref(null)
const dllRef = ref(null)
const serviceRef = ref(null)
const wslcRef = ref(null)
const mobyRef = ref(null)
const dockerRef = ref(null)
const vhdRef = ref(null)
const vhdxRef = ref(null)
const arrows = ref([])
const dockerOffset = ref(0)

function pos(el, side) {
  if (!el || !diagramRef.value) return null
  const c = diagramRef.value.getBoundingClientRect()
  const r = el.getBoundingClientRect()
  const cx = r.left + r.width / 2 - c.left
  const cy = r.top + r.height / 2 - c.top
  switch (side) {
    case 'right':  return { x: r.right - c.left, y: cy }
    case 'left':   return { x: r.left - c.left, y: cy }
    case 'top':    return { x: cx, y: r.top - c.top }
    case 'bottom': return { x: cx, y: r.bottom - c.top }
    default:       return { x: cx, y: cy }
  }
}

function smoothH(from, to) {
  const midX = (from.x + to.x) / 2
  return `M ${from.x} ${from.y} C ${midX} ${from.y}, ${midX} ${to.y}, ${to.x} ${to.y}`
}

function updateArrows() {
  const result = []

  // COM Y-fork: wslcsdk.dll + wslc.exe → wslservice.exe
  const dllP = pos(dllRef.value, 'right')
  const wslcP = pos(wslcRef.value, 'right')
  const svcP = pos(serviceRef.value, 'left')
  if (dllP && wslcP && svcP) {
    const srcMaxX = Math.max(dllP.x, wslcP.x)
    const mergeX = srcMaxX + (svcP.x - srcMaxX) * 0.4
    const mergeY = svcP.y
    const maxR = 12

    const topDy = Math.abs(mergeY - dllP.y)
    const tr = Math.max(2, Math.min(maxR, topDy * 0.4))
    result.push({
      path: [
        `M ${dllP.x} ${dllP.y}`,
        `L ${mergeX - tr} ${dllP.y}`,
        `Q ${mergeX} ${dllP.y}, ${mergeX} ${dllP.y + tr}`,
        `L ${mergeX} ${mergeY}`,
      ].join(' '),
      color: '#7c3aed', marker: 'none', strokeWidth: 2,
    })

    const botDy = Math.abs(wslcP.y - mergeY)
    const br = Math.max(2, Math.min(maxR, botDy * 0.4))
    result.push({
      path: [
        `M ${wslcP.x} ${wslcP.y}`,
        `L ${mergeX - br} ${wslcP.y}`,
        `Q ${mergeX} ${wslcP.y}, ${mergeX} ${wslcP.y - br}`,
        `L ${mergeX} ${mergeY}`,
      ].join(' '),
      color: '#7c3aed', marker: 'none', strokeWidth: 2,
    })

    result.push({
      path: `M ${mergeX} ${mergeY} L ${svcP.x} ${svcP.y}`,
      color: '#7c3aed', marker: 'url(#ahs-purple)', strokeWidth: 2,
      label: 'IPC', labelSize: 9,
      labelX: (mergeX + svcP.x) / 2,
      labelY: mergeY + 20,
      labelColor: '#6d28d9',
    })
  }

  // hvsocket: wslservice.exe → moby
  const a = pos(serviceRef.value, 'right')
  const b = pos(mobyRef.value, 'left')
  if (a && b) {
    result.push({
      path: smoothH(a, b),
      color: '#0891b2', marker: 'url(#ahs-cyan)', strokeWidth: 2, dashed: true,
      label: 'hvsocket',
      labelX: (a.x + b.x) / 2,
      labelY: (a.y + b.y) / 2 - 14,
      labelColor: '#0e7490',
    })
  }

  // Phase 2+: moby → /var/lib/<container-storage> ("Writes to")
  if (props.phase >= 2) {
    const mobyBot = pos(mobyRef.value, 'bottom')
    const dockerTop = pos(dockerRef.value, 'top')
    if (mobyBot && dockerTop) {
      result.push({
        path: `M ${mobyBot.x} ${mobyBot.y} L ${dockerTop.x} ${dockerTop.y}`,
        color: '#059669', marker: 'url(#ahs-green)', strokeWidth: 2,
        label: 'Writes to',
        labelX: mobyBot.x + 50,
        labelY: (mobyBot.y + dockerTop.y) / 2,
        labelColor: '#047857',
      })
    }
  }

  // Phase 3: /var/lib/<container-storage> → Storage VHD + vhdx ("Backed by" Y-fork)
  if (props.phase >= 3) {
    const dockerP = pos(dockerRef.value, 'left')
    const vhdP = pos(vhdRef.value, 'right')
    const vhdxP = pos(vhdxRef.value, 'right')

    if (dockerP && vhdP && vhdxP) {
      const tgtMaxX = Math.max(vhdP.x, vhdxP.x)
      const forkX = tgtMaxX + (dockerP.x - tgtMaxX) * 0.55
      const forkY = dockerP.y
      const maxR = 12

      // Stem: docker → fork point (straight horizontal)
      result.push({
        path: `M ${dockerP.x} ${dockerP.y} L ${forkX} ${forkY}`,
        color: '#d97706', marker: 'none', strokeWidth: 2,
        label: 'Backed by',
        labelX: (dockerP.x + forkX) / 2,
        labelY: forkY - 14,
        labelColor: '#d97706',
      })

      // Top branch: fork → Storage VHD (up then left)
      const topDy = Math.abs(forkY - vhdP.y)
      const tr = Math.max(2, Math.min(maxR, topDy * 0.4))
      result.push({
        path: [
          `M ${forkX} ${forkY}`,
          `L ${forkX} ${vhdP.y + tr}`,
          `Q ${forkX} ${vhdP.y}, ${forkX - tr} ${vhdP.y}`,
          `L ${vhdP.x} ${vhdP.y}`,
        ].join(' '),
        color: '#d97706', marker: 'url(#ahs-amber)', strokeWidth: 2,
      })

      // Bottom branch: fork → vhdx path (down then left)
      const botDy = Math.abs(vhdxP.y - forkY)
      const br = Math.max(2, Math.min(maxR, botDy * 0.4))
      result.push({
        path: [
          `M ${forkX} ${forkY}`,
          `L ${forkX} ${vhdxP.y - br}`,
          `Q ${forkX} ${vhdxP.y}, ${forkX - br} ${vhdxP.y}`,
          `L ${vhdxP.x} ${vhdxP.y}`,
        ].join(' '),
        color: '#d97706', marker: 'url(#ahs-amber)', strokeWidth: 2,
      })
    }
  }

  arrows.value = result
}

// Compute docker offset immediately on first activation, before any phase transition
watch(() => props.isActive, async (active) => {
  if (active && dockerOffset.value === 0) {
    await nextTick()
    // Read positions immediately — docker has no translateY, VHD/vhdx have 12px
    if (vhdRef.value && vhdxRef.value && dockerRef.value && diagramRef.value) {
      const c = diagramRef.value.getBoundingClientRect()
      const vhdR = vhdRef.value.getBoundingClientRect()
      const vhdxR = vhdxRef.value.getBoundingClientRect()
      const dockerR = dockerRef.value.getBoundingClientRect()
      const vhdY = vhdR.top + vhdR.height / 2 - c.top - 12
      const vhdxY = vhdxR.top + vhdxR.height / 2 - c.top - 12
      const dockerY = dockerR.top + dockerR.height / 2 - c.top
      const midY = (vhdY + vhdxY) / 2
      dockerOffset.value = midY - dockerY
    }
  }
}, { immediate: true })

watch([() => props.isActive, () => props.phase], async ([active]) => {
  if (active) {
    await nextTick()
    setTimeout(updateArrows, 520)
  }
})
</script>

<style scoped>
#slide-arch-storage::before { background: var(--accent-purple); bottom: -300px; left: -100px; }
#slide-arch-storage {
  text-align: center;
  gap: 1.2rem;
  padding: 2.5rem 3rem;
  transform: scale(0.95);
  transition: opacity 0.65s ease, transform 0.65s ease;
}

#slide-arch-storage.active {
  transform: scale(1);
}

/* Override Windows grid — no vhdx row needed now */
.arch-win-grid {
  grid-template-areas:
    "app    svc"
    "wslc   svc";
  grid-template-rows: 1fr 1fr;
}

.arch-vhdx-pos {
  margin-top: 0.5rem;
}

/* Ensure linux layout fills available space */
.arch-linux-layout {
  flex: 1;
}

/* Storage card boxes */
.arch-storage-card {
  border-radius: 10px;
  padding: 0.45rem 1rem;
  text-align: center;
  font-weight: 700;
  font-size: 1.1rem;
  font-family: 'Courier New', Consolas, monospace;
  letter-spacing: 0.02em;
}

.storage-linux {
  border: 1.5px solid rgba(5,150,105,0.3);
  background: rgba(5,150,105,0.06);
  color: #047857;
}

.storage-win {
  border: 1.5px solid rgba(37,99,235,0.3);
  background: rgba(37,99,235,0.06);
  color: #1d4ed8;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.arch-vhd-pos {
  margin-top: 0.5rem;
}

/* Phase reveal transitions */
.arch-docker-pos {
  transition: opacity 0.5s ease, visibility 0.5s;
}
.arch-vhd-pos,
.arch-vhdx-pos {
  transition: opacity 0.5s ease, transform 0.5s ease, visibility 0.5s;
}

/* Phase 1: hide new storage boxes */
.storage-phase-1 .arch-docker-pos {
  opacity: 0; visibility: hidden;
}
.storage-phase-1 .arch-vhd-pos,
.storage-phase-1 .arch-vhdx-pos {
  opacity: 0; visibility: hidden; transform: translateY(12px);
}

/* Phase 2: docker visible, VHD + vhdx hidden */
.storage-phase-2 .arch-vhd-pos,
.storage-phase-2 .arch-vhdx-pos {
  opacity: 0; visibility: hidden; transform: translateY(12px);
}

/* Phase 3: everything visible */
</style>

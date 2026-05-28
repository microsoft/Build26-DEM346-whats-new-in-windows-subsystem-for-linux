<template>
  <div
    class="slide arch-slide"
    :class="[{ active: isActive, 'exit-left': isExitLeft }, `cmd-phase-${phase}`]"
    id="slide-arch-command"
  >
    <span class="tag fade-up" style="background:rgba(124,58,237,0.1);color:#6d28d9;border:1px solid rgba(124,58,237,0.25);">Deep Dive</span>
    <h2 class="fade-up cmd-title"><code>wslc run -it -v C:\data:/data debian:latest</code></h2>

    <div class="arch-diagram fade-up" ref="diagramRef">

      <!-- SVG connection arrows -->
      <svg v-if="arrows.length" class="arch-arrow-overlay">
        <defs>
          <marker id="ahc-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed" />
          </marker>
          <marker id="ahc-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0891b2" />
          </marker>
          <marker id="ahc-emerald" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#059669" />
          </marker>
          <marker id="ahc-amber" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
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
                </div>
              </div>

              <!-- C:\data host path -->
              <div class="arch-cdata-pos arch-reveal">
                <div class="arch-volume-card" ref="cdataRef">C:\data</div>
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

              <div class="arch-debian-pos arch-reveal">
                <div class="arch-ctr-card" ref="debianRef">
                  <div class="arch-ctr-title">debian:latest</div>
                  <span class="arch-chip chip-teal">/bin/bash</span>
                </div>
              </div>

              <div class="arch-data-pos arch-reveal">
                <div class="arch-volume-card" ref="dataRef">/data</div>
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
const debianRef = ref(null)
const dataRef = ref(null)
const cdataRef = ref(null)
const arrows = ref([])

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
      color: '#7c3aed', marker: 'url(#ahc-purple)', strokeWidth: 2,
      label: 'IPC', labelSize: 9,
      labelX: (mergeX + svcP.x) / 2,
      labelY: mergeY + 24,
      labelColor: '#6d28d9',
    })
  }

  // hvsocket: wslservice.exe → moby
  const a = pos(serviceRef.value, 'right')
  const b = pos(mobyRef.value, 'left')
  if (a && b) {
    result.push({
      path: smoothH(a, b),
      color: '#0891b2', marker: 'url(#ahc-cyan)', strokeWidth: 2, dashed: true,
      label: 'hvsocket',
      labelX: (a.x + b.x) / 2,
      labelY: (a.y + b.y) / 2 - 14,
      labelColor: '#0e7490',
    })
  }

  // run: moby → debian:latest (phase 2+)
  if (props.phase >= 2) {
    const mb = pos(mobyRef.value, 'bottom')
    const dt = pos(debianRef.value, 'top')
    if (mb && dt) {
      result.push({
        path: `M ${mb.x} ${mb.y} L ${dt.x} ${dt.y}`,
        color: '#059669', marker: 'url(#ahc-emerald)', strokeWidth: 2,
        label: 'run',
        labelX: mb.x + 40,
        labelY: (mb.y + dt.y) / 2,
        labelColor: '#047857',
      })
    }
  }

  // volume: debian:latest → /data (phase 3+)
  if (props.phase >= 3) {
    const debBot = pos(debianRef.value, 'bottom')
    const dataTop = pos(dataRef.value, 'top')
    if (debBot && dataTop) {
      result.push({
        path: `M ${debBot.x} ${debBot.y} L ${dataTop.x} ${dataTop.y}`,
        color: '#d97706', marker: 'url(#ahc-amber)', strokeWidth: 2,
        label: 'volume',
        labelX: debBot.x + 46,
        labelY: (debBot.y + dataTop.y) / 2,
        labelColor: '#d97706',
      })
    }
  }

  // virtiofs: /data → C:\data (phase 4)
  if (props.phase >= 4) {
    const dataP = pos(dataRef.value, 'left')
    const cdataP = pos(cdataRef.value, 'right')
    if (dataP && cdataP) {
      result.push({
        path: smoothH(dataP, cdataP),
        color: '#d97706', marker: 'url(#ahc-amber)', strokeWidth: 2, dashed: true,
        label: 'virtiofs',
        labelX: (dataP.x + cdataP.x) / 2,
        labelY: (dataP.y + cdataP.y) / 2 - 14,
        labelColor: '#d97706',
      })
    }
  }

  arrows.value = result
}

watch([() => props.isActive, () => props.phase], async ([active]) => {
  if (active) {
    await nextTick()
    setTimeout(updateArrows, 520)
  }
})
</script>

<style scoped>
#slide-arch-command::before { background: var(--accent-purple); bottom: -300px; left: -100px; }
#slide-arch-command {
  text-align: center;
  gap: 1.2rem;
  padding: 2.5rem 3rem;
  transform: scale(0.95);
  transition: opacity 0.65s ease, transform 0.65s ease;
}

#slide-arch-command.active {
  transform: scale(1);
}

.cmd-title {
  font-size: 1.6rem;
  margin-bottom: 0.2rem;
}

.cmd-title code {
  font-family: 'Courier New', Consolas, monospace;
  background: rgba(37,99,235,0.08);
  border: 1px solid rgba(37,99,235,0.25);
  border-radius: 8px;
  padding: 0.2rem 0.6rem;
  color: #1d4ed8;
  font-size: 1.4rem;
  letter-spacing: 0.01em;
}

/* Override Windows grid layout */
.arch-win-grid {
  grid-template-areas:
    "app    svc"
    "wslc   svc"
    "cdata  .";
  grid-template-columns: 1fr auto;
  grid-template-rows: 1fr 1fr auto;
}

.arch-cdata-pos {
  grid-area: cdata;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 0.5rem;
}

/* Ensure linux layout fills available space */
.arch-linux-layout {
  flex: 1;
}

.arch-debian-pos {
  display: flex;
  justify-content: center;
}

.arch-data-pos {
  display: flex;
  justify-content: center;
}

.arch-ctr-card {
  border: 1.5px solid rgba(13,148,136,0.3);
  background: rgba(13,148,136,0.04);
  border-radius: 10px;
  padding: 0.65rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.arch-ctr-title {
  font-size: 1.01rem;
  font-weight: 700;
  color: #0f766e;
  letter-spacing: 0.03em;
}

.arch-volume-card {
  border-radius: 8px;
  padding: 0.35rem 0.9rem;
  text-align: center;
  font-weight: 700;
  font-size: 1.1rem;
  font-family: 'Courier New', Consolas, monospace;
  letter-spacing: 0.02em;
  border: 1.5px solid rgba(217,119,6,0.3);
  background: rgba(217,119,6,0.06);
  color: #b45309;
}

/* Phase reveal transitions */
.arch-debian-pos,
.arch-data-pos,
.arch-cdata-pos {
  transition: opacity 0.5s ease, transform 0.5s ease, visibility 0.5s;
}

/* Phase 1: hide debian, /data, C:\data */
.cmd-phase-1 .arch-debian-pos,
.cmd-phase-1 .arch-data-pos,
.cmd-phase-1 .arch-cdata-pos {
  opacity: 0; visibility: hidden; transform: translateY(12px);
}

/* Phase 2: show debian, hide /data + C:\data */
.cmd-phase-2 .arch-data-pos,
.cmd-phase-2 .arch-cdata-pos {
  opacity: 0; visibility: hidden; transform: translateY(12px);
}

/* Phase 3: show /data, hide C:\data */
.cmd-phase-3 .arch-cdata-pos {
  opacity: 0; visibility: hidden; transform: translateY(12px);
}

/* Phase 4: everything visible */
</style>

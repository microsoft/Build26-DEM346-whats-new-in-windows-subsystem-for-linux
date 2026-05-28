<template>
  <div
    class="slide arch-slide"
    :class="[
      { active: isActive, 'exit-left': isExitLeft },
      `arch-phase-${phase}`
    ]"
    id="slide-arch"
  >
    <span class="tag fade-up" style="background:rgba(124,58,237,0.1);color:#6d28d9;border:1px solid rgba(124,58,237,0.25);">Deep Dive</span>
    <h2 class="fade-up" style="font-size:2rem; margin-bottom:0.2rem;">Architecture Details</h2>

    <div class="arch-diagram fade-up" ref="diagramRef">

      <!-- SVG connection arrows -->
      <svg v-if="arrows.length" class="arch-arrow-overlay">
        <defs>
          <marker id="ah-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed" />
          </marker>
          <marker id="ah-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0891b2" />
          </marker>
          <marker id="ah-emerald" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#059669" />
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
              <div class="arch-win-app-box arch-reveal">
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
              <div class="arch-service-pos arch-reveal">
                <span class="arch-chip chip-pink" ref="serviceRef">wslservice.exe</span>
              </div>

              <!-- WSL Containers CLI -->
              <div class="arch-wslc-pos arch-reveal">
                <div class="arch-win-cli-box">
                  <div class="arch-box-title cli-title">WSL Containers CLI</div>
                  <span class="arch-chip chip-blue" ref="wslcRef">wslc.exe</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ── Linux Virtual Machine ── -->
          <div class="arch-zone arch-zone-linux">
            <div class="arch-zone-label linux-label">Linux Virtual Machine</div>

            <div class="arch-linux-layout">
              <div class="arch-moby-pos arch-reveal">
                <span class="arch-chip chip-green" ref="mobyRef">container runtime (moby)</span>
              </div>

              <div class="arch-containers-row arch-reveal">
                <div class="arch-ctr-card" ref="debianRef">
                  <div class="arch-ctr-title">Debian container</div>
                  <span class="arch-chip chip-teal">/bin/bash</span>
                </div>
                <div class="arch-ctr-card" ref="nginxRef">
                  <div class="arch-ctr-title">nginx container</div>
                  <span class="arch-chip chip-teal">/usr/bin/nginx</span>
                </div>
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
  phase: {
    type: Number,
    default: 1,
  },
})

const diagramRef = ref(null)
const dllRef = ref(null)
const serviceRef = ref(null)
const wslcRef = ref(null)
const mobyRef = ref(null)
const debianRef = ref(null)
const nginxRef = ref(null)
const arrows = ref([])
const arrowKey = ref(0)

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

// Orthogonal elbow path with a smooth rounded corner
function elbowPath(from, to, startDir, maxRadius = 16) {
  const dx = Math.abs(to.x - from.x)
  const dy = Math.abs(to.y - from.y)
  const r = Math.max(2, Math.min(maxRadius, dx * 0.45, dy * 0.45))

  if (startDir === 'down') {
    const sx = Math.sign(to.x - from.x)
    return [
      `M ${from.x} ${from.y}`,
      `L ${from.x} ${to.y - r}`,
      `Q ${from.x} ${to.y}, ${from.x + r * sx} ${to.y}`,
      `L ${to.x} ${to.y}`,
    ].join(' ')
  }

  if (startDir === 'right') {
    const sy = Math.sign(to.y - from.y)
    return [
      `M ${from.x} ${from.y}`,
      `L ${to.x - r} ${from.y}`,
      `Q ${to.x} ${from.y}, ${to.x} ${from.y + r * sy}`,
      `L ${to.x} ${to.y}`,
    ].join(' ')
  }

  return `M ${from.x} ${from.y} L ${to.x} ${to.y}`
}

// Smooth horizontal S-curve for crossing zone boundaries
function smoothH(from, to) {
  const midX = (from.x + to.x) / 2
  return `M ${from.x} ${from.y} C ${midX} ${from.y}, ${midX} ${to.y}, ${to.x} ${to.y}`
}

function updateArrows() {
  const result = []

  if (props.phase >= 3) {
    // Merged COM Y-fork: wslcsdk.dll + wslc.exe → wslservice.exe
    const dllP = pos(dllRef.value, 'right')
    const wslcP = pos(wslcRef.value, 'right')
    const svcP = pos(serviceRef.value, 'left')
    if (dllP && wslcP && svcP) {
      const srcMaxX = Math.max(dllP.x, wslcP.x)
      const mergeX = srcMaxX + (svcP.x - srcMaxX) * 0.4
      const mergeY = svcP.y
      const maxR = 12

      // Top branch: dll → merge
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

      // Bottom branch: wslc → merge
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

      // Stem: merge → service (straight horizontal line)
      result.push({
        path: `M ${mergeX} ${mergeY} L ${svcP.x} ${svcP.y}`,
        color: '#7c3aed', marker: 'url(#ah-purple)', strokeWidth: 2,
        label: 'IPC', labelSize: 9,
        labelX: (mergeX + svcP.x) / 2,
        labelY: mergeY + 24,
        labelColor: '#6d28d9',
      })
    }
  }

  if (props.phase >= 4) {
    // hvsocket: wslservice.exe → moby (smooth S-curve across zones)
    const a = pos(serviceRef.value, 'right')
    const b = pos(mobyRef.value, 'left')
    if (a && b) {
      result.push({
        path: smoothH(a, b),
        color: '#0891b2', marker: 'url(#ah-cyan)', strokeWidth: 2, dashed: true,
        label: 'hvsocket',
        labelX: (a.x + b.x) / 2,
        labelY: (a.y + b.y) / 2 - 14,
        labelColor: '#0e7490',
      })
    }
  }

  if (props.phase >= 5) {
    // moby → containers: symmetric Y-fork with rounded elbows
    const mb = pos(mobyRef.value, 'bottom')
    const dt = pos(debianRef.value, 'top')
    const nt = pos(nginxRef.value, 'top')
    if (mb && dt && nt) {
      const forkY = mb.y + (dt.y - mb.y) * 0.45
      const maxR = 12

      // Shared vertical stem (no arrowhead)
      result.push({
        path: `M ${mb.x} ${mb.y} L ${mb.x} ${forkY}`,
        color: '#059669', marker: 'none', strokeWidth: 2,
      })

      // Left branch → Debian
      const ldx = Math.abs(mb.x - dt.x)
      const ldy = Math.abs(dt.y - forkY)
      const lr = Math.max(2, Math.min(maxR, ldx * 0.4, ldy * 0.4))
      result.push({
        path: [
          `M ${mb.x} ${forkY}`,
          `L ${dt.x + lr} ${forkY}`,
          `Q ${dt.x} ${forkY}, ${dt.x} ${forkY + lr}`,
          `L ${dt.x} ${dt.y}`,
        ].join(' '),
        color: '#059669', marker: 'url(#ah-emerald)', strokeWidth: 2,
      })

      // Right branch → nginx
      const rdx = Math.abs(nt.x - mb.x)
      const rdy = Math.abs(nt.y - forkY)
      const rr = Math.max(2, Math.min(maxR, rdx * 0.4, rdy * 0.4))
      result.push({
        path: [
          `M ${mb.x} ${forkY}`,
          `L ${nt.x - rr} ${forkY}`,
          `Q ${nt.x} ${forkY}, ${nt.x} ${forkY + rr}`,
          `L ${nt.x} ${nt.y}`,
        ].join(' '),
        color: '#059669', marker: 'url(#ah-emerald)', strokeWidth: 2,
      })
    }
  }

  arrows.value = result
  arrowKey.value++
}

watch(() => props.phase, async () => {
  await nextTick()
  setTimeout(updateArrows, 520)
})

watch(() => props.isActive, async (val) => {
  if (val) {
    await nextTick()
    setTimeout(updateArrows, 520)
  }
})
</script>

<style scoped>
#slide-arch::before { background: var(--accent-purple); bottom: -300px; left: -100px; }
#slide-arch {
  text-align: center;
  gap: 1.2rem;
  padding: 2.5rem 3rem;
  transform: scale(0.95);
  transition: opacity 0.65s ease, transform 0.65s ease;
}

#slide-arch.active {
  transform: scale(1);
}
</style>

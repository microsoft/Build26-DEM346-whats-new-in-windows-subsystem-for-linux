<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-arch-overview">
    <span class="tag arch-ov-tag fade-up">Architecture Overview</span>
    <h2 class="fade-up" style="text-align:center;">Each app gets its own Linux VM</h2>

    <div class="arch-ov-stack fade-up">
      <!-- Apps row -->
      <div class="arch-ov-apps-row">
        <div class="arch-ov-app" v-for="app in apps" :key="app.name">
          <div class="arch-ov-app-label">{{ app.name }}</div>
          <div class="arch-ov-vm">
            <div class="arch-ov-vm-label">WSL Utility VM</div>
            <div class="arch-ov-containers">
              <div class="arch-ov-container" v-for="n in app.containers" :key="n">
                <span class="arch-ov-ctr-icon">📦</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Windows OS layer -->
      <div class="arch-ov-layer arch-ov-windows">
        <span>Windows OS</span>
      </div>

      <!-- Hyper-V layer -->
      <div class="arch-ov-layer arch-ov-hyperv">
        <span>Hyper-V</span>
      </div>

      <!-- Hardware layer -->
      <div class="arch-ov-layer arch-ov-hardware">
        <span>Hardware</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})

const apps = [
  { name: 'App A', containers: 3 },
  { name: 'App B', containers: 1 },
  { name: 'App C', containers: 2 },
]
</script>

<style scoped>
#slide-arch-overview::before { background: var(--accent-purple); bottom: -400px; right: -200px; }
#slide-arch-overview {
  gap: 2rem;
  transition: opacity 0.65s ease, transform 0.65s ease;
}

/* Zoom-in exit: scale up + fade when advancing to detail slide */
#slide-arch-overview.exit-left {
  opacity: 0;
  transform: scale(1.06);
}

.arch-ov-tag {
  background: rgba(124,58,237,0.1); color: #6d28d9;
  border: 1px solid rgba(124,58,237,0.25);
}

/* Diagram stack */
.arch-ov-stack {
  display: flex;
  flex-direction: column;
  gap: 0;
  max-width: 900px;
  width: 100%;
}

/* Base layer style */
.arch-ov-layer {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  border: 1px solid;
  text-align: center;
}

.arch-ov-hardware {
  background: rgba(71,85,105,0.08);
  border-color: rgba(71,85,105,0.3);
  color: #334155;
  border-radius: 0 0 14px 14px;
}

.arch-ov-hyperv {
  background: rgba(37,99,235,0.06);
  border-color: rgba(37,99,235,0.3);
  color: #1d4ed8;
  border-bottom: none;
}

.arch-ov-windows {
  background: rgba(37,99,235,0.04);
  border-color: rgba(37,99,235,0.25);
  color: #1d4ed8;
  padding: 0.7rem 1.5rem;
  font-size: 0.9rem;
  border-bottom: none;
}

/* Apps row */
.arch-ov-apps-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.8rem;
  padding: 1rem;
  background: rgba(37,99,235,0.03);
  border: 1px solid rgba(37,99,235,0.25);
  border-bottom: none;
  border-radius: 14px 14px 0 0;
}

/* Each app card */
.arch-ov-app {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 12px;
  padding: 0.8rem;
  text-align: center;
}

.arch-ov-app-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

/* Linux VM box inside each app */
.arch-ov-vm {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(5,150,105,0.06);
  border: 1px solid rgba(5,150,105,0.3);
  border-radius: 10px;
  padding: 0.6rem;
}

.arch-ov-vm-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #047857;
  text-align: center;
}

/* Container boxes */
.arch-ov-containers {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
  flex-wrap: wrap;
}

.arch-ov-container {
  background: rgba(124,58,237,0.08);
  border: 1px solid rgba(124,58,237,0.25);
  border-radius: 8px;
  padding: 0.35rem 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arch-ov-ctr-icon {
  font-size: 1.1rem;
}
</style>

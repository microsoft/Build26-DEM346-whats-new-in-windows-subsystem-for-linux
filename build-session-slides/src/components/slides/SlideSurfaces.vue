<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-surfaces">
    <span class="tag surfaces-tag fade-up">Interaction Surfaces</span>
    <h2 class="fade-up" style="text-align:center; margin-bottom:0.5rem;">Different doors, same engine</h2>
    <div class="surfaces-layout">
      <div class="surface-col cli">
        <div class="col-icon">⌨️</div>
        <h3>WSL Container CLI</h3>
        <span class="tagline">"Built-in container CLI for Windows"</span>
        <ul>
          <li>Developer-facing command-line tool</li>
          <li>Familiar workflow: build, run, push</li>
          <li>Volumes, GPU access, &amp; port forwarding</li>
          <li>Interactive shells &amp; compatibility with VS Code remote</li>
        </ul>
      </div>
      <div class="surfaces-divider">
        <div class="line"></div>
        <span>OR</span>
        <div class="line"></div>
      </div>
      <div class="surface-col api">
        <div class="col-icon">🧩</div>
        <h3>WSL Container API</h3>
        <span class="tagline">"Containers as a platform capability"</span>
        <ul>
          <li>Nuget package for WSL containers API</li>
          <li>Embed containers — invisible to users</li>
          <li>Session-based lifecycle control</li>
          <li>Resource sharing with the host: Files, GPU, network</li>
        </ul>
      </div>
    </div>
    <div class="shared-engine fade-up">
      Both using <strong>the same technology</strong> that powers <strong>WSL today</strong>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})
</script>

<style scoped>
#slide-surfaces::before { background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)); bottom: -300px; right: -200px; }
#slide-surfaces { gap: 2rem; }

.surfaces-tag {
  background: rgba(5,150,105,0.1); color: #047857;
  border: 1px solid rgba(5,150,105,0.25);
}

.surfaces-layout {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  max-width: 1100px;
  width: 100%;
  align-items: stretch;
}

.surface-col {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 2.2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.surface-col.cli { border-top: 3px solid var(--accent-green); }
.surface-col.api { border-top: 3px solid var(--accent-blue); }

.surface-col .col-icon {
  font-size: 2.2rem;
  margin-bottom: 0.2rem;
}

.surface-col h3 {
  font-size: 1.4rem; font-weight: 700; color: var(--text-primary);
}

.surface-col .tagline {
  font-size: 0.95rem; color: var(--text-muted); font-style: italic;
}

.surface-col ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.surface-col li {
  font-size: 0.95rem;
  color: var(--text-secondary);
  padding-left: 1.4rem;
  position: relative;
}

.surface-col.cli li::before {
  content: '▸'; position: absolute; left: 0; color: var(--accent-green);
}

.surface-col.api li::before {
  content: '▸'; position: absolute; left: 0; color: var(--accent-blue);
}

.surfaces-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.surfaces-divider .line {
  width: 1px; height: 60px;
  background: var(--card-border);
}

.shared-engine {
  text-align: center;
  margin-top: 0.5rem;
  padding: 0.8rem 2rem;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.shared-engine strong { color: var(--text-primary); }
</style>

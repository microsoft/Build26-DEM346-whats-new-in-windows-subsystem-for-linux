<template>
  <div class="slide demo-slide" :class="{ active: isActive, 'exit-left': isExitLeft }" :id="slideId">
    <h1 class="demo-title fade-up" :style="titleStyle">DEMO</h1>
    <h3 class="fade-up">{{ subtitle }}</h3>
    <div class="terminal-hint fade-up" :class="{ 'api-hint': variant === 'api' }">
      <span>{{ command }}</span>
      <span class="cursor"></span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
  variant: {
    type: String,
    default: 'cli',
    validator: (v) => ['cli', 'api'].includes(v),
  },
})

const slideId = computed(() => props.variant === 'cli' ? 'slide-demo1' : 'slide-demo2')

const titleStyle = computed(() => props.variant === 'cli'
  ? 'color:#047857;'
  : 'color:#1d4ed8;'
)

const subtitle = computed(() => props.variant === 'cli'
  ? 'Building & running a Linux container on Windows'
  : 'Embedding a Linux container inside a Windows app'
)

const command = computed(() => props.variant === 'cli'
  ? '$ wslc container run --rm -it ubuntu bash'
  : 'WslcContainerCreate(m_session, &containerSettings, &m_container, &containerErrorMessage);'
)

</script>

<style scoped>
#slide-demo1::before { background: var(--accent-green); top: 50%; left: 50%; transform: translate(-50%,-50%); width: 600px; height: 600px; opacity: 0.12; }
#slide-demo2::before { background: var(--accent-blue); top: 50%; left: 50%; transform: translate(-50%,-50%); width: 600px; height: 600px; opacity: 0.12; }

.demo-slide { text-align: center; gap: 1.5rem; }

.demo-title {
  font-size: 6rem;
  font-weight: 800;
  letter-spacing: 0.3em;
  margin: 0;
  text-transform: uppercase;
}

.demo-slide h3 { font-size: 1.3rem; font-weight: 400; }

.terminal-hint {
  display: inline-flex; align-items: center; gap: 0.6rem;
  background: rgba(5,150,105,0.08);
  border: 1px solid rgba(5,150,105,0.25);
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #047857;
  margin-top: 0.5rem;
}

.terminal-hint.api-hint {
  background: rgba(37,99,235,0.08);
  border-color: rgba(37,99,235,0.25);
  color: #1d4ed8;
}

.terminal-hint .cursor {
  display: inline-block;
  width: 8px; height: 18px;
  background: currentColor;
  animation: blink 1s step-end infinite;
  opacity: 0.7;
}

@keyframes blink { 50% { opacity: 0; } }
</style>

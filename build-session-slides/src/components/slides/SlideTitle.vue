<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-title">
    <span class="tag event-tag fade-up">BUILD 2026</span>
    <img src="/MainIcon.png" alt="WSL Containers" class="wsl-icon fade-up" />
    <h1 class="fade-up">WSL Containers</h1>
    <p class="fade-up" style="color:var(--text-muted); font-size:1rem; margin-top:0.5rem;">Pooja Trivedi &amp; Craig Loewen</p>
  </div>
</template>

<script setup>
defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})
</script>

<style scoped>
#slide-title::before { background: var(--accent-purple); top: -300px; right: -200px; }
#slide-title { text-align: center; gap: 1.2rem; }

.wsl-icon {
  width: 128px;
  height: 128px;
  object-fit: contain;
}

#slide-title h1 {
  background: linear-gradient(135deg, #1e293b 0%, #7c3aed 50%, #2563eb 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 5rem;
}

.subtitle {
  font-size: 1.4rem; color: var(--text-secondary); font-weight: 400;
}

.event-tag {
  background: rgba(124,58,237,0.1); color: #6d28d9;
  border: 1px solid rgba(124,58,237,0.3);
}
</style>

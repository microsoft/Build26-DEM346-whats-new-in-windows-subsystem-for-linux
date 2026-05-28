<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-wellsfargo">
    <span class="tag fade-up" style="background:rgba(5,150,105,0.1);color:#047857;border:1px solid rgba(5,150,105,0.25);">Partner</span>
    <div class="logo-showcase fade-up">
      <img src="/wellsfargologo.png" alt="Wells Fargo" class="logo-wide" />
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
#slide-wellsfargo::before { background: var(--accent-green); top: 50%; left: 50%; transform: translate(-50%,-50%); width: 600px; height: 600px; opacity: 0.12; }

#slide-wellsfargo { text-align: center; gap: 1.5rem; }

.logo-showcase {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-showcase .logo-wide {
  max-width: 420px;
  height: auto;
  border-radius: 12px;
  object-fit: contain;
  filter: drop-shadow(0 4px 24px rgba(0,0,0,0.15));
}
</style>

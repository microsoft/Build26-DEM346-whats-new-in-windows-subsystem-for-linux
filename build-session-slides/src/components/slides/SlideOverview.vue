<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-overview">
    <span class="tag overview-tag fade-up">Overview</span>
    <h2 class="fade-up">Linux containers, built into Windows</h2>
    <div class="feature-grid">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <div class="icon">{{ feature.icon }}</div>
        <div>
          <h4>{{ feature.title }}</h4>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})

const features = [
  { icon: '🐧', title: 'Run Locally', description: 'Linux Containers are a 1st class feature on Windows' },
  { icon: '📦', title: 'Part of WSL', description: 'Shipped as a new feature in WSL' },
  { icon: '🏢', title: 'Enterprise Ready', description: 'Intune & MDE integration out of the box' },
]
</script>

<style scoped>
#slide-overview::before { background: var(--accent-blue); bottom: -400px; left: -200px; }
#slide-overview { gap: 2.5rem; }

.overview-tag {
  background: rgba(37,99,235,0.1); color: #1d4ed8;
  border: 1px solid rgba(37,99,235,0.25);
}

#slide-overview h2 { text-align: center; }

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.8rem;
  max-width: 1000px;
  width: 100%;
}

.feature-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 2rem 1.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.2rem;
  transition: border-color 0.3s, background 0.3s, transform 0.3s;
}

.feature-card:hover {
  border-color: rgba(0,0,0,0.15);
  background: rgba(0,0,0,0.03);
  transform: translateY(-4px);
}

.feature-card .icon {
  font-size: 2.2rem;
  flex-shrink: 0;
  width: 56px; height: 56px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 14px;
}

.feature-card:nth-child(1) .icon { background: rgba(124,58,237,0.1); }
.feature-card:nth-child(2) .icon { background: rgba(5,150,105,0.1); }
.feature-card:nth-child(3) .icon { background: rgba(37,99,235,0.1); }

.feature-card h4 {
  font-size: 1.1rem; font-weight: 700; margin-bottom: 0.2rem;
}

.feature-card p {
  font-size: 0.92rem; color: var(--text-muted); line-height: 1.5;
  max-width: none;
}
</style>

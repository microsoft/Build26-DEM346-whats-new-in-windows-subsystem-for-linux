<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-usecases">
    <span class="tag usecases-tag fade-up">Use Cases</span>
    <h2 class="fade-up" style="text-align:center;">Who is this for?</h2>
    <div class="usecase-cards">
      <div class="usecase-card" v-for="uc in usecases" :key="uc.title">
        <div class="card-icon">{{ uc.icon }}</div>
        <h3>{{ uc.title }}</h3>
        <ul>
          <li v-for="item in uc.items" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})

const usecases = [
  {
    icon: '👩‍💻',
    title: 'Container Developers',
    items: [
      'Easier to get started, run and build Linux containers',
      'Integrated API and CLI - Opinionated approach',
      'Improvements to underlying VM tech used by everyone, e.g: Cross OS file performance speed',
    ],
  },
  {
    icon: '🏗️',
    title: 'App Builders & ISVs',
    items: [
      'Ship Linux-powered features inside Windows apps',
      'AI/ML models, backend services, cloud to local runtimes',
      'Build directly with Windows APIs',
    ],
  },
  {
    icon: '🏢',
    title: 'Enterprise IT',
    items: [
      'Managed container workflows with Intune & MDE',
      'Policy enforcement & compliance visibility',
      'No opaque VM solutions',
    ],
  },
]
</script>

<style scoped>
#slide-usecases::before { background: var(--accent-pink); top: -400px; left: 50%; }
#slide-usecases { gap: 2rem; }

.usecases-tag {
  background: rgba(219,39,119,0.1); color: #be185d;
  border: 1px solid rgba(219,39,119,0.25);
}

.usecase-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  max-width: 1100px;
  width: 100%;
}

.usecase-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  transition: transform 0.3s, border-color 0.3s;
}

.usecase-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0,0,0,0.15);
}

.usecase-card .card-icon {
  font-size: 2.4rem;
  margin-bottom: 0.3rem;
}

.usecase-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
}

.usecase-card ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.usecase-card li {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.5;
  padding-left: 1.2rem;
  position: relative;
}

.usecase-card:nth-child(1) li::before { content: '·'; position: absolute; left: 0; font-weight: 900; color: var(--accent-green); font-size: 1.2rem; }
.usecase-card:nth-child(2) li::before { content: '·'; position: absolute; left: 0; font-weight: 900; color: var(--accent-blue); font-size: 1.2rem; }
.usecase-card:nth-child(3) li::before { content: '·'; position: absolute; left: 0; font-weight: 900; color: var(--accent-pink); font-size: 1.2rem; }
</style>

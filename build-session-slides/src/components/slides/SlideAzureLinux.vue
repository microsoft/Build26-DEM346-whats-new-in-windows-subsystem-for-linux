<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-azurelinux">
    <h1 class="fade-up">Azure Linux 4.0</h1>
    <p class="subtitle fade-up">Microsoft's Linux distro now available for general use</p>

    <div class="features-grid fade-up">
      <div class="feature-card">
        <h3>🔒 Single Vendor, Secure Supply Chain</h3>
        <p>Microsoft provides the entire stack for Linux, with full supply chain attestation from build to deployment.</p>
      </div>
      <div class="feature-card">
        <h3>☁️ The Same Distro That Runs AKS</h3>
        <p>Use the same tools and setup that powers Azure, giving you a consistent and proven environment.</p>
      </div>
      <div class="feature-card">
        <h3>⚡ Try It Now</h3>
        <p>Available today as a VM, with a WSL distro coming soon.</p>
      </div>
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
#slide-azurelinux::before { background: var(--accent-blue); top: -150px; left: -100px; }
#slide-azurelinux { text-align: center; gap: 1.5rem; }

#slide-azurelinux h1 {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1e293b 0%, #2563eb 60%, #7c3aed 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--text-muted);
  margin-top: -0.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  max-width: 950px;
  margin-top: 1rem;
}

.feature-card {
  background: rgba(37, 99, 235, 0.05);
  border: 1px solid rgba(37, 99, 235, 0.15);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: left;
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.feature-card p {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.5;
}
</style>

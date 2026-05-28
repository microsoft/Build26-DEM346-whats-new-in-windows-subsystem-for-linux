<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-thankyou">
    <h1 class="fade-up">Thank you!</h1>
    <h3 class="fade-up">Questions?</h3>
    <div class="preview-cta fade-up">
      <p class="preview-label">🚀 Watch the CLI blog for news of when WSL Containers goes live!</p>
      <a href="https://aka.ms/cliblog" target="_blank" class="preview-link">aka.ms/cliblog</a>
    </div>
    <div class="contact-row fade-up">
      <div class="contact-item">📧 Pooja Trivedi</div>
      <div class="contact-item">📧 Craig Loewen</div>
      <div class="contact-item">🔗 <a href="https://aka.ms/wsl" target="_blank">aka.ms/wsl</a></div>
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
#slide-thankyou::before { background: var(--accent-purple); top: -200px; right: -100px; }
#slide-thankyou { text-align: center; gap: 1.5rem; }

#slide-thankyou h1 {
  font-size: 5rem;
  background: linear-gradient(135deg, #1e293b 0%, #7c3aed 60%, #2563eb 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}

#slide-thankyou h3 {
  font-size: 2rem; font-weight: 400; color: var(--text-muted);
}

.contact-row {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.contact-item a {
  color: var(--accent-blue);
  text-decoration: none;
}

.contact-item a:hover { text-decoration: underline; }

.preview-cta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  padding: 1.2rem 2.5rem;
  background: rgba(124,58,237,0.08);
  border: 1px solid rgba(124,58,237,0.25);
  border-radius: 16px;
  margin-top: 0.5rem;
}

.preview-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-link {
  font-size: 1rem;
  color: var(--accent-blue);
  text-decoration: none;
  font-weight: 500;
}

.preview-link:hover { text-decoration: underline; }
</style>

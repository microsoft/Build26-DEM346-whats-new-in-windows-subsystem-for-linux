<template>
  <div class="slide" :class="{ active: isActive, 'exit-left': isExitLeft }" id="slide-moonray">
    <span class="tag fade-up" style="background:rgba(37,99,235,0.1);color:#1d4ed8;border:1px solid rgba(37,99,235,0.25);">Partner</span>
    <img src="/moonraylogo.webp" alt="Moonray" class="logo-hero fade-up" />
    <div class="carousel fade-up">
      <div
        v-for="(movie, i) in movies"
        :key="movie.alt"
        class="carousel-item"
        :class="{ visible: i === activeIndex }"
      >
        <img :src="movie.src" :alt="movie.alt" class="movie-still" />
      </div>
    </div>
    <span class="copyright fade-up">© DreamWorks Animation LLC. All Rights Reserved.</span>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  isActive: Boolean,
  isExitLeft: Boolean,
})

const movies = [
  { src: '/thebadguys.jpg', alt: 'The Bad Guys' },
  { src: '/thewildrobot.jpg', alt: 'The Wild Robot' },
  { src: '/thewildrobot2.png', alt: 'The Wild Robot 2' },
]

const activeIndex = ref(0)
let timer = null

function startCycle() {
  stopCycle()
  timer = setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % movies.length
  }, 5000)
}

function stopCycle() {
  if (timer) { clearInterval(timer); timer = null }
}

watch(() => props.isActive, (active) => {
  if (active) { activeIndex.value = 0; startCycle() }
  else { stopCycle() }
}, { immediate: true })

onUnmounted(() => stopCycle())
</script>

<style scoped>
#slide-moonray::before { background: var(--accent-blue); top: 50%; left: 50%; transform: translate(-50%,-50%); width: 600px; height: 600px; opacity: 0.12; }

#slide-moonray { text-align: center; gap: 1.2rem; }

.logo-hero {
  width: 220px;
  height: auto;
  border-radius: 16px;
  object-fit: contain;
  filter: drop-shadow(0 4px 24px rgba(0,0,0,0.15));
}

.carousel {
  position: relative;
  width: 480px;
  height: 270px;
  margin: 0 auto;
}

.carousel-item {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.8s ease;
  pointer-events: none;
}

.carousel-item.visible {
  opacity: 1;
  pointer-events: auto;
}

.movie-still {
  width: 480px;
  height: 270px;
  object-fit: cover;
  border-radius: 12px;
  filter: drop-shadow(0 4px 24px rgba(0,0,0,0.18));
}

.copyright {
  font-size: 0.65rem;
  color: rgba(0,0,0,0.6);
  text-align: center;
}
</style>

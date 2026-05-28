<template>
  <div class="deck" @click="handleClick">
    <SlideTitle     :is-active="current === 0" :is-exit-left="exitLeft === 0" />
    <SlideOverview  :is-active="current === 1" :is-exit-left="exitLeft === 1" />
    <SlideDemo      :is-active="current === 2" :is-exit-left="exitLeft === 2" variant="cli" />
    <SlideSurfaces  :is-active="current === 3" :is-exit-left="exitLeft === 3" />
    <SlideUseCases  :is-active="current === 4" :is-exit-left="exitLeft === 4" />
    <SlideDemo      :is-active="current === 5" :is-exit-left="exitLeft === 5" variant="api" />
    <SlideArchOverview :is-active="current === 6" :is-exit-left="exitLeft === 6" />
    <SlideArchitecture
      :is-active="current === 7"
      :is-exit-left="exitLeft === 7"
      :phase="archPhase"
    />
    <SlideArchStorage :is-active="current === 8" :is-exit-left="exitLeft === 8" :phase="storagePhase" />
    <SlideArchCommand :is-active="current === 9" :is-exit-left="exitLeft === 9" :phase="commandPhase" />
    <SlideAzureLinux :is-active="current === 10" :is-exit-left="exitLeft === 10" />
    <SlideThankYou  :is-active="current === 11" :is-exit-left="exitLeft === 11" />
  </div>

  <!-- Slide counter -->
  <div class="slide-counter">{{ current + 1 }} / {{ total }}</div>


</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import SlideTitle from './components/slides/SlideTitle.vue'
import SlideOverview from './components/slides/SlideOverview.vue'
import SlideDemo from './components/slides/SlideDemo.vue'
import SlideSurfaces from './components/slides/SlideSurfaces.vue'
import SlideUseCases from './components/slides/SlideUseCases.vue'
import SlideArchOverview from './components/slides/SlideArchOverview.vue'
import SlideArchitecture from './components/slides/SlideArchitecture.vue'
import SlideArchStorage from './components/slides/SlideArchStorage.vue'
import SlideArchCommand from './components/slides/SlideArchCommand.vue'
import SlideAzureLinux from './components/slides/SlideAzureLinux.vue'
import SlideThankYou from './components/slides/SlideThankYou.vue'

const total = 12
const ARCH_INDEX = 7
const ARCH_PHASES = 5
const STORAGE_INDEX = 8
const STORAGE_PHASES = 3
const COMMAND_INDEX = 9
const COMMAND_PHASES = 4

function readHash() {
  const m = location.hash.match(/^#(\d+)(?:\.(\d+))?$/)
  if (!m) return { slide: 0, phase: 1 }
  return { slide: Math.min(Number(m[1]), total - 1), phase: m[2] ? Number(m[2]) : 1 }
}

const init = readHash()
const current = ref(init.slide)
const exitLeft = ref(-1)
const archPhase = ref(init.slide === ARCH_INDEX ? init.phase : 1)
const storagePhase = ref(init.slide === STORAGE_INDEX ? init.phase : 1)
const commandPhase = ref(init.slide === COMMAND_INDEX ? init.phase : 1)
const navHintHidden = ref(false)

watch([current, archPhase, storagePhase, commandPhase], ([s, ap, sp, cp]) => {
  if (s === ARCH_INDEX) history.replaceState(null, '', `#${s}.${ap}`)
  else if (s === STORAGE_INDEX) history.replaceState(null, '', `#${s}.${sp}`)
  else if (s === COMMAND_INDEX) history.replaceState(null, '', `#${s}.${cp}`)
  else history.replaceState(null, '', `#${s}`)
})

function goTo(index, direction) {
  if (index < 0 || index >= total || index === current.value) return

  exitLeft.value = direction === 'forward' ? current.value : -1
  current.value = index

  if (index === ARCH_INDEX) {
    archPhase.value = direction === 'forward' ? 1 : ARCH_PHASES
  }
  if (index === STORAGE_INDEX) {
    storagePhase.value = direction === 'forward' ? 1 : STORAGE_PHASES
  }
  if (index === COMMAND_INDEX) {
    commandPhase.value = direction === 'forward' ? 1 : COMMAND_PHASES
  }
}

function next() {
  if (current.value === ARCH_INDEX && archPhase.value < ARCH_PHASES) {
    archPhase.value++
    return
  }
  if (current.value === STORAGE_INDEX && storagePhase.value < STORAGE_PHASES) {
    storagePhase.value++
    return
  }
  if (current.value === COMMAND_INDEX && commandPhase.value < COMMAND_PHASES) {
    commandPhase.value++
    return
  }
  goTo(current.value + 1, 'forward')
}

function prev() {
  if (current.value === ARCH_INDEX && archPhase.value > 1) {
    archPhase.value--
    return
  }
  if (current.value === STORAGE_INDEX && storagePhase.value > 1) {
    storagePhase.value--
    return
  }
  if (current.value === COMMAND_INDEX && commandPhase.value > 1) {
    commandPhase.value--
    return
  }
  goTo(current.value - 1, 'backward')
}

function handleClick(e) {
  if (e.target.closest('a, button')) return
  if (e.clientX > window.innerWidth / 2) next()
  else prev()
  navHintHidden.value = true
}

function onKeydown(e) {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); next() }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev() }
  else if (e.key === 'Home') { e.preventDefault(); goTo(0, 'backward') }
  else if (e.key === 'End') { e.preventDefault(); goTo(total - 1, 'forward') }
  else if (e.key === 'f' || e.key === 'F') { toggleFullscreen() }
  navHintHidden.value = true
}

let touchStartX = 0
function onTouchStart(e) { touchStartX = e.touches[0].clientX }
function onTouchEnd(e) {
  const diff = touchStartX - e.changedTouches[0].clientX
  if (Math.abs(diff) > 50) {
    if (diff > 0) next(); else prev()
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {})
  } else {
    document.exitFullscreen()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('touchstart', onTouchStart)
  document.addEventListener('touchend', onTouchEnd)
  setTimeout(() => { navHintHidden.value = true }, 8000)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('touchstart', onTouchStart)
  document.removeEventListener('touchend', onTouchEnd)
})
</script>

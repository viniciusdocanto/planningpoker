<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isDark = ref<boolean>(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const applyTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    document.documentElement.style.colorScheme = 'dark'
    localStorage.setItem('poker-theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    document.documentElement.style.colorScheme = 'light'
    localStorage.setItem('poker-theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('poker-theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme()
})
</script>

<template>
  <button 
    @click="toggleTheme"
    class="relative w-12 h-12 flex items-center justify-center rounded-2xl glass transition-all duration-300 hover:scale-110 active:scale-95 group"
    aria-label="Alternar tema"
  >
    <!-- Sun icon -->
    <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-amber-400 group-hover:rotate-12 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707.707M12 5a7 7 0 100 14 7 7 0 000-14z" />
    </svg>
    <!-- Moon icon -->
    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 group-hover:-rotate-12 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  </button>
</template>

<style scoped>
.glass {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}
</style>

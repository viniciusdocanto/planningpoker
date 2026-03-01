<script setup lang="ts">
import { onBeforeMount } from 'vue'
import { RouterView } from 'vue-router'

onBeforeMount(() => {
  const savedTheme = localStorage.getItem('poker-theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <RouterView />
</template>

<style>
#app {
  width: 100vw;
  min-height: 100vh;
}
</style>

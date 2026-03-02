<template>
  <div class="text-center mb-10 animate-float">
    <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-5 bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 shadow-lg glow-purple">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h4m6-16h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-6 0V3" />
      </svg>
    </div>
    <div class="flex items-center justify-center gap-3 mb-3">
      <h1 class="text-5xl font-extrabold tracking-tight text-gradient leading-tight">{{ t('home.title') }}</h1>
      <span class="px-2 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-[10px] font-black uppercase tracking-widest h-fit mt-1">{{ t('home.beta') }}</span>
    </div>
    <p class="text-black dark:text-slate-400 text-lg max-w-sm font-black mx-auto">
      {{ t('home.tagline') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

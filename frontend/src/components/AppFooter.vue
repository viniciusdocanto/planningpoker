<template>
  <footer class="mt-8 pb-8 text-[10px] text-black dark:text-slate-600 uppercase tracking-widest font-black flex flex-col items-center gap-1.5">
    <div class="flex items-center">
      <a href="https://github.com/viniciusdocanto/planningpoker" target="_blank" class="hover:text-indigo-800 dark:hover:text-indigo-400 transition-colors">
        {{ $t('common.openSource') }}
      </a>
      <span class="mx-2 opacity-50">|</span>
      <a href="https://docanto.net" target="_blank" class="hover:text-fuchsia-800 dark:hover:text-fuchsia-400 transition-colors font-black underline decoration-fuchsia-500/30 underline-offset-4">
        {{ $t('common.by') }}
      </a>
    </div>
    <span class="opacity-30 tracking-normal normal-case font-mono text-[8px]">v{{ version }}</span>
  </footer>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t: $t } = useI18n()

defineProps<{
  version: string
}>()
</script>

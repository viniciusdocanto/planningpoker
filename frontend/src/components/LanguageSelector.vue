<template>
  <div class="relative inline-block text-left">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-black bg-slate-950/5 dark:bg-white/10 hover:bg-slate-900/10 dark:hover:bg-white/20 text-black dark:text-white border border-slate-300 dark:border-white/10 transition-all uppercase tracking-wider"
    >
      <span>{{ currentLanguageLabel }}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-3 w-3 transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="absolute right-0 mt-2 w-32 rounded-2xl glass border border-slate-200 dark:border-white/10 shadow-2xl overflow-hidden z-[100]"
    >
      <div class="p-1.5 flex flex-col gap-1">
        <button
          v-for="(label, lang) in languages"
          :key="lang"
          @click="setLanguage(lang)"
          class="flex items-center justify-between px-3 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
          :class="locale === lang
            ? 'bg-indigo-600 text-white'
            : 'text-black dark:text-slate-300 hover:bg-slate-950/5 dark:hover:bg-white/5'"
        >
          {{ label }}
          <span v-if="locale === lang" class="text-[8px]">●</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const isOpen = ref(false)

const languages = {
  pt: 'PT',
  en: 'EN',
  es: 'ES'
}

const currentLanguageLabel = computed(() => languages[locale.value as keyof typeof languages])

const setLanguage = (lang: string) => {
  locale.value = lang
  localStorage.setItem('poker-locale', lang)
  isOpen.value = false
}

// Close on outside click (simple implementation)
const closeOnOutside = (e: MouseEvent) => {
  if (isOpen.value && !(e.target as HTMLElement).closest('.relative')) {
    isOpen.value = false
  }
}

import { onMounted, onUnmounted } from 'vue'
onMounted(() => window.addEventListener('click', closeOnOutside))
onUnmounted(() => window.removeEventListener('click', closeOnOutside))
</script>

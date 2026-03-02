<template>
  <div v-if="!(gameState?.revealed)" class="fixed bottom-0 left-0 w-full z-20">
    <div class="glass border-t border-slate-300 dark:border-white/10 px-4 pt-2 pb-4 backdrop-blur-3xl shadow-[0_-20px_50px_rgba(0,0,0,0.15)]">
      <div class="max-w-5xl mx-auto flex flex-col gap-6">
        <!-- Scrollable Deck Area (Height fixed to prevent clipping) -->
        <div class="flex gap-2.5 overflow-x-auto overflow-y-visible justify-start sm:justify-center custom-scrollbar h-[130px] items-center px-2">
          <button
            v-for="card in deck"
            :key="card"
            @click="$emit('select-card', card)"
            class="flex-shrink-0 w-[52px] h-[72px] rounded-xl font-black text-lg border-2 transition-all duration-200 card-hover select-none"
            :class="myVote === card
              ? 'bg-gradient-to-b from-indigo-500 to-indigo-700 border-indigo-600 text-white card-selected shadow-lg shadow-indigo-500/40'
              : 'bg-white dark:bg-slate-800 text-black dark:text-slate-100 border-slate-300 dark:border-white/10 hover:border-indigo-500/60 transition-colors'"
          >
            {{ card }}
          </button>
        </div>

        <!-- Footer unified with HomeView (v0.6.7) -->
        <footer class="pb-1 text-center">
          <div class="text-[9px] text-black dark:text-slate-600 uppercase tracking-widest font-black flex flex-col items-center gap-1.5">
            <div class="flex items-center">
              <a href="https://github.com/viniciusdocanto/planningpoker" target="_blank" class="hover:text-indigo-800 dark:hover:text-indigo-400 transition-colors">{{ $t('common.openSource') }}</a>
              <span class="mx-2 opacity-50">|</span>
              <a href="https://docanto.net" target="_blank" class="hover:text-fuchsia-800 dark:hover:text-fuchsia-400 transition-colors font-black underline decoration-fuchsia-500/30 underline-offset-4">{{ $t('common.by') }}</a>
            </div>
            <span class="font-bold text-orange-700 tracking-normal normal-case font-mono text-[10px]">v{{ version }}</span>
          </div>
        </footer>
      </div>
    </div>
  </div>

  <!-- Clean spacer footer for revealed results state (when deck is gone) -->
  <footer v-else class="mt-20 mb-10 text-center px-4">
    <div class="text-[9px] text-black dark:text-slate-600 uppercase tracking-widest font-black flex flex-col items-center gap-1.5">
      <div class="flex items-center">
        <a href="https://github.com/viniciusdocanto/planningpoker" target="_blank" class="hover:text-indigo-800 dark:hover:text-indigo-400 transition-colors">{{ $t('common.openSource') }}</a>
        <span class="mx-2 opacity-50">|</span>
        <a href="https://docanto.net" target="_blank" class="hover:text-fuchsia-800 dark:hover:text-fuchsia-400 transition-colors font-black underline decoration-fuchsia-500/30 underline-offset-4">{{ $t('common.by') }}</a>
      </div>
      <span class="font-bold text-orange-700 tracking-normal normal-case font-mono text-[10px]">v{{ version }}</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
import type { GameState, CardValue } from '../types/poker'

defineProps<{
  gameState: GameState
  myVote: CardValue | null
  deck: readonly string[]
  version: string
}>()

defineEmits<{
  (e: 'select-card', card: string): void
}>()
</script>

<template>
  <div v-if="gameState?.revealed" class="max-w-5xl mx-auto mb-6">
    <div class="glass rounded-2xl p-6 border-slate-400 dark:border-white/5 shadow-2xl">
      <h2 class="text-sm font-black text-black dark:text-slate-300 uppercase tracking-widest mb-4">{{ $t('room.results') }}</h2>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(data, user) in (gameState.users || {})"
          :key="user"
          class="flex items-center gap-2 bg-slate-950/5 dark:bg-white/5 rounded-xl px-4 py-2.5 border border-slate-400 dark:border-white/[0.06]"
        >
          <span v-if="user === gameState.host" class="text-amber-800 dark:text-yellow-400 text-xs">👑</span>
          <span class="text-sm font-black text-black dark:text-slate-300">{{ user === userName ? $t('room.you') : user }}</span>
          <span class="font-bold text-sm px-2 py-0.5 rounded-lg"
            :class="data.voted ? 'bg-indigo-500/30 text-indigo-300' : 'bg-white/5 text-slate-600'"
          >{{ data.voted ? data.vote : '—' }}</span>
        </div>
      </div>
      <div v-if="voteAverage !== null" class="mt-4 pt-4 border-t border-slate-400 dark:border-white/5 flex items-center gap-3">
        <span class="text-xs font-black text-black dark:text-slate-500 uppercase tracking-wider">{{ $t('room.average') }}</span>
        <span class="text-3xl font-black text-gradient">{{ voteAverage }}</span>
      </div>
      <p v-if="isHost" class="mt-3 text-[10px] font-black text-black dark:text-slate-600 uppercase tracking-wide">
        {{ $t('room.roundEnded') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GameState } from '../types/poker'

defineProps<{
  gameState: GameState
  userName: string
  isHost: boolean
  voteAverage: number | string | null
}>()
</script>

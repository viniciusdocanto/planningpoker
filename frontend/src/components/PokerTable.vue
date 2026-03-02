<template>
  <div class="max-w-5xl mx-auto py-10 flex flex-col items-center">
    
    <!-- Timer display (visible to all) -->
    <div
      v-if="timeLeft !== null && !(gameState?.revealed)"
      class="mb-6 flex flex-col items-center gap-1"
    >
      <div
        class="relative w-20 h-20 flex items-center justify-center"
      >
        <svg class="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="34" fill="none" stroke-width="6"
            class="stroke-slate-200 dark:stroke-white/10" />
          <circle cx="40" cy="40" r="34" fill="none" stroke-width="6"
            stroke-linecap="round"
            :stroke-dasharray="213.6"
            :stroke-dashoffset="213.6 * (1 - timerProgress)"
            :class="timeLeft <= 10 ? 'stroke-rose-500 animate-pulse' : 'stroke-indigo-500'"
            style="transition: stroke-dashoffset 0.5s linear;"
          />
        </svg>
        <span
          class="text-2xl font-black tabular-nums"
          :class="timeLeft <= 10 ? 'text-rose-500' : 'text-black dark:text-white'"
        >{{ timeLeft }}</span>
      </div>
      <span class="text-[10px] uppercase tracking-widest font-black text-slate-400">{{ $t('room.seconds') }}</span>
    </div>

    <!-- Empty state -->
    <div v-if="Object.keys(gameState.users || {}).length === 0" class="text-center py-20 text-slate-600">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto mb-4 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <p class="text-lg font-medium text-slate-500">{{ $t('room.waitingPlayers') }}</p>
      <p class="text-sm mt-1 text-slate-600">{{ $t('room.inviteHint') }}</p>
    </div>

    <template v-else>
      <!-- Players arranged above and below the table oval -->
      <div class="w-full flex flex-wrap justify-center gap-8 mb-10 pt-10">
        <div
          v-for="(data, user) in (gameState.users || {})"
          :key="user"
          class="flex flex-col items-center gap-3"
        >
          <!-- Player Card on table -->
          <div
            class="w-14 h-20 rounded-xl flex items-center justify-center relative transition-all duration-500 select-none"
            :class="[
              data.voted && !gameState.revealed
                ? 'bg-gradient-to-b from-indigo-500 to-purple-600 -translate-y-2 shadow-[0_8px_32px_rgba(99,102,241,0.5)]'
                : '',
              !data.voted && !gameState.revealed
                ? 'border-2 border-dashed border-slate-300/50 dark:border-white/10 opacity-40 bg-slate-200/30 dark:bg-white/5'
                : '',
              gameState.revealed && data.voted
                ? 'bg-white shadow-[0_8px_40px_rgba(255,255,255,0.2)] border border-slate-200 dark:border-transparent'
                : '',
              gameState.revealed && !data.voted
                ? 'bg-slate-200/30 dark:bg-white/5 border border-slate-300/50 dark:border-white/10'
                : '',
            ]"
          >
            <!-- Card back pattern -->
            <div v-if="data.voted && !gameState.revealed" class="absolute inset-2 rounded-lg border border-white/20 pointer-events-none"></div>
            <div v-if="data.voted && !gameState.revealed" class="absolute inset-3 rounded border border-white/10 pointer-events-none"></div>
            <!-- Revealed vote -->
            <span v-if="gameState.revealed && data.voted" class="text-gray-900 text-2xl font-extrabold">{{ data.vote }}</span>
            <span v-if="gameState.revealed && !data.voted" class="text-slate-500 text-lg">—</span>
          </div>

          <!-- Player info -->
          <div class="text-center">
            <span class="flex items-center justify-center gap-1 text-xs font-black leading-tight"
              :class="user === userName ? 'text-indigo-900 dark:text-indigo-400' : 'text-black dark:text-slate-300'"
            >
              <span v-if="user === gameState.host" class="text-amber-700 dark:text-yellow-400 tracking-tighter">👑</span>
              {{ user === userName ? $t('room.you') : user }}
            </span>
            <span v-if="data.voted && !gameState.revealed" class="text-[10px] text-green-600 dark:text-green-400 font-bold tracking-wide uppercase">{{ $t('room.voted') }}</span>
            <span v-if="!data.voted && !gameState.revealed" class="text-[10px] text-amber-600/80 dark:text-yellow-500/80 font-medium tracking-wide">{{ $t('room.thinking') }}</span>
            <span v-if="gameState.revealed && !data.voted" class="text-[10px] text-slate-500 dark:text-slate-600">{{ $t('room.didntVote') }}</span>
          </div>
        </div>
      </div>

      <!-- Oval poker table center -->
      <div class="relative w-72 h-36 rounded-full flex items-center justify-center
        bg-slate-200/50 dark:bg-gradient-to-b dark:from-emerald-900/60 dark:to-emerald-950/80
        border-4 border-slate-300 dark:border-emerald-700/40
        shadow-[0_10px_40px_rgba(0,0,0,0.05),inset_0_2px_10px_rgba(0,0,0,0.05)] dark:shadow-[0_0_60px_rgba(16,185,129,0.15),inset_0_2px_20px_rgba(0,0,0,0.4)]
        mb-10"
      >
        <div class="absolute inset-3 rounded-full border border-slate-300/50 dark:border-emerald-600/20 pointer-events-none"></div>
        <template v-if="gameState?.revealed && voteAverage !== null">
          <div class="text-center">
            <span class="text-4xl font-black text-white drop-shadow-md">{{ voteAverage }}</span>
            <p class="text-[10px] text-emerald-200 font-bold mt-0.5 tracking-[0.2em] uppercase">{{ $t('room.average') }}</p>
          </div>
        </template>
        <template v-else-if="gameState?.revealed">
          <span class="text-slate-400 dark:text-emerald-500/60 text-xs font-bold uppercase tracking-widest">{{ $t('room.noVotes') }}</span>
        </template>
        <template v-else>
          <div class="text-center">
            <p class="text-indigo-600 dark:text-white text-sm font-black drop-shadow-sm">
              {{ $t('room.votesCount', { count: Object.values(gameState?.users || {}).filter(u => (u as any)?.voted).length, total: Object.keys(gameState?.users || {}).length }) }}
            </p>
          </div>
        </template>
      </div>

      <!-- Non-host hint -->
      <p v-if="!(gameState?.revealed) && !isHost" class="text-xs text-slate-600 mb-4">
        {{ $t('room.waitingHost', { host: gameState?.host || '...' }) }}
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { GameState } from '../types/poker'

defineProps<{
  gameState: GameState
  userName: string
  isHost: boolean
  timeLeft: number | null
  timerProgress: number
  voteAverage: number | string | null
}>()
</script>

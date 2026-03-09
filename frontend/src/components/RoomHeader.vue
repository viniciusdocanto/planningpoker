<template>
  <header class="glass rounded-2xl px-5 py-4 mb-6 flex justify-between items-center max-w-5xl mx-auto border-white/10 dark:border-white/5">
    <!-- Left: Room info -->
    <div class="flex flex-col gap-0.5 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <!-- Planning Poker logo small -->
        <div 
          @click="$emit('go-home')"
          class="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-fuchsia-500 flex items-center justify-center shrink-0 cursor-pointer hover:scale-105 transition-transform"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h4m6-16h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-6 0V3" />
          </svg>
        </div>
        <span class="text-black dark:text-slate-300 font-mono text-xs truncate max-w-[140px] sm:max-w-xs font-black shadow-sm bg-white/50 dark:bg-transparent px-2 py-0.5 rounded" :title="roomId">{{ roomId }}</span>
        <button
          @click="$emit('copy-link')"
          class="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-900 dark:hover:bg-white/10 text-slate-800 dark:text-slate-400 hover:text-white dark:hover:text-white transition-all border border-slate-300 dark:border-white/5 font-bold"
        >
          <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-green-600 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          {{ copied ? $t('room.copied') : $t('room.share') }}
        </button>
      </div>
      <div class="flex items-center gap-2 text-[10px] text-black dark:text-slate-500 uppercase tracking-wider font-black">
        <span>{{ userName }}</span>
        <span v-if="isHost" class="text-amber-700 dark:text-yellow-400 font-bold">👑 {{ $t('room.host') }}</span>
        <!-- WS status dot -->
        <span class="flex items-center gap-1" :class="wsStatus === 'connected' ? 'text-green-600 dark:text-green-500' : 'text-amber-700 dark:text-yellow-500 animate-pulse-soft'">
          · <span class="w-1.5 h-1.5 rounded-full inline-block" :class="wsStatus === 'connected' ? 'bg-green-600 dark:bg-green-500' : 'bg-amber-700 dark:bg-yellow-500'"></span>
          {{ wsStatus === 'connected' ? 'OK' : '...' }}
        </span>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-3 shrink-0">
      <ThemeToggle />

      <!-- History button (shows only when there are rounds) -->
      <div v-if="(gameState?.history?.length || 0) > 0" class="relative">
        <button
          ref="historyBtnRef"
          @click="$emit('toggle-history')"
          class="flex items-center gap-1.5 px-2.5 py-2 rounded-xl text-xs font-bold bg-slate-950/5 dark:bg-white/10 hover:bg-slate-900/10 dark:hover:bg-white/20 text-black dark:text-white border border-slate-300 dark:border-white/10 transition-all"
          :title="$t('room.historyTitle')"
        >
          <span>📋</span>
          <span class="hidden sm:inline">{{ $t('room.history') }}</span>
          <span class="px-1.5 py-0.5 rounded-full bg-indigo-600 text-white text-[9px] font-black leading-none">
            {{ gameState?.history?.length || 0 }}
          </span>
        </button>

        <!-- Dropdown via Teleport to avoid stacking context clipping -->
        <Teleport to="body">
          <div
            v-if="showHistory"
            :style="historyPanelStyle"
            class="fixed w-72 sm:w-96 rounded-2xl glass border border-slate-200 dark:border-white/10 shadow-2xl overflow-hidden"
            style="z-index: 9998;"
          >
            <div class="p-3 border-b border-slate-200 dark:border-white/10 flex items-center justify-between">
              <span class="text-xs font-black uppercase tracking-wider text-black dark:text-white">{{ $t('room.historyTitle') }}</span>
              <button @click="$emit('close-history')" class="text-slate-400 hover:text-black dark:hover:text-white text-sm">✕</button>
            </div>
            <div class="max-h-80 overflow-y-auto p-3 flex flex-col gap-3">
              <div
                v-for="entry in [...(gameState.history || [])].reverse()"
                :key="entry.round"
                class="rounded-xl border border-slate-200 dark:border-white/10 bg-white/50 dark:bg-white/5 p-3"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[11px] font-black uppercase tracking-wider text-indigo-500">
                    {{ $t('room.round') }} {{ entry.round }}
                  </span>
                  <span v-if="entry.average !== null" class="text-[11px] font-black px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
                    {{ $t('room.average') }}: {{ entry.average }}
                  </span>
                  <span v-else class="text-[11px] text-slate-400 italic">{{ $t('room.noAverage') }}</span>
                </div>
                <div class="flex flex-wrap gap-1.5">
                  <div
                    v-for="(vote, user) in (entry.votes || {})"
                    :key="user"
                    class="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10"
                  >
                    <span class="text-[10px] text-slate-500 dark:text-slate-400">{{ user }}</span>
                    <span class="font-black text-xs text-black dark:text-white">{{ vote }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Teleport>
      </div>

      <!-- Timer controls (host only, when not revealed) -->
      <div v-if="isHost && !gameState.revealed" class="flex items-center gap-1.5 bg-slate-100 dark:bg-white/5 p-1 rounded-xl border border-slate-300 dark:border-white/10">
        <button v-for="secs in [30, 60, 90]" :key="secs"
          @click="$emit('start-timer', secs)"
          class="px-2.5 py-1.5 rounded-lg text-[10px] sm:text-[11px] font-black transition-all"
          :class="[
            gameState.timer_end !== null && gameState.timer_duration === secs
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30 active:scale-95'
              : 'text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-white/10 active:scale-95'
          ]"
        >{{ secs }}s</button>
        
        <template v-if="gameState.timer_end !== null">
          <div class="w-px h-4 bg-slate-300 dark:bg-white/10 mx-0.5"></div>
          <button @click="$emit('cancel-timer')"
            class="p-1.5 rounded-lg text-rose-500 hover:bg-rose-500 hover:text-white transition-all active:scale-90"
            :title="$t('room.cancelTimer')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </template>
      </div>

      <button
        v-if="isHost"
        @click="$emit('handle-action')"
        class="px-5 py-2 rounded-xl text-white font-black text-sm shadow-lg transition-all duration-200 active:scale-95"
        :class="gameState.revealed
          ? 'bg-gradient-to-r from-rose-500 to-rose-600 shadow-rose-500/20 hover:opacity-90'
          : 'bg-gradient-to-r from-indigo-500 to-purple-600 shadow-indigo-500/20 hover:opacity-90'"
      >
        {{ gameState.revealed ? $t('room.reset') : $t('room.reveal') }}
      </button>
      <button
        @click="$emit('leave')"
        class="px-4 py-2 rounded-xl text-black dark:text-white font-black text-sm bg-slate-950/5 dark:bg-white/10 hover:bg-slate-900/10 dark:hover:bg-white/20 transition-all active:scale-95"
      >
        {{ $t('room.leave') }}
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import type { GameState, WsStatus } from '../types/poker'
import ThemeToggle from './ThemeToggle.vue'
import { ref } from 'vue'

defineProps<{
  roomId: string
  userName: string
  isHost: boolean
  wsStatus: WsStatus
  gameState: GameState
  copied: boolean
  showHistory: boolean
  historyPanelStyle: any
}>()

const historyBtnRef = ref<HTMLElement | null>(null)
defineExpose({ historyBtnRef })

defineEmits<{
  (e: 'go-home'): void
  (e: 'copy-link'): void
  (e: 'toggle-history'): void
  (e: 'close-history'): void
  (e: 'start-timer', secs: number): void
  (e: 'cancel-timer'): void
  (e: 'handle-action'): void
  (e: 'leave'): void
}>()
</script>

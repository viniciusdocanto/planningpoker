<template>
  <div class="min-h-screen pb-36 px-4 pt-4 relative">
    <ToastContainer />
    <!-- Header -->
    <header class="glass rounded-2xl px-5 py-4 mb-6 flex justify-between items-center max-w-5xl mx-auto border-white/10 dark:border-white/5">
      <!-- Left: Room info -->
      <div class="flex flex-col gap-0.5 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Planning Poker logo small -->
          <div 
            @click="router.push('/')"
            class="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-fuchsia-500 flex items-center justify-center shrink-0 cursor-pointer hover:scale-105 transition-transform"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h4m6-16h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-6 0V3" />
            </svg>
          </div>
          <span class="text-black dark:text-slate-300 font-mono text-xs truncate max-w-[140px] sm:max-w-xs font-black shadow-sm bg-white/50 dark:bg-transparent px-2 py-0.5 rounded" :title="roomId">{{ roomId }}</span>
          <button
            @click="copyInviteLink"
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
            @click="toggleHistory"
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
                <button @click="showHistory = false" class="text-slate-400 hover:text-black dark:hover:text-white text-sm">✕</button>
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
        <div v-if="isHost && !gameState.revealed" class="flex items-center gap-1.5">
          <template v-if="gameState.timer_end === null">
            <span class="text-[10px] text-slate-400 hidden sm:inline">⏱</span>
            <button v-for="secs in [30, 60, 90]" :key="secs"
              @click="startTimer(secs)"
              class="px-2 py-1.5 rounded-lg text-[11px] font-black bg-slate-950/5 dark:bg-white/10 hover:bg-indigo-500 hover:text-white text-black dark:text-slate-300 border border-slate-300 dark:border-white/10 transition-all"
            >{{ secs }}s</button>
          </template>
          <button v-else @click="cancelTimer"
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-black bg-rose-500/10 hover:bg-rose-500 hover:text-white text-rose-600 dark:text-rose-400 border border-rose-400/30 transition-all"
          >{{ $t('room.cancelTimer') }}</button>
        </div>

        <button
          v-if="isHost"
          @click="handleAction"
          class="px-5 py-2 rounded-xl text-white font-black text-sm shadow-lg transition-all duration-200 active:scale-95"
          :class="gameState.revealed
            ? 'bg-gradient-to-r from-rose-500 to-rose-600 shadow-rose-500/20 hover:opacity-90'
            : 'bg-gradient-to-r from-indigo-500 to-purple-600 shadow-indigo-500/20 hover:opacity-90'"
        >
          {{ gameState.revealed ? $t('room.reset') : $t('room.reveal') }}
        </button>
        <button
          @click="leaveRoom"
          class="px-4 py-2 rounded-xl text-black dark:text-white font-black text-sm bg-slate-950/5 dark:bg-white/10 hover:bg-slate-900/10 dark:hover:bg-white/20 transition-all active:scale-95"
        >
          {{ $t('room.leave') }}
        </button>
      </div>
    </header>

    <!-- Table -->
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
      <div v-if="Object.keys(gameState.users).length === 0" class="text-center py-20 text-slate-600">
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

    <!-- Results panel after reveal -->
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

    <!-- Fixed card deck at bottom -->
    <div v-if="!(gameState?.revealed)" class="fixed bottom-0 left-0 w-full z-20">
      <div class="glass border-t border-slate-300 dark:border-white/10 px-4 pt-2 pb-4 backdrop-blur-3xl shadow-[0_-20px_50px_rgba(0,0,0,0.15)]">
        <div class="max-w-5xl mx-auto flex flex-col gap-6">
          <!-- Scrollable Deck Area (Height fixed to prevent clipping) -->
          <div class="flex gap-2.5 overflow-x-auto overflow-y-visible justify-start sm:justify-center custom-scrollbar h-[130px] items-center px-2">
            <button
              v-for="card in deck"
              :key="card"
              @click="selectCard(card)"
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
              <span class="opacity-30 tracking-normal normal-case font-mono text-[8px]">v{{ appVersion }}</span>
            </div>
          </footer>
        </div>
      </div>
    </div>

    <!-- Clean spacer footer for revealed results state (when deck is gone) -->
    <footer v-if="gameState?.revealed" class="mt-20 mb-10 text-center px-4">
      <div class="text-[9px] text-black dark:text-slate-600 uppercase tracking-widest font-black flex flex-col items-center gap-1.5">
        <div class="flex items-center">
          <a href="https://github.com/viniciusdocanto/planningpoker" target="_blank" class="hover:text-indigo-800 dark:hover:text-indigo-400 transition-colors">{{ $t('common.openSource') }}</a>
          <span class="mx-2 opacity-50">|</span>
          <a href="https://docanto.net" target="_blank" class="hover:text-fuchsia-800 dark:hover:text-fuchsia-400 transition-colors font-black underline decoration-fuchsia-500/30 underline-offset-4">{{ $t('common.by') }}</a>
        </div>
        <span class="opacity-30 tracking-normal normal-case font-mono text-[8px]">v{{ appVersion }}</span>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
// Planning Poker - RoomView - MIT License - (c) 2026 Vinicius do Canto
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import ToastContainer from '../components/ToastContainer.vue'
import type { GameState, WsServerMessage, WsStatus, CardValue, DeckType } from '../types/poker'
import { DECKS, DECK_LABELS } from '../types/poker'
import { useToast } from '../composables/useToast'
import { useFeedback } from '../composables/useFeedback'
import { useI18n } from 'vue-i18n'

const { t: $t } = useI18n()
const route = useRoute()
const router = useRouter()
const roomId = ref<string>(String(route.params.id))
const userName = ref<string>(
  sessionStorage.getItem('playerName') ?? localStorage.getItem('poker-player-name') ?? ''
)

// Redirect if no name
if (!userName.value) {
  router.push(`/?room=${roomId.value}`)
}

const appVersion: string = __APP_VERSION__
const { addToast } = useToast()
const { vibrate, playRevealSound, playClickSound } = useFeedback()

const gameState = ref<GameState>({ users: {}, revealed: false, host: null, deck_type: (sessionStorage.getItem('poker-deck') as DeckType) || 'fibonacci', round_number: 0, history: [], timer_end: null, timer_duration: 60 })
const myVote = ref<CardValue | null>(null)
const copied = ref<boolean>(false)
const wsStatus = ref<WsStatus>('connecting')

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

const deck = computed<readonly string[]>(() => DECKS[gameState.value.deck_type] ?? DECKS.fibonacci)

const isHost = computed<boolean>(() => gameState.value.host === userName.value)

// --- Timer ---
const timeLeft = ref<number | null>(null)
let timerInterval: ReturnType<typeof setInterval> | null = null

const timerProgress = computed<number>(() => {
  const duration = gameState.value?.timer_duration ?? 60
  if (timeLeft.value === null || duration <= 0) return 1
  return Math.max(0, timeLeft.value / duration)
})

const startTimer = (secs: number): void => {
  if (ws?.readyState === WebSocket.OPEN)
    ws.send(JSON.stringify({ action: 'start_timer', value: String(secs) }))
}

const cancelTimer = (): void => {
  if (ws?.readyState === WebSocket.OPEN)
    ws.send(JSON.stringify({ action: 'cancel_timer' }))
}

const updateTimer = () => {
  const end = gameState.value?.timer_end
  if (end) {
    const diff = end - Date.now() / 1000
    if (diff > 0) {
      timeLeft.value = Math.ceil(diff)
    } else {
      timeLeft.value = 0
    }
  } else {
    timeLeft.value = null
  }
}

onMounted(() => {
  timerInterval = setInterval(updateTimer, 500)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

const showHistory = ref<boolean>(false)
const historyBtnRef = ref<HTMLElement | null>(null)
const historyPanelPos = ref<{ top: number; right: number }>({ top: 0, right: 0 })

const historyPanelStyle = computed(() => ({
  top: `${historyPanelPos.value.top}px`,
  right: `${historyPanelPos.value.right}px`,
}))

const toggleHistory = (): void => {
  if (!showHistory.value && historyBtnRef.value) {
    const rect = historyBtnRef.value.getBoundingClientRect()
    historyPanelPos.value = {
      top: rect.bottom + 8,
      right: window.innerWidth - rect.right,
    }
  }
  showHistory.value = !showHistory.value
}

const voteAverage = computed<number | string | null>(() => {
  if (!gameState.value?.revealed || !gameState.value?.users) return null
  const nums = Object.values(gameState.value.users)
    .filter(d => d.voted && d.vote != null && !isNaN(parseFloat(d.vote)))
    .map(d => parseFloat(d.vote!))
  if (!nums.length) return null
  const avg = nums.reduce((a, b) => a + b, 0) / nums.length
  return Number.isInteger(avg) ? avg : avg.toFixed(1)
})

const rawWsUrl: string = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
// Ensure correct protocol (replace http/https with ws/wss)
const WS_BASE: string = rawWsUrl.replace(/^http/, 'ws')

const connect = (): void => {
  if (!userName.value) { router.push('/'); return }
  const deckParam = sessionStorage.getItem('poker-deck') || 'fibonacci'
  ws = new WebSocket(`${WS_BASE}/ws/${roomId.value}/${encodeURIComponent(userName.value)}?deck=${encodeURIComponent(deckParam)}`)
  ws.onopen = () => {
    console.log('🔌 WebSocket: Connected!')
    wsStatus.value = 'connected'
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
    addToast($t('room.connected'), 'success')
  }
  ws.onmessage = (e: MessageEvent<string>) => {
    try {
      const msg = JSON.parse(e.data) as WsServerMessage
      if (msg.type === 'state_update' && msg.data) {
        const wasRevealed = gameState.value?.revealed ?? false
        
        // Use a temporary object to ensure all defaults are applied before replacing the ref
        const rawData = msg.data as any
        const updatedState: GameState = {
          ...gameState.value,
          ...rawData,
          users: rawData.users || {},
          history: rawData.history || []
        }
        
        gameState.value = updatedState

        // Play reveal sound only once when state changes to revealed
        if (gameState.value.revealed && !wasRevealed) {
          playRevealSound()
        }
        
        const me = (gameState.value.users as any)[userName.value]
        if (me && !me.voted) myVote.value = null
      } else if (msg.type === 'event_notify') {
        if (msg.event === 'user_joined' && msg.user !== userName.value) {
          addToast($t('room.userJoined', { user: msg.user || '?' }), 'info')
        } else if (msg.event === 'user_left' && msg.user !== userName.value) {
          addToast($t('room.userLeft', { user: msg.user || '?' }), 'warning')
        } else if (msg.event === 'deck_changed') {
          const label = msg.deck_type ? $t(`decks.${msg.deck_type}`) : '?'
          addToast($t('room.deckChanged', { deck: label }), 'info')
        }
      }
    } catch (err) {
      console.warn('Received invalid message from server:', err)
    }
  }
  ws.onclose = (event: CloseEvent) => {
    console.warn(`🔌 WebSocket: Connection closed (Code: ${event.code}). Reconnecting...`)
    wsStatus.value = 'reconnecting'
    reconnectTimer = setTimeout(connect, 3000)
    if (event.code !== 1000 && event.code !== 1001) {
      addToast('Conexão perdida. Reconectando...', 'error', 3000)
    }
  }
  ws.onerror = (err: Event) => {
    console.error('🔌 WebSocket: Error:', err)
    ws?.close()
  }
}

onMounted(connect)
onUnmounted(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer)
  if (ws) { ws.onclose = null; ws.close() }
})

const copyInviteLink = async (): Promise<void> => {
  try {
    const origin = window.location.origin
    const base = import.meta.env.BASE_URL
    const fullBase = (origin + base).replace(/\/+$/, '')
    await navigator.clipboard.writeText(`${fullBase}/?room=${roomId.value}`)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (e) { console.error(e) }
}

const selectCard = (card: string): void => {
  if (myVote.value !== card) {
    vibrate(40)
    playClickSound()
  }
  myVote.value = card as CardValue
  if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'vote', value: card }))
}
const handleAction = (): void => {
  if (gameState.value.revealed) {
    resetVotes()
  } else {
    revealVotes()
  }
}
const revealVotes = (): void => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'reveal' })) }
const resetVotes = (): void => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'reset' })) }
const leaveRoom = (): void => { if (ws) { ws.onclose = null; ws.close() }; router.push('/') }
</script>

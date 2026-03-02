<template>
  <div class="min-h-screen pb-36 px-4 pt-4 relative">
    <ToastContainer />
    
    <RoomHeader
      ref="headerRef"
      :room-id="roomId"
      :user-name="userName"
      :is-host="isHost"
      :ws-status="wsStatus"
      :game-state="gameState"
      :copied="copied"
      :show-history="showHistory"
      :history-panel-style="historyPanelStyle"
      @go-home="router.push('/')"
      @copy-link="copyInviteLink"
      @toggle-history="toggleHistory"
      @close-history="showHistory = false"
      @start-timer="startTimer"
      @cancel-timer="cancelTimer"
      @handle-action="handleAction"
      @leave="leaveRoom"
    />

    <PokerTable
      :game-state="gameState"
      :user-name="userName"
      :is-host="isHost"
      :time-left="timeLeft"
      :timer-progress="timerProgress"
      :vote-average="voteAverage"
    />

    <ResultsPanel
      :game-state="gameState"
      :user-name="userName"
      :is-host="isHost"
      :vote-average="voteAverage"
    />

    <VotingDeck
      :game-state="gameState"
      :my-vote="myVote"
      :deck="deck"
      :version="appVersion"
      @select-card="selectCard"
    />

  </div>
</template>

<script setup lang="ts">
// Planning Poker - RoomView - MIT License - (c) 2026 Vinicius do Canto
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ToastContainer from '../components/ToastContainer.vue'
import RoomHeader from '../components/RoomHeader.vue'
import PokerTable from '../components/PokerTable.vue'
import ResultsPanel from '../components/ResultsPanel.vue'
import VotingDeck from '../components/VotingDeck.vue'
import type { GameState, WsServerMessage, WsStatus, CardValue, DeckType } from '../types/poker'
import { DECKS } from '../types/poker'
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
const headerRef = ref<any>(null)
const historyPanelPos = ref<{ top: number; right: number }>({ top: 0, right: 0 })

const historyPanelStyle = computed(() => ({
  top: `${historyPanelPos.value.top}px`,
  right: `${historyPanelPos.value.right}px`,
}))

const toggleHistory = (): void => {
  if (!showHistory.value && headerRef.value?.historyBtnRef) {
    const rect = headerRef.value.historyBtnRef.getBoundingClientRect()
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

<style scoped>
/* Transições e estilos globais para este view */
.pop-enter-active { animation: pop-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-leave-active { animation: pop-in 0.2s reverse; }
@keyframes pop-in { 0% { transform: scale(0.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

.animate-pulse-soft { animation: pulse-soft 2s ease-in-out infinite; }
@keyframes pulse-soft { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(0.98); } }
</style>
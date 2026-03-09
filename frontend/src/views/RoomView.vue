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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ToastContainer from '../components/ToastContainer.vue'
import RoomHeader from '../components/RoomHeader.vue'
import PokerTable from '../components/PokerTable.vue'
import ResultsPanel from '../components/ResultsPanel.vue'
import VotingDeck from '../components/VotingDeck.vue'
import { useRoomWebSocket } from '../composables/useRoomWebSocket'

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
const copied = ref<boolean>(false)

const {
  gameState,
  myVote,
  wsStatus,
  deck,
  isHost,
  connect,
  disconnect,
  selectCard,
  handleAction,
  leaveRoom,
  startTimer,
  cancelTimer
} = useRoomWebSocket(roomId.value, userName.value)

// --- Timer ---
const timeLeft = ref<number | null>(null)
let timerInterval: ReturnType<typeof setInterval> | null = null

const timerProgress = computed<number>(() => {
  const duration = gameState.value?.timer_duration ?? 60
  if (timeLeft.value === null || duration <= 0) return 1
  return Math.max(0, timeLeft.value / duration)
})

const updateTimer = () => {
  const end = gameState.value?.timer_end
  if (end) {
    const now = Date.now() / 1000
    const diff = end - now
    if (diff > 0) {
      timeLeft.value = Math.ceil(diff)
    } else {
      timeLeft.value = 0
    }
  } else {
    timeLeft.value = null
  }
}

// Ensure timer updates immediately when sync arrives
watch(() => gameState.value?.timer_end, updateTimer)

onMounted(() => {
  connect()
  timerInterval = setInterval(updateTimer, 500)
})

onUnmounted(() => {
  disconnect()
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
</script>

<style scoped>
/* Transições e estilos globais para este view */
.pop-enter-active { animation: pop-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-leave-active { animation: pop-in 0.2s reverse; }
@keyframes pop-in { 0% { transform: scale(0.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

.animate-pulse-soft { animation: pulse-soft 2s ease-in-out infinite; }
@keyframes pulse-soft { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(0.98); } }
</style>
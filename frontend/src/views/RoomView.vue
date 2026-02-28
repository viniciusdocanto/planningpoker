<template>
  <div class="min-h-screen pb-36 px-4 pt-4 relative">

    <!-- Header -->
    <header class="glass rounded-2xl px-5 py-4 mb-6 flex justify-between items-center max-w-5xl mx-auto">
      <!-- Left: Room info -->
      <div class="flex flex-col gap-0.5 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Planning Poker logo small -->
          <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-fuchsia-500 flex items-center justify-center shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h4m6-16h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-6 0V3" />
            </svg>
          </div>
          <span class="text-slate-300 font-mono text-xs truncate max-w-[140px] sm:max-w-xs" :title="roomId">{{ roomId }}</span>
          <button
            @click="copyInviteLink"
            class="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg glass-hover text-slate-400 hover:text-white transition-all"
          >
            <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            {{ copied ? 'Copiado!' : 'Copiar link' }}
          </button>
        </div>
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <span>Jogando como <span class="text-indigo-400 font-semibold">{{ userName }}</span></span>
          <span v-if="isHost" class="text-yellow-400">· 👑 Host</span>
          <!-- WS status dot -->
          <span class="flex items-center gap-1" :class="wsStatus === 'connected' ? 'text-green-500' : 'text-yellow-500 animate-pulse-soft'">
            · <span class="w-1.5 h-1.5 rounded-full inline-block" :class="wsStatus === 'connected' ? 'bg-green-500' : 'bg-yellow-500'"></span>
            {{ wsStatus === 'connected' ? 'Conectado' : 'Reconectando...' }}
          </span>
        </div>
      </div>

      <!-- Right: Actions -->
      <div class="flex items-center gap-2 shrink-0">
        <button
          v-if="isHost && !gameState.revealed"
          @click="revealVotes"
          class="bg-gradient-to-r from-indigo-500 to-purple-500 hover:opacity-90 text-white text-sm font-semibold px-5 py-2 rounded-xl transition-all shadow-lg shadow-indigo-500/20"
        >
          Revelar 🎴
        </button>
        <button
          v-if="isHost && gameState.revealed"
          @click="resetVotes"
          class="bg-gradient-to-r from-rose-500 to-pink-500 hover:opacity-90 text-white text-sm font-semibold px-5 py-2 rounded-xl transition-all shadow-lg shadow-rose-500/20"
        >
          Nova rodada 🔄
        </button>
        <button
          @click="leaveRoom"
          class="glass glass-hover text-slate-400 hover:text-white text-sm px-4 py-2 rounded-xl transition-all"
        >
          Sair
        </button>
      </div>
    </header>

    <!-- Table -->
    <div class="max-w-5xl mx-auto py-10 flex flex-col items-center">

      <!-- Empty state -->
      <div v-if="Object.keys(gameState.users).length === 0" class="text-center py-20 text-slate-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto mb-4 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p class="text-lg font-medium text-slate-500">Aguardando jogadores...</p>
        <p class="text-sm mt-1 text-slate-600">Compartilhe o link para convidar o time!</p>
      </div>

      <template v-else>
        <!-- Players arranged above and below the table oval -->
        <div class="w-full flex flex-wrap justify-center gap-8 mb-10">
          <div
            v-for="(data, user) in gameState.users"
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
                  ? 'border-2 border-dashed border-white/10 opacity-40 bg-white/5'
                  : '',
                gameState.revealed && data.voted
                  ? 'bg-white shadow-[0_8px_40px_rgba(255,255,255,0.2)]'
                  : '',
                gameState.revealed && !data.voted
                  ? 'bg-white/5 border border-white/10'
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
              <span class="flex items-center justify-center gap-1 text-xs font-medium"
                :class="user === userName ? 'text-indigo-400' : 'text-slate-300'"
              >
                <span v-if="user === gameState.host" class="text-yellow-400">👑</span>
                {{ user === userName ? 'Você' : user }}
              </span>
              <span v-if="data.voted && !gameState.revealed" class="text-[10px] text-green-400 font-semibold tracking-wide uppercase">Votou</span>
              <span v-if="!data.voted && !gameState.revealed" class="text-[10px] text-yellow-500/80 tracking-wide">pensando...</span>
              <span v-if="gameState.revealed && !data.voted" class="text-[10px] text-slate-600">não votou</span>
            </div>
          </div>
        </div>

        <!-- Oval poker table center -->
        <div class="relative w-72 h-36 rounded-full flex items-center justify-center
          bg-gradient-to-b from-emerald-900/60 to-emerald-950/80
          border-4 border-emerald-700/40
          shadow-[0_0_60px_rgba(16,185,129,0.15),inset_0_2px_20px_rgba(0,0,0,0.4)]
          mb-10"
        >
          <div class="absolute inset-3 rounded-full border border-emerald-600/20 pointer-events-none"></div>
          <template v-if="gameState.revealed && voteAverage !== null">
            <div class="text-center">
              <span class="text-4xl font-black text-white drop-shadow-lg">{{ voteAverage }}</span>
              <p class="text-xs text-emerald-400/70 font-medium mt-0.5 tracking-wider uppercase">média</p>
            </div>
          </template>
          <template v-else-if="gameState.revealed">
            <span class="text-emerald-500/50 text-sm font-medium">Sem votos</span>
          </template>
          <template v-else>
            <div class="text-center">
              <p class="text-emerald-500/40 text-sm font-medium">
                {{ Object.values(gameState.users).filter(u => u.voted).length }}/{{ Object.keys(gameState.users).length }}
              </p>
              <p class="text-emerald-600/30 text-xs">votaram</p>
            </div>
          </template>
        </div>

        <!-- Non-host hint -->
        <p v-if="!isHost && !gameState.revealed" class="text-xs text-slate-600 mb-4">
          Aguardando <span class="text-yellow-500 font-medium">{{ gameState.host }}</span> revelar as cartas.
        </p>
      </template>
    </div>

    <!-- Results panel after reveal -->
    <div v-if="gameState.revealed" class="max-w-5xl mx-auto mb-6">
      <div class="glass rounded-2xl p-6 border border-white/5">
        <h2 class="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">📊 Resultados</h2>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="(data, user) in gameState.users"
            :key="user"
            class="flex items-center gap-2 bg-white/5 rounded-xl px-4 py-2.5 border border-white/[0.06]"
          >
            <span v-if="user === gameState.host" class="text-yellow-400 text-xs">👑</span>
            <span class="text-sm text-slate-300">{{ user === userName ? 'Você' : user }}</span>
            <span class="font-bold text-sm px-2 py-0.5 rounded-lg"
              :class="data.voted ? 'bg-indigo-500/30 text-indigo-300' : 'bg-white/5 text-slate-600'"
            >{{ data.voted ? data.vote : '—' }}</span>
          </div>
        </div>
        <div v-if="voteAverage !== null" class="mt-4 pt-4 border-t border-white/5 flex items-center gap-3">
          <span class="text-xs text-slate-500">Média dos votos numéricos</span>
          <span class="text-3xl font-black text-gradient">{{ voteAverage }}</span>
        </div>
        <p v-if="isHost" class="mt-3 text-xs text-slate-600">
          Clique em <span class="text-rose-400 font-medium">Nova rodada 🔄</span> no topo quando estiver pronto.
        </p>
      </div>
    </div>

    <!-- Fixed card deck at bottom -->
    <div v-if="!gameState.revealed" class="fixed bottom-0 left-0 w-full z-20">
      <div class="glass border-t border-white/5 px-4 pt-4 pb-5 backdrop-blur-xl">
        <div class="max-w-5xl mx-auto flex gap-2.5 overflow-x-auto justify-start sm:justify-center custom-scrollbar">
          <button
            v-for="card in deck"
            :key="card"
            @click="selectCard(card)"
            class="flex-shrink-0 w-[52px] h-[72px] rounded-xl font-bold text-lg border-2 transition-all duration-200 card-hover select-none"
            :class="myVote === card
              ? 'bg-gradient-to-b from-indigo-400 to-indigo-600 border-indigo-400 text-white card-selected shadow-[0_0_20px_rgba(99,102,241,0.6)]'
              : 'bg-white text-gray-800 border-gray-200/20 hover:border-indigo-400/60'"
          >
            {{ card }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const roomId = route.params.id
const userName = sessionStorage.getItem('playerName')
const deck = ['0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕']

const gameState = ref({ users: {}, revealed: false, host: null })
const myVote = ref(null)
const copied = ref(false)
const wsStatus = ref('connecting')

let ws = null
let reconnectTimer = null

const isHost = computed(() => gameState.value.host === userName)

const voteAverage = computed(() => {
  if (!gameState.value.revealed) return null
  const nums = Object.values(gameState.value.users)
    .filter(d => d.voted && !isNaN(parseFloat(d.vote)))
    .map(d => parseFloat(d.vote))
  if (!nums.length) return null
  const avg = nums.reduce((a, b) => a + b, 0) / nums.length
  return Number.isInteger(avg) ? avg : avg.toFixed(1)
})

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

const connect = () => {
  if (!userName) { router.push('/'); return }
  ws = new WebSocket(`${WS_BASE}/ws/${roomId}/${encodeURIComponent(userName)}`)
  ws.onopen = () => { wsStatus.value = 'connected'; if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null } }
  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data)
      if (msg.type === 'state_update') {
        gameState.value = msg.data
        if (gameState.value.users[userName] && !gameState.value.users[userName].voted) myVote.value = null
      }
    } catch (err) {
      console.warn('Received invalid message from server:', err)
    }
  }
  ws.onclose = () => { wsStatus.value = 'reconnecting'; reconnectTimer = setTimeout(connect, 3000) }
  ws.onerror = () => ws.close()
}

onMounted(connect)
onUnmounted(() => { if (reconnectTimer) clearTimeout(reconnectTimer); if (ws) { ws.onclose = null; ws.close() } })

const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(`${window.location.origin}/?room=${roomId}`)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (e) { console.error(e) }
}

const selectCard = (card) => {
  myVote.value = card
  if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'vote', value: card }))
}
const revealVotes = () => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'reveal' })) }
const resetVotes = () => { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'reset' })) }
const leaveRoom = () => { if (ws) { ws.onclose = null; ws.close() }; router.push('/') }
</script>

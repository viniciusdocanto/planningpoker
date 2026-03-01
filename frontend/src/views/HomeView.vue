<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-4 relative">

    <!-- Top Controls -->
    <div class="fixed top-6 right-6 z-50 flex items-center gap-3">
      <LanguageSelector />
      <ThemeToggle />
    </div>

    <!-- Logo + Tagline -->
    <div class="text-center mb-10 animate-float">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-5 bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 shadow-lg glow-purple">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h4m6-16h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-6 0V3" />
        </svg>
      </div>
      <h1 class="text-5xl font-extrabold tracking-tight text-gradient mb-3">{{ $t('home.title') }}</h1>
      <p class="text-black dark:text-slate-400 text-lg max-w-sm font-black">
        {{ $t('home.tagline') }}
      </p>
    </div>

    <!-- Card -->
    <div class="glass rounded-3xl p-8 w-full max-w-md card-shadow border-slate-200 dark:border-white/5">

      <!-- Join via link - special state -->
      <template v-if="isJoiningViaLink">
        <div class="flex items-center gap-3 mb-6 p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
          <div class="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-500 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-[10px] text-indigo-800 dark:text-indigo-400 font-black uppercase tracking-wider mb-0.5">{{ $t('home.enteringRoom') }}</p>
            <p class="text-black dark:text-white font-mono text-sm truncate" :title="roomId">{{ roomId }}</p>
          </div>
        </div>
      </template>

      <template v-else>
        <h2 class="text-xl font-black text-black dark:text-white mb-6">{{ $t('home.joinOrCreate') }}</h2>
      </template>

      <div class="space-y-4">
        <!-- Name Input -->
        <div>
          <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2">{{ $t('home.yourName') }}</label>
          <input
            v-model="userName"
            type="text"
            :placeholder="$t('home.namePlaceholder')"
            autofocus
            @keyup.enter="handleAction"
            class="w-full bg-slate-950/5 dark:bg-white/5 border border-slate-500 dark:border-white/10 rounded-xl px-4 py-3.5 text-black dark:text-white placeholder-slate-700 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-500/40 transition-all text-sm font-black"
          >
        </div>

        <!-- Room ID Input (only if NOT joining via link) -->
        <div v-if="!isJoiningViaLink">
          <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2">{{ $t('home.roomId') }} <span class="normal-case font-normal text-slate-700 dark:text-slate-500">{{ $t('home.optional') }}</span></label>
          <input
            v-model="roomId"
            type="text"
            :placeholder="$t('home.roomPlaceholder')"
            @keyup.enter="handleAction"
            class="w-full bg-slate-950/5 dark:bg-white/5 border border-slate-500 dark:border-white/10 rounded-xl px-4 py-3.5 text-black dark:text-white placeholder-slate-700 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-500/40 transition-all text-sm font-black"
          >
        </div>

        <!-- Deck type selector (only when creating a new room) -->
        <div v-if="!isJoiningViaLink && !roomId.trim()">
          <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2">{{ $t('home.deckType') }}</label>
          <div class="flex gap-2">
            <button
              v-for="(label, type) in DECK_LABELS"
              :key="type"
              type="button"
              @click="deckType = type as DeckType"
              :class="[
                'flex-1 py-2.5 rounded-xl text-xs font-bold transition-all duration-150 border',
                deckType === type
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-500/30'
                  : 'bg-slate-950/5 dark:bg-white/5 border-slate-500 dark:border-white/10 text-black dark:text-slate-300 hover:border-indigo-400'
              ]"
            >{{ label }}</button>
          </div>
        </div>

        <!-- Action Button -->
        <button
          @click="handleAction"
          :disabled="!isNameValid"
          class="w-full relative overflow-hidden font-black py-4 rounded-xl transition-all duration-200 text-sm mt-2
            bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-500
            text-white shadow-lg shadow-purple-500/25
            hover:opacity-90 hover:scale-[1.01]
            disabled:opacity-40 disabled:cursor-not-allowed
            active:scale-[0.98]"
        >
          <span class="relative z-10 flex items-center justify-center gap-2">
            {{ isJoiningViaLink || roomId.trim() ? $t('home.joinRoom') : $t('home.createRoom') }}
          </span>
        </button>

        <!-- Error message -->
        <p v-if="errorMsg" class="text-rose-400 text-xs text-center mt-1">⚠️ {{ errorMsg }}</p>
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-8 text-[10px] text-black dark:text-slate-600 uppercase tracking-widest font-black flex flex-col items-center gap-1.5">
      <div class="flex items-center">
        <a href="https://github.com/viniciusdocanto/planningpoker" target="_blank" class="hover:text-indigo-800 dark:hover:text-indigo-400 transition-colors">{{ $t('common.openSource') }}</a>
        <span class="mx-2 opacity-50">|</span>
        <a href="https://docanto.net" target="_blank" class="hover:text-fuchsia-800 dark:hover:text-fuchsia-400 transition-colors font-black underline decoration-fuchsia-500/30 underline-offset-4">{{ $t('common.by') }}</a>
      </div>
      <span class="opacity-30 tracking-normal normal-case font-mono text-[8px]">v{{ appVersion }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// Planning Poker - HomeView - MIT License - (c) 2026 Vinicius do Canto
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import LanguageSelector from '../components/LanguageSelector.vue'
import type { DeckType } from '../types/poker'
import { DECK_LABELS } from '../types/poker'
import { useI18n } from 'vue-i18n'

const { t: $t } = useI18n()
const router = useRouter()
const route = useRoute()
const userName = ref<string>('')
const roomId = ref<string>('')
const deckType = ref<DeckType>('fibonacci')
const isJoiningViaLink = ref<boolean>(false)
const errorMsg = ref<string>('')

// Mirrors the server-side validation rules
const VALID_NAME_RE = /^[a-zA-ZÀ-ÿ0-9\s\-.]{1,30}$/u
const VALID_ROOM_RE = /^[A-Za-z0-9\-_]{1,40}$/

const isNameValid = computed(() =>
  userName.value.trim().length > 0 && VALID_NAME_RE.test(userName.value.trim())
)

onMounted(() => {
  // Load saved name
  const savedName = localStorage.getItem('poker-player-name')
  if (savedName) userName.value = savedName

  if (route.query.room) {
    const roomParam = String(route.query.room)
    if (VALID_ROOM_RE.test(roomParam)) {
      roomId.value = roomParam
      isJoiningViaLink.value = true
    }
  }
})

const generateRandomId = (length: number = 20): string => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  return result
}

const handleAction = () => {
  errorMsg.value = ''
  const name = userName.value.trim()
  if (!name) return

  if (!VALID_NAME_RE.test(name)) {
    errorMsg.value = 'Nome inválido. Use apenas letras (incluindo acentos), números, espaços, hífens ou pontos (máx. 30 chars).'
    return
  }

  const customRoom = roomId.value.trim()
  if (customRoom && !VALID_ROOM_RE.test(customRoom)) {
    errorMsg.value = 'ID de sala inválido. Use apenas letras, números, hífens ou underscores (máx. 40 chars).'
    return
  }

  const targetRoom = customRoom || generateRandomId(20)
  
  // Persist name
  localStorage.setItem('poker-player-name', name)
  sessionStorage.setItem('playerName', name)
  // Store deck choice in sessionStorage — keeps the URL clean
  sessionStorage.setItem('poker-deck', deckType.value)
  router.push(`/room/${targetRoom}`)
}
const appVersion: string = __APP_VERSION__
</script>


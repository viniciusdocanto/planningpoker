<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-4 relative">

    <!-- Top Controls -->
    <div class="fixed top-6 right-6 z-50 flex items-center gap-3">
      <LanguageSelector />
      <ThemeToggle />
    </div>

    <!-- Logo + Tagline -->
    <HomeHeader />

    <!-- Card -->
    <EntranceCard
      v-model:userName="userName"
      v-model:roomId="roomId"
      v-model:deckType="deckType"
      :is-joining-via-link="isJoiningViaLink"
      :deck-labels="DECK_LABELS"
      :error-msg="errorMsg"
      :is-name-valid="isNameValid"
      @action="handleAction"
    />

    <!-- Footer -->
    <AppFooter :version="appVersion" class="mt-10" />
  </div>
</template>

<script setup lang="ts">
// Planning Poker - HomeView - MIT License - (c) 2026 Vinicius do Canto
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import LanguageSelector from '../components/LanguageSelector.vue'
import AppFooter from '../components/AppFooter.vue'
import HomeHeader from '../components/HomeHeader.vue'
import EntranceCard from '../components/EntranceCard.vue'
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


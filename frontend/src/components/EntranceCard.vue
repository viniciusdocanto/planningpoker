<template>
  <div class="glass rounded-3xl p-8 w-full max-w-md card-shadow border-slate-200 dark:border-white/5 mx-auto text-left">

    <!-- Join via link - special state -->
    <template v-if="props.isJoiningViaLink">
      <div class="flex items-center gap-3 mb-6 p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
        <div class="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-indigo-500 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div class="min-w-0">
          <p class="text-[10px] text-indigo-800 dark:text-indigo-400 font-black uppercase tracking-wider mb-0.5">{{ t('home.enteringRoom') }}</p>
          <p class="text-black dark:text-white font-mono text-sm truncate" :title="props.roomId">{{ props.roomId }}</p>
        </div>
      </div>
    </template>

    <template v-else>
      <h2 class="text-xl font-black text-black dark:text-white mb-6">{{ t('home.joinOrCreate') }}</h2>
    </template>

    <div class="space-y-4">
      <!-- Name Input -->
      <div>
        <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2 leading-none">{{ t('home.yourName') }}</label>
        <input
          :value="props.userName"
          @input="$emit('update:userName', ($event.target as HTMLInputElement).value)"
          type="text"
          :placeholder="t('home.namePlaceholder')"
          autofocus
          @keyup.enter="$emit('action')"
          class="w-full bg-slate-950/5 dark:bg-white/5 border border-slate-500 dark:border-white/10 rounded-xl px-4 py-3.5 text-black dark:text-white placeholder-slate-700 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-500/40 transition-all text-sm font-black"
        >
      </div>

      <!-- Room ID Input (only if NOT joining via link) -->
      <div v-if="!props.isJoiningViaLink">
        <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2 leading-none">
          {{ t('home.roomId') }} <span class="normal-case font-normal text-slate-700 dark:text-slate-500">{{ t('home.optional') }}</span>
        </label>
        <input
          :value="props.roomId"
          @input="$emit('update:roomId', ($event.target as HTMLInputElement).value)"
          type="text"
          :placeholder="t('home.roomPlaceholder')"
          @keyup.enter="$emit('action')"
          class="w-full bg-slate-950/5 dark:bg-white/5 border border-slate-500 dark:border-white/10 rounded-xl px-4 py-3.5 text-black dark:text-white placeholder-slate-700 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-500/40 transition-all text-sm font-black"
        >
      </div>

      <!-- Deck type selector (only when creating a new room) -->
      <div v-if="!props.isJoiningViaLink && !props.roomId.trim()">
        <label class="block text-xs font-black text-black dark:text-slate-400 uppercase tracking-wider mb-2 leading-none">{{ t('home.deckType') }}</label>
        <div class="flex gap-2">
          <button
            v-for="(label, type) in props.deckLabels"
            :key="type"
            type="button"
            @click="$emit('update:deckType', type)"
            :class="[
              'flex-1 py-2.5 rounded-xl text-xs font-bold transition-all duration-150 border',
              props.deckType === type
                ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-500/30'
                : 'bg-slate-950/5 dark:bg-white/5 border-slate-500 dark:border-white/10 text-black dark:text-slate-300 hover:border-indigo-400'
            ]"
          >{{ label }}</button>
        </div>
      </div>

      <!-- Action Button -->
      <button
        @click="$emit('action')"
        :disabled="!props.isNameValid"
        class="w-full relative overflow-hidden font-black py-4 rounded-xl transition-all duration-200 text-sm mt-2
          bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-500
          text-white shadow-lg shadow-purple-500/25
          hover:opacity-90 hover:scale-[1.01]
          disabled:opacity-40 disabled:cursor-not-allowed
          active:scale-[0.98]"
      >
        <span class="relative z-10 flex items-center justify-center gap-2">
          {{ props.isJoiningViaLink || props.roomId.trim() ? t('home.joinRoom') : t('home.createRoom') }}
        </span>
      </button>

      <!-- Error message -->
      <p v-if="props.errorMsg" class="text-rose-400 text-xs text-center mt-1 font-bold">⚠️ {{ props.errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DeckType } from '../types/poker'
const { t } = useI18n()

const props = defineProps<{
  isJoiningViaLink: boolean
  userName: string
  roomId: string
  deckType: DeckType
  deckLabels: Record<string, string>
  errorMsg: string
  isNameValid: boolean
}>()

defineEmits(['update:userName', 'update:roomId', 'update:deckType', 'action'])
</script>

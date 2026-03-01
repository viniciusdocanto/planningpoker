<script setup lang="ts">
// Planning Poker - ToastContainer - MIT License - (c) 2026 Vinicius do Canto
import { useToast } from '../composables/useToast'
import type { ToastType } from '../composables/useToast'

const { toasts, removeToast } = useToast()

const icons: Record<ToastType, string> = {
  success: '✅',
  error: '❌',
  info: 'ℹ️',
  warning: '⚠️',
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast" tag="div" class="toast-list">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast--${toast.type}`]"
          role="alert"
          @click="removeToast(toast.id)"
        >
          <span class="toast__icon">{{ icons[toast.type] }}</span>
          <span class="toast__message">{{ toast.message }}</span>
          <button class="toast__close" @click.stop="removeToast(toast.id)" aria-label="Fechar">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  pointer-events: none;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 240px;
  max-width: 360px;
  cursor: pointer;
  pointer-events: all;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.toast:hover { transform: scale(1.02); }

.toast--success { background: rgba(22, 163, 74, 0.85); color: #fff; }
.toast--error   { background: rgba(220, 38, 38, 0.85); color: #fff; }
.toast--info    { background: rgba(37, 99, 235, 0.85);  color: #fff; }
.toast--warning { background: rgba(202, 138, 4, 0.85);  color: #fff; }

.toast__icon   { font-size: 1rem; flex-shrink: 0; }
.toast__message { flex: 1; line-height: 1.4; }
.toast__close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 0.25rem;
  flex-shrink: 0;
  transition: color 0.15s;
}
.toast__close:hover { color: #fff; }

/* TransitionGroup animations */
.toast-enter-active,
.toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from { opacity: 0; transform: translateX(120%); }
.toast-leave-to  { opacity: 0; transform: translateX(120%); }
</style>

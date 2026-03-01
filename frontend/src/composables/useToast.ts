// Planning Poker - useToast composable - MIT License - (c) 2026 Vinicius do Canto
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
    id: number
    message: string
    type: ToastType
}

const toasts = ref<Toast[]>([])
let nextId = 0

export function useToast() {
    const addToast = (message: string, type: ToastType = 'info', duration = 4000): void => {
        const id = ++nextId
        toasts.value.push({ id, message, type })
        setTimeout(() => removeToast(id), duration)
    }

    const removeToast = (id: number): void => {
        toasts.value = toasts.value.filter(t => t.id !== id)
    }

    return { toasts, addToast, removeToast }
}

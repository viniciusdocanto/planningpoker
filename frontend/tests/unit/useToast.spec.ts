import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useToast } from '../../src/composables/useToast'

describe('useToast composable', () => {
    beforeEach(() => {
        vi.useFakeTimers()
        const { toasts } = useToast()
        toasts.value = []
    })

    it('adds and removes toasts correctly', () => {
        const { toasts, addToast, removeToast } = useToast()
        expect(toasts.value.length).toBe(0)

        addToast('Message 1', 'success', 2000)
        expect(toasts.value.length).toBe(1)
        expect(toasts.value[0].message).toBe('Message 1')
        expect(toasts.value[0].type).toBe('success')

        const toastId = toasts.value[0].id
        removeToast(toastId)
        expect(toasts.value.length).toBe(0)
    })

    it('auto-removes toast after duration', () => {
        const { toasts, addToast } = useToast()
        addToast('Timed message', 'info', 3000)
        expect(toasts.value.length).toBe(1)

        vi.advanceTimersByTime(3000)
        expect(toasts.value.length).toBe(0)
    })
})

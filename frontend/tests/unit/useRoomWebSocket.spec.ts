import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useRoomWebSocket } from '../../src/composables/useRoomWebSocket'

// Mock dependencies
vi.mock('vue-router', () => ({
    useRoute: vi.fn(),
    useRouter: vi.fn(() => ({
        push: vi.fn()
    }))
}))

vi.mock('vue-i18n', () => ({
    useI18n: vi.fn(() => ({
        t: (key: string) => key
    }))
}))

vi.mock('../../src/composables/useToast', () => ({
    useToast: vi.fn(() => ({
        addToast: vi.fn()
    }))
}))

vi.mock('../../src/composables/useFeedback', () => ({
    useFeedback: vi.fn(() => ({
        vibrate: vi.fn(),
        playRevealSound: vi.fn(),
        playClickSound: vi.fn()
    }))
}))

describe('useRoomWebSocket composable', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        sessionStorage.clear()
        localStorage.clear()
    })

    it('initializes with default values and fibonacci deck', () => {
        const { gameState, wsStatus, isHost, deck } = useRoomWebSocket('room123', 'John')

        expect(wsStatus.value).toBe('connecting')
        expect(gameState.value.revealed).toBe(false)
        expect(gameState.value.users).toEqual({})
        expect(gameState.value.deck_type).toBe('fibonacci')
        expect(isHost.value).toBe(false)
        expect(deck.value).toContain('5')
        expect(deck.value).toContain('?')
    })

    it('identifies as host if userName matches gameState.host', () => {
        const { gameState, isHost } = useRoomWebSocket('room123', 'John')
        expect(isHost.value).toBe(false)

        gameState.value.host = 'John'
        expect(isHost.value).toBe(true)
    })

    it('selects card and updates myVote', () => {
        const { myVote, selectCard } = useRoomWebSocket('room123', 'John')
        expect(myVote.value).toBe(null)

        // Cannot fully test send over WS unless we mock WebSocket, 
        // but we can ensure the reactive state updates locally
        selectCard('8')
        expect(myVote.value).toBe('8')
    })
})

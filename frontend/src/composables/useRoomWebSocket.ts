// Planning Poker - useRoomWebSocket - MIT License - (c) 2026 Vinicius do Canto
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from './useToast'
import { useFeedback } from './useFeedback'
import type { GameState, WsServerMessage, WsStatus, CardValue, DeckType } from '../types/poker'
import { DECKS } from '../types/poker'

export function useRoomWebSocket(roomId: string, userName: string) {
    const router = useRouter()
    const { t: $t } = useI18n()
    const { addToast } = useToast()
    const { vibrate, playRevealSound, playClickSound } = useFeedback()

    const gameState = ref<GameState>({
        users: {}, revealed: false, host: null,
        deck_type: (sessionStorage.getItem('poker-deck') as DeckType) || 'fibonacci',
        round_number: 0, history: [], timer_end: null, timer_duration: 60,
        server_time: Date.now() / 1000
    })

    const myVote = ref<CardValue | null>(null)
    const wsStatus = ref<WsStatus>('connecting')
    const serverSkew = ref<number>(0) // serverTime - localTime

    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null

    const deck = computed<readonly string[]>(() => DECKS[gameState.value.deck_type] ?? DECKS.fibonacci)
    const isHost = computed<boolean>(() => gameState.value.host === userName)

    const rawWsUrl: string = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const WS_BASE: string = rawWsUrl.replace(/^http/, 'ws')

    const connect = (): void => {
        if (!userName) { router.push('/'); return }
        const deckParam = sessionStorage.getItem('poker-deck') || 'fibonacci'
        ws = new WebSocket(`${WS_BASE}/ws/${roomId}/${encodeURIComponent(userName)}?deck=${encodeURIComponent(deckParam)}`)

        ws.onopen = () => {
            console.log('🔌 WebSocket: Connected!')
            wsStatus.value = 'connected'
            if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
            addToast($t('room.connected'), 'success')
        }

        ws.onmessage = (e: MessageEvent<string>) => {
            try {
                const msg = JSON.parse(e.data) as WsServerMessage
                if (msg.type === 'ping') {
                    if (ws?.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ action: 'pong' }))
                    }
                    return
                }
                if (msg.type === 'state_update' && msg.data) {
                    const wasRevealed = gameState.value?.revealed ?? false

                    const rawData = msg.data as any
                    const updatedState: GameState = {
                        ...gameState.value,
                        ...rawData,
                        users: rawData.users || {},
                        history: rawData.history || []
                    }

                    if (rawData.server_time) {
                        serverSkew.value = rawData.server_time - (Date.now() / 1000)
                    }

                    gameState.value = updatedState

                    // Debug: check timer update
                    if (updatedState.timer_end) {
                        console.log(`⏱️ Timer sync: ends at ${updatedState.timer_end} (now: ${Date.now() / 1000})`)
                    }

                    if (gameState.value.revealed && !wasRevealed) {
                        playRevealSound()
                    }

                    const me = (gameState.value.users as any)[userName]
                    if (me && !me.voted) myVote.value = null
                } else if (msg.type === 'event_notify') {
                    if (msg.event === 'user_joined' && msg.user !== userName) {
                        addToast($t('room.userJoined', { user: msg.user || '?' }), 'info')
                    } else if (msg.event === 'user_left' && msg.user !== userName) {
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

    const disconnect = (): void => {
        if (reconnectTimer) clearTimeout(reconnectTimer)
        if (ws) { ws.onclose = null; ws.close() }
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
    const leaveRoom = (): void => { disconnect(); router.push('/') }

    const startTimer = (secs: number): void => {
        if (ws?.readyState === WebSocket.OPEN)
            ws.send(JSON.stringify({ action: 'start_timer', value: String(secs) }))
    }

    const cancelTimer = (): void => {
        if (ws?.readyState === WebSocket.OPEN)
            ws.send(JSON.stringify({ action: 'cancel_timer' }))
    }

    return {
        gameState,
        myVote,
        wsStatus,
        serverSkew,
        deck,
        isHost,
        connect,
        disconnect,
        selectCard,
        handleAction,
        revealVotes,
        resetVotes,
        leaveRoom,
        startTimer,
        cancelTimer
    }
}

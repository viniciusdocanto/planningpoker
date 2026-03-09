// Planning Poker - Shared Types - MIT License - (c) 2026 Vinicius do Canto

/** Individual user vote state sent by the server */
export interface UserData {
    vote?: string | null
    voted: boolean
}

/** A completed voting round stored in history */
export interface RoundRecord {
    round: number
    votes: Record<string, string>
    average: number | null
}

/** Full game state received via WebSocket state_update messages */
export interface GameState {
    users: Record<string, UserData>
    revealed: boolean
    host: string | null
    deck_type: DeckType
    round_number: number
    history: RoundRecord[]
    timer_end: number | null
    timer_duration: number
}

/** Outgoing WebSocket message shape */
export interface WsOutMessage {
    action: 'vote' | 'reveal' | 'reset'
    value?: string
}

/** Event notification sent by the server (user joined/left or deck changed) */
export interface WsEventMessage {
    type: 'event_notify'
    event: 'user_joined' | 'user_left' | 'deck_changed'
    user: string
    deck_type?: DeckType
}

/** Incoming WebSocket message wrapper */
export interface WsInMessage {
    type: 'state_update'
    data: GameState
}

/** Incoming Ping message from server */
export interface WsPingMessage {
    type: 'ping'
}

/** All possible incoming WebSocket messages */
export type WsServerMessage = WsInMessage | WsEventMessage | WsPingMessage

/** WebSocket connection status */
export type WsStatus = 'connecting' | 'connected' | 'reconnecting'

/** Supported deck types */
export type DeckType = 'fibonacci' | 'powers2' | 'tshirt'

export const DECKS: Record<DeckType, readonly string[]> = {
    fibonacci: ['0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'],
    powers2: ['0', '1', '2', '4', '8', '16', '32', '64', '?', '☕'],
    tshirt: ['XS', 'S', 'M', 'L', 'XL', 'XXL', '?', '☕'],
} as const

export const DECK_LABELS: Record<DeckType, string> = {
    fibonacci: 'Fibonacci',
    powers2: 'Potências de 2',
    tshirt: 'T-Shirt Sizes',
}

/** Valid Fibonacci/special card values */
export const DECK = DECKS.fibonacci
export type CardValue = string

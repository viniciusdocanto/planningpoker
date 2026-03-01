// Planning Poker - Shared Types - MIT License - (c) 2026 Vinicius do Canto

/** Individual user vote state sent by the server */
export interface UserData {
    vote?: string | null
    voted: boolean
}

/** Full game state received via WebSocket state_update messages */
export interface GameState {
    users: Record<string, UserData>
    revealed: boolean
    host: string | null
}

/** Outgoing WebSocket message shape */
export interface WsOutMessage {
    action: 'vote' | 'reveal' | 'reset'
    value?: string
}

/** Incoming WebSocket message wrapper */
export interface WsInMessage {
    type: 'state_update'
    data: GameState
}

/** WebSocket connection status */
export type WsStatus = 'connecting' | 'connected' | 'reconnecting'

/** Valid Fibonacci/special card values */
export const DECK = ['0', '½', '1', '2', '3', '5', '8', '13', '21', '34', '55', '89', '?', '☕'] as const
export type CardValue = (typeof DECK)[number]

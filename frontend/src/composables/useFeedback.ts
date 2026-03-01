/**
 * Planning Poker - useFeedback Composable
 * Handles haptic and sound feedback using native browser APIs.
 */

export function useFeedback() {
    /**
     * Triggers a short vibration if supported by the device.
     * @param duration - Duration in milliseconds (default 50ms)
     */
    const vibrate = (duration = 50) => {
        if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
            try {
                navigator.vibrate(duration)
            } catch (e) {
                // Ignore errors in browsers that might block vibration
            }
        }
    }

    /**
     * Synthesizes a subtle card flip/reveal sound.
     */
    const playRevealSound = () => {
        if (typeof window === 'undefined') return
        try {
            const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext
            if (!AudioContextClass) return

            const ctx = new AudioContextClass()
            const osc = ctx.createOscillator()
            const gain = ctx.createGain()

            // Card flip sound is often a quick mid-to-high frequency transition
            osc.type = 'sine'
            osc.frequency.setValueAtTime(400, ctx.currentTime)
            osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.1)

            gain.gain.setValueAtTime(0, ctx.currentTime)
            gain.gain.linearRampToValueAtTime(0.1, ctx.currentTime + 0.02)
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15)

            osc.connect(gain)
            gain.connect(ctx.destination)

            osc.start()
            osc.stop(ctx.currentTime + 0.15)

            // Close context after playback to save resources
            setTimeout(() => ctx.close(), 200)
        } catch (e) {
            // Browsers might block audio until interaction
        }
    }

    /**
     * Synthesizes a subtle button click sound.
     */
    const playClickSound = () => {
        if (typeof window === 'undefined') return
        try {
            const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext
            if (!AudioContextClass) return

            const ctx = new AudioContextClass()
            const osc = ctx.createOscillator()
            const gain = ctx.createGain()

            osc.type = 'sine'
            osc.frequency.setValueAtTime(800, ctx.currentTime)
            osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.05)

            gain.gain.setValueAtTime(0, ctx.currentTime)
            gain.gain.linearRampToValueAtTime(0.05, ctx.currentTime + 0.01)
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05)

            osc.connect(gain)
            gain.connect(ctx.destination)

            osc.start()
            osc.stop(ctx.currentTime + 0.05)
            setTimeout(() => ctx.close(), 100)
        } catch (e) { }
    }

    return {
        vibrate,
        playRevealSound,
        playClickSound
    }
}

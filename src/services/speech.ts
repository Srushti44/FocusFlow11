// Web Speech API Native Text-To-Speech Controller

class SpeechController {
  private synth: SpeechSynthesis | null = null;
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private isSpeaking = false;
  private isPaused = false;
  private onEndCallback: (() => void) | null = null;
  private listeners: Set<(state: { isSpeaking: boolean; isPaused: boolean; isSupported: boolean }) => void> = new Set();

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
    }
  }

  public subscribe(listener: (state: { isSpeaking: boolean; isPaused: boolean; isSupported: boolean }) => void) {
    this.listeners.add(listener);
    listener(this.getState());
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    const state = this.getState();
    this.listeners.forEach((fn) => fn(state));
  }

  public speak(text: string, rate: number = 1.0, onEnd?: () => void) {
    if (!this.synth) {
      console.warn('[FocusFlow TTS] Speech synthesis is not supported on this platform.');
      return;
    }

    this.stop();
    this.onEndCallback = onEnd || null;

    const cleanText = text.replace(/[*_#`~>]/g, '').trim();
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = Math.max(0.5, Math.min(2.0, rate));
    utterance.pitch = 1.0;

    utterance.onend = () => {
      this.isSpeaking = false;
      this.isPaused = false;
      this.currentUtterance = null;
      this.notify();
      if (this.onEndCallback) {
        const cb = this.onEndCallback;
        this.onEndCallback = null;
        cb();
      }
    };

    utterance.onerror = (e) => {
      // Chrome emits 'canceled' or 'interrupted' event upon synth.cancel(); gracefully reset
      this.isSpeaking = false;
      this.isPaused = false;
      this.onEndCallback = null;
      this.currentUtterance = null;
      this.notify();
    };

    this.currentUtterance = utterance;
    try {
      this.synth.speak(utterance);
      this.isSpeaking = true;
      this.isPaused = false;
      this.notify();
    } catch (err) {
      console.warn('[FocusFlow TTS] Speak error:', err);
      this.isSpeaking = false;
      this.notify();
    }
  }

  public pause() {
    if (this.synth && this.isSpeaking && !this.isPaused) {
      try {
        this.synth.pause();
        this.isPaused = true;
        this.notify();
      } catch {}
    }
  }

  public resume() {
    if (this.synth && this.isPaused) {
      try {
        this.synth.resume();
        this.isPaused = false;
        this.notify();
      } catch {}
    }
  }

  public stop() {
    this.onEndCallback = null;
    if (this.currentUtterance) {
      this.currentUtterance.onend = null;
      this.currentUtterance.onerror = null;
      this.currentUtterance = null;
    }
    if (this.synth) {
      if (this.synth.paused) {
        try {
          this.synth.resume();
        } catch {}
      }
      try {
        this.synth.cancel();
      } catch (err) {
        console.warn('[FocusFlow TTS] Cancel error:', err);
      }
      this.isSpeaking = false;
      this.isPaused = false;
      this.notify();
    }
  }

  public getState() {
    return {
      isSpeaking: this.isSpeaking,
      isPaused: this.isPaused,
      isSupported: !!this.synth
    };
  }
}

export const speechService = new SpeechController();

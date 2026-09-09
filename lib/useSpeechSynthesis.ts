'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseSpeechSynthesisOptions {
  onEnd?: () => void;
  onError?: (error: string) => void;
}

export function useSpeechSynthesis(options?: UseSpeechSynthesisOptions) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [currentText, setCurrentText] = useState<string | null>(null);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);
    }
  }, []);

  const stop = useCallback(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentText(null);
      setVoiceNotice(null);
    }
  }, []);

  const pause = useCallback(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window && isPlaying) {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  }, [isPlaying]);

  const resume = useCallback(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window && isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    }
  }, [isPaused]);

  const speak = useCallback(
    (text: string, lang: string = 'en') => {
      if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
        options?.onError?.('Text-to-speech is not supported in this browser.');
        return;
      }

      // Stop any current utterance
      window.speechSynthesis.cancel();
      setVoiceNotice(null);

      // Strip markdown bold/asterisks and clean text
      const cleanText = text
        .replace(/[*_#`~]/g, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/https?:\/\/\S+/g, '')
        .trim();

      if (!cleanText) return;

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utteranceRef.current = utterance;
      setCurrentText(cleanText);

      const voices = window.speechSynthesis.getVoices();
      const normLang = (lang || 'en').toLowerCase();

      let targetVoice: SpeechSynthesisVoice | undefined;

      if (normLang.startsWith('mr') || normLang === 'marathi') {
        targetVoice = voices.find(
          (v) => v.lang.toLowerCase().startsWith('mr') || v.name.toLowerCase().includes('marathi')
        );
        if (!targetVoice) {
          // Honest fallback notice: Do NOT substitute Hindi for Marathi
          setVoiceNotice(
            'Marathi voice is not installed on this device/browser. Displaying text-only response.'
          );
          options?.onError?.(
            'A Marathi speech synthesis voice is not installed in your browser. Speech output cannot be played in Marathi.'
          );
          return;
        }
      } else if (normLang.startsWith('hi') || normLang === 'hindi') {
        targetVoice = voices.find(
          (v) => v.lang.toLowerCase().startsWith('hi') || v.name.toLowerCase().includes('hindi')
        );
      } else {
        // English (prefer Indian English if available, else default)
        targetVoice =
          voices.find((v) => v.lang.toLowerCase() === 'en-in') ||
          voices.find((v) => v.lang.toLowerCase().startsWith('en'));
      }

      if (targetVoice) {
        utterance.voice = targetVoice;
        utterance.lang = targetVoice.lang;
      }

      utterance.rate = 0.95; // Clear maritime advisory cadence
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        setIsPlaying(true);
        setIsPaused(false);
      };

      utterance.onend = () => {
        setIsPlaying(false);
        setIsPaused(false);
        setCurrentText(null);
        options?.onEnd?.();
      };

      utterance.onerror = (e: any) => {
        // Ignore interrupted errors caused by explicit stop()
        if (e.error !== 'interrupted') {
          setIsPlaying(false);
          setIsPaused(false);
          options?.onError?.(`Speech playback error: ${e.error}`);
        }
      };

      window.speechSynthesis.speak(utterance);
    },
    [options]
  );

  return {
    isPlaying,
    isPaused,
    isSupported,
    currentText,
    voiceNotice,
    speak,
    pause,
    resume,
    stop,
  };
}

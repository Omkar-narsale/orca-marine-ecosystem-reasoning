'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseSpeechRecognitionOptions {
  onResult?: (transcript: string) => void;
  onError?: (error: string) => void;
}

export function useSpeechRecognition(options?: UseSpeechRecognitionOptions) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      setIsSupported(Boolean(SpeechRecognition));
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        // ignore if already stopped
      }
      setIsListening(false);
    }
  }, []);

  const startListening = useCallback(
    (lang: string = 'en') => {
      setError(null);
      if (typeof window === 'undefined') return;

      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;

      if (!SpeechRecognition) {
        setError('Speech recognition is not supported in this browser.');
        options?.onError?.('Speech recognition is not supported in this browser.');
        return;
      }

      // Stop previous instance if running
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }

      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      // Match language tag
      const langMap: Record<string, string> = {
        en: 'en-IN',
        english: 'en-IN',
        hi: 'hi-IN',
        hindi: 'hi-IN',
        mr: 'mr-IN',
        marathi: 'mr-IN',
      };
      recognition.lang = langMap[lang.toLowerCase()] || 'en-IN';
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };

      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const item = event.results[i];
          if (item[0]?.transcript) {
            currentTranscript += item[0].transcript;
          }
        }
        setTranscript(currentTranscript);
        if (event.results[0]?.isFinal) {
          options?.onResult?.(currentTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        const errMsg = event.error === 'not-allowed'
          ? 'Microphone permission denied. Please allow microphone access.'
          : event.error === 'no-speech'
          ? 'No speech detected. Please speak again.'
          : `Speech recognition error: ${event.error}`;
        setError(errMsg);
        setIsListening(false);
        options?.onError?.(errMsg);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      try {
        recognition.start();
      } catch (err: any) {
        setError(err?.message || 'Could not start speech recognition.');
        setIsListening(false);
      }
    },
    [options]
  );

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  };
}

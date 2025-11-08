import { useState, useRef, useCallback } from 'react';

/**
 * Hook para gerenciar gravação de áudio
 * Fornece métodos para iniciar/parar gravação
 */
export const useAudio = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const audioUnlockedRef = useRef(false);

  const _unlockAudio = async () => {
    try {
      if (!audioContextRef.current) {
        const AC = window.AudioContext || window.webkitAudioContext;
        audioContextRef.current = new AC();
      }

      if (audioContextRef.current && !audioUnlockedRef.current) {
        // resume the context on user gesture to unlock audio on iOS
        await audioContextRef.current.resume();

        // play a tiny silent buffer to ensure the output is unlocked
        const buffer = audioContextRef.current.createBuffer(1, 1, 22050);
        const src = audioContextRef.current.createBufferSource();
        src.buffer = buffer;
        src.connect(audioContextRef.current.destination);
        src.start(0);
        audioUnlockedRef.current = true;
      }
    } catch (err) {
      // ignore errors; unlocking is best-effort
      console.warn('Audio unlock failed:', err);
    }
  };

  const startRecording = useCallback(async () => {
    try {
      // Try to unlock audio on the first user gesture
      await _unlockAudio();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw error;
    }
  }, []);

  const stopRecording = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorderRef.current || !isRecording) {
        reject(new Error('No recording in progress'));
        return;
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        audioChunksRef.current = [];

        // Stop all tracks
        mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
        // Ensure audio is unlocked (another user gesture boundary)
        _unlockAudio().catch(() => {});

        setIsRecording(false);
        resolve(audioBlob);
      };

      mediaRecorderRef.current.stop();
    });
  }, [isRecording]);

  const playAudio = useCallback((audioBlob) => {
    const url = URL.createObjectURL(audioBlob);
    const audio = new Audio(url);
    audio.play();
    return audio;
  }, []);

  return {
    isRecording,
    startRecording,
    stopRecording,
    playAudio,
  };
};

export default useAudio;

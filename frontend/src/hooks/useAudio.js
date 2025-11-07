import { useState, useRef, useCallback } from 'react';

/**
 * Hook para gerenciar gravação de áudio
 * Fornece métodos para iniciar/parar gravação
 */
export const useAudio = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    try {
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

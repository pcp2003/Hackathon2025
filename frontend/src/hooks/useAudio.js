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

  const playAudio = useCallback((input) => {
    return new Promise((resolve) => {
      let url;
      
      // Handle Blob or string URL
      if (input instanceof Blob) {
        url = URL.createObjectURL(input);
      } else if (typeof input === 'string') {
        // If it's a string, it could be a path or URL
        url = input;
      } else {
        console.error('Invalid audio input:', input);
        resolve(null);
        return;
      }

      const audio = new Audio(url);
      
      audio.onended = () => {
        if (input instanceof Blob) {
          URL.revokeObjectURL(url);
        }
        resolve(audio);
      };

      audio.onerror = (err) => {
        console.error('Audio playback error:', err);
        if (input instanceof Blob) {
          URL.revokeObjectURL(url);
        }
        resolve(null);
      };

      audio.play().catch(err => {
        console.error('Failed to play audio:', err);
        if (input instanceof Blob) {
          URL.revokeObjectURL(url);
        }
        resolve(null);
      });
    });
  }, []);

  return {
    isRecording,
    startRecording,
    stopRecording,
    playAudio,
  };
};

export default useAudio;

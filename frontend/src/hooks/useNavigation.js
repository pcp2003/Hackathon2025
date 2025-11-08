import { useState, useCallback, useRef } from 'react';
import apiClient from '../services/api';

/**
 * Hook para gerenciar lógica central de navegação
 * Orquestra: transcrição → análise de destino → cálculo de rota → áudio de instrução
 */
export const useNavigation = (currentLocation) => {
  const [destination, setDestination] = useState(null);
  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const audioRef = useRef(null);

  /**
   * Reproduz áudio e aguarda conclusão
   */
  const playAudioFile = useCallback((audioPath) => {
    return new Promise((resolve) => {
      // Converter para URL absoluta se necessário
      const audioUrl = audioPath.startsWith('http') 
        ? audioPath 
        : `${apiClient.getBaseUrl()}${audioPath}`;
      
      const audio = new Audio(audioUrl);
      // iOS-friendly attributes
      audio.playsInline = true;
      audio.preload = 'auto';
      audio.muted = false;
      audio.volume = 1.0;

      audioRef.current = audio;
      setIsPlayingAudio(true);

      audio.onended = () => {
        console.log('Audio ended');
        setIsPlayingAudio(false);
        resolve();
      };

      audio.onerror = (error) => {
        console.error('Error playing audio:', error);
        setIsPlayingAudio(false);
        resolve();
      };

      // log play promise result
      const p = audio.play();
      if (p && typeof p.then === 'function') {
        p.then(() => {
          console.log('Audio playback started');
        }).catch((err) => {
          console.error('Error starting audio (promise):', err);
          setIsPlayingAudio(false);
          resolve();
        });
      }
    });
  }, []);

  // Play an audio Blob directly
  const playAudioBlob = useCallback((audioBlob) => {
    return new Promise((resolve) => {
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      // iOS-friendly attributes
      audio.playsInline = true;
      audio.preload = 'auto';
      audio.muted = false;
      audio.volume = 1.0;

      audioRef.current = audio;
      setIsPlayingAudio(true);

      audio.onended = () => {
        console.log('Audio blob ended');
        setIsPlayingAudio(false);
        URL.revokeObjectURL(url);
        resolve();
      };

      audio.onerror = (error) => {
        console.error('Error playing audio blob:', error);
        setIsPlayingAudio(false);
        URL.revokeObjectURL(url);
        resolve();
      };

      const p = audio.play();
      if (p && typeof p.then === 'function') {
        p.then(() => {
          console.log('Audio blob playback started');
        }).catch((err) => {
          console.error('Error starting audio blob (promise):', err);
          setIsPlayingAudio(false);
          URL.revokeObjectURL(url);
          resolve();
        });
      }
    });
  }, []);

  /**
   * Gera e reproduz áudio inicial após calcular rota
   */
  const playInitialGuidance = useCallback(async (originName, destName, routeData) => {
    try {
      const response = await apiClient.generateInitialGuidance(
        originName,
        destName,
        routeData.total_distance,
        routeData.total_duration
      );
      // Response may be a Blob (binary audio) or a JSON object with audio path
      if (response instanceof Blob) {
        await playAudioBlob(response);
      } else if (response && response.audio) {
        await playAudioFile(response.audio);
      } else {
        console.error('Unexpected TTS response format', response);
      }
    } catch (err) {
      console.error('Error generating initial guidance:', err);
    }
  }, [playAudioFile, playAudioBlob]);

  /**
   * Gera e reproduz áudio para um passo específico
   */
  const playStepGuidance = useCallback(async (stepIndex, instruction) => {
    try {
      const response = await apiClient.generateStepGuidance(
        stepIndex,
        instruction,
        stepIndex + 1 // User-facing step number
      );
      if (response instanceof Blob) {
        await playAudioBlob(response);
      } else if (response && response.audio) {
        await playAudioFile(response.audio);
      } else {
        console.error('Unexpected TTS response format', response);
      }
    } catch (err) {
      console.error('Error generating step guidance:', err);
    }
  }, [playAudioFile, playAudioBlob]);

  /**
   * Transcreve áudio, análisa destino, calcula rota e reproduz instruções
   */
  const handleTranscribe = useCallback(
    async (audioBlob) => {
      setIsLoading(true);
      setError(null);

      try {
        // Transcreve áudio
        const transcribeResult = await apiClient.transcribe(audioBlob);
        console.log('Transcribed:', transcribeResult.text);

        // Análisa destino
        const destinationResult = await apiClient.analyzeDestination(
          transcribeResult.text
        );
        setDestination(destinationResult);

        // Calcula rota
        if (currentLocation) {
          const routeResult = await apiClient.getRoute(
            currentLocation.latitude,
            currentLocation.longitude,
            destinationResult.latitude,
            destinationResult.longitude
          );
          setRoute(routeResult);
          setCurrentStepIndex(0);

          // Reproduz orientação inicial com contexto da rota
          await playInitialGuidance(
            `your current location`,
            destinationResult.destination_address,
            routeResult
          );

          // Reproduz primeira instrução de passo
          if (routeResult.steps && routeResult.steps.length > 0) {
            await playStepGuidance(0, routeResult.steps[0].instruction);
          }
        }
      } catch (err) {
        const errorMessage = err.message || 'An error occurred. Please try again.';
        setError(errorMessage);
        console.error('Navigation error:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [currentLocation, playInitialGuidance, playStepGuidance]
  );

  /**
   * Avança para o próximo passo e reproduz sua instrução
   */
  const moveToNextStep = useCallback(async () => {
    if (!route || !route.steps) return;

    const nextIndex = currentStepIndex + 1;
    if (nextIndex < route.steps.length) {
      setCurrentStepIndex(nextIndex);
      await playStepGuidance(nextIndex, route.steps[nextIndex].instruction);
    } else {
      // Rota completada
      setError(null);
      console.log('Route completed!');
    }
  }, [route, currentStepIndex, playStepGuidance]);

  /**
   * Para reprodução de áudio atual
   */
  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlayingAudio(false);
    }
  }, []);

  return {
    destination,
    route,
    currentStepIndex,
    isLoading,
    isPlayingAudio,
    error,
    handleTranscribe,
    moveToNextStep,
    playStepGuidance,
    stopAudio,
  };
};

export default useNavigation;

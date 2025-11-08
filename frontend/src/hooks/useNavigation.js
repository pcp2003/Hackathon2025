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
      let audioUrl;
      if (audioPath.startsWith('http')) {
        // Already absolute URL
        audioUrl = audioPath;
      } else if (audioPath.startsWith('/audio/')) {
        // Relative path from API, construct full URL
        audioUrl = `${apiClient.getBaseUrl()}${audioPath}`;
      } else if (audioPath.startsWith('/')) {
        // Root-relative path
        audioUrl = `${apiClient.getBaseUrl()}${audioPath}`;
      } else {
        // Assume it's a relative filename
        audioUrl = `${apiClient.getBaseUrl()}/audio/${audioPath}`;
      }
      
      console.log('Playing audio from URL:', audioUrl);
      
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      setIsPlayingAudio(true);

      audio.onended = () => {
        setIsPlayingAudio(false);
        resolve();
      };

      audio.onerror = (error) => {
        console.error('Error playing audio from:', audioUrl, error);
        setIsPlayingAudio(false);
        resolve();
      };

      audio.play().catch((err) => {
        console.error('Error starting audio playback:', err);
        setIsPlayingAudio(false);
        resolve();
      });
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
      await playAudioFile(response.audio);
    } catch (err) {
      console.error('Error generating initial guidance:', err);
    }
  }, [playAudioFile]);

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
      await playAudioFile(response.audio);
    } catch (err) {
      console.error('Error generating step guidance:', err);
    }
  }, [playAudioFile]);

  /**
   * Gera e reproduz áudio de erro
   */
  const playErrorGuidance = useCallback(async (errorMessage) => {
    try {
      const response = await apiClient.generateGuidance(errorMessage);
      await playAudioFile(response.audio);
    } catch (err) {
      console.error('Error generating error guidance:', err);
    }
  }, [playAudioFile]);

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

          // Check if route calculation was successful
          if (routeResult.success === false) {
            // Route calculation failed - play error audio and reset state
            console.log('Route calculation failed:', routeResult.error_message);
            
            // Generate user-friendly error messages
            let userMessage = '';
            if (routeResult.error_message.includes('too far away')) {
              userMessage = 'I cannot calculate the route because the destination is too far away. Please try a closer destination.';
            } else if (routeResult.error_message.includes('No useful sound')) {
              userMessage = 'I did not hear anything useful. Please speak your destination again.';
            } else {
              userMessage = routeResult.error_message || 'I could not calculate the route. Please try again.';
            }
            
            // Play error message and wait for it to finish
            await playErrorGuidance(userMessage);
            
            // Then reset state so user can record again
            setDestination(null);
            setRoute(null);
            return;
          }

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
    [currentLocation, playInitialGuidance, playStepGuidance, playErrorGuidance]
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

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
      // Validate audioPath
      if (!audioPath || typeof audioPath !== 'string') {
        console.warn('Invalid audio path:', audioPath);
        resolve();
        return;
      }

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
        console.error('Error playing audio from:', audioUrl, error);
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
   * Força idioma inglês sempre, mesmo se instrução contém nomes em português
   */
  const playStepGuidance = useCallback(async (stepIndex, instruction) => {
    try {
      // Instruction format: "Turn right on Avenida Paulista"
      // We need to ensure TTS always speaks in English, even if street names are Portuguese
      // Send language: 'en' to backend to force English speech
      const response = await apiClient.generateStepGuidance(
        stepIndex,
        instruction,
        stepIndex + 1, // User-facing step number
        'en' // Force English language for TTS
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
  }, [playAudioBlob, playAudioFile]);

  /**
   * Gera e reproduz áudio de erro
   */
  const playErrorGuidance = useCallback(async (errorMessage) => {
    try {
      const response = await apiClient.generateGuidance(errorMessage);
      // Check if response has audio property before using it
      if (response && response.audio) {
        await playAudioFile(response.audio);
      } else if (response instanceof Blob) {
        // Response might be a Blob directly
        await playAudioBlob(response);
      } else {
        console.warn('No audio in error response:', response);
      }
    } catch (err) {
      console.error('Error generating error guidance:', err);
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

        // Check if transcription resulted in useful sound
        if (!transcribeResult.text || transcribeResult.text.trim() === '' || transcribeResult.error_message) {
          console.log('No useful sound recognized');
          const userMessage = 'I did not hear anything useful. Please speak your destination again.';
          await playErrorGuidance(userMessage);
          setDestination(null);
          setRoute(null);
          setIsLoading(false);
          return;
        }

        // Análisa destino
        const destinationResult = await apiClient.analyzeDestination(
          transcribeResult.text
        );
        setDestination(destinationResult);

        // Validate that destination coordinates are valid (not NaN)
        if (!destinationResult.latitude || !destinationResult.longitude || 
            isNaN(destinationResult.latitude) || isNaN(destinationResult.longitude)) {
          console.log('Invalid destination coordinates:', destinationResult);
          const userMessage = 'I did not understand that destination. Please speak a different location.';
          await playErrorGuidance(userMessage);
          setDestination(null);
          setRoute(null);
          setIsLoading(false);
          return;
        }

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
            
            // Generate user-friendly error messages based on error type or message content
            let userMessage = '';
            const errorMsg = routeResult.error_message || '';
            const errorType = routeResult.error_type || '';
            
            // Check error type first, then error message content
            if (errorType === 'distance_exceeded' || errorMsg.includes('too far away') || errorMsg.includes('kilometers away')) {
              userMessage = 'I cannot calculate the route because the destination is too far away. Please try a closer destination.';
            } else if (errorType === 'no_route_found' || errorMsg.includes('no route')) {
              userMessage = 'I could not find a route to that destination. Please try a different location.';
            } else if (errorMsg.includes('temporarily unavailable') || errorMsg.includes('service') || errorMsg.includes('error')) {
              userMessage = 'The navigation service is temporarily unavailable. Please try again in a moment.';
            } else {
              userMessage = errorMsg || 'I could not calculate the route. Please try again.';
            }
            
            // Play error message if audio is available
            if (routeResult.audio) {
              await playErrorGuidance(userMessage);
            }
            
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
    playErrorGuidance,
    playAudioFile,
    stopAudio,
  };
};

export default useNavigation;

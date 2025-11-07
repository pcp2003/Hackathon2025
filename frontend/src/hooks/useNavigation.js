import { useState, useCallback } from 'react';
import apiClient from '../services/api';

/**
 * Hook para gerenciar lógica central de navegação
 * Orquestra: transcrição → análise de destino → cálculo de rota
 */
export const useNavigation = (currentLocation) => {
  const [destination, setDestination] = useState(null);
  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTranscribe = useCallback(
    async (audioBlob) => {
      setIsLoading(true);
      setError(null);

      try {
        // Transcribe audio
        const transcribeResult = await apiClient.transcribe(audioBlob);
        console.log('Transcribed:', transcribeResult.text);

        // Analyze destination
        const destinationResult = await apiClient.analyzeDestination(
          transcribeResult.text
        );
        setDestination(destinationResult);

        // Get route
        if (currentLocation) {
          const routeResult = await apiClient.getRoute(
            currentLocation.latitude,
            currentLocation.longitude,
            destinationResult.latitude,
            destinationResult.longitude
          );
          setRoute(routeResult);

          // Generate and play guidance
          const firstInstruction = routeResult.steps[0]?.instruction;
          if (firstInstruction) {
            const audioGuidance = await apiClient.generateGuidance(firstInstruction);
            const audio = new Audio(URL.createObjectURL(audioGuidance));
            audio.play();
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
    [currentLocation]
  );

  return {
    destination,
    route,
    isLoading,
    error,
    handleTranscribe,
  };
};

export default useNavigation;

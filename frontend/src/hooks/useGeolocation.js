import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/api';

/**
 * Hook para gerenciar geolocalização do navegador
 * Fornece localização atual, monitoramento contínuo e integração com API
 */
export const useGeolocation = (destination, onStepCompleted) => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  const [watchId, setWatchId] = useState(null);
  const [isUpdatingLocation, setIsUpdatingLocation] = useState(false);

  /**
   * Notifica servidor de atualização de localização e verifica progresso na rota
   */
  const notifyLocationUpdate = useCallback(
    async (lat, lon) => {
      if (!destination || isUpdatingLocation) return;

      try {
        setIsUpdatingLocation(true);
        const response = await apiClient.updateLocation(
          lat,
          lon,
          destination.latitude,
          destination.longitude
        );

        console.log('Location updated on server:', response);

        // Se usuário saiu da rota, podemos implementar lógica de recalculamento
        if (response.needs_recalculation) {
          console.log('User is off-route. Recalculation needed.');
          // TODO: Trigger route recalculation
        }

        // Se chegou ao próximo passo, notifica o hook de navegação
        if (onStepCompleted && response.step_completed) {
          onStepCompleted();
        }
      } catch (err) {
        console.error('Error notifying location update:', err);
      } finally {
        setIsUpdatingLocation(false);
      }
    },
    [destination, isUpdatingLocation, onStepCompleted]
  );

  useEffect(() => {
    const initializeLocation = async () => {
      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
          });
        });

        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
        };

        setLocation(newLocation);

        // Notifica servidor da localização inicial
        if (destination) {
          await notifyLocationUpdate(newLocation.latitude, newLocation.longitude);
        }
      } catch (err) {
        setError('Could not get your location. Please enable location services.');
        console.error('Location error:', err);
      }
    };

    initializeLocation();

    // Watch location for changes
    const id = navigator.geolocation.watchPosition(
      (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
        };

        setLocation(newLocation);

        // Notifica servidor de cada atualização de localização
        notifyLocationUpdate(newLocation.latitude, newLocation.longitude);
      },
      (err) => {
        console.error('Watch location error:', err);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );

    setWatchId(id);

    return () => {
      if (id !== null) {
        navigator.geolocation.clearWatch(id);
      }
    };
  }, [destination, notifyLocationUpdate]);

  return { location, error, watchId };
};

export default useGeolocation;

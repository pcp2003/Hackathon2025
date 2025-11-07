import React, { useState, useEffect } from 'react';
import VoiceInput from '../components/VoiceInput';
import Map from '../components/Map';
import RouteDisplay from '../components/RouteDisplay';
import apiClient from '../services/apiClient';
import locationService from '../services/locationService';
import './App.css';

export const App = () => {
  const [currentLocation, setCurrentLocation] = useState(null);
  const [destination, setDestination] = useState(null);
  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [locationWatch, setLocationWatch] = useState(null);

  // Get initial location
  useEffect(() => {
    const initializeLocation = async () => {
      try {
        const location = await locationService.getCurrentLocation();
        setCurrentLocation(location);
      } catch (error) {
        setError('Could not get your location. Please enable location services.');
        console.error('Location error:', error);
      }
    };

    initializeLocation();

    // Watch location for changes
    const watchId = locationService.watchLocation(
      (location) => {
        setCurrentLocation(location);
      },
      (error) => {
        console.error('Watch location error:', error);
      }
    );

    setLocationWatch(watchId);

    return () => {
      if (watchId !== null) {
        locationService.clearWatch(watchId);
      }
    };
  }, []);

  const handleTranscribe = async (audioBlob) => {
    setIsLoading(true);
    setError(null);

    try {
      // Transcribe audio
      const transcribeResult = await apiClient.transcribe(audioBlob);
      console.log('Transcribed:', transcribeResult.text);

      // Analyze destination
      const destinationResult = await apiClient.analyzeDestination(transcribeResult.text);
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
      setError(err.message || 'An error occurred. Please try again.');
      console.error('Navigation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🧭 NaviAcess</h1>
        <p>Voice Navigation for Everyone</p>
      </header>

      <main className="main-content">
        {error && <div className="error-message">{error}</div>}

        <div className="container">
          <VoiceInput onTranscribe={handleTranscribe} isLoading={isLoading} />

          {currentLocation && destination && (
            <Map
              destination={destination}
              currentLocation={currentLocation}
              route={route}
            />
          )}

          {destination && (
            <div className="destination-info">
              <h2>Destination: {destination.destination}</h2>
            </div>
          )}

          <RouteDisplay route={route} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
};

export default App;

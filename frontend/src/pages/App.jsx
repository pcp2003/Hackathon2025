import React from 'react';
import VoiceInput from '../components/VoiceInput';
import Map from '../components/Map';
import RouteDisplay from '../components/RouteDisplay';
import { useGeolocation, useNavigation } from '../hooks';
import '../styles/index.css';

export const App = () => {
  const { location: currentLocation, error: locationError } = useGeolocation();
  const { destination, route, isLoading, error, handleTranscribe } = useNavigation(currentLocation);

  const displayError = error || locationError;

  return (
    <div className="app">
      <header className="header">
        <h1>🧭 NaviAcess</h1>
        <p>Voice Navigation for Everyone</p>
      </header>

      <main className="main-content">
        {displayError && <div className="alert alert-error">{displayError}</div>}

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

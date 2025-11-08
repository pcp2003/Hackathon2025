import React from 'react';
import VoiceInput from '../components/VoiceInput';
import Map from '../components/Map';
import RouteDisplay from '../components/RouteDisplay';
import { useGeolocation, useNavigation } from '../hooks';

export const App = () => {
  const { location: currentLocation, error: locationError } = useGeolocation();
  const { destination, route, isLoading, error, handleTranscribe } = useNavigation(currentLocation);

  const displayError = error || locationError;

  return (
    <div className="app">
      <header className="header">
        <h1>NaviAccess</h1>
        <p>Voice Navigation for Visually Impaired Users</p>
      </header>

      <main className="main-content">
        {displayError && <div className="alert alert-error">{displayError}</div>}

        <div className="container">
          {!destination && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '70vh',
              gap: '24px'
            }}>
              <VoiceInput onTranscribe={handleTranscribe} isLoading={isLoading} />
            </div>
          )}

          {destination && (
            <>
              {currentLocation && (
                <Map
                  destination={destination}
                  currentLocation={currentLocation}
                  route={route}
                />
              )}

              <RouteDisplay route={route} isLoading={isLoading} />
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;

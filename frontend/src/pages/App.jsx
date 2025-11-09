import React from 'react';
import VoiceInput from '../components/VoiceInput';
import Map from '../components/Map';
import RouteDisplay from '../components/RouteDisplay';
import EnableAudio from '../components/EnableAudio';
import { useGeolocation, useNavigation } from '../hooks';

export const App = () => {
  const { location: currentLocation, error: locationError } = useGeolocation();
  const { destination, route, isLoading, error, handleTranscribe, playStepGuidance, isPlayingAudio } = useNavigation(currentLocation);

  const displayError = error || locationError;

  return (
    <div className="app">
    <header className="header">
      <div className="header-content">
        <div className="header-text">
          <h1>NaviAcess</h1>
          <p className="tagline">Voice-guided navigation for the visually impaired</p>
          <p className="description">
            <strong>Demo Version:</strong> This interface demonstrates AI-powered capabilities including real-time image analysis and voice synthesis via ElevenLabs. 
            The production version for blind users would feature a drastically simplified interface with a single action button, minimal visual elements, and voice-first interaction. 
            Future iterations will incorporate video analysis and be optimized as a mobile app for seamless smartphone navigation.
          </p>
        </div>
      </div>
    </header>      <main className="main-content">
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

              <RouteDisplay route={route} isLoading={isLoading} playStepGuidance={playStepGuidance} isPlayingAudio={isPlayingAudio} />
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;

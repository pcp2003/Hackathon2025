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
          </div>
        </div>
      </header>

      <main className="main-content">
        {displayError && <div className="alert alert-error">{displayError}</div>}

        <div className="container">
          {!destination ? (
            <div className="hero-section">
              <div className="hero-content">
                <div className="hero-text">
                  <h2 className="hero-title">Your AI-Powered Navigation Assistant</h2>
                  <p className="hero-subtitle">
                    Navigate urban environments independently with real-time voice guidance
                  </p>
                  <div className="hero-features">
                    <div className="feature-badge">
                      <span>Voice Input</span>
                    </div>
                    <div className="feature-badge">
                      <span>Real-time GPS</span>
                    </div>
                    <div className="feature-badge">
                      <span>Voice Guidance</span>
                    </div>
                  </div>
                </div>

                <div className="hero-cta-section">
                  <div className="voice-input-wrapper">
                    <div className="glow-ring"></div>
                    <VoiceInput onTranscribe={handleTranscribe} isLoading={isLoading} />
                  </div>
                  <p className="hero-hint">Tap the button and tell your destination</p>
                </div>

                <div className="hero-divider"></div>

                <div className="hero-info-cards">
                  <div className="info-card">
                    <h3>Quick Navigation</h3>
                    <p>Get to your destination faster with optimized routing</p>
                  </div>
                  <div className="info-card">
                    <h3>Safe & Reliable</h3>
                    <p>Real-time recalculation keeps you on track</p>
                  </div>
                  <div className="info-card">
                    <h3>Accessible Design</h3>
                    <p>Built with accessibility and inclusivity in mind</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
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

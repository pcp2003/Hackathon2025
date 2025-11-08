import React from 'react';
import ImageAnalyzer from './ImageAnalyzer';

export const RouteDisplay = ({ route, isLoading, playStepGuidance, isPlayingAudio }) => {
  if (isLoading) {
    return <div className="route-display loading">Loading route...</div>;
  }

  if (!route || !route.steps) {
    return null;
  }

  return (
    <div className="route-display">
      <h3>Navigation Steps</h3>
      <div className="route-info">
        <p>Distance: <span>{(route.total_distance / 1000).toFixed(2)} km</span></p>
        <p>Duration: <span>{(route.total_duration / 60).toFixed(0)} min</span></p>
      </div>
      <div className="steps-list">
        {route.steps.map((step, index) => (
          <div key={index} className="step">
            <span className="step-number">{index + 1}</span>
            <div className="step-content">
              <p className="instruction">{step.instruction}</p>
              <small className="distance">
                {(step.distance).toFixed(0)}m • {(step.duration).toFixed(0)}s
              </small>
            </div>
            <div className="step-actions">
              <button
                className="play-step-button"
                onClick={() => playStepGuidance(index, step.instruction)}
                disabled={isPlayingAudio}
              >
                ▶️ Play
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Image Analysis Section */}
      <ImageAnalyzer />
    </div>
  );
};

export default RouteDisplay;

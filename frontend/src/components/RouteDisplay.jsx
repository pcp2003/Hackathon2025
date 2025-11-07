import React from 'react';
import './RouteDisplay.css';

export const RouteDisplay = ({ route, isLoading }) => {
  if (isLoading) {
    return <div className="route-display loading">Loading route...</div>;
  }

  if (!route || !route.steps) {
    return <div className="route-display empty">No route available</div>;
  }

  return (
    <div className="route-display">
      <h3>Navigation Steps</h3>
      <div className="route-info">
        <p>Distance: {(route.total_distance / 1000).toFixed(2)} km</p>
        <p>Duration: {(route.total_duration / 60).toFixed(0)} minutes</p>
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
          </div>
        ))}
      </div>
    </div>
  );
};

export default RouteDisplay;

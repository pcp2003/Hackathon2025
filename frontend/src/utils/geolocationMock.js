/**
 * Geolocation Mock Helper
 * 
 * Use this to simulate user movement in development/testing
 * Especially useful for testing the audio guidance flow
 */

/**
 * Set up mock geolocation in the browser console
 * Simulates a journey from Lisbon to Carcavelos
 */
export function setupGeolocationMock() {
  // Real coordinates for testing
  const LISBON_START = { lat: 38.7307129, lon: -9.1299245 };
  const CARCAVELOS_END = { lat: 38.6792232, lon: -9.3352361 };

  // Journey waypoints (simulating 6 steps)
  const waypoints = [
    { lat: 38.7307129, lon: -9.1299245, instruction: 'Starting point' },
    { lat: 38.7300000, lon: -9.1300000, instruction: 'Walking north' },
    { lat: 38.7290000, lon: -9.1310000, instruction: 'Turning left' },
    { lat: 38.7200000, lon: -9.1400000, instruction: 'Crossing street' },
    { lat: 38.7000000, lon: -9.2000000, instruction: 'Halfway point' },
    { lat: 38.6792232, lon: -9.3352361, instruction: 'Destination reached' },
  ];

  let currentWaypoint = 0;
  let isSimulating = false;

  /**
   * Get next waypoint in the journey
   */
  function getNextWaypoint() {
    if (currentWaypoint < waypoints.length) {
      return waypoints[currentWaypoint++];
    }
    return null;
  }

  /**
   * Start simulating movement
   * @param {number} intervalMs - Time between position updates (default: 5000ms)
   */
  window.startGeolocationSimulation = function(intervalMs = 5000) {
    if (isSimulating) {
      console.log('❌ Simulation already running');
      return;
    }

    isSimulating = true;
    currentWaypoint = 0;
    let stepCount = 0;

    console.log('🗺️ Starting geolocation simulation...');
    console.log(`📍 Journey: Lisbon → Carcavelos (${waypoints.length} steps)`);
    console.log(`⏱️ Update interval: ${intervalMs}ms\n`);

    const interval = setInterval(() => {
      const waypoint = getNextWaypoint();

      if (waypoint) {
        stepCount++;
        console.log(
          `📍 Step ${stepCount}/${waypoints.length}: ${waypoint.lat.toFixed(4)}, ${waypoint.lon.toFixed(4)}`
        );
        console.log(`   📢 "${waypoint.instruction}"\n`);

        // Dispatch custom event that your app can listen to
        window.dispatchEvent(
          new CustomEvent('geolocationSimulated', {
            detail: {
              latitude: waypoint.lat,
              longitude: waypoint.lon,
              accuracy: 10,
              timestamp: new Date().toISOString(),
            },
          })
        );
      } else {
        clearInterval(interval);
        isSimulating = false;
        console.log('✅ Geolocation simulation complete!');
      }
    }, intervalMs);

    window.geolocationSimulationInterval = interval;
  };

  /**
   * Stop current simulation
   */
  window.stopGeolocationSimulation = function() {
    if (window.geolocationSimulationInterval) {
      clearInterval(window.geolocationSimulationInterval);
      isSimulating = false;
      console.log('⏹️ Geolocation simulation stopped');
    }
  };

  /**
   * Reset to start
   */
  window.resetGeolocationSimulation = function() {
    window.stopGeolocationSimulation();
    currentWaypoint = 0;
    console.log('🔄 Geolocation simulation reset');
  };

  /**
   * Jump to specific step
   */
  window.jumpToStep = function(stepNumber) {
    if (stepNumber > 0 && stepNumber <= waypoints.length) {
      currentWaypoint = stepNumber - 1;
      const waypoint = waypoints[currentWaypoint];
      console.log(`⏩ Jumped to step ${stepNumber}: ${waypoint.lat}, ${waypoint.lon}`);
    } else {
      console.log(`❌ Invalid step number. Choose 1-${waypoints.length}`);
    }
  };

  /**
   * Get current status
   */
  window.getSimulationStatus = function() {
    return {
      isRunning: isSimulating,
      currentStep: currentWaypoint + 1,
      totalSteps: waypoints.length,
      progress: `${currentWaypoint}/${waypoints.length}`,
    };
  };

  console.log('✅ Geolocation mock helper loaded!');
  console.log('\nAvailable commands:');
  console.log('  startGeolocationSimulation(ms)  - Start simulating movement');
  console.log('  stopGeolocationSimulation()     - Stop simulation');
  console.log('  resetGeolocationSimulation()    - Reset to start');
  console.log('  jumpToStep(n)                   - Jump to specific step');
  console.log('  getSimulationStatus()           - Check current status');
}

/**
 * Alternative: Mock navigator.geolocation directly
 * Use this if you want to intercept actual geolocation calls
 */
export function mockNavigatorGeolocation() {
  const originalGeolocation = navigator.geolocation;

  let watchCallbacks = [];
  let currentPosition = {
    coords: {
      latitude: 38.7307129,
      longitude: -9.1299245,
      accuracy: 10,
    },
  };

  const mockGeolocation = {
    getCurrentPosition(success, error, options) {
      console.log('📍 getCurrentPosition called');
      setTimeout(() => {
        success(currentPosition);
      }, 100);
    },

    watchPosition(success, error, options) {
      console.log('👁️ watchPosition started');
      const watchId = Math.random();
      watchCallbacks.push({ id: watchId, callback: success });
      return watchId;
    },

    clearWatch(watchId) {
      console.log(`🛑 watchPosition ${watchId} cleared`);
      watchCallbacks = watchCallbacks.filter((w) => w.id !== watchId);
    },
  };

  Object.defineProperty(navigator, 'geolocation', {
    writable: true,
    value: mockGeolocation,
  });

  /**
   * Update position and notify all watchers
   */
  window.updateMockPosition = function(latitude, longitude, accuracy = 10) {
    currentPosition = {
      coords: { latitude, longitude, accuracy },
      timestamp: Date.now(),
    };

    watchCallbacks.forEach((w) => {
      w.callback(currentPosition);
    });

    console.log(`📍 Position updated: ${latitude}, ${longitude}`);
  };

  console.log('✅ navigator.geolocation mocked!');
  console.log('\nUse: updateMockPosition(lat, lon, accuracy)');
}

/**
 * Create a realistic journey path from start to end
 * Useful for smooth simulation instead of discrete steps
 */
export function createJourneyPath(startLat, startLon, endLat, endLon, stepCount = 10) {
  const path = [];
  const latStep = (endLat - startLat) / stepCount;
  const lonStep = (endLon - startLon) / stepCount;

  for (let i = 0; i <= stepCount; i++) {
    path.push({
      latitude: startLat + latStep * i,
      longitude: startLon + lonStep * i,
      accuracy: 10,
    });
  }

  return path;
}

/**
 * Simulate smooth movement along a path
 */
export function simulateJourneyPath(path, intervalMs = 1000) {
  let currentIndex = 0;
  const interval = setInterval(() => {
    if (currentIndex < path.length) {
      const position = path[currentIndex];
      console.log(`📍 ${currentIndex}/${path.length}: ${position.latitude.toFixed(4)}, ${position.longitude.toFixed(4)}`);

      if (window.updateMockPosition) {
        window.updateMockPosition(
          position.latitude,
          position.longitude,
          position.accuracy
        );
      }

      currentIndex++;
    } else {
      clearInterval(interval);
      console.log('✅ Journey simulation complete!');
    }
  }, intervalMs);

  return () => clearInterval(interval);
}

export default {
  setupGeolocationMock,
  mockNavigatorGeolocation,
  createJourneyPath,
  simulateJourneyPath,
};

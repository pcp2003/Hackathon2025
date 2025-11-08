/**
 * Application configuration constants
 */

export const API_CONFIG = {
  // Use relative paths by default so frontend (served over HTTPS) calls the same origin
  // and Nginx can proxy /api to the backend. Override with VITE_API_URL if needed.
  BASE_URL: import.meta.env.VITE_API_URL || '',
  ENDPOINTS: {
    TRANSCRIBE: '/api/transcribe',
    ANALYZE: '/api/analyze',
    ROUTE: '/api/route',
    SPEAK: '/api/speak',
    SPEAK_INITIAL: '/api/speak-initial',
    SPEAK_STEP: '/api/speak-step',
    UPDATE_LOCATION: '/api/update-location',
    ANALYZE_IMAGE: '/api/analyze-image',
  },
  TIMEOUT: 30000, // 30 seconds
};

/**
 * Geolocation settings
 */
export const GEOLOCATION_CONFIG = {
  enableHighAccuracy: true,
  timeout: 10000, // 10 seconds
  maximumAge: 0,
};

/**
 * Audio recording settings
 */
export const AUDIO_CONFIG = {
  mimeType: 'audio/wav',
  sampleRate: 16000,
};

/**
 * Map settings
 */
export const MAP_CONFIG = {
  DEFAULT_CENTER: [40.7128, -74.0060], // New York
  DEFAULT_ZOOM: 13,
  TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  TILE_ATTRIBUTION: '© OpenStreetMap contributors',
  MAX_ZOOM: 19,
};

/**
 * UI Settings
 */
export const UI_CONFIG = {
  ANIMATION_DURATION: 300, // ms
};

export default {
  API_CONFIG,
  GEOLOCATION_CONFIG,
  AUDIO_CONFIG,
  MAP_CONFIG,
  UI_CONFIG,
};

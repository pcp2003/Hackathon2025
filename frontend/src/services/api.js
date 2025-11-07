import { API_CONFIG } from '../utils/constants';

/**
 * API Client for backend communication
 * Handles all HTTP requests to the backend
 */
const apiClient = {
  async request(endpoint, formData) {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      // Check if response is JSON or Blob (for audio)
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }

      return await response.blob();
    } catch (error) {
      console.error(`Request failed for ${endpoint}:`, error);
      throw error;
    }
  },

  async transcribe(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    return this.request(API_CONFIG.ENDPOINTS.TRANSCRIBE, formData);
  },

  async analyzeDestination(text) {
    const formData = new FormData();
    formData.append('text', text);

    return this.request(API_CONFIG.ENDPOINTS.ANALYZE, formData);
  },

  async getRoute(originLat, originLon, destLat, destLon) {
    const formData = new FormData();
    formData.append('origin_lat', originLat);
    formData.append('origin_lon', originLon);
    formData.append('dest_lat', destLat);
    formData.append('dest_lon', destLon);

    return this.request(API_CONFIG.ENDPOINTS.ROUTE, formData);
  },

  async generateGuidance(text) {
    const formData = new FormData();
    formData.append('text', text);

    return this.request(API_CONFIG.ENDPOINTS.SPEAK, formData);
  },

  async updateLocation(lat, lon, destLat, destLon) {
    const formData = new FormData();
    formData.append('latitude', lat);
    formData.append('longitude', lon);
    formData.append('destination_lat', destLat);
    formData.append('destination_lon', destLon);

    return this.request(API_CONFIG.ENDPOINTS.UPDATE_LOCATION, formData);
  },
};

export default apiClient;

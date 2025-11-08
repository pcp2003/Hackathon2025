import { API_CONFIG } from '../utils/constants';

/**
 * API Client for backend communication
 * Handles all HTTP requests to the backend
 */
const apiClient = {
  getBaseUrl() {
    return API_CONFIG.BASE_URL;
  },

  async request(endpoint, formData) {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
        // CORS headers - allow credentials and specify content type
        headers: {
          'Accept': '*/*',
        },
        credentials: 'include', // Include credentials if needed
        mode: 'cors', // Explicitly enable CORS
      });

      // Handle 422 Unprocessable Entity (no useful sound recognized) silently
      if (response.status === 422) {
        console.log(`Silent error for ${endpoint}: 422 - No useful sound recognized`);
        return { success: false, error_message: 'No useful sound recognized' };
      }

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

  async generateInitialGuidance(originName, destName, totalDistance, totalDuration) {
    const formData = new FormData();
    formData.append('origin_name', originName);
    formData.append('destination_name', destName);
    formData.append('total_distance', totalDistance);
    formData.append('total_duration', totalDuration);

    return this.request(API_CONFIG.ENDPOINTS.SPEAK_INITIAL, formData);
  },

  async generateStepGuidance(stepIndex, instruction, stepNumber) {
    const formData = new FormData();
    formData.append('step_index', stepIndex);
    formData.append('instruction', instruction);
    formData.append('step_number', stepNumber);

    return this.request(API_CONFIG.ENDPOINTS.SPEAK_STEP, formData);
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

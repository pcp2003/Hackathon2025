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

      // Check if response is JSON or Blob (for audio)
      const contentType = response.headers.get('content-type');
      
      if (!response.ok) {
        // Try to parse error response as JSON first
        if (contentType?.includes('application/json')) {
          try {
            const errorData = await response.json();
            console.error(`API Error for ${endpoint}: ${response.status}`, errorData);
            throw new Error(errorData.error_message || errorData.detail || response.statusText);
          } catch (e) {
            // Not JSON, handle as generic error
            console.error(`API Error for ${endpoint}: ${response.status} ${response.statusText}`);
            throw new Error(`API Error: ${response.statusText}`);
          }
        } else {
          // Handle 422 Unprocessable Entity (no useful sound recognized) silently
          if (response.status === 422) {
            console.log(`Silent error for ${endpoint}: 422 - No useful sound recognized`);
            return { success: false, error_message: 'No useful sound recognized' };
          }
          throw new Error(`API Error: ${response.statusText}`);
        }
      }

      // Successful response - check content type
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
    formData.append('origin_lat', String(parseFloat(originLat)));
    formData.append('origin_lon', String(parseFloat(originLon)));
    formData.append('dest_lat', String(parseFloat(destLat)));
    formData.append('dest_lon', String(parseFloat(destLon)));

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
    formData.append('total_distance', String(parseFloat(totalDistance)));
    formData.append('total_duration', String(parseFloat(totalDuration)));

    return this.request(API_CONFIG.ENDPOINTS.SPEAK_INITIAL, formData);
  },

  async generateStepGuidance(stepIndex, instruction, stepNumber, language = 'en') {
    const formData = new FormData();
    formData.append('step_index', String(parseInt(stepIndex)));
    formData.append('instruction', instruction);
    formData.append('step_number', String(parseInt(stepNumber)));
    formData.append('language', language);  // Force language for TTS

    return this.request(API_CONFIG.ENDPOINTS.SPEAK_STEP, formData);
  },

  async updateLocation(lat, lon, destLat, destLon) {
    const formData = new FormData();
    formData.append('latitude', String(parseFloat(lat)));
    formData.append('longitude', String(parseFloat(lon)));
    formData.append('destination_lat', String(parseFloat(destLat)));
    formData.append('destination_lon', String(parseFloat(destLon)));

    return this.request(API_CONFIG.ENDPOINTS.UPDATE_LOCATION, formData);
  },

  async analyzeImage(formData) {
    return this.request(API_CONFIG.ENDPOINTS.ANALYZE_IMAGE, formData);
  },
};

export default apiClient;

// Export individual functions for easier imports
export const analyzeImage = (formData) => apiClient.analyzeImage(formData);
export const transcribe = (audioBlob) => apiClient.transcribe(audioBlob);
export const analyzeDestination = (text) => apiClient.analyzeDestination(text);
export const getRoute = (originLat, originLon, destLat, destLon) => apiClient.getRoute(originLat, originLon, destLat, destLon);
export const generateGuidance = (text) => apiClient.generateGuidance(text);
export const generateInitialGuidance = (originName, destName, totalDistance, totalDuration) => apiClient.generateInitialGuidance(originName, destName, totalDistance, totalDuration);
export const generateStepGuidance = (stepIndex, instruction, stepNumber, language = 'en') => apiClient.generateStepGuidance(stepIndex, instruction, stepNumber, language);
export const updateLocation = (lat, lon, destLat, destLon) => apiClient.updateLocation(lat, lon, destLat, destLon);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = {
  async transcribe(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    
    const response = await fetch(`${API_URL}/api/transcribe`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Transcription failed');
    return response.json();
  },

  async analyzeDestination(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
  },

  async getRoute(originLat, originLon, destLat, destLon) {
    const formData = new FormData();
    formData.append('origin_lat', originLat);
    formData.append('origin_lon', originLon);
    formData.append('dest_lat', destLat);
    formData.append('dest_lon', destLon);
    
    const response = await fetch(`${API_URL}/api/route`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Route calculation failed');
    return response.json();
  },

  async generateGuidance(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await fetch(`${API_URL}/api/speak`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Guidance generation failed');
    return response.blob();
  },

  async updateLocation(lat, lon, destLat, destLon) {
    const formData = new FormData();
    formData.append('latitude', lat);
    formData.append('longitude', lon);
    formData.append('destination_lat', destLat);
    formData.append('destination_lon', destLon);
    
    const response = await fetch(`${API_URL}/api/update-location`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Location update failed');
    return response.json();
  },
};

export default apiClient;

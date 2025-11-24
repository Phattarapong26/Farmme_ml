// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Provinces
  provinces: `${API_BASE_URL}/api/v2/forecast/provinces`,
  provinceDetail: (provinceId: string) => `${API_BASE_URL}/api/v2/forecast/provinces/${provinceId}`,
  
  // Chat
  chat: `${API_BASE_URL}/api/chat`,
  
  // Forecast
  forecast: `${API_BASE_URL}/api/v2/forecast`,
  
  // Model
  model: `${API_BASE_URL}/api/model`,
  
  // Planting
  planting: `${API_BASE_URL}/api/planting`,
  
  // Health check
  health: `${API_BASE_URL}/health`,
};

import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useCropData = (province?: string) => {
  return useQuery({
    queryKey: ['cropData', province],
    queryFn: async () => {
      if (!province) return [];

      // Use real province prices endpoint
      const url = `${API_BASE_URL}/provinces/${encodeURIComponent(province)}/prices`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch crop data');

      const result = await response.json();

      // Return real crop price data from database
      return result.prices || [];
    },
    enabled: !!province,
    staleTime: 2 * 60 * 1000, // Cache for 2 minutes
  });
};

export const useCropCharacteristics = () => {
  return useQuery({
    queryKey: ['cropCharacteristics'],
    queryFn: async () => {
      // Fetch from real backend API
      const response = await fetch(`${API_BASE_URL}/api/v2/forecast/crops`);
      if (!response.ok) throw new Error('Failed to fetch crop characteristics');
      const data = await response.json();
      return data.crops || [];
    },
  });
};

export const useCropCultivation = (province?: string) => {
  return useQuery({
    queryKey: ['cropCultivation', province],
    queryFn: async () => {
      if (!province) return [];
      // Fetch from real backend API - crop cultivation data
      const response = await fetch(`${API_BASE_URL}/api/v2/forecast/crops?province=${encodeURIComponent(province)}`);
      if (!response.ok) return [];
      const data = await response.json();
      return data.crops || [];
    },
    enabled: !!province,
  });
};

export const useEconomicFactors = () => {
  return useQuery({
    queryKey: ['economicFactors'],
    queryFn: async () => {
      // Economic factors are not yet implemented in backend
      // Return empty array until backend endpoint is ready
      return [];
    },
    staleTime: 60 * 60 * 1000, // Cache for 1 hour
  });
};

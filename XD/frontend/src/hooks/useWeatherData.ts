import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useWeatherData = (province?: string) => {
  return useQuery({
    queryKey: ['weatherData', province],
    queryFn: async () => {
      if (!province) return [];
      // Fetch weather data from price-history endpoint (includes temperature and rainfall)
      const response = await fetch(`${API_BASE_URL}/api/v2/forecast/price-history?province=${encodeURIComponent(province)}&days=90`);
      if (!response.ok) return [];
      const data = await response.json();
      // Extract weather data from history
      return data.history?.map((item: any) => ({
        date: item.date,
        temperature: item.temperature,
        rainfall: item.rainfall
      })).filter((item: any) => item.temperature !== null || item.rainfall !== null) || [];
    },
    enabled: !!province,
    staleTime: 30 * 60 * 1000, // Cache for 30 minutes
  });
};

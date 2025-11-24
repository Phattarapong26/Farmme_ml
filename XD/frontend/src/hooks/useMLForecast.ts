import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

export const useMLForecast = (province?: string, cropType?: string) => {
  return useQuery({
    queryKey: ['mlForecast', province, cropType],
    queryFn: async () => {
      if (!province || !cropType) return null;

      // Use local backend forecast endpoint
      const response = await fetch(`${API_BASE_URL}/forecast/6months`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crop_id: 1, // Default crop ID
          price_history: [100, 105, 103, 108, 110],
          weather: [50, 25],
          crop_info: [3, 60, 2],
          calendar: [0, 1, 2]
        })
      });

      if (!response.ok) throw new Error('Failed to fetch forecast');
      return response.json();
    },
    enabled: !!province && !!cropType,
  });
};

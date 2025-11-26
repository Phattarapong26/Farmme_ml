import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface RecommendationParams {
  province?: string;
  waterAvailability?: string;
  budgetLevel?: string;
  experienceLevel?: string;
  riskTolerance?: string;
  timeConstraint?: number;
  cropPreference?: string;
}

export const useMLRecommendations = (params: RecommendationParams) => {
  return useQuery({
    queryKey: ['mlRecommendations', params],
    queryFn: async () => {
      // Use local backend recommend endpoint
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_history: [100, 105, 103, 108, 110],
          weather: [50, 25],
          crop_info: [3, 60, 2],
          calendar: [0, 1, 2]
        })
      });

      if (!response.ok) throw new Error('Failed to fetch recommendations');
      return response.json();
    },
    enabled: !!params.province,
  });
};

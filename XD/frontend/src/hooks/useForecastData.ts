import { useQuery } from '@tanstack/react-query';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v2/forecast';

interface ForecastProvincesResponse {
  success: boolean;
  provinces: string[];
  total: number;
}

interface CropInfo {
  crop_type: string;
  crop_category: string;
  growth_days: number;
}

interface ForecastCropsResponse {
  success: boolean;
  crops: CropInfo[];
  total: number;
}

interface PriceHistoryItem {
  date: string;
  price: number;
  temperature: number | null;  // From weather_data table by province
  rainfall: number | null;      // From weather_data table by province
}

interface PriceHistoryResponse {
  success: boolean;
  province: string;
  crop_type: string;
  history: PriceHistoryItem[];
  statistics: {
    avg_price: number;
    min_price: number;
    max_price: number;
    latest_price: number;
  };
}

// Get all provinces
export const useForecastProvinces = () => {
  return useQuery<ForecastProvincesResponse>({
    queryKey: ['forecast-provinces'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/provinces`);
      if (!response.ok) throw new Error('Failed to fetch provinces');
      return response.json();
    },
    staleTime: 1000 * 60 * 60, // Cache 1 hour
  });
};

// Get crops (optionally filtered by province)
export const useForecastCrops = (province?: string) => {
  return useQuery<ForecastCropsResponse>({
    queryKey: ['forecast-crops', province],
    queryFn: async () => {
      const url = province
        ? `${API_BASE}/crops?province=${encodeURIComponent(province)}`
        : `${API_BASE}/crops`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch crops');
      return response.json();
    },
    enabled: true,
    staleTime: 1000 * 60 * 30, // Cache 30 minutes
  });
};

// Get price history (or weather data if cropType is empty)
export const usePriceHistory = (
  province: string | undefined,
  cropType: string | undefined,
  days: number = 30
) => {
  return useQuery<PriceHistoryResponse>({
    queryKey: ['price-history', province, cropType, days],
    queryFn: async () => {
      if (!province) {
        throw new Error('Province is required');
      }

      const params = new URLSearchParams({
        province,
        crop_type: cropType || '', // Allow empty crop_type for weather data
        days: days.toString()
      });

      const response = await fetch(`${API_BASE}/price-history?${params}`);
      if (!response.ok) throw new Error('Failed to fetch price history');
      return response.json();
    },
    enabled: !!province, // Only require province, crop_type is optional
    staleTime: 1000 * 60 * 5, // Cache 5 minutes
  });
};

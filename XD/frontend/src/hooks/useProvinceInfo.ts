import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Type definitions matching backend response
export interface WeatherInfo {
  temperature_celsius: number | null;
  rainfall_mm: number | null;
  humidity_percent: number | null;
  date: string | null;
  data_age_days: number | null;
}

export interface CropCultivationInfo {
  crop_type: string;
  crop_category: string;
  planting_area_rai: number;
  average_yield_kg: number;
  success_rate: number;
  last_harvest_date: string | null;
}

export interface CultivationData {
  crops: CropCultivationInfo[];
  total_crops: number;
}

export interface CropPriceInfo {
  crop_type: string;
  price_per_kg: number;
  date: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  change_percent: number;
}

export interface PriceData {
  crops: CropPriceInfo[];
  total_crops: number;
}

export interface EconomicTimelinePoint {
  fertilizer_price: number | null;
  fuel_price: number | null;
  date: string | null;
}

export interface EconomicData {
  fertilizer_price: number | null;  // Latest value
  fuel_price: number | null;        // Latest value
  date: string | null;
  timeline: EconomicTimelinePoint[]; // Full timeline
  total_data_points: number;
}

export interface ProvinceComprehensiveData {
  weather: WeatherInfo;
  cultivation: CultivationData;
  prices: PriceData;
  economic: EconomicData;
}

export interface ProvinceInfo {
  success: boolean;
  province: string;
  data: ProvinceComprehensiveData;
  timestamp: string;
}

/**
 * Hook to fetch comprehensive province information
 * Includes weather, cultivation, prices, and economic data
 * 
 * @param provinceName - Thai province name (e.g., "เชียงใหม่")
 * @returns React Query result with province data
 */
export function useProvinceInfo(provinceName: string | null) {
  return useQuery<ProvinceInfo>({
    queryKey: ['province-info', provinceName],
    queryFn: async () => {
      if (!provinceName) {
        throw new Error('Province name is required');
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v2/provinces/${encodeURIComponent(provinceName)}/comprehensive`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Province "${provinceName}" not found`);
        }
        throw new Error(`Failed to fetch province info: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    },
    enabled: !!provinceName, // Only run query if provinceName is provided
    staleTime: 5 * 60 * 1000, // 5 minutes - data is considered fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache for 10 minutes
    retry: 2, // Retry failed requests up to 2 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
  });
}

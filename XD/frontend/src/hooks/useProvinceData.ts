import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

export interface ProvinceData {
  id?: string;
  name: string;
  supply: number;
  demand: number;
  price: number;
  dominant_crop: string;
  description: string;
  planting_area?: number;
  production_volume?: number;
  farmer_count?: number;
}

export interface CropPriceData {
  id: number;
  province: string;
  crop_type: string;
  price_per_kg: number;
  date: string;
  source?: string;
}

// Fetch all provinces
export const useAllProvinces = () => {
  return useQuery({
    queryKey: ['provinces'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/provinces`);
      if (!response.ok) {
        throw new Error('Failed to fetch provinces');
      }
      const data = await response.json();
      return data.provinces as ProvinceData[];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Fetch specific province by name
export const useProvinceByName = (provinceName: string | null) => {
  return useQuery({
    queryKey: ['province', provinceName],
    queryFn: async () => {
      if (!provinceName) return null;
      const response = await fetch(`${API_BASE_URL}/provinces/${encodeURIComponent(provinceName)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch province: ${provinceName}`);
      }
      const data = await response.json();
      return data.province as ProvinceData;
    },
    enabled: !!provinceName,
    staleTime: 5 * 60 * 1000,
  });
};

// Fetch crop prices for a province
export const useProvincePrices = (provinceName: string | null, cropType?: string) => {
  return useQuery({
    queryKey: ['province-prices', provinceName, cropType],
    queryFn: async () => {
      if (!provinceName) return [];
      const url = new URL(`${API_BASE_URL}/provinces/${encodeURIComponent(provinceName)}/prices`);
      if (cropType) {
        url.searchParams.append('crop_type', cropType);
      }
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`Failed to fetch prices for: ${provinceName}`);
      }
      const data = await response.json();
      return data.prices as CropPriceData[];
    },
    enabled: !!provinceName,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

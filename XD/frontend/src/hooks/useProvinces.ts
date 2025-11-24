import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';
const CACHE_KEY = 'farmme_provinces_cache';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

interface ProvincesData {
  success: boolean;
  provinces: string[];
  regions: Record<string, string[]>;
  total: number;
  cached?: boolean;
}

interface CachedData {
  data: ProvincesData;
  timestamp: number;
}

export const useProvinces = () => {
  const [provinces, setProvinces] = useState<string[]>([]);
  const [regions, setRegions] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProvinces = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check localStorage cache first
      const cachedString = localStorage.getItem(CACHE_KEY);
      if (cachedString) {
        try {
          const cached: CachedData = JSON.parse(cachedString);
          const now = Date.now();
          
          // Check if cache is still valid
          if (now - cached.timestamp < CACHE_TTL) {
            console.log('✅ Using cached provinces data');
            setProvinces(cached.data.provinces);
            setRegions(cached.data.regions);
            setLoading(false);
            return;
          } else {
            console.log('⏰ Cache expired, fetching fresh data');
            localStorage.removeItem(CACHE_KEY);
          }
        } catch (e) {
          console.error('Failed to parse cached data:', e);
          localStorage.removeItem(CACHE_KEY);
        }
      }

      // Fetch from API
      const response = await fetch(`${API_BASE_URL}/auth/provinces`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ProvincesData = await response.json();

      if (data.success && data.provinces && data.provinces.length > 0) {
        setProvinces(data.provinces);
        setRegions(data.regions || {});

        // Cache the data
        const cacheData: CachedData = {
          data: {
            success: true,
            provinces: data.provinces,
            regions: data.regions || {},
            total: data.total
          },
          timestamp: Date.now()
        };
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
        
        console.log(`✅ Fetched ${data.total} provinces from API`);
      } else {
        throw new Error('Invalid response format');
      }

      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching provinces:', err);
      setError(err.message || 'ไม่สามารถโหลดข้อมูลจังหวัดได้');
      
      // Use fallback provinces
      const fallbackProvinces = [
        'กรุงเทพมหานคร',
        'เชียงใหม่',
        'เชียงราย',
        'นครราชสีมา',
        'ขอนแก่น',
        'อุบลราชธานี',
        'สงขลา',
        'ภูเก็ต'
      ];
      
      setProvinces(fallbackProvinces);
      setRegions({ 'fallback': fallbackProvinces });
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProvinces();
  }, []);

  return {
    provinces,
    regions,
    loading,
    error,
    refetch: fetchProvinces
  };
};

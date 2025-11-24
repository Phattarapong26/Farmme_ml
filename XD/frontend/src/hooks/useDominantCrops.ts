import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface DominantCropInfo {
  crop_type: string;
  crop_category: string;
  total_area_rai: number;
}

interface DominantCropsResponse {
  success: boolean;
  provinces: Record<string, DominantCropInfo>;
  total: number;
}

/**
 * Hook to fetch dominant crops for all provinces from database
 * Returns mapping of province name -> dominant crop info
 */
export function useDominantCrops() {
  return useQuery<DominantCropsResponse>({
    queryKey: ['dominant-crops'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v2/map/dominant-crops`);
      if (!response.ok) {
        throw new Error('Failed to fetch dominant crops');
      }
      return response.json();
    },
    staleTime: 1000 * 60 * 30, // Cache for 30 minutes
    gcTime: 1000 * 60 * 60, // Keep in cache for 1 hour
  });
}

/**
 * Map crop type to crop key for coloring
 * Maps all 32+ crops in database to main agricultural categories
 */
export function mapCropTypeToKey(cropType: string, cropCategory: string): 'rice' | 'sugarcane' | 'cassava' | 'rubber' | 'corn' | 'mixed' {
  const lowerType = cropType?.toLowerCase() || '';
  const lowerCategory = cropCategory?.toLowerCase() || '';
  
  // Main field crops (พืชไร่หลัก)
  if (lowerType.includes('ข้าว') && !lowerType.includes('ข้าวโพด')) return 'rice';
  if (lowerType.includes('rice') && !lowerType.includes('corn')) return 'rice';
  if (lowerType.includes('อ้อย') || lowerType.includes('sugarcane')) return 'sugarcane';
  if (lowerType.includes('มันสำปะหลัง') || lowerType.includes('cassava')) return 'cassava';
  if (lowerType.includes('ยางพารา') || lowerType.includes('rubber')) return 'rubber';
  if (lowerType.includes('ข้าวโพด') || lowerType.includes('corn')) return 'corn';
  
  // Vegetables (ผัก) - map to mixed for display
  // Leafy vegetables (ผักใบ): คะน้า, กวางตุ้ง, ผักบุ้ง, ผักสลัด, ใบเหลียง
  if (lowerType.includes('คะน้า') || lowerType.includes('กวางตุ้ง') || 
      lowerType.includes('กะหล่ำ') || lowerType.includes('ผักบุ้ง') || 
      lowerType.includes('ผักสลัด') || lowerType.includes('ใบเหลียง') ||
      lowerType.includes('ขึ้นฉ่าย') || lowerType.includes('ผักหวานป่า')) {
    return 'mixed';
  }
  
  // Fruit vegetables (ผักผล): มะเขือ, พริก, ถั่ว, บวบ
  if (lowerType.includes('มะเขือ') || lowerType.includes('eggplant') ||
      lowerType.includes('พริก') || lowerType.includes('chili') ||
      lowerType.includes('ถั่ว') || lowerType.includes('bean') ||
      lowerType.includes('บวบ') || lowerType.includes('luffa') ||
      lowerType.includes('กระเจี๊ยบ') || lowerType.includes('okra')) {
    return 'mixed';
  }
  
  // Root vegetables (ผักราก): แครอท, หัวไชเท้า
  if (lowerType.includes('แครอท') || lowerType.includes('carrot') ||
      lowerType.includes('หัวไชเท้า') || lowerType.includes('radish')) {
    return 'mixed';
  }
  
  // Herbs (สมุนไพร): กระเทียม, หอมแดง, กระชาย, ขมิ้น, ข่า
  if (lowerType.includes('กระเทียม') || lowerType.includes('garlic') ||
      lowerType.includes('หอมแดง') || lowerType.includes('shallot') ||
      lowerType.includes('กระชาย') || lowerType.includes('ขมิ้น') ||
      lowerType.includes('ข่า') || lowerType.includes('มะกรูด')) {
    return 'mixed';
  }
  
  // Fruits (ผลไม้): ลำไย, สับปะรด
  if (lowerType.includes('ลำไย') || lowerType.includes('longan') ||
      lowerType.includes('สับปะรด') || lowerType.includes('pineapple')) {
    return 'mixed';
  }
  
  // Map based on category
  if (lowerCategory.includes('ข้าว')) return 'rice';
  if (lowerCategory.includes('อ้อย')) return 'sugarcane';
  if (lowerCategory.includes('มันสำปะหลัง')) return 'cassava';
  if (lowerCategory.includes('ยาง')) return 'rubber';
  if (lowerCategory.includes('ข้าวโพด')) return 'corn';
  if (lowerCategory.includes('พืชไร่')) return 'cassava';
  
  // Vegetables, herbs, and other crops default to mixed
  if (lowerCategory.includes('ผักใบ') || lowerCategory.includes('ผักผล') ||
      lowerCategory.includes('สมุนไพร') || lowerCategory.includes('ผลไม้')) {
    return 'mixed';
  }
  
  // Default to mixed
  return 'mixed';
}

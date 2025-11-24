import { useMutation, useQuery } from '@tanstack/react-query';

const API_BASE_URL = 'http://localhost:8000';

// ==================== Types ====================

interface PlantingScheduleRequest {
  province: string;
  crop_type: string;
  growth_days?: number;
  planting_area_rai?: number;
  start_date?: string;
  end_date?: string;
  top_n?: number;
  min_price_threshold?: number;
}

interface PlantingRecommendation {
  planting_date: string;
  harvest_date: string;
  predicted_price: number;
  predicted_rainfall: number;
  confidence: number;
  risk_score: number;
  recommendation: string;
  planting_area_rai?: number;
  expected_yield_kg?: number;
  expected_revenue?: number;
}

interface PlantingScheduleResponse {
  success: boolean;
  data: {
    crop_type: string;
    province: string;
    growth_days: number;
    date_range: {
      start: string;
      end: string;
    };
    recommendations: PlantingRecommendation[];
    statistics: {
      max_price: number;
      min_price: number;
      avg_price: number;
      total_dates_analyzed: number;
    };
    risk_warning: string | null;
  };
  timestamp: string;
}

interface Crop {
  name: string;
  category: string;
  growth_days: number;
  min_price: number;
  max_price: number;
}

interface CropComparison {
  crop_type: string;
  crop_category: string;
  growth_days: number;
  harvest_date: string;
  predicted_price: number;
  confidence: number;
  expected_yield_kg: number;
  expected_revenue: number;
  estimated_cost: number;
  expected_profit: number;
  roi_percent: number;
}

interface CompareResponse {
  success: boolean;
  province: string;
  planting_date: string;
  planting_area_rai: number;
  comparisons: CropComparison[];
  best_choice: string | null;
}

// ==================== Hooks ====================

/**
 * Get planting schedule recommendations with ML predictions
 * Uses existing /recommend-planting-date endpoint
 */
export const usePlantingSchedule = () => {
  return useMutation({
    mutationFn: async (request: PlantingScheduleRequest): Promise<PlantingScheduleResponse> => {
      const requestBody = {
        province: request.province,
        crop_type: request.crop_type,
        growth_days: request.growth_days || 90,
        planting_area_rai: request.planting_area_rai || 10,
        start_date: request.start_date,
        end_date: request.end_date,
        top_n: request.top_n || 10,
        min_price_threshold: request.min_price_threshold || 10
      };

      const response = await fetch(`${API_BASE_URL}/recommend-planting-date`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get planting schedule');
      }

      const data = await response.json();
      
      // Transform response to match expected format
      const recommendations = data.recommendations?.map((rec: any) => ({
        planting_date: rec.planting_date,
        harvest_date: rec.harvest_date,
        predicted_price: rec.predicted_price || rec.price || 25.0,
        predicted_rainfall: rec.rainfall || 100.0,
        confidence: rec.confidence || 0.8,
        risk_score: rec.risk_score || (1 - (rec.planting_score || 0.5)),
        recommendation: rec.recommendation || 'แนะนำ',
        planting_area_rai: requestBody.planting_area_rai,
        expected_yield_kg: requestBody.planting_area_rai * 500,
        expected_revenue: (rec.predicted_price || 25.0) * requestBody.planting_area_rai * 500
      })) || [];

      const prices = recommendations.map((r: any) => r.predicted_price);
      
      return {
        success: true,
        data: {
          crop_type: request.crop_type,
          province: request.province,
          growth_days: request.growth_days || 90,
          date_range: {
            start: request.start_date || new Date().toISOString().split('T')[0],
            end: request.end_date || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          },
          recommendations,
          statistics: {
            max_price: prices.length > 0 ? Math.max(...prices) : 0,
            min_price: prices.length > 0 ? Math.min(...prices) : 0,
            avg_price: prices.length > 0 ? prices.reduce((a: number, b: number) => a + b, 0) / prices.length : 0,
            total_dates_analyzed: recommendations.length
          },
          risk_warning: null
        },
        timestamp: new Date().toISOString()
      };
    },
  });
};

/**
 * Get available crops with their characteristics
 * Uses existing /api/v2/forecast/crops endpoint
 */
export const useAvailableCrops = () => {
  return useQuery({
    queryKey: ['available-crops'],
    queryFn: async (): Promise<{ success: boolean; crops: Crop[]; total: number }> => {
      const response = await fetch(`${API_BASE_URL}/api/v2/forecast/crops`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch crops');
      }
      
      const data = await response.json();
      
      // Transform response to match expected format
      const crops = data.crops?.map((crop: any) => ({
        name: crop.crop_type || crop.name,
        category: crop.crop_category || crop.category,
        growth_days: crop.growth_days || 90,
        min_price: crop.min_price || 0,
        max_price: crop.max_price || 0
      })) || [];
      
      return {
        success: true,
        crops,
        total: crops.length
      };
    },
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });
};

/**
 * Compare multiple crops for a specific planting date
 * Uses existing /api/v3/recommend-crops endpoint for comparison
 */
export const useCompareCrops = () => {
  return useMutation({
    mutationFn: async (request: {
      province: string;
      crop_types: string[];
      planting_date: string;
      planting_area_rai?: number;
    }): Promise<CompareResponse> => {
      // Use the crop recommendation endpoint to get comparison data
      const requestBody = {
        province: request.province,
        water_availability: "ปานกลาง",
        budget_level: "กลาง", 
        risk_tolerance: "ต่ำ",
        experience_level: "ปานกลาง",
        time_constraint: 90,
        soil_type: "ดินร่วน",
        preference: "ผักใบ",
        season: "ร้อน",
        top_n: request.crop_types.length
      };

      const response = await fetch(`${API_BASE_URL}/api/v3/recommend-crops`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to compare crops');
      }

      const data = await response.json();
      
      // Transform response to match expected format
      const comparisons = data.recommendations?.filter((rec: any) => 
        request.crop_types.includes(rec.crop_type)
      ).map((rec: any) => {
        const plantingDate = new Date(request.planting_date);
        const harvestDate = new Date(plantingDate.getTime() + (rec.growth_days || 90) * 24 * 60 * 60 * 1000);
        const expectedYield = (request.planting_area_rai || 10) * 500;
        const predictedPrice = 25.0; // Default price
        const expectedRevenue = predictedPrice * expectedYield;
        const estimatedCost = 5000 * (request.planting_area_rai || 10);
        const expectedProfit = expectedRevenue - estimatedCost;
        
        return {
          crop_type: rec.crop_type,
          crop_category: rec.crop_category,
          growth_days: rec.growth_days || 90,
          harvest_date: harvestDate.toISOString().split('T')[0],
          predicted_price: predictedPrice,
          confidence: rec.confidence || 85,
          expected_yield_kg: expectedYield,
          expected_revenue: expectedRevenue,
          estimated_cost: estimatedCost,
          expected_profit: expectedProfit,
          roi_percent: estimatedCost > 0 ? (expectedProfit / estimatedCost * 100) : 0
        };
      }) || [];

      const bestChoice = comparisons.length > 0 ? 
        comparisons.reduce((best: any, current: any) => 
          current.roi_percent > best.roi_percent ? current : best
        ).crop_type : null;

      return {
        success: true,
        province: request.province,
        planting_date: request.planting_date,
        planting_area_rai: request.planting_area_rai || 10,
        comparisons,
        best_choice: bestChoice
      };
    },
  });
};

// ==================== Legacy Hook (Keep for backward compatibility) ====================

interface LegacyPlantingRecommendationRequest {
  crop_type: string;
  province: string;
  growth_days: number;
}

export const usePlantingRecommendation = () => {
  return useMutation({
    mutationFn: async (request: LegacyPlantingRecommendationRequest) => {
      console.log('🚀 Sending planting recommendation request:', request);
      
      const response = await fetch(`${API_BASE_URL}/recommend-planting-date`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          crop_type: request.crop_type,
          province: request.province,
          growth_days: request.growth_days,
          planting_area_rai: 10.0,
          top_n: 10,
          min_price_threshold: 10.0
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Planting recommendation failed:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`Failed to get planting recommendation: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Planting recommendation response:', data);
      
      return data;
    },
  });
};

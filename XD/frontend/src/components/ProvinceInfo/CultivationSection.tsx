import { Sprout, TrendingUp } from 'lucide-react';
import type { CultivationData } from '@/hooks/useProvinceInfo';

interface CultivationSectionProps {
  data: CultivationData;
}

/**
 * CultivationSection Component
 * Displays top 5 crops by cultivation area with statistics
 * Shows planting area, average yield, and success rate
 */
export function CultivationSection({ data }: CultivationSectionProps) {
  const hasCrops = data.crops && data.crops.length > 0;

  if (!hasCrops) {
    return (
      <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-100">
        <div className="flex items-center gap-2 mb-2">
          <Sprout className="w-5 h-5 text-green-600" />
          <h4 className="font-semibold text-gray-800">พืชที่ปลูก (Top 5)</h4>
        </div>
        <div className="text-sm text-gray-500 text-center py-2">
          ไม่มีข้อมูลการปลูกพืช
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-100">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sprout className="w-5 h-5 text-green-600" />
          <h4 className="font-semibold text-gray-800">พืชที่ปลูก (Top 5)</h4>
        </div>
        <div className="text-xs text-gray-500">
          {data.total_crops} ชนิด
        </div>
      </div>
      
      <div className="space-y-3">
        {data.crops.map((crop, idx) => (
          <div 
            key={idx} 
            className="flex justify-between items-center p-2 bg-white rounded-md border border-green-100 hover:border-green-300 transition-colors"
          >
            <div className="flex-1">
              <div className="font-medium text-gray-800 text-sm">
                {crop.crop_type}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {crop.planting_area_rai.toFixed(1)} ไร่
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Yield */}
              <div className="text-right">
                <div className="text-xs text-gray-500">ผลผลิต</div>
                <div className="font-semibold text-sm text-gray-700">
                  {crop.average_yield_kg.toFixed(0)} kg
                </div>
              </div>
              
              {/* Success Rate */}
              <div className="text-right min-w-[60px]">
                <div className="text-xs text-gray-500">สำเร็จ</div>
                <div className="flex items-center justify-end gap-1">
                  <div className={`font-bold text-sm ${
                    crop.success_rate >= 80 ? 'text-green-600' :
                    crop.success_rate >= 60 ? 'text-yellow-600' :
                    'text-orange-600'
                  }`}>
                    {crop.success_rate.toFixed(0)}%
                  </div>
                  {crop.success_rate >= 80 && (
                    <TrendingUp className="w-3 h-3 text-green-600" />
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary note */}
      <div className="mt-3 pt-2 border-t border-green-200">
        <div className="text-xs text-gray-500 text-center">
          ข้อมูลจากการปลูกในรอบ 1 ปีที่ผ่านมา
        </div>
      </div>
    </div>
  );
}

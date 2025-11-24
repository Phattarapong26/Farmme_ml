import { TrendingUp, TrendingDown, Minus, DollarSign } from 'lucide-react';
import type { PriceData } from '@/hooks/useProvinceInfo';

interface PricesSectionProps {
  data: PriceData;
}

/**
 * TrendIndicator Component
 * Shows trend arrow and percentage change with appropriate color
 */
function TrendIndicator({ trend, change }: { trend: 'increasing' | 'decreasing' | 'stable'; change: number }) {
  if (trend === 'increasing') {
    return (
      <div className="flex items-center gap-1 text-green-600">
        <TrendingUp className="w-3 h-3" />
        <span className="text-xs font-medium">+{change.toFixed(1)}%</span>
      </div>
    );
  }
  
  if (trend === 'decreasing') {
    return (
      <div className="flex items-center gap-1 text-red-600">
        <TrendingDown className="w-3 h-3" />
        <span className="text-xs font-medium">{change.toFixed(1)}%</span>
      </div>
    );
  }
  
  return (
    <div className="flex items-center gap-1 text-gray-500">
      <Minus className="w-3 h-3" />
      <span className="text-xs font-medium">0%</span>
    </div>
  );
}

/**
 * PricesSection Component
 * Displays current crop prices with trend indicators
 * Shows price per kg and percentage change
 */
export function PricesSection({ data }: PricesSectionProps) {
  const hasPrices = data.crops && data.crops.length > 0;

  if (!hasPrices) {
    return (
      <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-100">
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="w-5 h-5 text-yellow-600" />
          <h4 className="font-semibold text-gray-800">ราคาตลาด</h4>
        </div>
        <div className="text-sm text-gray-500 text-center py-2">
          ไม่มีข้อมูลราคา
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-100">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-yellow-600" />
          <h4 className="font-semibold text-gray-800">ราคาตลาด</h4>
        </div>
        <div className="text-xs text-gray-500">
          {data.total_crops} ชนิด
        </div>
      </div>
      
      <div className="space-y-2">
        {data.crops.map((crop, idx) => (
          <div 
            key={idx} 
            className="flex justify-between items-center p-2 bg-white rounded-md border border-yellow-100 hover:border-yellow-300 transition-colors"
          >
            <div className="flex-1">
              <div className="font-medium text-gray-800 text-sm">
                {crop.crop_type}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {new Date(crop.date).toLocaleDateString('th-TH', {
                  month: 'short',
                  day: 'numeric'
                })}
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Price */}
              <div className="text-right">
                <div className="font-bold text-base text-gray-800">
                  ฿{crop.price_per_kg.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500">/กก.</div>
              </div>
              
              {/* Trend */}
              <div className="min-w-[60px] flex justify-end">
                <TrendIndicator trend={crop.trend} change={crop.change_percent} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-3 pt-2 border-t border-yellow-200">
        <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-green-600" />
            <span>เพิ่มขึ้น</span>
          </div>
          <div className="flex items-center gap-1">
            <TrendingDown className="w-3 h-3 text-red-600" />
            <span>ลดลง</span>
          </div>
          <div className="flex items-center gap-1">
            <Minus className="w-3 h-3 text-gray-500" />
            <span>คงที่</span>
          </div>
        </div>
      </div>
    </div>
  );
}

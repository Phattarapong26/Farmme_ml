import { DollarSign, Fuel, Leaf } from 'lucide-react';
import type { EconomicData } from '@/hooks/useProvinceInfo';

interface EconomicSectionProps {
  data: EconomicData;
}

/**
 * Formats a date string to Thai format
 */
function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'ไม่ทราบ';
  
  try {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('th-TH', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  } catch {
    return dateStr;
  }
}

/**
 * EconomicSection Component
 * Displays economic indicators relevant to farming
 * Shows fertilizer and fuel prices with full timeline
 */
export function EconomicSection({ data }: EconomicSectionProps) {
  const hasData = data.fertilizer_price !== null || data.fuel_price !== null;
  const hasTimeline = data.timeline && data.timeline.length > 0;

  if (!hasData) {
    return (
      <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="w-5 h-5 text-purple-600" />
          <h4 className="font-semibold text-gray-800">ปัจจัยเศรษฐกิจ</h4>
        </div>
        <div className="text-sm text-gray-500 text-center py-2">
          ไม่มีข้อมูลเศรษฐกิจ
        </div>
      </div>
    );
  }

  // Calculate statistics from timeline
  const fertilizerPrices = hasTimeline 
    ? data.timeline.map(d => d.fertilizer_price).filter((p): p is number => p !== null)
    : [];
  const fuelPrices = hasTimeline 
    ? data.timeline.map(d => d.fuel_price).filter((p): p is number => p !== null)
    : [];

  const fertilizerMin = fertilizerPrices.length > 0 ? Math.min(...fertilizerPrices) : null;
  const fertilizerMax = fertilizerPrices.length > 0 ? Math.max(...fertilizerPrices) : null;
  const fuelMin = fuelPrices.length > 0 ? Math.min(...fuelPrices) : null;
  const fuelMax = fuelPrices.length > 0 ? Math.max(...fuelPrices) : null;

  return (
    <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-purple-600" />
          <h4 className="font-semibold text-gray-800">ปัจจัยเศรษฐกิจ</h4>
        </div>
        {hasTimeline && (
          <div className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded-full font-medium">
            {data.total_data_points} จุดข้อมูล
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        {/* Fertilizer Price */}
        <div className="p-3 bg-white rounded-md border border-purple-100">
          <div className="flex items-center justify-center mb-2">
            <Leaf className="w-5 h-5 text-green-600" />
          </div>
          <div className="text-xs text-gray-600 text-center mb-1">
            ราคาปุ๋ย (ล่าสุด)
          </div>
          <div className="font-bold text-lg text-gray-800 text-center">
            {data.fertilizer_price !== null 
              ? `฿${data.fertilizer_price.toFixed(2)}`
              : 'N/A'}
          </div>
          {fertilizerMin !== null && fertilizerMax !== null && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <div className="text-xs text-gray-500 text-center">
                ช่วง: ฿{fertilizerMin.toFixed(2)} - ฿{fertilizerMax.toFixed(2)}
              </div>
            </div>
          )}
        </div>

        {/* Fuel Price */}
        <div className="p-3 bg-white rounded-md border border-purple-100">
          <div className="flex items-center justify-center mb-2">
            <Fuel className="w-5 h-5 text-orange-600" />
          </div>
          <div className="text-xs text-gray-600 text-center mb-1">
            ราคาน้ำมัน (ล่าสุด)
          </div>
          <div className="font-bold text-lg text-gray-800 text-center">
            {data.fuel_price !== null 
              ? `฿${data.fuel_price.toFixed(2)}`
              : 'N/A'}
          </div>
          {fuelMin !== null && fuelMax !== null && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <div className="text-xs text-gray-500 text-center">
                ช่วง: ฿{fuelMin.toFixed(2)} - ฿{fuelMax.toFixed(2)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Timeline info */}
      {hasTimeline && (
        <div className="mt-3 pt-2 border-t border-purple-200">
          <div className="text-xs text-gray-600 text-center">
            📊 ข้อมูลทั้งหมด: {data.total_data_points} จุด
          </div>
          <div className="text-xs text-gray-500 text-center mt-1">
            {data.timeline[0].date} ถึง {data.timeline[data.timeline.length - 1].date}
          </div>
        </div>
      )}

      {/* Data timestamp */}
      {data.date && (
        <div className="mt-2">
          <div className="text-xs text-gray-500 text-center">
            อัพเดทล่าสุด: {formatDate(data.date)}
          </div>
        </div>
      )}

      {/* Info note */}
      <div className="mt-2">
        <div className="text-xs text-gray-500 text-center">
          ราคาเฉลี่ยระดับประเทศ
        </div>
      </div>
    </div>
  );
}

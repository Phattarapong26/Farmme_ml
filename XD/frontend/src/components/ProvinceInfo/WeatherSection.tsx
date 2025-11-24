import { Cloud, Droplets, Wind } from 'lucide-react';
import type { WeatherInfo } from '@/hooks/useProvinceInfo';

interface WeatherSectionProps {
    data: WeatherInfo;
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
 * WeatherSection Component
 * Displays current weather information for a province
 * Shows temperature, rainfall, and humidity with appropriate icons
 */
export function WeatherSection({ data }: WeatherSectionProps) {
    const hasData = data.temperature_celsius !== null ||
        data.rainfall_mm !== null ||
        data.humidity_percent !== null;

    if (!hasData) {
        return (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex items-center gap-2 mb-2">
                    <Cloud className="w-5 h-5 text-blue-600" />
                    <h4 className="font-semibold text-gray-800">สภาพอากาศ</h4>
                </div>
                <div className="text-sm text-gray-500 text-center py-2">
                    ไม่มีข้อมูลสภาพอากาศ
                </div>
            </div>
        );
    }

    return (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
            <div className="flex items-center gap-2 mb-3">
                <Cloud className="w-5 h-5 text-blue-600" />
                <h4 className="font-semibold text-gray-800">สภาพอากาศ</h4>
            </div>

            <div className="grid grid-cols-3 gap-3">
                {/* Temperature */}
                <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                        <Wind className="w-4 h-4 text-orange-500" />
                    </div>
                    <div className="text-xs text-gray-600 mb-1">อุณหภูมิ</div>
                    <div className="font-bold text-lg text-gray-800">
                        {data.temperature_celsius !== null
                            ? `${data.temperature_celsius.toFixed(1)}°C`
                            : 'N/A'}
                    </div>
                </div>

                {/* Rainfall */}
                <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                        <Droplets className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="text-xs text-gray-600 mb-1">ฝน</div>
                    <div className="font-bold text-lg text-gray-800">
                        {data.rainfall_mm !== null
                            ? `${data.rainfall_mm.toFixed(1)} mm`
                            : 'N/A'}
                    </div>
                </div>

                {/* Humidity */}
                <div className="text-center">
                    <div className="flex items-center justify-center mb-1">
                        <Cloud className="w-4 h-4 text-cyan-500" />
                    </div>
                    <div className="text-xs text-gray-600 mb-1">ความชื้น</div>
                    <div className="font-bold text-lg text-gray-800">
                        {data.humidity_percent !== null
                            ? `${data.humidity_percent.toFixed(0)}%`
                            : 'N/A'}
                    </div>
                </div>
            </div>

            {/* Data timestamp */}
            {data.date && (
                <div className="mt-3 pt-2 border-t border-blue-200">
                    <div className="text-xs text-gray-500 text-center">
                        อัพเดท: {formatDate(data.date)}
                        {data.data_age_days !== null && data.data_age_days > 0 && (
                            <span className="ml-1">
                                ({data.data_age_days} วันที่แล้ว)
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

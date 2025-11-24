import React, { useState } from 'react';
import PriceForecastChart from './PriceForecastChart';
import { BarChart3, AlertCircle, Loader2 } from 'lucide-react';

interface ChartData {
  type: 'price_forecast';
  data: {
    historical: Array<{ date: string; price: number }>;
    forecast: Array<{
      date: string;
      price: number;
      confidence_low: number;
      confidence_high: number;
    }>;
    metadata: {
      crop_type: string;
      province: string;
      days_ahead: number;
      model_used: string;
      confidence: number;
      price_trend: string;
    };
  };
}

interface ChartMessageProps {
  chartData: ChartData;
  textResponse: string;
}

const ChartMessage: React.FC<ChartMessageProps> = ({ chartData, textResponse }) => {
  const [isChartLoading, setIsChartLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  // Simulate chart loading
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsChartLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  // Validate chart data
  const isValidChartData = () => {
    if (!chartData || !chartData.data) return false;
    const { historical, forecast, metadata } = chartData.data;
    
    if (!historical || !Array.isArray(historical) || historical.length === 0) {
      return false;
    }
    if (!forecast || !Array.isArray(forecast) || forecast.length === 0) {
      return false;
    }
    if (!metadata) {
      return false;
    }
    
    return true;
  };

  const handleChartError = () => {
    setHasError(true);
    setIsChartLoading(false);
  };

  return (
    <div className="space-y-3">
      {/* Text Response */}
      {textResponse && (
        <div className="text-sm leading-relaxed break-words whitespace-pre-wrap">
          {textResponse}
        </div>
      )}

      {/* Chart Section */}
      {chartData && (
        <div className="mt-3">
          {isChartLoading ? (
            // Loading state
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 text-green-500 animate-spin mb-3" />
              <p className="text-sm text-gray-600">กำลังโหลดกราฟ...</p>
            </div>
          ) : hasError || !isValidChartData() ? (
            // Error state
            <div className="bg-red-50 rounded-lg border border-red-200 p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800 mb-1">
                  ไม่สามารถแสดงกราฟได้
                </p>
                <p className="text-xs text-red-600">
                  ข้อมูลกราฟไม่สมบูรณ์ กรุณาลองใหม่อีกครั้ง
                </p>
              </div>
            </div>
          ) : (
            // Chart display
            <div className="relative">
              {/* Chart type indicator */}
              <div className="absolute top-2 right-2 z-10">
                <div className="bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full border border-gray-200 flex items-center gap-1">
                  <BarChart3 className="w-3 h-3 text-purple-600" />
                  <span className="text-xs text-gray-600 font-medium">
                    กราฟ interactive
                  </span>
                </div>
              </div>

              {/* Render chart based on type */}
              {chartData.type === 'price_forecast' && (
                <PriceForecastChart data={chartData.data} />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChartMessage;

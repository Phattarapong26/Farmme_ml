import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
  ReferenceDot
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, Calendar, DollarSign } from 'lucide-react';

interface PricePoint {
  date: string;
  price: number;
}

interface ForecastPoint {
  date: string;
  price: number;
  confidence_low: number;
  confidence_high: number;
}

interface ChartMetadata {
  crop_type: string;
  province: string;
  days_ahead: number;
  model_used: string;
  confidence: number;
  price_trend: string;
}

interface PriceForecastChartProps {
  data: {
    historical: PricePoint[];
    forecast: ForecastPoint[];
    metadata: ChartMetadata;
  };
}

const PriceForecastChart: React.FC<PriceForecastChartProps> = ({ data }) => {
  const { historical, forecast, metadata } = data;

  // Sample data to reduce points for smoother chart (like /forecast)
  const sampleData = (data: any[], maxPoints: number) => {
    if (data.length <= maxPoints) return data;
    
    const step = Math.ceil(data.length / maxPoints);
    const sampled = [];
    
    // Always include first and last points
    sampled.push(data[0]);
    
    for (let i = step; i < data.length - 1; i += step) {
      sampled.push(data[i]);
    }
    
    sampled.push(data[data.length - 1]);
    return sampled;
  };

  // Sample historical data (max 10 points for smooth chart)
  const sampledHistorical = sampleData(historical, 10);
  
  // Sample forecast data (max 10 points for smooth chart)
  const sampledForecast = sampleData(forecast, 10);

  // Combine historical and forecast data for chart
  const chartData = [
    // Historical data (sampled)
    ...sampledHistorical.map(item => ({
      date: item.date,
      historical_price: item.price,
      forecast_price: null,
      confidence_low: null,
      confidence_high: null,
      type: 'historical'
    })),
    // Bridge point - IMPORTANT: Connect historical to forecast seamlessly
    {
      date: sampledHistorical[sampledHistorical.length - 1]?.date || sampledForecast[0]?.date,
      historical_price: sampledHistorical[sampledHistorical.length - 1]?.price || null,
      forecast_price: sampledHistorical[sampledHistorical.length - 1]?.price || null, // Same price for continuity
      confidence_low: sampledHistorical[sampledHistorical.length - 1]?.price || null, // Same as price
      confidence_high: sampledHistorical[sampledHistorical.length - 1]?.price || null, // Same as price
      type: 'bridge'
    },
    // Forecast data (sampled)
    ...sampledForecast.map(item => ({
      date: item.date,
      historical_price: null,
      forecast_price: item.price,
      confidence_low: item.confidence_low,
      confidence_high: item.confidence_high,
      type: 'forecast'
    }))
  ];

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('th-TH', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const price = data.historical_price || data.forecast_price;
      const isHistorical = data.type === 'historical';
      
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-700 mb-2">
            {formatDate(data.date)}
          </p>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isHistorical ? 'bg-blue-500' : 'bg-green-500'}`}></div>
              <span className="text-xs text-gray-600">
                {isHistorical ? 'ราคาจริง' : 'ราคาทำนาย'}:
              </span>
              <span className="text-sm font-bold text-gray-800">
                {price?.toFixed(2)} บาท/กก.
              </span>
            </div>
            {!isHistorical && data.confidence_low && data.confidence_high && (
              <div className="text-xs text-gray-500 mt-1 pt-1 border-t border-gray-100">
                ช่วงความเชื่อมั่น: {data.confidence_low.toFixed(2)} - {data.confidence_high.toFixed(2)} บาท
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // Trend indicator
  const getTrendInfo = () => {
    const trend = metadata.price_trend;
    if (trend === 'increasing') {
      return {
        icon: TrendingUp,
        text: 'แนวโน้มขึ้น',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      };
    } else if (trend === 'decreasing') {
      return {
        icon: TrendingDown,
        text: 'แนวโน้มลง',
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200'
      };
    } else {
      return {
        icon: Minus,
        text: 'แนวโน้มคงที่',
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200'
      };
    }
  };

  const trendInfo = getTrendInfo();
  const TrendIcon = trendInfo.icon;

  // Calculate price range
  const allPrices = [
    ...historical.map(h => h.price),
    ...forecast.map(f => f.price)
  ];
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const priceRange = maxPrice - minPrice;
  const yAxisMin = Math.floor(minPrice - priceRange * 0.1);
  const yAxisMax = Math.ceil(maxPrice + priceRange * 0.1);

  return (
    <div className={`mt-4 p-4 rounded-lg border ${trendInfo.borderColor} ${trendInfo.bgColor}`}>
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-800">กราฟทำนายราคา</h3>
          </div>
          <div className="flex items-center gap-2">
            <TrendIcon className={`w-4 h-4 ${trendInfo.color}`} />
            <span className={`text-sm font-medium ${trendInfo.color}`}>
              {trendInfo.text}
            </span>
          </div>
        </div>
        
        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>{metadata.crop_type} • {metadata.province}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">
              {metadata.days_ahead} วันข้างหน้า
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
              ความเชื่อมั่น {(metadata.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg p-3 border border-gray-200">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatDate}
              tick={{ fontSize: 11 }}
              stroke="#9ca3af"
            />
            <YAxis 
              domain={[yAxisMin, yAxisMax]}
              tick={{ fontSize: 11 }}
              stroke="#9ca3af"
              label={{ 
                value: 'บาท/กก.', 
                angle: -90, 
                position: 'insideLeft',
                style: { fontSize: 11, fill: '#6b7280' }
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: '12px' }}
              iconType="line"
            />
            
            {/* Confidence interval area (behind lines) */}
            <Area
              type="natural"
              dataKey="confidence_high"
              stroke="none"
              fill="#86efac"
              fillOpacity={0.2}
              name="ช่วงความเชื่อมั่น"
            />
            <Area
              type="natural"
              dataKey="confidence_low"
              stroke="none"
              fill="#ffffff"
              fillOpacity={1}
            />
            
            {/* Historical price line - SMOOTH curve */}
            <Line
              type="natural"
              dataKey="historical_price"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 4 }}
              name="ราคาจริง"
              connectNulls={false}
              animationDuration={800}
            />
            
            {/* Forecast price line - SMOOTH curve */}
            <Line
              type="natural"
              dataKey="forecast_price"
              stroke="#22c55e"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ fill: '#22c55e', r: 4 }}
              name="ราคาทำนาย"
              connectNulls={false}
              animationDuration={800}
            />
            
            {/* Confidence bounds - Upper line (สูงสุด) */}
            <Line
              type="natural"
              dataKey="confidence_high"
              stroke="#fbbf24"
              strokeWidth={1.5}
              strokeDasharray="3 3"
              dot={false}
              name="ราคาสูงสุด"
              connectNulls={true}
              opacity={0.6}
            />
            
            {/* Confidence bounds - Lower line (ต่ำสุด) */}
            <Line
              type="natural"
              dataKey="confidence_low"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="3 3"
              dot={false}
              name="ราคาต่ำสุด"
              connectNulls={true}
              opacity={0.6}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Price Statistics */}
      <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        <div className="bg-blue-50 p-2 rounded">
          <div className="text-blue-600 font-medium">ราคาสูงสุด</div>
          <div className="text-blue-800 font-bold">{maxPrice.toFixed(2)} บาท</div>
        </div>
        <div className="bg-red-50 p-2 rounded">
          <div className="text-red-600 font-medium">ราคาต่ำสุด</div>
          <div className="text-red-800 font-bold">{minPrice.toFixed(2)} บาท</div>
        </div>
        <div className="bg-purple-50 p-2 rounded">
          <div className="text-purple-600 font-medium">ราคาเฉลี่ย</div>
          <div className="text-purple-800 font-bold">
            {((maxPrice + minPrice) / 2).toFixed(2)} บาท
          </div>
        </div>
        <div className="bg-green-50 p-2 rounded">
          <div className="text-green-600 font-medium">ช่วงราคา</div>
          <div className="text-green-800 font-bold">
            {(maxPrice - minPrice).toFixed(2)} บาท
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-500"></div>
          <span>ราคาย้อนหลัง</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-green-500 border-dashed border-t-2 border-green-500"></div>
          <span>ราคาทำนาย</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-3 bg-green-200 opacity-40"></div>
          <span>ช่วงความเชื่อมั่น</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-yellow-500 border-dashed border-t border-yellow-500"></div>
          <span>ราคาสูงสุด/ต่ำสุด</span>
        </div>
      </div>

      {/* Model info */}
      <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500 text-center">
        ทำนายโดย ML Model: {metadata.model_used} • แสดง {chartData.length} จุดข้อมูล
      </div>
    </div>
  );
};

export default PriceForecastChart;

import { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ChevronDown, TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import { LineChart, Line, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useForecastProvinces, useForecastCrops, usePriceHistory } from '@/hooks/useForecastData';
import { useQuery } from '@tanstack/react-query';
import { Button } from './ui/button';

interface RealForecastChartProps {
  province?: string;
  selectedPlant: string;
  onPlantChange: (plant: string) => void;
}

type TimeFrame = 7 | 30 | 90 | 180;

const API_BASE = 'http://localhost:8000';

// Custom Tooltip Component with Confidence Interval
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || payload.length === 0) return null;
  
  const data = payload[0].payload;
  const fullDate = new Date(data.fullDate).toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  return (
    <div className="bg-white p-4 border-2 border-gray-300 rounded-lg shadow-xl min-w-[280px]">
      <p className="text-sm font-bold text-gray-800 mb-2 border-b pb-2">
        📅 {fullDate}
      </p>
      {data.historicalPrice && (
        <div className="flex items-center gap-2 mb-1">
          <span className="text-lg">📊</span>
          <p className="text-sm font-semibold text-blue-600">
            ราคาจริง: <span className="font-bold">{data.historicalPrice.toFixed(2)}</span> บาท/กก.
          </p>
        </div>
      )}
      {data.predictedPrice && (
        <>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">🔮</span>
            <p className="text-sm font-semibold text-orange-600">
              ราคาพยากรณ์: <span className="font-bold">{data.predictedPrice.toFixed(2)}</span> บาท/กก.
            </p>
          </div>
          {data.confidence && (
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">🎯</span>
              <p className="text-xs text-purple-600">
                ความเชื่อมั่น: <span className="font-bold">{(data.confidence * 100).toFixed(0)}%</span>
              </p>
            </div>
          )}
          {data.confidenceUpper && data.confidenceLower && (
            <div className="mt-2 pt-2 border-t bg-gray-50 p-2 rounded">
              <p className="text-xs font-semibold text-gray-700 mb-1">📊 ช่วงความเชื่อมั่น:</p>
              <p className="text-xs text-green-600">
                ↑ สูงสุด: <strong>{data.confidenceUpper.toFixed(2)}</strong> บาท/กก.
              </p>
              <p className="text-xs text-red-600">
                ↓ ต่ำสุด: <strong>{data.confidenceLower.toFixed(2)}</strong> บาท/กก.
              </p>
              <p className="text-xs text-gray-500 mt-1">
                ช่วง: ±{((data.confidenceUpper - data.predictedPrice)).toFixed(2)} บาท
              </p>
            </div>
          )}
        </>
      )}
      {data.historicalPrice && data.predictedPrice && (
        <div className="mt-2 pt-2 border-t">
          <p className="text-xs text-gray-600">
            ส่วนต่าง: {Math.abs(data.predictedPrice - data.historicalPrice).toFixed(2)} บาท/กก.
          </p>
        </div>
      )}
    </div>
  );
};

const RealForecastChart: React.FC<RealForecastChartProps> = ({ province, selectedPlant, onPlantChange }) => {
  // State for province and time frame selection
  const [selectedProvince, setSelectedProvince] = useState<string>(province || '');
  const [timeFrame, setTimeFrame] = useState<TimeFrame>(7); // Changed from 90 to 7 (most accurate)

  // Fetch provinces and crops from database
  const { data: provincesData } = useForecastProvinces();
  const { data: cropsData } = useForecastCrops(selectedProvince);
  const { data: priceHistory } = usePriceHistory(selectedProvince, selectedPlant, timeFrame);

  // Update selected province when prop changes
  useEffect(() => {
    if (province && province !== selectedProvince) {
      setSelectedProvince(province);
    }
  }, [province]);

  // Fetch ML model predictions from backend
  const { data: mlForecast, isLoading: isForecastLoading, error: forecastError } = useQuery({
    queryKey: ['ml-price-forecast', selectedProvince, selectedPlant, timeFrame],
    queryFn: async () => {
      if (!selectedProvince || !selectedPlant) return null;

      try {
        // Get crop info for the selected plant
        const cropInfo = cropsData?.crops.find(c => c.crop_type === selectedPlant);

        // Backend will fetch REAL data automatically (weather, economic, cultivation)
        const response = await fetch(`${API_BASE}/api/v2/model/predict-price-forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            province: selectedProvince,
            crop_type: selectedPlant,
            crop_category: cropInfo?.crop_category || 'ผักอื่นๆ',
            days_ahead: timeFrame // Use the actual timeframe selected
          })
        });

        if (!response.ok) {
          console.error(`ML forecast API error: ${response.status} ${response.statusText}`);
          return null;
        }

        const result = await response.json();
        console.log('ML Forecast result:', result);
        return result;

      } catch (error) {
        console.error('ML forecast fetch error:', error);
        return null;
      }
    },
    enabled: !!selectedProvince && !!selectedPlant,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
    retry: 2,
    retryDelay: 1000
  });

  // Calculate trend and recommendation
  const analysis = useMemo(() => {
    if (!priceHistory?.history || priceHistory.history.length === 0) return null;

    const history = priceHistory.history;
    const prices = history.map(h => h.price);
    const avgPrice = priceHistory.statistics.avg_price;
    const latestPrice = priceHistory.statistics.latest_price;

    // Simple trend calculation
    const recentPrices = prices.slice(0, Math.min(10, prices.length));
    const olderPrices = prices.slice(-Math.min(10, prices.length));
    const recentAvg = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
    const olderAvg = olderPrices.reduce((a, b) => a + b, 0) / olderPrices.length;
    const trend = recentAvg > olderAvg ? 'increasing' : 'decreasing';

    // Calculate forecast trend if available
    let forecastTrend = trend;
    if (mlForecast?.success && mlForecast.forecast?.length > 0) {
      const firstForecast = mlForecast.forecast[0].predicted_price;
      const lastForecast = mlForecast.forecast[mlForecast.forecast.length - 1].predicted_price;
      forecastTrend = lastForecast > firstForecast ? 'increasing' : 'decreasing';
    }

    return {
      trend: forecastTrend,
      recommendation: forecastTrend === 'increasing' ? 'ราคาดี ควรปลูก' : 'ราคาอาจลดลง ควรรอดู',
      avgHistoricalPrice: avgPrice,
      latestPrice: latestPrice,
      historicalDataPoints: history.length
    };
  }, [priceHistory, mlForecast]);

  const chartData = useMemo(() => {
    if (!priceHistory?.history) return [];

    // Calculate appropriate data points based on timeframe
    const getDataPoints = (timeFrame: number) => {
      if (timeFrame <= 7) return { historical: timeFrame, forecast: timeFrame }; // Show all 7 days
      if (timeFrame <= 30) return { historical: 15, forecast: 15 };
      if (timeFrame <= 90) return { historical: 30, forecast: 30 };
      return { historical: 60, forecast: 60 };
    };

    const dataPoints = getDataPoints(timeFrame);

    // Get historical data - reverse to show oldest to newest
    const historicalData = priceHistory.history
      .slice()
      .reverse()
      .slice(-dataPoints.historical) // Use calculated historical points
      .map(item => ({
        date: new Date(item.date).toLocaleDateString('th-TH', { 
          day: 'numeric', 
          month: timeFrame <= 7 ? 'numeric' : 'short' // Show day/month for 7 days
        }),
        fullDate: item.date,
        historicalPrice: item.price,
        predictedPrice: null,
        confidenceUpper: null,
        confidenceLower: null,
        type: 'historical'
      }));

    // Get ML forecast data if available with confidence intervals
    const forecastData = mlForecast?.success && mlForecast.forecast
      ? mlForecast.forecast
        .slice(0, dataPoints.forecast) // Use calculated forecast points
        .map((item: any) => {
          const predictedPrice = item.predicted_price;
          const confidence = item.confidence_score || 0.8;
          
          // Calculate confidence interval based on MAE and confidence score
          // Higher confidence = narrower interval
          const mae = mlForecast.metadata?.mae || 6.97;
          const intervalWidth = mae * (1 - confidence) * 2; // Adjust interval based on confidence
          
          return {
            date: new Date(item.date).toLocaleDateString('th-TH', { 
              day: 'numeric', 
              month: timeFrame <= 7 ? 'numeric' : 'short' // Show day/month for 7 days
            }),
            fullDate: item.date,
            historicalPrice: null,
            predictedPrice: predictedPrice,
            confidenceUpper: predictedPrice + intervalWidth,
            confidenceLower: Math.max(0, predictedPrice - intervalWidth), // Don't go below 0
            confidence: confidence,
            type: 'forecast'
          };
        })
      : [];

    // Create a bridge point to connect historical and forecast data
    // Use the last historical price as the first forecast point
    if (historicalData.length > 0 && forecastData.length > 0) {
      const lastHistorical = historicalData[historicalData.length - 1];
      const bridgePoint = {
        date: lastHistorical.date,
        fullDate: lastHistorical.fullDate,
        historicalPrice: lastHistorical.historicalPrice,
        predictedPrice: lastHistorical.historicalPrice, // Connect with same price
        confidenceUpper: lastHistorical.historicalPrice,
        confidenceLower: lastHistorical.historicalPrice,
        type: 'bridge'
      };
      return [...historicalData, bridgePoint, ...forecastData];
    }

    return [...historicalData, ...forecastData];
  }, [priceHistory, mlForecast, timeFrame]);

  // Calculate Y-axis domain based on actual data
  const yAxisDomain = useMemo(() => {
    if (chartData.length === 0) return [0, 100];

    const allPrices = chartData
      .map(d => [d.historicalPrice, d.predictedPrice])
      .flat()
      .filter((price): price is number => price !== null && price !== undefined);

    if (allPrices.length === 0) return [0, 100];

    const minPrice = Math.min(...allPrices);
    const maxPrice = Math.max(...allPrices);
    const range = maxPrice - minPrice;
    
    // Add 10% padding on top and bottom for better visualization
    const padding = range * 0.1 || 5; // Use 5 as minimum padding if range is 0
    
    return [
      Math.max(0, Math.floor(minPrice - padding)), // Don't go below 0
      Math.ceil(maxPrice + padding)
    ];
  }, [chartData]);

  const currentPrice = useMemo(() => {
    return priceHistory?.statistics.latest_price || 0;
  }, [priceHistory]);

  const priceChange = useMemo(() => {
    if (!analysis?.trend) return 0;
    return analysis.trend === 'increasing' ? 5 : analysis.trend === 'decreasing' ? -5 : 0;
  }, [analysis]);

  const timeFrameOptions: { value: TimeFrame; label: string; badge: string; badgeColor: string }[] = [
    { value: 7, label: '7 วัน', badge: '⭐ แม่นสุด', badgeColor: 'bg-green-500' },
    { value: 30, label: '30 วัน', badge: '✅ แม่น', badgeColor: 'bg-blue-500' },
    { value: 90, label: '90 วัน', badge: '⚠️ พอใช้', badgeColor: 'bg-yellow-500' },
    { value: 180, label: '180 วัน', badge: '❌ ไม่แนะนำ', badgeColor: 'bg-red-500' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">📈</span>
              </div>
              การพยากรณ์ราคาพืช (ML Model)
            </div>
          </div>

          {/* Province and Crop Selectors */}
          <div className="flex flex-wrap gap-3 items-center">
            {/* Province Selector */}
            <div className="relative">
              <select
                value={selectedProvince}
                onChange={(e) => setSelectedProvince(e.target.value)}
                className="appearance-none bg-blue-500 text-white px-4 py-2 pr-8 rounded-lg text-sm font-medium cursor-pointer hover:bg-blue-600 transition-colors"
              >
                <option value="" className="bg-white text-gray-800">เลือกจังหวัด</option>
                {provincesData?.provinces.map((prov) => (
                  <option key={prov} value={prov} className="bg-white text-gray-800">
                    {prov}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white pointer-events-none" />
            </div>

            {/* Crop Selector */}
            <div className="relative">
              <select
                value={selectedPlant}
                onChange={(e) => onPlantChange(e.target.value)}
                className="appearance-none bg-green-500 text-white px-4 py-2 pr-8 rounded-lg text-sm font-medium cursor-pointer hover:bg-green-600 transition-colors"
                disabled={!selectedProvince}
              >
                {cropsData?.crops.map((crop) => (
                  <option key={crop.crop_type} value={crop.crop_type} className="bg-white text-gray-800">
                    {crop.crop_type} ({crop.crop_category})
                  </option>
                )) || <option>กำลังโหลด...</option>}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white pointer-events-none" />
            </div>

            {/* Time Frame Selector with Accuracy Badges */}
            <div className="flex gap-2 items-center ml-auto flex-wrap">
              <Calendar className="w-4 h-4 text-gray-500" />
              {timeFrameOptions.map((option) => (
                <Button
                  key={option.value}
                  variant={timeFrame === option.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeFrame(option.value)}
                  className={`${timeFrame === option.value ? option.badgeColor + ' text-white hover:opacity-90' : 'hover:bg-gray-100'} transition-all`}
                  title={`ความแม่นยำ: ${option.badge}`}
                >
                  <span>{option.label}</span>
                  {timeFrame === option.value && (
                    <span className="ml-1 text-xs opacity-90">{option.badge}</span>
                  )}
                </Button>
              ))}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Accuracy Info Panel */}
        

        <div className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm text-blue-600 font-medium">ราคาปัจจุบัน</p>
              <p className="text-lg font-bold text-blue-700">{currentPrice.toFixed(2)} บาท/กก.</p>
            </div>
            <div className={`${priceChange >= 0 ? 'bg-green-50' : 'bg-red-50'} p-3 rounded-lg`}>
              <p className={`text-sm font-medium ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                แนวโน้ม
              </p>
              <div className="flex items-center gap-2">
                {priceChange >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                )}
                <p className={`text-lg font-bold ${priceChange >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                  {priceChange > 0 ? '+' : ''}{priceChange}%
                </p>
              </div>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg">
              <p className="text-sm text-orange-600 font-medium">คำแนะนำ</p>
              <p className="text-sm font-bold text-orange-700">{analysis?.recommendation || 'กำลังโหลด...'}</p>
            </div>
            {mlForecast?.success && (
              <div className="bg-purple-50 p-3 rounded-lg">
                <p className="text-sm text-purple-600 font-medium">การพยากรณ์</p>
                <p className="text-sm font-bold text-purple-700">
                  {mlForecast.forecast?.length || 0} วันข้างหน้า
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="w-full h-96">
          {isForecastLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-500 border-t-transparent mx-auto mb-4"></div>
                <p className="text-gray-600 font-medium text-lg">กำลังโหลดข้อมูลจาก ML Model...</p>
                <p className="text-gray-500 text-sm mt-2">โปรดรอสักครู่</p>
              </div>
            </div>
          ) : forecastError ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-red-500 text-6xl mb-4">⚠️</div>
                <p className="text-red-600 font-semibold text-lg">ไม่สามารถโหลดข้อมูลการพยากรณ์ได้</p>
                <p className="text-gray-600 text-sm mt-2">กรุณาลองใหม่อีกครั้งหรือเลือกพืช/จังหวัดอื่น</p>
              </div>
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-gray-400 text-6xl mb-4">📊</div>
                <p className="text-gray-700 font-semibold text-lg">ไม่พบข้อมูลสำหรับการแสดงผล</p>
                <p className="text-gray-500 text-sm mt-2">กรุณาเลือกจังหวัดและพืชที่ต้องการ</p>
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" strokeWidth={1} opacity={0.5} />
                <XAxis
                  dataKey="date"
                  angle={timeFrame <= 7 ? 0 : -45}
                  textAnchor={timeFrame <= 7 ? "middle" : "end"}
                  height={timeFrame <= 7 ? 70 : 90}
                  tick={{ fontSize: 13, fill: '#374151', fontWeight: 500 }}
                  interval={timeFrame <= 7 ? 0 : 'preserveStartEnd'}
                  stroke="#9ca3af"
                  strokeWidth={1}
                />
                <YAxis
                  domain={yAxisDomain}
                  label={{ 
                    value: 'ราคา (บาท/กก.)', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fontSize: 14, fill: '#374151', fontWeight: 600 }
                  }}
                  tick={{ fontSize: 13, fill: '#374151', fontWeight: 500 }}
                  stroke="#9ca3af"
                  strokeWidth={1}
                  tickFormatter={(value) => `${value.toFixed(0)} บาท`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  verticalAlign="top"
                  height={50}
                  iconType="line"
                  wrapperStyle={{
                    paddingBottom: '20px',
                    fontSize: '14px',
                    fontWeight: 600
                  }}
                  formatter={(value: string) => (
                    <span style={{ color: '#374151' }}>{value}</span>
                  )}
                />
                {/* Confidence Interval Area (behind the lines) */}
                <Area
                  type="natural"
                  dataKey="confidenceUpper"
                  stroke="none"
                  fill="#fef3c7"
                  fillOpacity={0.3}
                  connectNulls={true}
                />
                <Area
                  type="natural"
                  dataKey="confidenceLower"
                  stroke="none"
                  fill="#fef3c7"
                  fillOpacity={0.3}
                  connectNulls={true}
                />
                {/* Historical Price Line */}
                <Line
                  type="natural"
                  dataKey="historicalPrice"
                  stroke="#2563eb"
                  strokeWidth={3}
                  name="📊 ราคาในอดีต"
                  dot={false}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                  connectNulls={true}
                />
                {/* Predicted Price Line */}
                <Line
                  type="natural"
                  dataKey="predictedPrice"
                  stroke="#f97316"
                  strokeWidth={3}
                  strokeDasharray="8 4"
                  name="🔮 ราคาพยากรณ์ (ML)"
                  dot={false}
                  activeDot={{ r: 6, strokeWidth: 2 }}
                  connectNulls={true}
                />
                {/* Confidence Interval Boundaries */}
                <Line
                  type="natural"
                  dataKey="confidenceUpper"
                  stroke="#fbbf24"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  name="📈 ช่วงความเชื่อมั่น (บน)"
                  dot={false}
                  connectNulls={true}
                  opacity={0.5}
                />
                <Line
                  type="natural"
                  dataKey="confidenceLower"
                  stroke="#fbbf24"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  name="📉 ช่วงความเชื่อมั่น (ล่าง)"
                  dot={false}
                  connectNulls={true}
                  opacity={0.5}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

      </CardContent>
    </Card>
  );
};

export default RealForecastChart;

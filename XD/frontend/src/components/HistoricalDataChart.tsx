import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ChevronDown, TrendingUp, TrendingDown, Droplets, Thermometer, DollarSign, Calendar, Filter } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend, Area, AreaChart, ComposedChart } from 'recharts';
import { useForecastProvinces, useForecastCrops, usePriceHistory } from '@/hooks/useForecastData';

interface HistoricalDataChartProps {
  province?: string;
  selectedPlant: string;
  onPlantChange: (plant: string) => void;
  dataType: 'price' | 'temperature' | 'rainfall';
  onDataTypeChange: (type: 'price' | 'temperature' | 'rainfall') => void;
}

const HistoricalDataChart: React.FC<HistoricalDataChartProps> = ({ 
  province, 
  selectedPlant, 
  onPlantChange,
  dataType,
  onDataTypeChange 
}) => {
  const [timeRange, setTimeRange] = useState<'1m' | '3m' | '6m' | '1y'>('6m');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area'>('line');
  const [selectedProvince, setSelectedProvince] = useState<string>(province || '');
  
  // Fetch provinces and crops from database
  const { data: provincesData } = useForecastProvinces();
  const { data: cropsData } = useForecastCrops(selectedProvince);
  
  // Calculate days based on time range
  // Use 9999 for '1y' to get all available data
  const timeRangeMap = {
    '1m': 30,
    '3m': 90,
    '6m': 180,
    '1y': 9999  // Get all available data
  };
  const days = timeRangeMap[timeRange];
  
  // Fetch data from database
  // For price: need both province and crop_type
  // For temperature/rainfall: only need province (crop_type is ignored)
  const cropTypeParam = dataType === 'price' ? selectedPlant : '';
  const { data: priceHistory, isLoading } = usePriceHistory(selectedProvince, cropTypeParam, days);


  const chartData = useMemo(() => {
    if (!priceHistory?.history) return [];

    // Map data based on selected dataType
    // Note: temperature and rainfall come from weather_data table (by province only)
    // price comes from crop_prices table (by province + crop_type)
    const historicalData = priceHistory.history
      .filter((item: any) => {
        // Filter out null values for the selected data type
        if (dataType === 'temperature') return item.temperature !== null && item.temperature !== undefined;
        if (dataType === 'rainfall') return item.rainfall !== null && item.rainfall !== undefined;
        return item.price !== null && item.price !== undefined;
      })
      .reverse()
      .map((item: any) => ({
        date: new Date(item.date).toLocaleDateString('th-TH', { month: 'short', day: 'numeric' }),
        price: item.price || 0,
        temperature: item.temperature !== null && item.temperature !== undefined ? item.temperature : 0,
        rainfall: item.rainfall !== null && item.rainfall !== undefined ? item.rainfall : 0,
        type: 'historical'
      }));

    return historicalData;
  }, [priceHistory, dataType]);

  const stats = useMemo(() => {
    if (chartData.length === 0) return { avg: 0, max: 0, min: 0, trend: 0 };

    const values = chartData
      .filter(d => d.type === 'historical')
      .map(d => d[dataType]);
    
    if (values.length === 0) return { avg: 0, max: 0, min: 0, trend: 0 };

    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    
    // Calculate trend (compare last value with average)
    const lastValue = values[values.length - 1];
    const trend = ((lastValue - avg) / avg) * 100;

    return { avg, max, min, trend };
  }, [chartData, dataType]);

  const dataTypeConfig = {
    price: {
      label: 'ราคา',
      unit: 'บาท/กก.',
      color: '#3b82f6',
      icon: DollarSign,
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    temperature: {
      label: 'อุณหภูมิ',
      unit: '°C',
      color: '#f59e0b',
      icon: Thermometer,
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600'
    },
    rainfall: {
      label: 'ปริมาณฝน',
      unit: 'มม.',
      color: '#06b6d4',
      icon: Droplets,
      bgColor: 'bg-cyan-50',
      textColor: 'text-cyan-600'
    }
  };

  const config = dataTypeConfig[dataType];
  const Icon = config.icon;

  // Helper function to format Y-axis based on data type
  const getYAxisFormatter = (dataType: 'price' | 'temperature' | 'rainfall') => {
    switch (dataType) {
      case 'price':
        return (value: number) => `${value.toFixed(0)} บาท`;
      case 'temperature':
        return (value: number) => `${value.toFixed(0)}°C`;
      case 'rainfall':
        return (value: number) => `${value.toFixed(0)} มม.`;
      default:
        return (value: number) => value.toFixed(0);
    }
  };

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    const dataKey = dataType;

    switch (chartType) {
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={getYAxisFormatter(dataType)} />
            <Tooltip />
            <Legend />
            <Bar dataKey={dataKey} fill={config.color} name={`${config.label} (${config.unit})`} />
          </BarChart>
        );
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={getYAxisFormatter(dataType)} />
            <Tooltip />
            <Legend />
            <Area 
              type="natural" 
              dataKey={dataKey} 
              stroke={config.color} 
              strokeWidth={3}
              fill={config.color}
              fillOpacity={0.2}
              name={`${config.label} (${config.unit})`}
              dot={false}
              activeDot={{ r: 6, strokeWidth: 2, stroke: '#fff' }}
              connectNulls={true}
            />
          </AreaChart>
        );
      default:
        return (
          <ComposedChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis tickFormatter={getYAxisFormatter(dataType)} />
            <Tooltip />
            <Legend />
            <Line 
              type="natural" 
              dataKey={dataKey} 
              stroke={config.color} 
              strokeWidth={3}
              name={`${config.label} (${config.unit})`}
              dot={false}
              activeDot={{ r: 6, strokeWidth: 2, stroke: '#fff' }}
              connectNulls={true}
            />
          </ComposedChart>
        );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Icon className={`w-6 h-6 ${config.textColor}`} />
            <span>ข้อมูล{config.label}ในอดีต</span>
            {selectedProvince !== 'ทั้งหมด' && <span className="text-sm text-gray-500">- {selectedProvince}</span>}
          </div>
          <div className="flex gap-2 flex-wrap">
            {/* Province Selector */}
            <div className="relative">
              <select 
                value={selectedProvince}
                onChange={(e) => setSelectedProvince(e.target.value)}
                className="appearance-none bg-blue-500 text-white px-4 py-2 pr-8 rounded-lg text-sm font-medium cursor-pointer hover:bg-blue-600 transition-colors"
              >
                <option value="">เลือกจังหวัด</option>
                {provincesData?.provinces.map((prov) => (
                  <option key={prov} value={prov} className="bg-white text-gray-800">
                    {prov}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white pointer-events-none" />
            </div>
            
            {/* Plant Selector - Only show when dataType is 'price' */}
            {dataType === 'price' && (
              <div className="relative">
                <select 
                  value={selectedPlant}
                  onChange={(e) => onPlantChange(e.target.value)}
                  className="appearance-none bg-green-500 text-white px-4 py-2 pr-8 rounded-lg text-sm font-medium cursor-pointer hover:bg-green-600 transition-colors"
                >
                  <option value="">เลือกพืช</option>
                  {cropsData?.crops.map((crop) => (
                    <option key={crop.crop_type} value={crop.crop_type} className="bg-white text-gray-800">
                      {crop.crop_type} ({crop.crop_category})
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white pointer-events-none" />
              </div>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="mb-6 space-y-4">
          {/* Data Type Selector */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => onDataTypeChange('price')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                dataType === 'price' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <DollarSign className="w-4 h-4 inline mr-1" />
              ราคา
            </button>
            <button
              onClick={() => onDataTypeChange('temperature')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                dataType === 'temperature' 
                  ? 'bg-orange-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Thermometer className="w-4 h-4 inline mr-1" />
              อุณหภูมิ
            </button>
            <button
              onClick={() => onDataTypeChange('rainfall')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                dataType === 'rainfall' 
                  ? 'bg-cyan-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Droplets className="w-4 h-4 inline mr-1" />
              ปริมาณฝน
            </button>
          </div>

          {/* Time Range and Chart Type */}
          <div className="flex gap-2 flex-wrap items-center">
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              {(['1m', '3m', '6m', '1y'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    timeRange === range 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {range === '1m' ? '1 เดือน' : range === '3m' ? '3 เดือน' : range === '6m' ? '6 เดือน' : '1 ปี'}
                </button>
              ))}
            </div>

            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              {(['line', 'bar', 'area'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setChartType(type)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    chartType === type 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {type === 'line' ? 'เส้น' : type === 'bar' ? 'แท่ง' : 'พื้นที่'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className={`${config.bgColor} p-3 rounded-lg`}>
            <p className={`text-sm ${config.textColor} font-medium`}>ค่าเฉลี่ย</p>
            <p className={`text-lg font-bold ${config.textColor}`}>
              {stats.avg.toFixed(2)} {config.unit}
            </p>
          </div>
          <div className={`${config.bgColor} p-3 rounded-lg`}>
            <p className={`text-sm ${config.textColor} font-medium`}>สูงสุด</p>
            <p className={`text-lg font-bold ${config.textColor}`}>
              {stats.max.toFixed(2)} {config.unit}
            </p>
          </div>
          <div className={`${config.bgColor} p-3 rounded-lg`}>
            <p className={`text-sm ${config.textColor} font-medium`}>ต่ำสุด</p>
            <p className={`text-lg font-bold ${config.textColor}`}>
              {stats.min.toFixed(2)} {config.unit}
            </p>
          </div>
          <div className={`${stats.trend >= 0 ? 'bg-green-50' : 'bg-red-50'} p-3 rounded-lg`}>
            <p className={`text-sm font-medium ${stats.trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              แนวโน้ม
            </p>
            <div className="flex items-center gap-2">
              {stats.trend >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-600" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-600" />
              )}
              <p className={`text-lg font-bold ${stats.trend >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {stats.trend > 0 ? '+' : ''}{stats.trend.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* Chart */}
        {isLoading ? (
          <div className="w-full h-96 flex items-center justify-center">
            <div className="text-gray-500">กำลังโหลดข้อมูล...</div>
          </div>
        ) : chartData.length === 0 ? (
          <div className="w-full h-96 flex items-center justify-center">
            <div className="text-gray-500">ไม่มีข้อมูล</div>
          </div>
        ) : (
          <div className="w-full h-96">
            <ResponsiveContainer width="100%" height="100%">
              {renderChart()}
            </ResponsiveContainer>
          </div>
        )}

        {/* Data Summary */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold mb-2 flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            สรุปข้อมูล
          </h4>
          <div className="space-y-2 text-sm">
            <p>• จำนวนข้อมูล: {chartData.filter(d => d.type === 'historical').length} จุดข้อมูล</p>
            <p>• ช่วงเวลา: {timeRange === '1m' ? '1 เดือน' : timeRange === '3m' ? '3 เดือน' : timeRange === '6m' ? '6 เดือน' : '1 ปี'}</p>
            <p>• ประเภทข้อมูล: {config.label} ({config.unit})</p>
            <p className="text-gray-500 text-xs mt-2">
              ข้อมูลจากฐานข้อมูลการพยากรณ์ที่บันทึกไว้ในระบบ
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default HistoricalDataChart;

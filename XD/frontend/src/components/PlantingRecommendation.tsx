import React, { useState, useEffect, FormEvent } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { usePlantingRecommendation } from '@/hooks/usePlantingRecommendation';
import { Calendar, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Info, Sparkles, BarChart3, Clock, DollarSign } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, ReferenceLine, Area, AreaChart, Bar, BarChart, Legend } from 'recharts';
import { SiPytorch } from 'react-icons/si';
import { GiBrain, GiArtificialIntelligence } from 'react-icons/gi';
import { MdAutoGraph, MdShowChart, MdTimeline } from 'react-icons/md';
import { BsGraphUpArrow, BsRobot } from 'react-icons/bs';
import { IoSparkles } from 'react-icons/io5';

interface PlantingRecommendationProps {
  defaultProvince?: string;
  defaultCrop?: string;
}

const PlantingRecommendation = ({
  defaultProvince = '',
  defaultCrop = ''
}: PlantingRecommendationProps) => {
  const [province, setProvince] = useState(defaultProvince);
  const [cropType, setCropType] = useState(defaultCrop);
  const [growthDays, setGrowthDays] = useState<number>(0);
  const [crops, setCrops] = useState<any[]>([]);
  const [provinces, setProvinces] = useState<any[]>([]);
  const [timeframe, setTimeframe] = useState<'3M' | '6M' | '1Y' | 'ALL'>('6M');
  const [metaLoading, setMetaLoading] = useState(true);

  const { mutate, data, isPending, error } = usePlantingRecommendation();

  // Debug: Log response data
  React.useEffect(() => {
    if (data) {
      console.log('📊 ML Model Response:', {
        success: data.success,
        hasRecommendations: !!data.recommendations,
        recommendationsCount: data.recommendations?.length || 0,
        hasMLScenarios: !!data.ml_scenarios,
        mlScenariosCount: data.ml_scenarios?.length || 0,
        modelUsed: data.model_info?.model_used || 'unknown',
        sampleRecommendation: data.recommendations?.[0],
        priceAnalysis: data.price_analysis,
        combinedTimelineCount: data.combined_timeline?.length || 0,
        monthlyTrendCount: data.monthly_price_trend?.length || 0,
        allRecommendations: data.recommendations?.map((r: any) => ({
          planting_date: r.planting_date,
          harvest_date: r.harvest_date,
          predicted_price: r.predicted_price,
          confidence: r.confidence
        }))
      });
    }
  }, [data]);

  React.useEffect(() => {
    const fetchWithLogging = async (url: string, name: string) => {
      try {
        const response = await fetch(url);
        const contentType = response.headers.get('content-type') || '';
        const isJson = contentType.includes('application/json');

        console.log(`[${name} Response]`, {
          url,
          status: response.status,
          statusText: response.statusText,
          contentType,
          isJson
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`[${name} Error]`, {
            status: response.status,
            statusText: response.statusText,
            body: errorText
          });
          throw new Error(`${name} request failed with status ${response.status}: ${response.statusText}`);
        }

        if (!isJson) {
          const text = await response.text();
          console.error(`[${name} Error] Expected JSON but got:`, text.substring(0, 200));
          throw new Error(`Expected JSON response but got ${contentType}`);
        }

        return response.json();
      } catch (error) {
        console.error(`[${name} Fetch Error]`, error);
        throw error;
      }
    };

    const fetchData = async () => {
      setMetaLoading(true);
      try {
        const [cropsData, provincesData] = await Promise.all([
          fetchWithLogging('/api/v2/forecast/crops', 'Crops'),
          fetchWithLogging('/api/v2/forecast/provinces', 'Provinces')
        ]);

        setCrops(Array.isArray(cropsData?.crops) ? cropsData.crops : []);
        setProvinces(Array.isArray(provincesData?.provinces) ? provincesData.provinces : []);
      } catch (error) {
        console.error('Error in fetchData:', error);
        setCrops([]);
        setProvinces([]);
      } finally {
        setMetaLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (cropType && province && growthDays) {
      mutate({ crop_type: cropType, province, growth_days: growthDays });
    }
  };

  // Update form when props change
  useEffect(() => {
    if (defaultProvince) setProvince(defaultProvince);
    if (defaultCrop) setCropType(defaultCrop);
  }, [defaultProvince, defaultCrop]);

  const getRecommendationColor = (level: string) => {
    switch (level) {
      case 'excellent':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'good':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'moderate':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'poor':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getRecommendationIcon = (level: string) => {
    switch (level) {
      case 'excellent':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'good':
        return <TrendingUp className="h-5 w-5 text-blue-600" />;
      case 'moderate':
        return <Info className="h-5 w-5 text-yellow-600" />;
      case 'poor':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  const handleCropSelect = async (selectedCrop: string) => {
    const crop = crops.find(c => c.crop_type === selectedCrop || c.name === selectedCrop);
    if (crop) {
      setCropType(crop.crop_type || crop.name);
      setGrowthDays(crop.growth_days);
      
      // ✅ FIXED: Fetch provinces for this specific crop
      try {
        const response = await fetch(`/api/v2/planting-schedule/provinces?crop_type=${encodeURIComponent(crop.crop_type || crop.name)}`);
        if (response.ok) {
          const data = await response.json();
          if (data.success && Array.isArray(data.provinces)) {
            setProvinces(data.provinces);
            console.log(`✅ Loaded ${data.provinces.length} provinces for crop: ${crop.crop_type || crop.name}`);
            
            // Reset province if current selection is not in the new list
            if (province && !data.provinces.includes(province)) {
              setProvince('');
              console.log(`⚠️ Reset province selection - not available for this crop`);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching provinces for crop:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      <Card className="border-2  shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3 text-xl">
              <div className="p-2 bg-primary/10 rounded-lg">
                <GiBrain className="h-6 w-6 text-primary" />
              </div>
              คำแนะนำช่วงเวลาเพาะปลูกที่เหมาะสม
            </CardTitle>
            <Badge variant="secondary" className="gap-1.5 px-3 py-1">
              <BsRobot className="h-3.5 w-3.5" />
              AI-Powered
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-2 flex items-center gap-2">
            <IoSparkles className="h-4 w-4 text-yellow-500" />
             วิเคราะห์สถานการณ์จริงเพื่อหาช่วงเวลาที่ขายได้ราคาดีที่สุด
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="crop">ชื่อพืช</Label>
                <select
                  id="crop"
                  value={cropType}
                  onChange={(e) => handleCropSelect(e.target.value)}
                  required
                  className="w-full rounded border p-2"
                >
                  <option value="">เลือกพืช</option>
                  {crops.map((c) => (
                    <option key={c.crop_type || c.name} value={c.crop_type || c.name}>
                      {(c.crop_type || c.name) + (c.growth_days ? ` (${c.growth_days} วัน)` : '')}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="province">จังหวัด</Label>
                <select
                  id="province"
                  value={province}
                  onChange={(e) => setProvince(e.target.value)}
                  required
                  className="w-full rounded border p-2"
                >
                  <option value="">เลือกจังหวัด</option>
                  {provinces.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="growthDays">ระยะเวลาเจริญเติบโต (วัน)</Label>
                <Input
                  id="growthDays"
                  type="number"
                  value={growthDays}
                  readOnly
                  disabled
                  placeholder="ระบบเติมอัตโนมัติเมื่อเลือกพืช"
                />
              </div>
            </div>

            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? 'กำลังวิเคราะห์...' : 'วิเคราะห์ช่วงเวลาที่เหมาะสม'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            เกิดข้อผิดพลาดจาก ML Model: {error.message}
            <br />
            <span className="text-xs mt-1 block">
              กรุณาตรวจสอบว่า ML Model (planting_calendar_modelUpdate.pkl) ทำงานอยู่หรือไม่
            </span>
          </AlertDescription>
        </Alert>
      )}
      {/* Results Display - Only Real ML Model Data */}
      {data && data.success && data.recommendations && data.recommendations.length > 0 && (
        <div className="space-y-6">
          

          {/* Detailed Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">✅ ช่วงเวลาที่แนะนำ</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">เดือนที่ควรเพาะปลูก:</p>
                  <p className="text-lg font-semibold text-green-600">
                    {data.recommendation.optimal_planting_month}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    เพื่อเก็บเกี่ยวใน {data.recommendation.best_harvest_month} (ราคาสูงสุด {data.price_analysis.best_price} ฿/กก.)
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">⚠️ ช่วงเวลาที่ควรหลีกเลี่ยง</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">เดือนที่ไม่ควรเพาะปลูก:</p>
                  <p className="text-lg font-semibold text-red-600">
                    {data.recommendation.warning_planting_month}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    จะเก็บเกี่ยวใน {data.recommendation.worst_harvest_month} (ราคาต่ำสุด {data.price_analysis.worst_price} ฿/กก.)
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Price Analysis Tabs */}
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <MdShowChart className="h-5 w-5 text-primary" />
                  การวิเคราะห์ราคาจาก ML Model
                </CardTitle>
                <Badge variant="outline" className="gap-1">
                  <SiPytorch className="h-3 w-3" />
                  Predicted Data
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="timeline" className="w-full">
                <TabsList className="grid w-full grid-cols-5">
                  <TabsTrigger value="timeline" className="gap-2">
                    <MdTimeline className="h-4 w-4" />
                    Timeline
                  </TabsTrigger>
                  <TabsTrigger value="trend" className="gap-2">
                    <MdShowChart className="h-4 w-4" />
                    แนวโน้มราคา
                  </TabsTrigger>
                  <TabsTrigger value="comparison" className="gap-2">
                    <BarChart3 className="h-4 w-4" />
                    เปรียบเทียบเดือน
                  </TabsTrigger>
                  <TabsTrigger value="detail" className="gap-2">
                    <BsGraphUpArrow className="h-4 w-4" />
                    รายละเอียด
                  </TabsTrigger>
                  <TabsTrigger value="scenarios" className="gap-2">
                    <MdAutoGraph className="h-4 w-4" />
                    ทุก Scenarios
                  </TabsTrigger>
                </TabsList>

                {/* Timeline Tab - Historical + ML Forecast */}
                <TabsContent value="timeline" className="space-y-4">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-blue-800 dark:text-blue-200 flex items-center gap-2">
                        <GiBrain className="h-3 w-3" />
                        <span className="font-semibold">Timeline Chart:</span> แสดงทั้งข้อมูลจริงจาก Database และราคาที่ ML ทำนาย
                      </p>

                      {/* Timeframe Selector */}
                      <div className="flex gap-1">
                        {(['3M', '6M', '1Y', 'ALL'] as const).map((tf) => (
                          <button
                            key={tf}
                            onClick={() => setTimeframe(tf)}
                            className={`px-3 py-1 text-xs font-medium rounded transition-colors ${timeframe === tf
                              ? 'bg-blue-600 text-white'
                              : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700'
                              }`}
                            title={
                              tf === '3M' ? 'แสดง 3 เดือนย้อนหลัง + 3 เดือนข้างหน้า' :
                              tf === '6M' ? 'แสดง 6 เดือนย้อนหลัง + 6 เดือนข้างหน้า' :
                              tf === '1Y' ? 'แสดง 1 ปีย้อนหลัง + 1 ปีข้างหน้า' :
                              'แสดงข้อมูลทั้งหมด'
                            }
                          >
                            {tf}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-4 text-xs mt-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-0.5 bg-green-500" style={{ borderTop: '3px solid #22c55e' }}></div>
                        <span className="text-green-700 dark:text-green-300 font-semibold">เส้นเขียวทึบ = ข้อมูลจริงจาก Database</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-0.5 border-t-2 border-dashed border-purple-600"></div>
                        <span className="text-purple-800 dark:text-purple-200 font-semibold">เส้นม่วงประ = ML ทำนายอนาคต</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-0.5 bg-red-500 border-t-2 border-dashed"></div>
                        <span className="text-red-600 dark:text-red-400 font-semibold">เส้นแดงประ = วันนี้</span>
                      </div>
                    </div>
                  </div>

                  {data.recommendations && data.recommendations.length > 0 ? (
                    <>
                      {/* Show warning if no historical data */}
                      {data.combined_timeline && 
                       data.combined_timeline.filter((d: any) => d.type === 'historical').length === 0 && (
                        <Alert className="mb-4">
                          <Info className="h-4 w-4" />
                          <AlertDescription>
                            ⚠️ ไม่มีข้อมูลจริงจาก Database สำหรับ {cropType} ในจังหวัด {province} - แสดงเฉพาะการทำนายจาก ML Model
                          </AlertDescription>
                        </Alert>
                      )}
                      
                      <div className="h-80 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={(() => {
                          // ✅ Use combined_timeline from backend (includes historical + forecast)
                          let timelineData: any[] = [];
                          
                          if (data.combined_timeline && data.combined_timeline.length > 0) {
                            timelineData = data.combined_timeline;
                          } else {
                            // Fallback: Generate from recommendations
                            data.recommendations.forEach((rec: any) => {
                              const price = rec.predicted_price || rec.price;
                              if (price && price > 0) {
                                timelineData.push({
                                  date: rec.harvest_date,
                                  average_price: price,
                                  type: "ml_forecast",
                                  label: "ML Prediction"
                                });
                              }
                            });
                          }

                          // Sort by date
                          const sortedData = timelineData
                            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

                          // Filter based on timeframe
                          const now = new Date();
                          let startDate = new Date();
                          let endDate = new Date();

                          if (timeframe === '3M') {
                            startDate.setMonth(now.getMonth() - 3);
                            endDate.setMonth(now.getMonth() + 3);
                          } else if (timeframe === '6M') {
                            startDate.setMonth(now.getMonth() - 6);
                            endDate.setMonth(now.getMonth() + 6);
                          } else if (timeframe === '1Y') {
                            startDate.setFullYear(now.getFullYear() - 1);
                            endDate.setFullYear(now.getFullYear() + 1);
                          } else {
                            startDate.setFullYear(now.getFullYear() - 10);
                            endDate.setFullYear(now.getFullYear() + 10);
                          }

                          const filteredData = sortedData.filter((item: any) => {
                            const itemDate = new Date(item.date);
                            return itemDate >= startDate && itemDate <= endDate;
                          });

                          const historicalData = filteredData.filter((d: any) => d.type === 'historical');
                          const forecastData = filteredData.filter((d: any) => d.type === 'ml_forecast');
                          
                          console.log('📊 Timeline data breakdown:', {
                            total: filteredData.length,
                            historical: historicalData.length,
                            forecast: forecastData.length,
                            historicalSample: historicalData.slice(0, 3),
                            forecastSample: forecastData.slice(0, 3),
                            allTypes: [...new Set(filteredData.map((d: any) => d.type))]
                          });

                          return filteredData;
                        })()}>
                          <defs>
                            <linearGradient id="historicalGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05} />
                            </linearGradient>
                            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.05} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                          <XAxis
                            dataKey="date"
                            tick={{ fontSize: 10 }}
                            angle={-45}
                            textAnchor="end"
                            height={80}
                          />
                          <YAxis
                            tick={{ fontSize: 11 }}
                            label={{ value: 'ราคา (฿/กก.)', angle: -90, position: 'insideLeft', fontSize: 11 }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'hsl(var(--background))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '8px',
                              padding: '12px'
                            }}
                            formatter={(value: any, name: string, props: any) => {
                              const type = props.payload.type;
                              const isHistorical = type === 'historical';
                              const label = isHistorical ? '📊 ราคาจริง (Database)' : '🤖 ML ทำนาย';
                              const source = isHistorical ? 'ข้อมูลจริงจากฐานข้อมูล' : 'ทำนายโดย ML Model';
                              return [
                                <div key="price" className="space-y-1">
                                  <div className="font-semibold">{label}</div>
                                  <div className="text-lg font-bold">{value} ฿/กก.</div>
                                  <div className="text-xs text-muted-foreground">{source}</div>
                                </div>
                              ];
                            }}
                            labelFormatter={(label: string) => {
                              const date = new Date(label);
                              return date.toLocaleDateString('th-TH', { 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric' 
                              });
                            }}
                          />
                          <Legend 
                            wrapperStyle={{ paddingTop: '20px' }}
                            formatter={(value: string, entry: any) => {
                              if (value === 'ราคาจริง (Database)') {
                                return <span className="text-green-700 font-semibold">📊 ราคาจริง (Database)</span>;
                              }
                              if (value === 'ML ทำนาย') {
                                return <span className="text-purple-700 font-semibold">🤖 ML ทำนาย</span>;
                              }
                              return value;
                            }}
                          />
                          
                          {/* Reference line for today */}
                          <ReferenceLine
                            x={new Date().toISOString().split('T')[0]}
                            stroke="#ef4444"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            label={{ 
                              value: '← อดีต | วันนี้ | อนาคต →', 
                              position: 'top',
                              fontSize: 12,
                              fill: '#ef4444',
                              fontWeight: 'bold'
                            }}
                          />

                          {/* Historical Data Line (Solid Green) - Only show historical points */}
                          <Line
                            dataKey={(item: any) => item.type === 'historical' ? item.average_price : null}
                            stroke="#22c55e"
                            strokeWidth={3}
                            dot={(props: any) => {
                              const { cx, cy, payload } = props;
                              if (payload.type !== 'historical') return null;
                              return (
                                <circle
                                  cx={cx}
                                  cy={cy}
                                  r={6}
                                  fill="#22c55e"
                                  stroke="#fff"
                                  strokeWidth={2}
                                />
                              );
                            }}
                            name="ราคาจริง (Database)"
                            connectNulls={true}
                          />

                          {/* ML Forecast Line (Dashed Purple) - Only show forecast points */}
                          <Line
                            dataKey={(item: any) => item.type === 'ml_forecast' ? item.average_price : null}
                            stroke="#a855f7"
                            strokeWidth={3}
                            strokeDasharray="8 4"
                            dot={(props: any) => {
                              const { cx, cy, payload } = props;
                              if (payload.type !== 'ml_forecast') return null;
                              return (
                                <circle
                                  cx={cx}
                                  cy={cy}
                                  r={6}
                                  fill="#a855f7"
                                  stroke="#fff"
                                  strokeWidth={2}
                                />
                              );
                            }}
                            name="ML ทำนาย"
                            connectNulls={true}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    </>
                  ) : (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        ไม่มีข้อมูล timeline จาก ML Model สำหรับ {cropType} ในจังหวัด {province}
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Summary Cards - Show when we have ML recommendations */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="p-2 bg-green-600 rounded-lg">
                            <Calendar className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-xs font-medium">ML Scenarios</span>
                        </div>
                        <p className="text-2xl font-bold text-green-600">
                          {data.recommendations?.length || 0}
                        </p>
                        <p className="text-xs text-muted-foreground">จาก ML Model</p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="p-2 bg-purple-600 rounded-lg">
                            <GiBrain className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-xs font-medium">Price Range</span>
                        </div>
                        <p className="text-lg font-bold text-purple-600">
                          {data.price_analysis?.worst_price || 0} - {data.price_analysis?.best_price || 0}
                        </p>
                        <p className="text-xs text-muted-foreground">฿/กก. (ML Predicted)</p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="p-2 bg-blue-600 rounded-lg">
                            <MdTimeline className="h-4 w-4 text-white" />
                          </div>
                          <span className="text-xs font-medium">Date Range</span>
                        </div>
                        <p className="text-sm font-bold text-blue-600">
                          {(() => {
                            if (!data.recommendations || data.recommendations.length === 0) return 'N/A';
                            const dates = data.recommendations.map((r: any) => new Date(r.planting_date));
                            const minDate = new Date(Math.min(...dates.map(d => d.getTime())));
                            const maxDate = new Date(Math.max(...dates.map(d => d.getTime())));
                            return `${minDate.toLocaleDateString('th-TH', { month: 'short' })} - ${maxDate.toLocaleDateString('th-TH', { month: 'short' })}`;
                          })()}
                        </p>
                        <p className="text-xs text-muted-foreground">ช่วงเวลาปลูก</p>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                {/* Trend Tab */}
                <TabsContent value="trend" className="space-y-4">
                  <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                    <p className="text-xs text-blue-800 dark:text-blue-200 flex items-center gap-2">
                      <Info className="h-3 w-3" />
                      กราฟนี้แสดงราคาเฉลี่ยที่ ML Model ทำนายจาก {data.recommendations?.length || 0} scenarios จริง
                      • คำนวณจากข้อมูล recommendations ที่ ML predict เท่านั้น
                    </p>
                  </div>
                  {data.recommendations && data.recommendations.length > 0 ? (
                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={(() => {
                          // Generate monthly trend from actual ML recommendations only
                          const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
                          const monthlyData: { [key: string]: { total: number; count: number; month: string } } = {};

                          // Group recommendations by harvest month
                          data.recommendations.forEach((rec: any) => {
                            const harvestDate = new Date(rec.harvest_date);
                            const monthIndex = harvestDate.getMonth();
                            const monthKey = thaiMonths[monthIndex];
                            const price = rec.predicted_price || rec.price;

                            if (price && price > 0) {
                              if (!monthlyData[monthKey]) {
                                monthlyData[monthKey] = { total: 0, count: 0, month: monthKey };
                              }
                              monthlyData[monthKey].total += price;
                              monthlyData[monthKey].count += 1;
                            }
                          });

                          // Calculate average for each month and sort by Thai calendar
                          const result = thaiMonths
                            .map(month => {
                              if (monthlyData[month] && monthlyData[month].count > 0) {
                                return {
                                  month,
                                  average_price: Math.round(monthlyData[month].total / monthlyData[month].count * 10) / 10,
                                  scenarios_count: monthlyData[month].count
                                };
                              }
                              return null;
                            })
                            .filter(item => item !== null);

                          console.log('📊 Monthly trend data:', result);
                          return result;
                        })()}>
                          <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                          <XAxis
                            dataKey="month"
                            tick={{ fontSize: 11 }}
                            stroke="hsl(var(--muted-foreground))"
                          />
                          <YAxis
                            tick={{ fontSize: 11 }}
                            stroke="hsl(var(--muted-foreground))"
                            label={{ value: 'ราคาที่ ML ทำนาย (฿/กก.)', angle: -90, position: 'insideLeft', fontSize: 11 }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'hsl(var(--background))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '8px'
                            }}
                            formatter={(value: any) => [`${value} ฿/กก.`, 'ML Predicted Price']}
                          />
                          <ReferenceLine
                            y={data.price_analysis.average_price}
                            stroke="hsl(var(--muted-foreground))"
                            strokeDasharray="5 5"
                            label={{ value: `เฉลี่ย: ${data.price_analysis.average_price} ฿`, fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                          />
                          <ReferenceLine
                            y={data.price_analysis.best_price}
                            stroke="#22c55e"
                            strokeDasharray="5 5"
                            label={{ value: `สูงสุด: ${data.price_analysis.best_price} ฿`, fontSize: 11, fill: '#22c55e' }}
                          />
                          <ReferenceLine
                            y={data.price_analysis.worst_price}
                            stroke="#ef4444"
                            strokeDasharray="5 5"
                            label={{ value: `ต่ำสุด: ${data.price_analysis.worst_price} ฿`, fontSize: 11, fill: '#ef4444' }}
                          />
                          <Area
                            type="monotone"
                            dataKey="average_price"
                            stroke="hsl(var(--primary))"
                            strokeWidth={3}
                            fill="url(#colorPrice)"
                            name="ราคาที่ ML ทำนาย"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        ไม่มีข้อมูลแนวโน้มราคาจาก ML Model สำหรับ {cropType} ในจังหวัด {province}
                      </AlertDescription>
                    </Alert>
                  )}
                </TabsContent>

                {/* Comparison Tab */}
                <TabsContent value="comparison" className="space-y-4">
                  <div className="p-3 bg-purple-50 dark:bg-purple-950 rounded-lg">
                    <p className="text-xs text-purple-800 dark:text-purple-200 flex items-center gap-2">
                      <BarChart3 className="h-3 w-3" />
                      เปรียบเทียบราคาที่ ML ทำนายแต่ละเดือน (เรียงจากสูงไปต่ำ) • คำนวณจาก ML recommendations เท่านั้น
                    </p>
                  </div>
                  {data.recommendations && data.recommendations.length > 0 ? (
                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={(() => {
                          // Generate monthly comparison from actual ML recommendations only
                          const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
                          const monthlyData: { [key: string]: { total: number; count: number; month: string } } = {};

                          // Group recommendations by harvest month
                          data.recommendations.forEach((rec: any) => {
                            const harvestDate = new Date(rec.harvest_date);
                            const monthIndex = harvestDate.getMonth();
                            const monthKey = thaiMonths[monthIndex];
                            const price = rec.predicted_price || rec.price;

                            if (price && price > 0) {
                              if (!monthlyData[monthKey]) {
                                monthlyData[monthKey] = { total: 0, count: 0, month: monthKey };
                              }
                              monthlyData[monthKey].total += price;
                              monthlyData[monthKey].count += 1;
                            }
                          });

                          // Calculate average and sort by price (high to low)
                          const result = Object.values(monthlyData)
                            .filter(data => data.count > 0)
                            .map(data => ({
                              month: data.month,
                              average_price: Math.round(data.total / data.count * 10) / 10,
                              scenarios_count: data.count
                            }))
                            .sort((a, b) => b.average_price - a.average_price);

                          console.log('📊 Monthly comparison data:', result);
                          return result;
                        })()}>
                          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                          <XAxis
                            dataKey="month"
                            tick={{ fontSize: 10 }}
                            angle={-45}
                            textAnchor="end"
                            height={80}
                          />
                          <YAxis
                            tick={{ fontSize: 11 }}
                            label={{ value: 'ML Predicted Price (฿/กก.)', angle: -90, position: 'insideLeft', fontSize: 11 }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'hsl(var(--background))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '8px'
                            }}
                            formatter={(value: any) => [`${value} ฿/กก.`, 'Predicted Price']}
                          />
                          <Bar
                            dataKey="average_price"
                            fill="hsl(var(--primary))"
                            radius={[8, 8, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        ไม่มีข้อมูลเปรียบเทียบราคาจาก ML Model สำหรับ {cropType} ในจังหวัด {province}
                      </AlertDescription>
                    </Alert>
                  )}
                </TabsContent>

                {/* Detail Tab */}
                <TabsContent value="detail" className="space-y-4">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                    <p className="text-xs text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
                      <BsGraphUpArrow className="h-3 w-3" />
                      แต่ละการ์ดแสดงราคาเฉลี่ยที่ ML ทำนายจาก ML recommendations เท่านั้น • จำนวน scenarios ในแต่ละเดือนแสดงจำนวนจริงจาก ML Model
                    </p>
                  </div>
                  {data.recommendations && data.recommendations.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {(() => {
                        // Generate monthly data from actual ML recommendations only
                        const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
                        const monthlyData: { [key: string]: { total: number; count: number; month: string; prices: number[] } } = {};

                        // Group recommendations by harvest month
                        data.recommendations.forEach((rec: any) => {
                          const harvestDate = new Date(rec.harvest_date);
                          const monthIndex = harvestDate.getMonth();
                          const monthKey = thaiMonths[monthIndex];
                          const price = rec.predicted_price || rec.price;

                          if (price && price > 0) {
                            if (!monthlyData[monthKey]) {
                              monthlyData[monthKey] = { total: 0, count: 0, month: monthKey, prices: [] };
                            }
                            monthlyData[monthKey].total += price;
                            monthlyData[monthKey].count += 1;
                            monthlyData[monthKey].prices.push(price);
                          }
                        });

                        // Calculate average price from all valid recommendations
                        const allPrices = data.recommendations
                          .map((r: any) => r.predicted_price || r.price)
                          .filter((price: number) => price && price > 0);
                        const avgPrice = allPrices.length > 0 ? allPrices.reduce((a: number, b: number) => a + b, 0) / allPrices.length : 0;
                        const maxPrice = allPrices.length > 0 ? Math.max(...allPrices) : 0;
                        const minPrice = allPrices.length > 0 ? Math.min(...allPrices) : 0;

                        const result = Object.values(monthlyData)
                          .filter((item: any) => item.count > 0)
                          .map((item: any) => {
                            const average_price = Math.round(item.total / item.count * 10) / 10;
                            const isPeak = maxPrice > 0 && Math.abs(average_price - maxPrice) < 0.1;
                            const isLow = minPrice > 0 && Math.abs(average_price - minPrice) < 0.1;
                            const diffPercent = avgPrice > 0 ? ((average_price - avgPrice) / avgPrice * 100).toFixed(1) : '0.0';

                            return { ...item, average_price, isPeak, isLow, diffPercent };
                          });

                        console.log('📊 Monthly detail data:', result);
                        return result.map((item: any) => {
                          return (
                            <Card
                              key={item.month}
                              className={`${item.isPeak ? 'border-2 border-green-500 bg-green-50 dark:bg-green-950' :
                                item.isLow ? 'border-2 border-red-500 bg-red-50 dark:bg-red-950' : ''
                                }`}
                            >
                              <CardContent className="pt-4">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center gap-2">
                                    <span className="font-semibold text-sm">{item.month}</span>
                                    <Badge variant="outline" className="text-xs">
                                      {item.count} scenarios
                                    </Badge>
                                  </div>
                                  {item.isPeak && <Badge className="bg-green-600">ราคาดีที่สุด</Badge>}
                                  {item.isLow && <Badge variant="destructive">ราคาต่ำสุด</Badge>}
                                </div>
                                <div className="space-y-2">
                                  <div className="flex items-baseline gap-2">
                                    <DollarSign className="h-4 w-4 text-primary" />
                                    <span className="text-2xl font-bold">{item.average_price}</span>
                                    <span className="text-sm text-muted-foreground">฿/กก.</span>
                                  </div>
                                  <div className="flex items-center gap-2 text-xs">
                                    {Number(item.diffPercent) >= 0 ? (
                                      <TrendingUp className="h-3 w-3 text-green-600" />
                                    ) : (
                                      <TrendingDown className="h-3 w-3 text-red-600" />
                                    )}
                                    <span className={Number(item.diffPercent) >= 0 ? 'text-green-600' : 'text-red-600'}>
                                      {item.diffPercent}% from avg
                                    </span>
                                  </div>
                                  {item.prices && item.prices.length > 0 && (
                                    <div className="text-xs text-muted-foreground pt-2 border-t">
                                      <div className="flex justify-between">
                                        <span>ต่ำสุด: {Math.min(...item.prices).toFixed(1)} ฿</span>
                                        <span>สูงสุด: {Math.max(...item.prices).toFixed(1)} ฿</span>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          );
                        });
                      })()}
                    </div>
                  ) : (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        ไม่มีข้อมูลรายละเอียดจาก ML Model สำหรับ {cropType} ในจังหวัด {province}
                      </AlertDescription>
                    </Alert>
                  )}
                </TabsContent>

                {/* ML Scenarios Tab - แสดงรายละเอียดทุก scenario */}
                <TabsContent value="scenarios" className="space-y-4">
                  <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                    <p className="text-xs text-green-800 dark:text-green-200 flex items-center gap-2">
                      <GiBrain className="h-3 w-3" />
                      ตารางนี้แสดงรายละเอียดทุก scenario ที่ ML Model วิเคราะห์จริง • เรียงตามราคาที่ ML ทำนายได้ (สูง → ต่ำ)
                    </p>
                  </div>

                  {(() => {
                    // Use ml_scenarios if available, otherwise transform recommendations (only real ML data)
                    const thaiMonths = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                      "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"];

                    let scenarios = data.ml_scenarios;

                    // If no ml_scenarios, transform recommendations but only if they exist and have valid data
                    if (!scenarios && data.recommendations && data.recommendations.length > 0) {
                      scenarios = data.recommendations
                        .filter((rec: any) => rec.predicted_price || rec.price) // Only include items with valid prices
                        .map((rec: any, idx: number) => {
                          const harvestDate = new Date(rec.harvest_date);
                          return {
                            scenario_num: idx + 1,
                            planting_date: rec.planting_date,
                            harvest_date: rec.harvest_date,
                            harvest_month: thaiMonths[harvestDate.getMonth()],
                            ml_predicted_price: rec.predicted_price || rec.price,
                            confidence: rec.confidence || 0.8
                          };
                        })
                        .sort((a: any, b: any) => b.ml_predicted_price - a.ml_predicted_price); // Sort by price descending
                    }

                    console.log('📊 ML Scenarios data:', scenarios);

                    if (!scenarios || scenarios.length === 0) {
                      return (
                        <Alert>
                          <Info className="h-4 w-4" />
                          <AlertDescription>
                            ไม่มีข้อมูล ML scenarios สำหรับ {cropType} ในจังหวัด {province} - ML Model ไม่สามารถทำนายได้
                          </AlertDescription>
                        </Alert>
                      );
                    }

                    return (
                      <div className="border rounded-lg overflow-hidden">
                        <div className="max-h-96 overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-green-700 text-white sticky top-0">
                              <tr>
                                <th className="px-3 py-2 text-left font-semibold">#</th>
                                <th className="px-3 py-2 text-left font-semibold">วันปลูก</th>
                                <th className="px-3 py-2 text-left font-semibold">วันเก็บเกี่ยว</th>
                                <th className="px-3 py-2 text-left font-semibold">เดือนเก็บเกี่ยว</th>
                                <th className="px-3 py-2 text-right font-semibold">ราคาที่ ML ทำนาย</th>
                                <th className="px-3 py-2 text-center font-semibold">Confidence</th>
                              </tr>
                            </thead>
                            <tbody>
                              {scenarios.map((scenario: any, idx: number) => {
                                const isTop3 = idx < 3;
                                const isBottom3 = idx >= scenarios.length - 3;

                                return (
                                  <tr
                                    key={scenario.scenario_num}
                                    className={`border-t ${isTop3 ? 'bg-green-50 dark:bg-green-950' :
                                      isBottom3 ? 'bg-red-50 dark:bg-red-950' :
                                        'hover:bg-gray-50 dark:hover:bg-gray-900'
                                      }`}
                                  >
                                    <td className="px-3 py-2">
                                      {isTop3 && <span className="inline-block w-6 h-6 rounded-full bg-green-600 text-white text-xs flex items-center justify-center">{idx + 1}</span>}
                                      {isBottom3 && <span className="inline-block w-6 h-6 rounded-full bg-red-600 text-white text-xs flex items-center justify-center">{idx + 1}</span>}
                                      {!isTop3 && !isBottom3 && <span className="text-muted-foreground">{idx + 1}</span>}
                                    </td>
                                    <td className="px-3 py-2 font-mono text-xs">{scenario.planting_date}</td>
                                    <td className="px-3 py-2 font-mono text-xs">{scenario.harvest_date}</td>
                                    <td className="px-3 py-2">
                                      <Badge variant="outline" className="text-xs">
                                        {scenario.harvest_month}
                                      </Badge>
                                    </td>
                                    <td className="px-3 py-2 text-right">
                                      <span className={`font-bold ${isTop3 ? 'text-green-600' :
                                        isBottom3 ? 'text-red-600' : ''
                                        }`}>
                                        {scenario.ml_predicted_price} ฿
                                      </span>
                                    </td>
                                    <td className="px-3 py-2 text-center">
                                      <Badge variant="secondary" className="text-xs">
                                        {Math.round(scenario.confidence * 100)}%
                                      </Badge>
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Summary Stats for ML Scenarios - Only Real Data */}
                  {data.recommendations && data.recommendations.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <Card>
                        <CardContent className="pt-4 pb-3">
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">ML Scenarios</p>
                            <p className="text-2xl font-bold text-primary">{data.total_scenarios_analyzed || data.ml_scenarios?.length || data.recommendations?.length || 0}</p>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-4 pb-3">
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">เดือนที่วิเคราะห์</p>
                            <p className="text-2xl font-bold text-blue-600">
                              {(() => {
                                const uniqueMonths = new Set();
                                data.recommendations?.forEach((rec: any) => {
                                  const harvestDate = new Date(rec.harvest_date);
                                  uniqueMonths.add(harvestDate.getMonth());
                                });
                                return uniqueMonths.size;
                              })()}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-4 pb-3">
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">ช่วงราคา ML</p>
                            <p className="text-sm font-bold text-green-600">{data.price_analysis?.best_price || 0} ฿</p>
                            <p className="text-xs text-muted-foreground">→</p>
                            <p className="text-sm font-bold text-red-600">{data.price_analysis?.worst_price || 0} ฿</p>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="pt-4 pb-3">
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground mb-1">ผลต่างราคา</p>
                            <p className="text-2xl font-bold text-purple-600">
                              {(() => {
                                const best = data.price_analysis?.best_price || 0;
                                const worst = data.price_analysis?.worst_price || 0;
                                if (worst > 0) {
                                  return ((best - worst) / worst * 100).toFixed(0);
                                }
                                return '0';
                              })()}%
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </TabsContent>
              </Tabs>

              {/* Price Summary - Only Real ML Data */}
              {data.price_analysis && (data.price_analysis.best_price > 0 || data.price_analysis.worst_price > 0) && (
                <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">ML ราคาสูงสุด</p>
                    <p className="text-lg font-semibold text-green-600">
                      {data.price_analysis.best_price || 0} ฿
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">ML ราคาเฉลี่ย</p>
                    <p className="text-lg font-semibold">
                      {data.price_analysis.average_price || 0} ฿
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">ML ราคาต่ำสุด</p>
                    <p className="text-lg font-semibold text-red-600">
                      {data.price_analysis.worst_price || 0} ฿
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>


        </div>
      )}

      {/* No data message - Only show when ML model has no results */}
      {data && (!data.success || !data.recommendations || data.recommendations.length === 0) && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {data.message || `ไม่มีข้อมูลจาก ML Model สำหรับ ${cropType} ในจังหวัด ${province} - โปรดลองเลือกพืชหรือจังหวัดอื่น`}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default PlantingRecommendation;

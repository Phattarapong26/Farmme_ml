import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import ProvinceSelector from '@/components/dashboard/ProvinceSelector';
import SimplifiedStatsCard from '@/components/dashboard/SimplifiedStatsCard';
import ChartCategoryTabs, { ChartCategory } from '@/components/dashboard/ChartCategoryTabs';
import RechartsContainer from '@/components/dashboard/RechartsContainer';
import TimeSeriesLineChart from '@/components/dashboard/charts/TimeSeriesLineChart';
import MultiLineChart from '@/components/dashboard/charts/MultiLineChart';
import AreaChartComponent from '@/components/dashboard/charts/AreaChartComponent';
import BarChartComponent from '@/components/dashboard/charts/BarChartComponent';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/hooks/useAuth';
import {
  DollarSign,
  Users,
  Thermometer,
  TrendingUp,
  PieChart,
  BarChart3,
  CloudRain,
  Activity,
  Leaf,
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface DashboardData {
  success: boolean;
  province: string;
  statistics: {
    avg_price: number;
    total_crop_types: number;
    most_profitable_crop: string;
    most_profitable_profit: number;
    current_temp: number;
    current_rainfall: number;
    total_population?: number;
    working_age_population?: number;
    agricultural_population?: number;
    total_farmers?: number;
    avg_farm_size?: number;
  };
  price_history: any[];
  weather_data: any[];
  crop_distribution: any[];
  profitability: any[];
  farmer_skills: any[];
  economic_timeline: any[];
  soil_analysis: any[];
  roi_details: any[];
  // NEW: Actionable insights
  seasonal_recommendations: any[];
  price_volatility: any[];
  planting_window: any[];
  market_trends: any[];
  market_potential: any;
  cached: boolean;
  timestamp: string;
}

const DashboardOverview: React.FC = () => {
  const { user } = useAuth();
  const [selectedProvince, setSelectedProvince] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<ChartCategory>('overview');

  // Fetch provinces list
  const { data: provincesData } = useQuery({
    queryKey: ['dashboard-provinces'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/dashboard/provinces`);
      if (!response.ok) throw new Error('Failed to fetch provinces');
      return response.json();
    },
  });

  const provinces = provincesData?.provinces || [];

  // Auto-select user's province when component mounts
  useEffect(() => {
    // Only auto-select if:
    // 1. User has a province
    // 2. Province exists in the provinces list
    // 3. No province is currently selected (to avoid overriding manual selection)
    if (user?.province && provinces.length > 0 && !selectedProvince) {
      if (provinces.includes(user.province)) {
        setSelectedProvince(user.province);
      }
    }
  }, [user, provinces, selectedProvince]);

  // Fetch dashboard data (all data, no time range limit)
  const { data: dashboardData, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard-overview', selectedProvince],
    queryFn: async () => {
      if (!selectedProvince) return null;
      // Use 365 days to get all available data
      const response = await fetch(
        `${API_BASE}/api/dashboard/overview?province=${encodeURIComponent(selectedProvince)}&days_back=365`
      );
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      
      // Debug: Log new data fields
      console.log('Dashboard Data:', {
        seasonal_recommendations: data.seasonal_recommendations,
        price_volatility: data.price_volatility,
        planting_window: data.planting_window,
        market_trends: data.market_trends,
      });
      
      return data;
    },
    enabled: !!selectedProvince,
  });

  const stats = dashboardData?.statistics;

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Province Selector */}
        <div className="mb-8">
          <ProvinceSelector
            selectedProvince={selectedProvince}
            onProvinceChange={setSelectedProvince}
            provinces={provinces}
          />
        </div>

        {!selectedProvince ? (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="text-center">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-2xl font-bold text-gray-700 mb-2">เลือกจังหวัดเพื่อดูข้อมูล</h2>
              <p className="text-gray-500">กรุณาเลือกจังหวัดจากด้านบนเพื่อแสดงภาพรวมข้อมูลเกษตรกรรม</p>
            </div>
          </div>
        ) : isLoading ? (
          <div className="space-y-6">
            {/* Stats Cards Skeleton */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-white shadow-md rounded-lg p-6">
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-8 w-24 mb-2" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
            {/* Charts Skeleton */}
            <Skeleton className="h-12 w-full rounded-lg" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-[350px] w-full rounded-lg" />
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-red-600 mb-2">เกิดข้อผิดพลาด</h2>
              <p className="text-gray-500">ไม่สามารถโหลดข้อมูลได้ กรุณาลองใหม่อีกครั้ง</p>
            </div>
          </div>
        ) : stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Statistics Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
              {[
                {
                  title: 'ราคาเฉลี่ย',
                  value: stats.avg_price,
                  unit: 'บาท/กก.',
                  icon: <DollarSign className="w-6 h-6" />,
                  trend: { direction: 'up' as const, value: 5.2 },
                  decimalPlaces: 2,
                },
                {
                  title: 'ประชากรทั้งหมด',
                  value: stats.total_population ? (stats.total_population / 1000).toFixed(0) : 0,
                  unit: 'K คน',
                  icon: <Users className="w-6 h-6" />,
                },
                {
                  title: 'จำนวนพืช',
                  value: stats.total_crop_types,
                  unit: 'ชนิด',
                  icon: <Leaf className="w-6 h-6" />,
                },
                {
                  title: 'พืชกำไรสูงสุด',
                  value: stats.most_profitable_profit,
                  unit: 'บาท/กก.',
                  icon: <TrendingUp className="w-6 h-6" />,
                  trend: { direction: 'up' as const, value: 12.3 },
                  decimalPlaces: 2,
                },
                {
                  title: 'อุณหภูมิปัจจุบัน',
                  value: stats.current_temp,
                  unit: '°C',
                  icon: <Thermometer className="w-6 h-6" />,
                  decimalPlaces: 1,
                },
              ].map((stat, index) => (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <SimplifiedStatsCard {...stat} />
                </motion.div>
              ))}
            </div>

           

            {/* Chart Category Tabs */}
            <div className="mb-6">
              <ChartCategoryTabs activeCategory={activeCategory} onCategoryChange={setActiveCategory} />
            </div>

            {/* Charts Grid */}
            <motion.div
              key={activeCategory}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {activeCategory === 'overview' && (
                <>
                  <RechartsContainer
                    title="💡 พืชแนะนำตามฤดูกาล"
                    description="พืชที่เหมาะสมกับฤดูกาลปัจจุบัน"
                    icon={<Leaf className="w-5 h-5" />}
                  >
                    {dashboardData?.seasonal_recommendations && dashboardData.seasonal_recommendations.length > 0 ? (
                      <BarChartComponent
                        data={dashboardData.seasonal_recommendations}
                        dataKey="avg_price"
                        xAxisKey="crop_type"
                        yAxisLabel="ราคาเฉลี่ย (บาท/กก.)"
                        color="#10b981"
                        angleLabels
                      />
                    ) : (
                      <div className="flex items-center justify-center h-[250px] text-gray-500">
                        <p>ไม่มีข้อมูลพืชแนะนำสำหรับจังหวัดนี้</p>
                      </div>
                    )}
                  </RechartsContainer>

                  <RechartsContainer
                    title="📊 ความผันผวนของราคา"
                    description="ความเสี่ยงด้านราคาของแต่ละพืช"
                    icon={<Activity className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.price_volatility || []}
                      dataKey="volatility"
                      xAxisKey="crop_type"
                      yAxisLabel="ความผันผวน (บาท)"
                      color="#ef4444"
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="📈 แนวโน้มความต้องการตลาด"
                    description={` วันที่ผ่านมา`}
                    icon={<TrendingUp className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.market_trends || []}
                      dataKey="change_percent"
                      xAxisKey="crop_type"
                      yAxisLabel="การเปลี่ยนแปลง (%)"
                      colors={dashboardData?.market_trends?.map((t: any) => 
                        t.change_percent > 0 ? '#10b981' : '#ef4444'
                      )}
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="🌱 ช่วงเวลาปลูกที่ดีที่สุด"
                    description="วิเคราะห์จากรูปแบบราคา"
                    icon={<Leaf className="w-5 h-5" />}
                  >
                    {dashboardData?.planting_window && dashboardData.planting_window.length > 0 ? (
                      <BarChartComponent
                        data={dashboardData.planting_window}
                        dataKey="avg_yield"
                        xAxisKey="month"
                        yAxisLabel="ดัชนีราคา"
                        color="#3b82f6"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-[250px] text-gray-500">
                        <p>ไม่มีข้อมูลช่วงเวลาปลูกสำหรับจังหวัดนี้</p>
                      </div>
                    )}
                  </RechartsContainer>

                  <RechartsContainer
                    title="💰 พืชที่ให้ผลกำไรสูงสุด"
                    description="Top 10 พืชเรียงตามกำไร"
                    icon={<TrendingUp className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.profitability?.slice(0, 10) || []}
                      dataKey="avg_profit"
                      xAxisKey="crop_type"
                      yAxisLabel="กำไร (บาท)"
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="🌤️ สภาพอากาศ"
                    description="ค่าเฉลี่ยรายเดือน"
                    icon={<CloudRain className="w-5 h-5" />}
                  >
                    <MultiLineChart
                      data={dashboardData?.weather_data || []}
                      series={[
                        { key: 'temperature', name: 'อุณหภูมิ (°C)', color: '#f59e0b', yAxisId: 'left' },
                        { key: 'rainfall', name: 'ปริมาณฝน (มม.)', color: '#3b82f6', yAxisId: 'right' },
                      ]}
                      leftYAxisLabel="อุณหภูมิ (°C)"
                      rightYAxisLabel="ฝน (มม.)"
                    />
                  </RechartsContainer>
                </>
              )}

              {activeCategory === 'price' && (
                <>
                  <RechartsContainer
                    title="📈 แนวโน้มราคาพืช"
                    description={` วันที่ผ่านมา`}
                    icon={<BarChart3 className="w-5 h-5" />}
                  >
                    <TimeSeriesLineChart
                      data={dashboardData?.price_history || []}
                      dataKeys={['price']}
                      colors={['#10b981']}
                      yAxisLabel="ราคา (บาท/กก.)"
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="⚠️ ความเสี่ยงด้านราคา"
                    description="ความผันผวนของราคาแต่ละพืช"
                    icon={<Activity className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.price_volatility || []}
                      dataKey="volatility"
                      xAxisKey="crop_type"
                      yAxisLabel="ความผันผวน (บาท)"
                      colors={dashboardData?.price_volatility?.map((v: any) => 
                        v.risk_level === 'สูง' ? '#ef4444' : '#10b981'
                      )}
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="💰 พืชที่ให้กำไรสูงสุด"
                    description="Top 10 พืช"
                    icon={<TrendingUp className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.profitability?.slice(0, 10) || []}
                      dataKey="avg_profit"
                      xAxisKey="crop_type"
                      yAxisLabel="กำไรเฉลี่ย (บาท)"
                      color="#10b981"
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="📊 การวิเคราะห์ ROI"
                    description="ผลตอบแทนจากการลงทุน"
                    icon={<DollarSign className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.roi_details?.slice(0, 10) || []}
                      dataKey="roi"
                      xAxisKey="crop_type"
                      yAxisLabel="ROI (%)"
                      color="#8b5cf6"
                      angleLabels
                    />
                  </RechartsContainer>
                </>
              )}

              {activeCategory === 'weather' && (
                <>
                  <RechartsContainer
                    title="แนวโน้มอุณหภูมิ"
                    description="ค่าเฉลี่ยรายเดือน"
                    icon={<Thermometer className="w-5 h-5" />}
                  >
                    <TimeSeriesLineChart
                      data={dashboardData?.weather_data || []}
                      dataKeys={['temperature']}
                      colors={['#f59e0b']}
                      yAxisLabel="อุณหภูมิ (°C)"
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="ปริมาณฝน"
                    description="ค่าเฉลี่ยรายเดือน"
                    icon={<CloudRain className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.weather_data || []}
                      dataKey="rainfall"
                      xAxisKey="date"
                      yAxisLabel="ปริมาณฝน (มม.)"
                      color="#3b82f6"
                    />
                  </RechartsContainer>
                </>
              )}

              {activeCategory === 'economic' && (
                <>
                  <RechartsContainer
                    title="🏙️ ศักยภาพตลาด"
                    description="วิเคราะห์จากข้อมูลประชากร"
                    icon={<Users className="w-5 h-5" />}
                  >
                    {dashboardData?.market_potential && dashboardData.market_potential.total_population > 0 ? (
                      <div className="p-6 space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 mb-1">ประชากรทั้งหมด</p>
                            <p className="text-2xl font-bold text-blue-700">
                              {(dashboardData.market_potential.total_population / 1000).toFixed(0)}K
                            </p>
                          </div>
                          <div className="bg-green-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 mb-1">ผู้บริโภคศักยภาพ</p>
                            <p className="text-2xl font-bold text-green-700">
                              {(dashboardData.market_potential.potential_consumers / 1000).toFixed(0)}K
                            </p>
                          </div>
                          <div className="bg-purple-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 mb-1">ขนาดตลาด</p>
                            <p className="text-2xl font-bold text-purple-700">
                              {dashboardData.market_potential.market_size}
                            </p>
                          </div>
                          <div className="bg-orange-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 mb-1">สัดส่วนเกษตรกร</p>
                            <p className="text-2xl font-bold text-orange-700">
                              {dashboardData.market_potential.agricultural_ratio}%
                            </p>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <p className="text-sm text-gray-700">
                            💡 {dashboardData.market_potential.market_description}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-[250px] text-gray-500">
                        <p>ไม่มีข้อมูลประชากรสำหรับจังหวัดนี้</p>
                      </div>
                    )}
                  </RechartsContainer>

                  <RechartsContainer
                    title="📈 แนวโน้มความต้องการตลาด"
                    description={` วันที่ผ่านมา`}
                    icon={<TrendingUp className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.market_trends || []}
                      dataKey="change_percent"
                      xAxisKey="crop_type"
                      yAxisLabel="การเปลี่ยนแปลง (%)"
                      colors={dashboardData?.market_trends?.map((t: any) => 
                        t.change_percent > 0 ? '#10b981' : '#ef4444'
                      )}
                      angleLabels
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="⛽ ราคาน้ำมัน"
                    description="ค่าเฉลี่ยรายเดือน"
                    icon={<Activity className="w-5 h-5" />}
                  >
                    <TimeSeriesLineChart
                      data={dashboardData?.economic_timeline || []}
                      dataKeys={['fuel_price']}
                      colors={['#8b5cf6']}
                      yAxisLabel="ราคา (บาท)"
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="🌾 ราคาปุ๋ย"
                    description="ค่าเฉลี่ยรายเดือน"
                    icon={<Activity className="w-5 h-5" />}
                  >
                    <TimeSeriesLineChart
                      data={dashboardData?.economic_timeline || []}
                      dataKeys={['fertilizer_price']}
                      colors={['#10b981']}
                      yAxisLabel="ราคา (บาท)"
                    />
                  </RechartsContainer>
                </>
              )}

              {activeCategory === 'farming' && (
                <>
                  <RechartsContainer
                    title="การกระจายขนาดฟาร์ม"
                    description="จำนวนเกษตรกร"
                    icon={<Users className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.farmer_skills || []}
                      dataKey="count"
                      xAxisKey="farm_size"
                      yAxisLabel="จำนวน"
                    />
                  </RechartsContainer>

                  <RechartsContainer
                    title="สัดส่วนพืช"
                    description="ตามหมวดหมู่"
                    icon={<Leaf className="w-5 h-5" />}
                  >
                    <BarChartComponent
                      data={dashboardData?.crop_distribution || []}
                      dataKey="count"
                      xAxisKey="crop_type"
                      yAxisLabel="จำนวน"
                      angleLabels
                    />
                  </RechartsContainer>
                </>
              )}
            </motion.div>

            {/* Cache Info */}
            {dashboardData?.cached && (
              <div className="mt-6 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-full text-sm text-emerald-700">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  ⚡ ข้อมูลจาก Cache - โหลดเร็วขึ้น!
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default DashboardOverview;



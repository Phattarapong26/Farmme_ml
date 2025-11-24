import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import { usePriceHistory } from '@/hooks/useForecastData';

interface ProvinceDataPanelProps {
  provinceName: string;
}

const ProvinceDataPanel: React.FC<ProvinceDataPanelProps> = ({ provinceName }) => {
  const [priceData, setPriceData] = useState<any[]>([]);
  const [cultivationData, setCultivationData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [forecast, setForecast] = useState<any | null>(null);
  const [selectedCrop, setSelectedCrop] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // ดึงข้อมูลราคาล่าสุดจาก API
        const pricesResponse = await fetch(
          `http://localhost:8000/api/v2/historical-data?province=${encodeURIComponent(provinceName)}&limit=50`
        );
        
        if (pricesResponse.ok) {
          const pricesData = await pricesResponse.json();
          setPriceData(pricesData.data || []);
          
          // หาพืชที่มีข้อมูลมากที่สุด
          if (pricesData.data && pricesData.data.length > 0) {
            const cropCounts = pricesData.data.reduce((acc: any, item: any) => {
              acc[item.crop_type] = (acc[item.crop_type] || 0) + 1;
              return acc;
            }, {});
            
            const mostCommonCrop = Object.entries(cropCounts)
              .sort(([,a]: any, [,b]: any) => b - a)[0][0] as string;
            
            setSelectedCrop(mostCommonCrop);
            
            // สร้าง forecast จากข้อมูลจริง
            const cropPrices = pricesData.data
              .filter((item: any) => item.crop_type === mostCommonCrop)
              .map((item: any) => item.price_per_kg);
            
            if (cropPrices.length > 0) {
              const avgPrice = cropPrices.reduce((a: number, b: number) => a + b, 0) / cropPrices.length;
              const recentPrices = cropPrices.slice(0, 5);
              const olderPrices = cropPrices.slice(-5);
              const recentAvg = recentPrices.reduce((a: number, b: number) => a + b, 0) / recentPrices.length;
              const olderAvg = olderPrices.reduce((a: number, b: number) => a + b, 0) / olderPrices.length;
              const trend = recentAvg > olderAvg ? 'เพิ่มขึ้น' : 'ลดลง';
              
              setForecast({
                trend,
                recommendation: trend === 'เพิ่มขึ้น' 
                  ? `ราคา${mostCommonCrop}มีแนวโน้มดี ควรพิจารณาปลูก` 
                  : `ราคา${mostCommonCrop}อาจลดลง ควรติดตามสถานการณ์`,
                avgPrice: avgPrice.toFixed(2)
              });
            }
          }
        }

        // ดึงข้อมูลการเพาะปลูก (ถ้ามี API)
        // TODO: สร้าง API endpoint สำหรับ cultivation data
        setCultivationData([]);
        
      } catch (error) {
        console.error('Error fetching province data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (provinceName) {
      fetchData();
    }
  }, [provinceName]);

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="w-6 h-6 animate-spin text-green-500" />
        </CardContent>
      </Card>
    );
  }

  const avgPrice = priceData.length > 0
    ? (priceData.reduce((sum, p) => sum + Number(p.price_per_kg), 0) / priceData.length).toFixed(2)
    : '0';

  const totalArea = cultivationData.length > 0
    ? cultivationData.reduce((sum, c) => sum + Number(c.planting_area_rai), 0).toFixed(2)
    : '0';

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">ข้อมูลจังหวัด{provinceName}</CardTitle>
          <CardDescription>ข้อมูลราคาและการเพาะปลูกล่าสุด</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* ราคาเฉลี่ย */}
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-sm text-gray-600">ราคาเฉลี่ย (บาท/กก.)</div>
            <div className="text-3xl font-bold text-green-600">{avgPrice}</div>
            <div className="text-xs text-gray-500 mt-1">จาก {priceData.length} รายการ</div>
          </div>

          {/* พื้นที่เพาะปลูก */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600">พื้นที่เพาะปลูกรวม (ไร่)</div>
            <div className="text-3xl font-bold text-blue-600">{totalArea}</div>
            <div className="text-xs text-gray-500 mt-1">จาก {cultivationData.length} แปลง</div>
          </div>

          {/* พืชที่เด่น */}
          {priceData.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-semibold text-gray-700">พืชที่มีข้อมูลราคา</div>
              <div className="flex flex-wrap gap-2">
                {[...new Set(priceData.map(p => p.crop_type))].slice(0, 5).map((crop) => (
                  <span
                    key={crop}
                    className="px-3 py-1 bg-white border border-green-200 text-green-700 rounded-full text-xs"
                  >
                    {crop}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ML Forecast */}
          {forecast && (
            <div className="p-4 bg-purple-50 rounded-lg space-y-2">
              <div className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                🤖 การคาดการณ์ (ML)
                {forecast.trend === 'เพิ่มขึ้น' ? (
                  <TrendingUp className="w-4 h-4 text-green-600" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-600" />
                )}
              </div>
              <div className="text-xs text-gray-600">{forecast.recommendation}</div>
              <div className="text-xs text-purple-600 mt-1">
                แนวโน้ม: {forecast.trend}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProvinceDataPanel;

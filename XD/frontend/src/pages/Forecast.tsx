import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { TrendingUp, BarChart3 } from 'lucide-react';
import RealForecastChart from '@/components/RealForecastChart';
import HistoricalDataChart from '@/components/HistoricalDataChart';
import { useForecastProvinces, useForecastCrops } from '@/hooks/useForecastData';

const Forecast = () => {
  const { data: provincesData } = useForecastProvinces();
  const [selectedProvince, setSelectedProvince] = useState<string>('');
  const { data: cropsData } = useForecastCrops(selectedProvince);
  const [selectedPlant, setSelectedPlant] = useState<string>('');
  const [showHistoricalData, setShowHistoricalData] = useState(false);
  const [dataType, setDataType] = useState<'price' | 'temperature' | 'rainfall'>('price');

  // Set default province and crop when data loads
  useEffect(() => {
    if (provincesData?.provinces && provincesData.provinces.length > 0 && !selectedProvince) {
      setSelectedProvince(provincesData.provinces[0]);
    }
  }, [provincesData, selectedProvince]);

  useEffect(() => {
    if (cropsData?.crops && cropsData.crops.length > 0 && !selectedPlant) {
      setSelectedPlant(cropsData.crops[0].crop_type);
    }
  }, [cropsData, selectedPlant]);

  const handlePlantChange = (plant: string) => {
    setSelectedPlant(plant);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* MapNavbar is now added in App.tsx */}
      
      <div className="max-w-7xl mx-auto p-4 sm:p-6">

        {/* View Toggle Buttons */}
        <div className="flex gap-3 mb-8 justify-center flex-wrap">
          <Card 
            className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
              !showHistoricalData
                ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg' 
                : 'bg-white hover:bg-gray-50 shadow-md'
            }`}
            onClick={() => setShowHistoricalData(false)}
          >
            <CardContent className="p-4 sm:p-6 flex items-center gap-3">
              <TrendingUp className={`w-5 h-5 sm:w-6 sm:h-6 ${!showHistoricalData ? 'text-white' : 'text-green-600'}`} />
              <span className="text-lg sm:text-xl font-semibold">พยากรณ์ราคา</span>
            </CardContent>
          </Card>
          
          <Card 
            className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
              showHistoricalData
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg' 
                : 'bg-white hover:bg-gray-50 shadow-md'
            }`}
            onClick={() => setShowHistoricalData(true)}
          >
            <CardContent className="p-4 sm:p-6 flex items-center gap-3">
              <BarChart3 className={`w-5 h-5 sm:w-6 sm:h-6 ${showHistoricalData ? 'text-white' : 'text-blue-600'}`} />
              <span className="text-lg sm:text-xl font-semibold">ข้อมูลในอดีต</span>
            </CardContent>
          </Card>
        </div>

        {!showHistoricalData ? (
          <div className="space-y-6">
            {/* Main Forecast Chart - Full Width */}
            <RealForecastChart 
              province={selectedProvince || undefined}
              selectedPlant={selectedPlant}
              onPlantChange={handlePlantChange}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Historical Data View */}
            <HistoricalDataChart 
              province={selectedProvince || undefined}
              selectedPlant={selectedPlant}
              onPlantChange={handlePlantChange}
              dataType={dataType}
              onDataTypeChange={setDataType}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Forecast;
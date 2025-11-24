import React from 'react';
import { MapPin } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ProvinceSelectorProps {
  selectedProvince: string | null;
  onProvinceChange: (province: string) => void;
  provinces: string[];
}

const ProvinceSelector: React.FC<ProvinceSelectorProps> = ({
  selectedProvince,
  onProvinceChange,
  provinces
}) => {
  return (
    <div className="mb-8 flex justify-between">
      <div className="flex items-center gap-4 mb-4">
        <MapPin className="w-8 h-8 text-emerald-600" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Dashboard Overview
          </h1>
          <p className="text-gray-600">ภาพรวมข้อมูลเกษตรกรรมและเศรษฐกิจ</p>
        </div>
      </div>
      <div>
      <Select value={selectedProvince || ""} onValueChange={onProvinceChange}>
        <SelectTrigger className="w-full md:w-80 h-12 text-lg">
          <SelectValue placeholder="เลือกจังหวัด" />
        </SelectTrigger>
        <SelectContent>
          {provinces.map((province) => (
            <SelectItem key={province} value={province}>
              {province}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      </div>
    </div>
  );
};

export default ProvinceSelector;

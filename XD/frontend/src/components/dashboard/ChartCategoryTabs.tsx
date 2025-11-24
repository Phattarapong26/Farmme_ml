import React from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LayoutDashboard, TrendingUp, CloudRain, DollarSign, Tractor } from 'lucide-react';

export type ChartCategory = 'overview' | 'price' | 'weather' | 'economic' | 'farming';

interface ChartCategoryTabsProps {
  activeCategory: ChartCategory;
  onCategoryChange: (category: ChartCategory) => void;
}

const categories: { value: ChartCategory; label: string; icon: React.ReactNode }[] = [
  { value: 'overview', label: 'ภาพรวม', icon: <LayoutDashboard className="w-4 h-4" /> },
  { value: 'price', label: 'ราคา', icon: <TrendingUp className="w-4 h-4" /> },
  { value: 'weather', label: 'สภาพอากาศ', icon: <CloudRain className="w-4 h-4" /> },
  { value: 'economic', label: 'เศรษฐกิจ', icon: <DollarSign className="w-4 h-4" /> },
  { value: 'farming', label: 'การเกษตร', icon: <Tractor className="w-4 h-4" /> },
];

const ChartCategoryTabs: React.FC<ChartCategoryTabsProps> = ({
  activeCategory,
  onCategoryChange,
}) => {
  return (
    <Tabs value={activeCategory} onValueChange={(value) => onCategoryChange(value as ChartCategory)}>
      <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 bg-gray-100 p-1 rounded-lg h-auto gap-1">
        {categories.map((category) => (
          <TabsTrigger
            key={category.value}
            value={category.value}
            className="data-[state=active]:bg-white data-[state=active]:text-emerald-600 data-[state=active]:shadow-sm flex items-center gap-2 py-3 px-4 transition-all"
          >
            {category.icon}
            <span className="font-medium">{category.label}</span>
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
};

export default ChartCategoryTabs;

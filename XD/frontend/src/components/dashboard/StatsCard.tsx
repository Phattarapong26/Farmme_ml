import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { NumberTicker } from '@/components/ui/number-ticker';
import { ArrowUpRight, ArrowDownRight, Minus, LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  title: string;
  value: number;
  unit?: string;
  trend?: number;
  icon: LucideIcon;
  colorClass: string;
  decimalPlaces?: number;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  unit,
  trend,
  icon: Icon,
  colorClass,
  decimalPlaces = 0
}) => {
  const getTrendIcon = () => {
    if (!trend || trend === 0) return <Minus className="w-3 h-3" />;
    return trend > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />;
  };

  const getTrendColor = () => {
    if (!trend || trend === 0) return 'bg-gray-100 text-gray-700';
    return trend > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';
  };

  return (
    <Card className={cn(
      'bg-gradient-to-br border-none hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:scale-105 cursor-pointer group',
      colorClass
    )}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-xl bg-white/50 backdrop-blur-sm group-hover:bg-white group-hover:shadow-md transition-all duration-300">
            <Icon className="w-6 h-6 group-hover:scale-110 transition-transform duration-300" />
          </div>
          {trend !== undefined && (
            <div className={cn(
              'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
              getTrendColor()
            )}>
              {getTrendIcon()}
              {Math.abs(trend).toFixed(1)}%
            </div>
          )}
        </div>
        <p className="text-sm font-medium text-gray-600 mb-2">{title}</p>
        <div className="flex items-baseline gap-2">
          <NumberTicker 
            value={value} 
            className="text-3xl font-bold text-gray-900"
            decimalPlaces={decimalPlaces}
            format={(num) => num.toLocaleString('th-TH', {
              minimumFractionDigits: decimalPlaces,
              maximumFractionDigits: decimalPlaces
            })}
          />
          {unit && <span className="text-sm text-gray-500">{unit}</span>}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsCard;

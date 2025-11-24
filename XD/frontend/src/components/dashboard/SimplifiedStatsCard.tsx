import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface SimplifiedStatsCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: number;
  };
  icon: React.ReactNode;
  decimalPlaces?: number;
}

const SimplifiedStatsCard: React.FC<SimplifiedStatsCardProps> = ({
  title,
  value,
  unit,
  trend,
  icon,
  decimalPlaces,
}) => {
  // Format value if it's a number
  const formattedValue = typeof value === 'number' && decimalPlaces !== undefined
    ? value.toFixed(decimalPlaces)
    : value;

  return (
    <Card className="bg-white shadow-md hover:shadow-lg transition-shadow duration-300 h-full">
      <CardContent className="p-6 h-full flex flex-col">
        <div className="flex items-start justify-between flex-1">
          <div className="flex-1 flex flex-col">
            <p className="text-sm text-gray-500 mb-1 font-medium">{title}</p>
            <p className="text-3xl font-bold text-gray-900 flex-1 flex items-center">
              {formattedValue}
              {unit && <span className="text-lg text-gray-500 ml-1">{unit}</span>}
            </p>
            {trend && (
              <div
                className={`flex items-center gap-1 mt-2 text-sm font-medium ${
                  trend.direction === 'up'
                    ? 'text-green-600'
                    : trend.direction === 'down'
                    ? 'text-red-600'
                    : 'text-gray-600'
                }`}
              >
                {trend.direction === 'up' && <ArrowUp className="w-4 h-4" />}
                {trend.direction === 'down' && <ArrowDown className="w-4 h-4" />}
                {trend.direction === 'neutral' && <Minus className="w-4 h-4" />}
                <span>{Math.abs(trend.value).toFixed(1)}%</span>
              </div>
            )}
          </div>
          <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 ml-4">
            <div className="text-emerald-600">{icon}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SimplifiedStatsCard;

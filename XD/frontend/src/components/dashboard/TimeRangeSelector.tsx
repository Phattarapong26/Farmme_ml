import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar } from 'lucide-react';

export type TimeRange = '7d' | '30d' | '90d';

interface TimeRangeSelectorProps {
  selectedRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
}

const timeRangeOptions: { value: TimeRange; label: string; days: number }[] = [
  { value: '7d', label: '7 วัน', days: 7 },
  { value: '30d', label: '30 วัน', days: 30 },
  { value: '90d', label: '90 วัน', days: 90 },
];

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  selectedRange,
  onRangeChange,
}) => {
  return (
    <div className="flex gap-3 justify-center flex-wrap">
      {timeRangeOptions.map((option) => (
        <Card
          key={option.value}
          className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
            selectedRange === option.value
              ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg'
              : 'bg-white hover:bg-gray-50 shadow-md'
          }`}
          onClick={() => onRangeChange(option.value)}
        >
          <CardContent className="p-4 sm:p-6 flex items-center gap-2 sm:gap-3">
            <Calendar
              className={`w-5 h-5 sm:w-6 sm:h-6 ${
                selectedRange === option.value ? 'text-white' : 'text-emerald-600'
              }`}
            />
            <span className="text-lg sm:text-xl font-semibold">{option.label}</span>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default TimeRangeSelector;

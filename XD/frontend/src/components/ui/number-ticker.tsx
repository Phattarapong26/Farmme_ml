import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface NumberTickerProps {
  value: number;
  duration?: number;
  decimalPlaces?: number;
  className?: string;
  format?: (num: number) => string;
}

export const NumberTicker: React.FC<NumberTickerProps> = ({
  value,
  duration = 2000,
  decimalPlaces = 0,
  className,
  format
}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    const increment = end / (duration / 16);
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value, duration]);

  const displayValue = format 
    ? format(count) 
    : count.toFixed(decimalPlaces);

  return (
    <span className={cn('tabular-nums', className)}>
      {displayValue}
    </span>
  );
};

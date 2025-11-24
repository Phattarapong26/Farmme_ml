import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface AreaSeries {
  key: string;
  name: string;
  color: string;
}

interface AreaChartComponentProps {
  data: any[];
  series: AreaSeries[];
  xAxisKey?: string;
  yAxisLabel?: string;
  height?: number;
}

const AreaChartComponent: React.FC<AreaChartComponentProps> = ({
  data,
  series,
  xAxisKey = 'date',
  yAxisLabel,
  height = 300,
}) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          {series.map((s) => (
            <linearGradient key={`gradient-${s.key}`} id={`color-${s.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={s.color} stopOpacity={0.8} />
              <stop offset="95%" stopColor={s.color} stopOpacity={0.1} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => {
            if (typeof value === 'string' && value.includes('-')) {
              const date = new Date(value);
              return `${date.getDate()}/${date.getMonth() + 1}`;
            }
            return value;
          }}
        />
        <YAxis
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          label={
            yAxisLabel
              ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fontSize: 12 } }
              : undefined
          }
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '12px',
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        {series.map((s) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={s.color}
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#color-${s.key})`}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default AreaChartComponent;

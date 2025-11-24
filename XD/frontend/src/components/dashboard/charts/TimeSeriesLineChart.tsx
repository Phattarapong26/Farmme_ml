import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TimeSeriesLineChartProps {
  data: any[];
  dataKeys: string[];
  colors?: string[];
  xAxisKey?: string;
  yAxisLabel?: string;
  height?: number;
}

const defaultColors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];

const TimeSeriesLineChart: React.FC<TimeSeriesLineChartProps> = ({
  data,
  dataKeys,
  colors = defaultColors,
  xAxisKey = 'date',
  yAxisLabel,
  height = 300,
}) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => {
            // Format date if it's a date string
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
        {dataKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colors[index % colors.length]}
            strokeWidth={2}
            dot={{ fill: colors[index % colors.length], r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TimeSeriesLineChart;

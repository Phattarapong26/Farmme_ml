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

interface DataSeries {
  key: string;
  name: string;
  color: string;
  yAxisId?: 'left' | 'right';
}

interface MultiLineChartProps {
  data: any[];
  series: DataSeries[];
  xAxisKey?: string;
  leftYAxisLabel?: string;
  rightYAxisLabel?: string;
  height?: number;
}

const MultiLineChart: React.FC<MultiLineChartProps> = ({
  data,
  series,
  xAxisKey = 'date',
  leftYAxisLabel,
  rightYAxisLabel,
  height = 300,
}) => {
  const hasRightAxis = series.some((s) => s.yAxisId === 'right');

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: hasRightAxis ? 30 : 10, left: 20, bottom: 5 }}>
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
          yAxisId="left"
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          label={
            leftYAxisLabel
              ? { value: leftYAxisLabel, angle: -90, position: 'insideLeft', style: { fontSize: 12 } }
              : undefined
          }
        />
        {hasRightAxis && (
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={
              rightYAxisLabel
                ? { value: rightYAxisLabel, angle: 90, position: 'insideRight', style: { fontSize: 12 } }
                : undefined
            }
          />
        )}
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
          <Line
            key={s.key}
            yAxisId={s.yAxisId || 'left'}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={s.color}
            strokeWidth={2}
            dot={{ fill: s.color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default MultiLineChart;

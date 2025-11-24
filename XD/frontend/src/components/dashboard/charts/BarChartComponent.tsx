import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface BarChartComponentProps {
  data: any[];
  dataKey: string;
  xAxisKey?: string;
  yAxisLabel?: string;
  color?: string;
  colors?: string[];
  height?: number;
  angleLabels?: boolean;
}

const BarChartComponent: React.FC<BarChartComponentProps> = ({
  data,
  dataKey,
  xAxisKey = 'name',
  yAxisLabel,
  color = '#10b981',
  colors,
  height = 300,
  angleLabels = false,
}) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: angleLabels ? 60 : 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          angle={angleLabels ? -45 : 0}
          textAnchor={angleLabels ? 'end' : 'middle'}
          height={angleLabels ? 100 : 30}
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
        <Bar dataKey={dataKey} radius={[8, 8, 0, 0]}>
          {colors
            ? data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))
            : data.map((entry, index) => <Cell key={`cell-${index}`} fill={color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default BarChartComponent;

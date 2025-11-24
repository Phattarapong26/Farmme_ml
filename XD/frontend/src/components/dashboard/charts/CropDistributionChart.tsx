import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface CropDistribution {
  crop_type: string;
  crop_category: string;
  count: number;
  percentage: number;
}

interface CropDistributionChartProps {
  data: CropDistribution[];
}

const CropDistributionChart: React.FC<CropDistributionChartProps> = ({ data }) => {
  const options = useMemo(() => {
    // Group by category
    const categoryData: { [key: string]: number } = {};
    
    data.forEach(item => {
      if (!categoryData[item.crop_category]) {
        categoryData[item.crop_category] = 0;
      }
      categoryData[item.crop_category] += item.percentage;
    });

    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      data: [{
        type: 'doughnut',
        startAngle: 60,
        innerRadius: '60%',
        indexLabel: '{label} - {y}%',
        indexLabelFontSize: 12,
        yValueFormatString: '#,##0.0',
        toolTipContent: '<b>{label}</b>: {y}%',
        dataPoints: Object.entries(categoryData).map(([category, percentage], index) => ({
          label: category,
          y: parseFloat(percentage.toFixed(1)),
          color: colors[index % colors.length]
        }))
      }]
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลการกระจายพืช</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default CropDistributionChart;

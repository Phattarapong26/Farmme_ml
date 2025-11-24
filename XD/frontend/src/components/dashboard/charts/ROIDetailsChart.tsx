import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface ROIData {
  crop_type: string;
  roi: number;
  margin: number;
  profit_per_rai: number;
}

interface ROIDetailsChartProps {
  data: ROIData[];
}

const ROIDetailsChart: React.FC<ROIDetailsChartProps> = ({ data }) => {
  const options = useMemo(() => {
    // Sort by ROI descending and take top 10
    const sortedData = [...data].sort((a, b) => b.roi - a.roi).slice(0, 10);
    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'];
    
    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      axisX: {
        title: 'ROI (%)',
        labelFontSize: 12
      },
      axisY: {
        title: 'พืช',
        labelFontSize: 12,
        reversed: true
      },
      toolTip: {
        contentFormatter: function(e: any) {
          const point = e.entries[0].dataPoint;
          return `<strong>${point.label}</strong><br/>ROI: ${point.y.toFixed(1)}%`;
        }
      },
      data: [
        {
          type: 'bar',
          indexLabel: '{y}%',
          indexLabelFontSize: 11,
          indexLabelPlacement: 'outside',
          dataPoints: sortedData.map((item, index) => ({
            label: item.crop_type,
            y: item.roi,
            color: colors[index % colors.length]
          }))
        }
      ]
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูล ROI</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '400px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default ROIDetailsChart;

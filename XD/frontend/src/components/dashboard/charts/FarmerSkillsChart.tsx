import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface FarmerSkillsData {
  experience: number;
  land_size: number;
  farmers: number;
}

interface FarmerSkillsChartProps {
  data: FarmerSkillsData[];
}

const FarmerSkillsChart: React.FC<FarmerSkillsChartProps> = ({ data }) => {
  const options = useMemo(() => {
    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      axisX: {
        title: 'ประสบการณ์ (ปี)',
        labelFontSize: 12
      },
      axisY: {
        title: 'ขนาดที่ดิน (ไร่)',
        labelFontSize: 12
      },
      toolTip: {
        contentFormatter: function(e: any) {
          const point = e.entries[0].dataPoint;
          return `<strong>เกษตรกร: ${point.z} คน</strong><br/>ประสบการณ์: ${point.x} ปี<br/>ที่ดิน: ${point.y} ไร่`;
        }
      },
      data: [{
        type: 'scatter',
        markerSize: 15,
        color: '#3b82f6',
        dataPoints: data.map(item => ({
          x: item.experience,
          y: item.land_size,
          z: item.farmers
        }))
      }]
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลทักษะเกษตรกร</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default FarmerSkillsChart;

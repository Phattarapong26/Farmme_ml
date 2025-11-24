import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface SoilData {
  soil_type: string;
  count: number;
}

interface SoilAnalysisChartProps {
  data: SoilData[];
}

const SoilAnalysisChart: React.FC<SoilAnalysisChartProps> = ({ data }) => {
  const options = useMemo(() => {
    const colors = ['#8b5a2b', '#d2691e', '#daa520', '#cd853f', '#f4a460', '#deb887'];
    
    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      toolTip: {
        contentFormatter: function(e: any) {
          return `<strong>${e.entries[0].dataPoint.label}</strong><br/>จำนวนพืช: ${e.entries[0].dataPoint.y} ชนิด<br/>สัดส่วน: ${e.entries[0].dataPoint.percentage.toFixed(1)}%`;
        }
      },
      data: [{
        type: 'pie',
        showInLegend: true,
        indexLabel: '{label}: {percentage}%',
        indexLabelFontSize: 12,
        dataPoints: data.map((item, index) => ({
          label: item.soil_type,
          y: item.count,
          color: colors[index % colors.length],
          percentage: (item.count / data.reduce((sum, d) => sum + d.count, 0)) * 100
        }))
      }]
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลประเภทดิน</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default SoilAnalysisChart;

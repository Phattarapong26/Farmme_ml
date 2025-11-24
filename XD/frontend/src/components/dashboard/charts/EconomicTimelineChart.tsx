import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface EconomicData {
  factor: string;
  value: number;
  date: string;
}

interface EconomicTimelineChartProps {
  data: EconomicData[];
}

const EconomicTimelineChart: React.FC<EconomicTimelineChartProps> = ({ data }) => {
  const options = useMemo(() => {
    // Group data by factor
    const groupedData: { [key: string]: any[] } = {};
    
    data.forEach(item => {
      if (!groupedData[item.factor]) {
        groupedData[item.factor] = [];
      }
      groupedData[item.factor].push({
        x: new Date(item.date),
        y: item.value
      });
    });

    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
    const dataSeries = Object.keys(groupedData).slice(0, 5).map((factor, index) => ({
      type: 'line',
      name: factor,
      showInLegend: true,
      color: colors[index % colors.length],
      lineThickness: 2,
      markerSize: 5,
      dataPoints: groupedData[factor].sort((a, b) => a.x.getTime() - b.x.getTime())
    }));

    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      axisX: {
        title: 'วันที่',
        labelFontSize: 12,
        valueFormatString: 'DD MMM'
      },
      axisY: {
        title: 'ค่า',
        labelFontSize: 12
      },
      toolTip: {
        shared: true,
        contentFormatter: function(e: any) {
          let content = `<strong>${e.entries[0].dataPoint.x.toLocaleDateString('th-TH')}</strong><br/>`;
          e.entries.forEach((entry: any) => {
            content += `${entry.dataSeries.name}: ${entry.dataPoint.y.toFixed(2)}<br/>`;
          });
          return content;
        }
      },
      legend: {
        cursor: 'pointer',
        itemclick: function(e: any) {
          e.dataSeries.visible = typeof(e.dataSeries.visible) === 'undefined' || e.dataSeries.visible;
          e.dataSeries.visible = !e.dataSeries.visible;
          e.chart.render();
        }
      },
      data: dataSeries
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลตัวชี้วัดเศรษฐกิจ</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default EconomicTimelineChart;

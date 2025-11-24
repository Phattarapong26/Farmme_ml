import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface PriceDataPoint {
  date: string;
  crop_type: string;
  price: number;
}

interface PriceTrendChartProps {
  data: PriceDataPoint[];
}

const PriceTrendChart: React.FC<PriceTrendChartProps> = ({ data }) => {
  const options = useMemo(() => {
    // Group data by crop type
    const groupedData: { [key: string]: { x: Date; y: number }[] } = {};
    
    data.forEach(item => {
      if (!groupedData[item.crop_type]) {
        groupedData[item.crop_type] = [];
      }
      groupedData[item.crop_type].push({
        x: new Date(item.date),
        y: item.price
      });
    });

    // Get top 5 crops by data points
    const topCrops = Object.entries(groupedData)
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 5);

    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

    return {
      animationEnabled: true,
      theme: 'light2',
      title: {
        text: '',
        fontSize: 0
      },
      axisX: {
        title: 'วันที่',
        valueFormatString: 'DD MMM',
        labelFontSize: 12
      },
      axisY: {
        title: 'ราคา (บาท/กก.)',
        prefix: '฿',
        labelFontSize: 12
      },
      toolTip: {
        shared: true,
        contentFormatter: function(e: any) {
          let content = `<strong>${e.entries[0].dataPoint.x.toLocaleDateString('th-TH', { 
            day: 'numeric', 
            month: 'short' 
          })}</strong><br/>`;
          e.entries.forEach((entry: any) => {
            content += `<span style="color:${entry.dataSeries.color}">${entry.dataSeries.name}</span>: ฿${entry.dataPoint.y.toFixed(2)}<br/>`;
          });
          return content;
        }
      },
      legend: {
        cursor: 'pointer',
        fontSize: 12,
        itemclick: function(e: any) {
          e.dataSeries.visible = !(typeof e.dataSeries.visible === 'undefined' || e.dataSeries.visible);
          e.chart.render();
        }
      },
      data: topCrops.map(([cropType, dataPoints], index) => ({
        type: 'line',
        name: cropType,
        showInLegend: true,
        color: colors[index],
        markerSize: 5,
        dataPoints: dataPoints.sort((a, b) => a.x.getTime() - b.x.getTime())
      }))
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลราคา</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default PriceTrendChart;

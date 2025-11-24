import React, { useMemo } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

interface WeatherDataPoint {
  date: string;
  temperature: number;
  rainfall: number;
}

interface WeatherChartProps {
  data: WeatherDataPoint[];
}

const WeatherChart: React.FC<WeatherChartProps> = ({ data }) => {
  const options = useMemo(() => {
    const temperatureData = data.map(item => ({
      x: new Date(item.date),
      y: item.temperature
    }));

    const rainfallData = data.map(item => ({
      x: new Date(item.date),
      y: item.rainfall
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
        valueFormatString: 'DD MMM',
        labelFontSize: 12
      },
      axisY: [{
        title: 'อุณหภูมิ (°C)',
        suffix: '°C',
        labelFontSize: 12,
        lineColor: '#f59e0b',
        tickColor: '#f59e0b',
        labelFontColor: '#f59e0b'
      }, {
        title: 'ปริมาณฝน (มม.)',
        suffix: ' มม.',
        labelFontSize: 12,
        lineColor: '#3b82f6',
        tickColor: '#3b82f6',
        labelFontColor: '#3b82f6'
      }],
      toolTip: {
        shared: true,
        contentFormatter: function(e: any) {
          let content = `<strong>${e.entries[0].dataPoint.x.toLocaleDateString('th-TH', { 
            day: 'numeric', 
            month: 'short' 
          })}</strong><br/>`;
          e.entries.forEach((entry: any) => {
            const suffix = entry.dataSeries.axisYIndex === 1 ? ' มม.' : '°C';
            content += `<span style="color:${entry.dataSeries.color}">${entry.dataSeries.name}</span>: ${entry.dataPoint.y.toFixed(1)}${suffix}<br/>`;
          });
          return content;
        }
      },
      legend: {
        cursor: 'pointer',
        fontSize: 12
      },
      data: [
        {
          type: 'line',
          name: 'อุณหภูมิ',
          showInLegend: true,
          color: '#f59e0b',
          markerSize: 5,
          lineThickness: 3,
          axisYIndex: 0,
          dataPoints: temperatureData
        },
        {
          type: 'area',
          name: 'ปริมาณฝน',
          showInLegend: true,
          color: '#3b82f6',
          fillOpacity: 0.3,
          lineThickness: 2,
          axisYIndex: 1,
          dataPoints: rainfallData
        }
      ]
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <p>ไม่มีข้อมูลสภาพอากาศ</p>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: '350px' }}>
      <CanvasJSChart options={options} />
    </div>
  );
};

export default WeatherChart;

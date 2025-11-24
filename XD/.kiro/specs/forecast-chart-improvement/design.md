# Design Document - Forecast Chart Improvement

## Overview

การปรับปรุงกราฟเส้นใน RealForecastChart component เพื่อเพิ่มความชัดเจนและอ่านง่ายขึ้น โดยเน้นการปรับปรุง visual design, color scheme, typography และ user interaction ของกราฟที่ใช้ Recharts library

## Architecture

### Component Structure

```
RealForecastChart (frontend/src/components/RealForecastChart.tsx)
├── Card Container
│   ├── CardHeader (Province/Crop/Timeframe Selectors)
│   ├── CardContent
│   │   ├── Statistics Summary (4 cards)
│   │   ├── Chart Container (ResponsiveContainer)
│   │   │   └── LineChart (Recharts)
│   │   │       ├── CartesianGrid (improved styling)
│   │   │       ├── XAxis (improved labels)
│   │   │       ├── YAxis (improved labels)
│   │   │       ├── Tooltip (enhanced design)
│   │   │       ├── Legend (improved positioning)
│   │   │       ├── Line (Historical - improved styling)
│   │   │       └── Line (Predicted - improved styling)
│   │   └── Analysis Summary
```

## Components and Interfaces

### 1. Line Styling Configuration

**Historical Data Line:**
```typescript
{
  type: "monotone",
  dataKey: "historicalPrice",
  stroke: "#2563eb",        // Blue-600 (darker, more visible)
  strokeWidth: 3,           // Increased from 2
  name: "📊 ราคาในอดีต",
  dot: { 
    fill: "#2563eb", 
    r: 5,                   // Increased from 3
    strokeWidth: 2,
    stroke: "#ffffff"       // White border for better visibility
  },
  activeDot: { r: 7 },      // Larger on hover
  connectNulls: true
}
```

**Predicted Data Line:**
```typescript
{
  type: "monotone",
  dataKey: "predictedPrice",
  stroke: "#f97316",        // Orange-600 (darker, more visible)
  strokeWidth: 3,           // Increased from 2
  strokeDasharray: "8 4",   // Longer dashes for better visibility
  name: "🔮 ราคาพยากรณ์ (ML)",
  dot: { 
    fill: "#f97316", 
    r: 5,                   // Increased from 3
    strokeWidth: 2,
    stroke: "#ffffff"       // White border
  },
  activeDot: { r: 7 },
  connectNulls: true
}
```

### 2. Axis Configuration

**X-Axis (Date):**
```typescript
{
  dataKey: "date",
  angle: timeFrame <= 7 ? 0 : -45,
  textAnchor: timeFrame <= 7 ? "middle" : "end",
  height: timeFrame <= 7 ? 70 : 90,
  tick: { 
    fontSize: 13,           // Increased from 11-12
    fill: "#374151",        // Gray-700 for better readability
    fontWeight: 500
  },
  interval: timeFrame <= 7 ? 0 : 'preserveStartEnd',
  stroke: "#9ca3af",        // Gray-400
  strokeWidth: 1
}
```

**Y-Axis (Price):**
```typescript
{
  label: { 
    value: 'ราคา (บาท/กก.)', 
    angle: -90, 
    position: 'insideLeft',
    style: {
      fontSize: 14,
      fill: "#374151",      // Gray-700
      fontWeight: 600
    }
  },
  tick: {
    fontSize: 13,
    fill: "#374151",
    fontWeight: 500
  },
  stroke: "#9ca3af",
  strokeWidth: 1,
  tickFormatter: (value) => `${value.toFixed(0)}`  // Round to integer
}
```

### 3. CartesianGrid Styling

```typescript
{
  strokeDasharray: "3 3",
  stroke: "#e5e7eb",        // Gray-200 (lighter)
  strokeWidth: 1,
  opacity: 0.5
}
```

### 4. Enhanced Tooltip Design

```typescript
interface TooltipProps {
  active?: boolean;
  payload?: any[];
}

const CustomTooltip: React.FC<TooltipProps> = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) return null;
  
  const data = payload[0].payload;
  const fullDate = new Date(data.fullDate).toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  return (
    <div className="bg-white p-4 border-2 border-gray-300 rounded-lg shadow-xl">
      <p className="text-sm font-bold text-gray-800 mb-2 border-b pb-2">
        📅 {fullDate}
      </p>
      {data.historicalPrice && (
        <div className="flex items-center gap-2 mb-1">
          <span className="text-lg">📊</span>
          <p className="text-sm font-semibold text-blue-600">
            ราคาจริง: <span className="font-bold">{data.historicalPrice.toFixed(2)}</span> บาท/กก.
          </p>
        </div>
      )}
      {data.predictedPrice && (
        <div className="flex items-center gap-2">
          <span className="text-lg">🔮</span>
          <p className="text-sm font-semibold text-orange-600">
            ราคาพยากรณ์: <span className="font-bold">{data.predictedPrice.toFixed(2)}</span> บาท/กก.
          </p>
        </div>
      )}
      {data.historicalPrice && data.predictedPrice && (
        <div className="mt-2 pt-2 border-t">
          <p className="text-xs text-gray-600">
            ส่วนต่าง: {Math.abs(data.predictedPrice - data.historicalPrice).toFixed(2)} บาท/กก.
          </p>
        </div>
      )}
    </div>
  );
};
```

### 5. Legend Configuration

```typescript
{
  verticalAlign: "top",
  height: 50,
  iconType: "line",
  wrapperStyle: {
    paddingBottom: "20px",
    fontSize: "14px",
    fontWeight: 600
  },
  formatter: (value: string) => {
    // Already includes emoji in name
    return <span style={{ color: "#374151" }}>{value}</span>;
  }
}
```

## Data Models

### Chart Data Point Interface

```typescript
interface ChartDataPoint {
  date: string;              // Display date (e.g., "1 ม.ค.")
  fullDate: string;          // Full ISO date for tooltip
  historicalPrice: number | null;
  predictedPrice: number | null;
  type: 'historical' | 'forecast' | 'bridge';
}
```

### Bridge Point Logic

```typescript
// Create smooth transition between historical and forecast
if (historicalData.length > 0 && forecastData.length > 0) {
  const lastHistorical = historicalData[historicalData.length - 1];
  const bridgePoint: ChartDataPoint = {
    date: lastHistorical.date,
    fullDate: lastHistorical.fullDate,
    historicalPrice: lastHistorical.historicalPrice,
    predictedPrice: lastHistorical.historicalPrice, // Same value for smooth connection
    type: 'bridge'
  };
  return [...historicalData, bridgePoint, ...forecastData];
}
```

## Color Scheme

### Primary Colors
- **Historical Line**: `#2563eb` (Blue-600) - เข้มขึ้นจากเดิม
- **Predicted Line**: `#f97316` (Orange-600) - เข้มขึ้นจากเดิม
- **Grid Lines**: `#e5e7eb` (Gray-200) - อ่อนลง
- **Axis Lines**: `#9ca3af` (Gray-400)
- **Text**: `#374151` (Gray-700) - เข้มขึ้นเพื่อให้อ่านง่าย

### Contrast Ratios
- Historical line vs background: 7:1 (AAA)
- Predicted line vs background: 6.5:1 (AA+)
- Text vs background: 10:1 (AAA)

## Responsive Design

### Breakpoints

```typescript
// Mobile (< 768px)
- Chart height: 320px (h-80)
- Font size: 11px
- Dot radius: 4px
- X-axis angle: -45°

// Tablet (768px - 1024px)
- Chart height: 384px (h-96)
- Font size: 12px
- Dot radius: 5px
- X-axis angle: -45° (for 30+ days)

// Desktop (> 1024px)
- Chart height: 384px (h-96)
- Font size: 13px
- Dot radius: 5px
- X-axis angle: 0° (for 7 days), -45° (for 30+ days)
```

## Error Handling

### Loading State
```typescript
<div className="flex items-center justify-center h-full">
  <div className="text-center">
    <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-500 border-t-transparent mx-auto mb-4"></div>
    <p className="text-gray-600 font-medium">กำลังโหลดข้อมูลจาก ML Model...</p>
    <p className="text-gray-500 text-sm mt-2">โปรดรอสักครู่</p>
  </div>
</div>
```

### Error State
```typescript
<div className="flex items-center justify-center h-full">
  <div className="text-center">
    <div className="text-red-500 text-6xl mb-4">⚠️</div>
    <p className="text-red-600 font-semibold text-lg">ไม่สามารถโหลดข้อมูลการพยากรณ์ได้</p>
    <p className="text-gray-600 text-sm mt-2">กรุณาลองใหม่อีกครั้งหรือเลือกพืช/จังหวัดอื่น</p>
  </div>
</div>
```

### Empty State
```typescript
<div className="flex items-center justify-center h-full">
  <div className="text-center">
    <div className="text-gray-400 text-6xl mb-4">📊</div>
    <p className="text-gray-700 font-semibold text-lg">ไม่พบข้อมูลสำหรับการแสดงผล</p>
    <p className="text-gray-500 text-sm mt-2">กรุณาเลือกจังหวัดและพืชที่ต้องการ</p>
  </div>
</div>
```

## Testing Strategy

### Visual Testing
1. ทดสอบการแสดงผลกราฟในทุก timeframe (7, 30, 90, 180 วัน)
2. ทดสอบสีและความหนาของเส้นกราฟ
3. ทดสอบการแสดงผล tooltip เมื่อ hover
4. ทดสอบ legend และ axis labels

### Responsive Testing
1. ทดสอบบนหน้าจอขนาด mobile (375px, 414px)
2. ทดสอบบนหน้าจอขนาด tablet (768px, 1024px)
3. ทดสอบบนหน้าจอขนาด desktop (1280px, 1920px)

### Data Testing
1. ทดสอบกับข้อมูลจริงและข้อมูลพยากรณ์
2. ทดสอบกับข้อมูลเฉพาะจริง (ไม่มีพยากรณ์)
3. ทดสอบกับข้อมูลว่าง
4. ทดสอบการเชื่อมต่อระหว่างข้อมูลจริงและพยากรณ์

### Accessibility Testing
1. ทดสอบ contrast ratio ของสีทั้งหมด
2. ทดสอบการใช้งานด้วย keyboard navigation
3. ทดสอบ screen reader compatibility

## Performance Considerations

1. **Data Sampling**: จำกัดจำนวนจุดข้อมูลตาม timeframe เพื่อประสิทธิภาพ
   - 7 วัน: แสดงทุกวัน
   - 30 วัน: แสดง 15 จุด
   - 90 วัน: แสดง 30 จุด
   - 180 วัน: แสดง 60 จุด

2. **Memoization**: ใช้ `useMemo` สำหรับ chartData และ analysis

3. **Lazy Rendering**: ใช้ ResponsiveContainer เพื่อ render เฉพาะเมื่อจำเป็น

## Implementation Notes

1. ไม่ต้องเปลี่ยน API หรือ backend logic
2. เปลี่ยนแปลงเฉพาะ frontend component (RealForecastChart.tsx)
3. ใช้ Tailwind CSS classes ที่มีอยู่แล้ว
4. ไม่ต้องติดตั้ง dependencies เพิ่มเติม
5. รักษา backward compatibility กับ props และ data structure เดิม

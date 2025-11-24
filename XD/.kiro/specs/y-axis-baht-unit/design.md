# Design Document

## Overview

การปรับปรุงการแสดงผลแกน Y ของกราฟราคาในหน้า Forecast โดยเพิ่มหน่วย "บาท" ต่อท้ายตัวเลขทุกค่าบนแกน Y เพื่อให้ผู้ใช้เข้าใจข้อมูลได้ง่ายขึ้นและกราฟดูสวยงามมากขึ้น การออกแบบนี้จะครอบคลุมทั้ง RealForecastChart และ HistoricalDataChart เพื่อให้มีความสอดคล้องกันทั้งระบบ

## Architecture

การแก้ไขจะเกิดขึ้นที่ Frontend Layer โดยเฉพาะในส่วนของ Chart Components:

```
Frontend
├── components/
│   ├── RealForecastChart.tsx (แก้ไข YAxis tickFormatter)
│   └── HistoricalDataChart.tsx (แก้ไข YAxis tickFormatter)
```

## Components and Interfaces

### 1. RealForecastChart Component

**ตำแหน่งที่ต้องแก้ไข:**
- YAxis component ใน LineChart (บรรทัดที่ 318-327)

**การเปลี่ยนแปลง:**
```typescript
// ปัจจุบัน
<YAxis
  label={{ 
    value: 'ราคา (บาท/กก.)', 
    angle: -90, 
    position: 'insideLeft',
    style: { fontSize: 14, fill: '#374151', fontWeight: 600 }
  }}
  tick={{ fontSize: 13, fill: '#374151', fontWeight: 500 }}
  stroke="#9ca3af"
  strokeWidth={1}
  tickFormatter={(value) => `${value.toFixed(0)}`}
/>

// แก้ไขเป็น
<YAxis
  label={{ 
    value: 'ราคา (บาท/กก.)', 
    angle: -90, 
    position: 'insideLeft',
    style: { fontSize: 14, fill: '#374151', fontWeight: 600 }
  }}
  tick={{ fontSize: 13, fill: '#374151', fontWeight: 500 }}
  stroke="#9ca3af"
  strokeWidth={1}
  tickFormatter={(value) => `${value.toFixed(0)} บาท`}
/>
```

### 2. HistoricalDataChart Component

**ตำแหน่งที่ต้องแก้ไข:**
- YAxis component ใน renderChart() function สำหรับทุกประเภทกราฟ (line, bar, area)

**การเปลี่ยนแปลง:**

สร้างฟังก์ชัน helper สำหรับจัดรูปแบบ Y-axis ตามประเภทข้อมูล:

```typescript
// เพิ่มฟังก์ชัน helper
const getYAxisFormatter = (dataType: 'price' | 'temperature' | 'rainfall') => {
  switch (dataType) {
    case 'price':
      return (value: number) => `${value.toFixed(0)} บาท`;
    case 'temperature':
      return (value: number) => `${value.toFixed(0)}°C`;
    case 'rainfall':
      return (value: number) => `${value.toFixed(0)} มม.`;
    default:
      return (value: number) => value.toFixed(0);
  }
};

// ใช้ใน YAxis component
<YAxis tickFormatter={getYAxisFormatter(dataType)} />
```

## Data Models

ไม่มีการเปลี่ยนแปลง Data Models เนื่องจากเป็นการปรับปรุงเฉพาะการแสดงผลเท่านั้น

## Error Handling

ไม่จำเป็นต้องมี Error Handling เพิ่มเติม เนื่องจาก:
- tickFormatter จะทำงานกับค่าตัวเลขที่ Recharts library จัดการให้อยู่แล้ว
- การใช้ toFixed(0) จะแปลงค่าเป็นจำนวนเต็มเสมอ
- การเพิ่มสตริง "บาท" ไม่มีผลต่อการคำนวณหรือการแสดงผลของกราฟ

## Testing Strategy

### Manual Testing

1. **RealForecastChart Testing:**
   - เปิดหน้า Forecast และเลือกโหมด "พยากรณ์ราคา"
   - ตรวจสอบว่าแกน Y แสดงหน่วย "บาท" ต่อท้ายทุกค่า
   - ทดสอบกับจังหวัดและพืชต่างๆ
   - ทดสอบกับช่วงเวลาต่างๆ (7, 30, 90, 180 วัน)
   - ตรวจสอบว่าค่าบนแกนไม่ทับซ้อนกัน

2. **HistoricalDataChart Testing:**
   - เปิดหน้า Forecast และเลือกโหมด "ข้อมูลในอดีต"
   - ทดสอบกับประเภทข้อมูล "ราคา" - ต้องแสดง "บาท"
   - ทดสอบกับประเภทข้อมูล "อุณหภูมิ" - ต้องแสดง "°C"
   - ทดสอบกับประเภทข้อมูล "ปริมาณฝน" - ต้องแสดง "มม."
   - ทดสอบกับประเภทกราฟต่างๆ (เส้น, แท่ง, พื้นที่)
   - ทดสอบกับช่วงเวลาต่างๆ (1m, 3m, 6m, 1y)

3. **Responsive Testing:**
   - ทดสอบบนหน้าจอขนาดต่างๆ (Desktop, Tablet, Mobile)
   - ตรวจสอบว่าข้อความบนแกน Y ไม่ล้นออกนอกกราฟ
   - ตรวจสอบว่าการหมุนข้อความบนแกน X (ถ้ามี) ไม่กระทบกับแกน Y

### Visual Regression Testing

- เปรียบเทียบภาพหน้าจอก่อนและหลังการแก้ไข
- ตรวจสอบว่าการเพิ่มหน่วยไม่ทำให้ layout เพี้ยน
- ตรวจสอบว่าสีและขนาดตัวอักษรยังคงเหมือนเดิม

## Implementation Notes

1. **ความสอดคล้อง (Consistency):**
   - ใช้รูปแบบเดียวกันทั้ง RealForecastChart และ HistoricalDataChart
   - ใช้ toFixed(0) เพื่อแสดงเป็นจำนวนเต็ม (ไม่มีทศนิยม)

2. **Performance:**
   - tickFormatter ทำงานเร็วมาก ไม่กระทบ performance
   - ไม่ต้องเพิ่ม memoization

3. **Accessibility:**
   - การเพิ่มหน่วยช่วยให้ผู้ใช้เข้าใจข้อมูลได้ง่ายขึ้น
   - Screen readers จะอ่านค่าพร้อมหน่วยได้ชัดเจนขึ้น

4. **Internationalization (i18n):**
   - ปัจจุบันใช้ภาษาไทยเท่านั้น
   - หากต้องการรองรับหลายภาษาในอนาคต ควรใช้ i18n library

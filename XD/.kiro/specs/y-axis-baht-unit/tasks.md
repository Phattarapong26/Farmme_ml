# Implementation Plan

- [x] 1. แก้ไข RealForecastChart component เพื่อเพิ่มหน่วย "บาท" ในแกน Y


  - แก้ไข tickFormatter ของ YAxis component ให้แสดง "บาท" ต่อท้ายตัวเลข
  - ใช้ toFixed(0) เพื่อแสดงเป็นจำนวนเต็ม
  - ตรวจสอบว่าการแสดงผลไม่มี TypeScript errors
  - _Requirements: 1.1, 1.3, 1.4_



- [ ] 2. แก้ไข HistoricalDataChart component เพื่อเพิ่มหน่วยในแกน Y
  - สร้างฟังก์ชัน getYAxisFormatter สำหรับจัดรูปแบบตามประเภทข้อมูล
  - แก้ไข YAxis ในทุกประเภทกราฟ (line, bar, area) ให้ใช้ formatter function
  - ตรวจสอบว่าแสดงหน่วย "บาท" สำหรับราคา, "°C" สำหรับอุณหภูมิ, "มม." สำหรับปริมาณฝน



  - ตรวจสอบว่าการแสดงผลไม่มี TypeScript errors
  - _Requirements: 1.2, 1.3, 1.5, 2.1, 2.2_

- [ ] 3. ทดสอบการแสดงผลบนหน้าจอ
  - ทดสอบ RealForecastChart กับจังหวัดและพืชต่างๆ
  - ทดสอบ RealForecastChart กับช่วงเวลาต่างๆ (7, 30, 90, 180 วัน)
  - ทดสอบ HistoricalDataChart กับทุกประเภทข้อมูล (ราคา, อุณหภูมิ, ปริมาณฝน)
  - ทดสอบ HistoricalDataChart กับทุกประเภทกราฟ (เส้น, แท่ง, พื้นที่)
  - ตรวจสอบว่าค่าบนแกนไม่ทับซ้อนกันและอ่านง่าย
  - ทดสอบ responsive design บนหน้าจอขนาดต่างๆ
  - _Requirements: 1.4, 1.5, 2.2, 2.3_

# Implementation Plan

- [x] 1. อัพเดท get_weather_data() function ให้คำนวณค่าเฉลี่ยรายเดือน


  - แก้ไข SQL query ให้ใช้ GROUP BY year, month
  - ใช้ AVG() function สำหรับ temperature และ rainfall
  - เปลี่ยนฟอร์แมต date เป็น "Mon YYYY" (ตรวจสอบ database type: PostgreSQL หรือ SQLite)
  - ลบ limit(50) และเรียงข้อมูลตามลำดับเวลา
  - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_



- [ ] 2. อัพเดท get_economic_timeline() function ให้คำนวณค่าเฉลี่ยรายเดือน
  - แก้ไข SQL query ให้ใช้ GROUP BY year, month แทน GROUP BY date
  - เปลี่ยนฟอร์แมต date เป็น "Mon YYYY"
  - ลบ LIMIT 100 เพราะข้อมูลรายเดือนมีน้อย


  - คำนวณค่าเฉลี่ยรายเดือนสำหรับ fuel_price และ fertilizer_price
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

- [ ] 3. อัพเดท Frontend chart descriptions
  - เปลี่ยน description ของกราฟแนวโน้มอุณหภูมิเป็น "ค่าเฉลี่ยรายเดือน"
  - เปลี่ยน description ของกราฟปริมาณฝนเป็น "ค่าเฉลี่ยรายเดือน"


  - เปลี่ยน description ของกราฟสภาพอากาศเป็น "ค่าเฉลี่ยรายเดือน"
  - เปลี่ยน description ของกราฟราคาน้ำมันเป็น "ค่าเฉลี่ยรายเดือน"
  - เปลี่ยน description ของกราฟราคาปุ๋ยเป็น "ค่าเฉลี่ยรายเดือน"
  - _Requirements: 1.4, 2.4_




- [ ] 4. ทดสอบ Backend functions
  - ทดสอบ get_weather_data() ว่าคำนวณค่าเฉลี่ยรายเดือนถูกต้อง
  - ทดสอบ get_economic_timeline() ว่าคำนวณค่าเฉลี่ยรายเดือนถูกต้อง
  - ทดสอบฟอร์แมต date ว่าเป็น "Mon YYYY"
  - ทดสอบกรณีไม่มีข้อมูลในบางเดือน
  - _Requirements: 3.4, 4.4_

- [ ] 5. ทดสอบ Frontend charts
  - ทดสอบกราฟแสดงข้อมูลรายเดือนถูกต้อง
  - ทดสอบแกน X แสดงชื่อเดือน-ปี
  - ทดสอบกับ days_back ต่างๆ (30, 90, 365)
  - ตรวจสอบว่าข้อมูลตรงกับ database
  - _Requirements: 1.4, 2.4, 4.1, 4.2, 4.3, 4.4_

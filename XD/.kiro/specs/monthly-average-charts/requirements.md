# Requirements Document

## Introduction

ฟีเจอร์นี้จะปรับปรุงกราฟในหน้า Dashboard Overview ให้แสดงข้อมูลเป็นค่าเฉลี่ยรายเดือนแทนที่จะเป็นรายวัน สำหรับกราฟ: แนวโน้มอุณหภูมิ, ปริมาณฝน, ราคาน้ำมัน, ราคาปุ๋ย, และสภาพอากาศ เพื่อให้ผู้ใช้เห็นแนวโน้มที่ชัดเจนขึ้นและลดความซับซ้อนของข้อมูล

## Glossary

- **Backend Service**: ส่วน dashboard_service.py ที่จัดการและประมวลผลข้อมูลจาก database
- **Weather Data**: ข้อมูลสภาพอากาศรายวัน (อุณหภูมิ, ปริมาณฝน) จากตาราง weather_data
- **Economic Timeline**: ข้อมูลเศรษฐกิจ (ราคาน้ำมัน, ราคาปุ๋ย) ที่คำนวณจากราคาพืช
- **Monthly Aggregation**: การรวมข้อมูลรายวันเป็นค่าเฉลี่ยรายเดือน
- **Frontend Charts**: กราฟที่แสดงในหน้า DashboardOverview component

## Requirements

### Requirement 1

**User Story:** ในฐานะผู้ใช้ ฉันต้องการเห็นกราฟแนวโน้มอุณหภูมิและปริมาณฝนเป็นค่าเฉลี่ยรายเดือน เพื่อให้เห็นแนวโน้มที่ชัดเจนและไม่ซับซ้อนเกินไป

#### Acceptance Criteria

1. WHEN Backend Service ดึงข้อมูลสภาพอากาศ, THE Backend Service SHALL คำนวณค่าเฉลี่ยอุณหภูมิและปริมาณฝนรายเดือนจากข้อมูลรายวัน
2. THE Backend Service SHALL จัดกลุ่มข้อมูลตามเดือนและปีจากฟิลด์ date ในตาราง weather_data
3. THE Backend Service SHALL ส่งข้อมูลที่มีฟอร์แมต month-year (เช่น "ม.ค. 2024") แทนที่จะเป็น date
4. WHEN Frontend แสดงกราฟสภาพอากาศ, THE Frontend SHALL แสดงข้อมูลรายเดือนบนแกน X

### Requirement 2

**User Story:** ในฐานะผู้ใช้ ฉันต้องการเห็นกราฟราคาน้ำมันและราคาปุ๋ยเป็นค่าเฉลี่ยรายเดือน เพื่อติดตามแนวโน้มต้นทุนการผลิตได้ง่ายขึ้น

#### Acceptance Criteria

1. WHEN Backend Service คำนวณ economic_timeline, THE Backend Service SHALL คำนวณค่าเฉลี่ยราคาน้ำมันและปุ๋ยรายเดือน
2. THE Backend Service SHALL จัดกลุ่มข้อมูลตามเดือนและปีจากฟิลด์ date ในตาราง crop_prices
3. THE Backend Service SHALL ส่งข้อมูลที่มีฟอร์แมต month-year แทนที่จะเป็น date
4. WHEN Frontend แสดงกราฟเศรษฐกิจ, THE Frontend SHALL แสดงข้อมูลรายเดือนบนแกน X

### Requirement 3

**User Story:** ในฐานะผู้ใช้ ฉันต้องการให้ข้อมูลที่แสดงตรงกับข้อมูลจริงใน database เพื่อความถูกต้องและน่าเชื่อถือ

#### Acceptance Criteria

1. THE Backend Service SHALL ใช้ SQL aggregation functions (AVG, GROUP BY) เพื่อคำนวณค่าเฉลี่ยรายเดือน
2. THE Backend Service SHALL ดึงข้อมูลจากตาราง weather_data และ crop_prices โดยตรง
3. THE Backend Service SHALL ไม่สร้างข้อมูลปลอมหรือใช้ค่าประมาณการ
4. WHEN ไม่มีข้อมูลในเดือนใดเดือนหนึ่ง, THE Backend Service SHALL ไม่แสดงข้อมูลเดือนนั้น (ไม่ใส่ค่า 0 หรือค่าเฉลี่ย)

### Requirement 4

**User Story:** ในฐานะผู้ใช้ ฉันต้องการให้กราฟแสดงข้อมูลย้อนหลังได้ตามช่วงเวลาที่เลือก เพื่อวิเคราะห์แนวโน้มระยะยาว

#### Acceptance Criteria

1. THE Backend Service SHALL รองรับพารามิเตอร์ days_back เพื่อกำหนดช่วงเวลาที่ต้องการดูข้อมูล
2. WHEN days_back มีค่ามาก (เช่น 365 วัน), THE Backend Service SHALL แสดงข้อมูลรายเดือนทั้งหมดในช่วงนั้น
3. THE Backend Service SHALL เรียงข้อมูลตามลำดับเวลาจากเก่าไปใหม่
4. THE Frontend SHALL แสดงข้อมูลทั้งหมดที่ Backend ส่งมาโดยไม่จำกัดจำนวน

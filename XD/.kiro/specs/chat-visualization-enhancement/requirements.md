# Requirements Document

## Introduction

ปรับปรุงระบบ Chat AI ให้มีความเป็นธรรมชาติมากขึ้น เข้าใจผู้ใช้ได้ดีขึ้น และสามารถแสดงกราฟทำนายราคาแบบ interactive ได้เมื่อผู้ใช้ต้องการ โดยใช้ Gemini Function Calling เพื่อเรียกใช้ ML Model และส่งข้อมูลกราฟกลับมาแสดงผลใน chat interface

## Glossary

- **Chat System**: ระบบสนทนาระหว่าง AI กับเกษตรกรผ่าน Gemini API
- **Gemini Function Calling**: กลไกที่ Gemini AI เรียกใช้ functions เพื่อดึงข้อมูลจาก ML models
- **Price Forecast Chart**: กราฟแสดงการทำนายราคาพืชในอนาคต
- **Natural Language Understanding**: ความสามารถในการเข้าใจภาษาธรรมชาติของผู้ใช้
- **Frontend Chat Component**: Component React ที่แสดงผลการสนทนาและกราฟ
- **Backend Chat Router**: API endpoint สำหรับจัดการ chat requests

## Requirements

### Requirement 1

**User Story:** ในฐานะเกษตรกร ฉันต้องการสนทนากับ AI ด้วยภาษาที่เป็นธรรมชาติ เพื่อให้รู้สึกสบายใจและเข้าใจง่าย

#### Acceptance Criteria

1. WHEN เกษตรกรส่งข้อความถามคำถาม, THE Chat System SHALL ตอบกลับด้วยภาษาไทยที่เป็นธรรมชาติและเข้าใจง่าย
2. WHEN เกษตรกรถามคำถามสั้นๆ, THE Chat System SHALL ตอบสั้นกระชับไม่เกิน 3 ประโยค
3. WHEN เกษตรกรถามคำถามซับซ้อน, THE Chat System SHALL ตอบอย่างละเอียดพร้อมแบ่งเป็นหัวข้อย่อย
4. THE Chat System SHALL ปรับโทนการสนทนาให้เข้ากับบริบทของคำถาม
5. THE Chat System SHALL หลีกเลี่ยงการใช้ศัพท์เทคนิคที่ยากเกินไป

### Requirement 2

**User Story:** ในฐานะเกษตรกร ฉันต้องการเห็นกราฟทำนายราคาเมื่อถามเรื่องราคา เพื่อให้เข้าใจแนวโน้มได้ชัดเจนขึ้น

#### Acceptance Criteria

1. WHEN เกษตรกรถามเรื่องราคาในอนาคต, THE Chat System SHALL เรียกใช้ get_price_prediction function
2. WHEN get_price_prediction function ส่งข้อมูลกลับมา, THE Chat System SHALL ส่งข้อมูลกราฟพร้อมคำตอบ
3. THE Frontend Chat Component SHALL แสดงกราฟ interactive เมื่อได้รับข้อมูลกราฟ
4. THE Price Forecast Chart SHALL แสดงข้อมูลราคาย้อนหลังและราคาทำนายในกราฟเดียวกัน
5. THE Price Forecast Chart SHALL มี bridge point เชื่อมต่อระหว่างข้อมูลจริงและข้อมูลทำนาย

### Requirement 3

**User Story:** ในฐานะเกษตรกร ฉันต้องการให้ AI เข้าใจคำถามที่หลากหลาย เพื่อไม่ต้องถามด้วยรูปแบบที่เฉพาะเจาะจง

#### Acceptance Criteria

1. WHEN เกษตรกรถามเรื่องราคาด้วยคำต่างๆ เช่น "ราคาจะเป็นยังไง" "ขายตอนไหนดี" "ราคาจะขึ้นไหม", THE Chat System SHALL เข้าใจว่าต้องการทำนายราคา
2. WHEN เกษตรกรถามเรื่องพืชที่ควรปลูก, THE Chat System SHALL เรียกใช้ get_crop_recommendations function
3. WHEN เกษตรกรถามเรื่องการรดน้ำหรือจัดการน้ำ, THE Chat System SHALL เรียกใช้ get_water_management_advice function
4. THE Chat System SHALL สามารถเข้าใจคำถามที่มีการพิมพ์ผิดเล็กน้อย
5. THE Chat System SHALL สามารถเข้าใจคำถามที่ใช้ภาษาพูดหรือภาษาถิ่น

### Requirement 4

**User Story:** ในฐานะเกษตรกร ฉันต้องการให้ AI จำบริบทการสนทนา เพื่อไม่ต้องบอกข้อมูลซ้ำๆ

#### Acceptance Criteria

1. WHEN เกษตรกรถามคำถามต่อเนื่อง, THE Chat System SHALL จำบริบทจากคำถามก่อนหน้า
2. WHEN เกษตรกรพูดถึง "พืชนั้น" หรือ "จังหวัดนั้น", THE Chat System SHALL เข้าใจว่าหมายถึงพืชหรือจังหวัดที่พูดถึงก่อนหน้า
3. THE Chat System SHALL เก็บประวัติการสนทนาไว้ในฐานข้อมูล
4. THE Chat System SHALL ใช้ข้อมูล user profile เพื่อให้คำแนะนำที่เหมาะสม

### Requirement 5

**User Story:** ในฐานะนักพัฒนา ฉันต้องการให้ระบบมีโครงสร้างที่ชัดเจน เพื่อง่ายต่อการบำรุงรักษาและขยายความสามารถ

#### Acceptance Criteria

1. THE Backend Chat Router SHALL แยก logic การจัดการ prompt ออกเป็น service
2. THE Chat System SHALL มี error handling ที่ครอบคลุม
3. THE Chat System SHALL log ข้อมูลสำคัญเพื่อการ debug
4. THE Frontend Chat Component SHALL แยก logic การแสดงกราฟออกเป็น component ย่อย
5. THE Chat System SHALL มี timeout protection สำหรับ API calls

### Requirement 6

**User Story:** ในฐานะเกษตรกร ฉันต้องการให้กราฟแสดงข้อมูลที่เข้าใจง่าย เพื่อตัดสินใจได้อย่างมั่นใจ

#### Acceptance Criteria

1. THE Price Forecast Chart SHALL แสดงวันที่บนแกน X และราคาบนแกน Y
2. THE Price Forecast Chart SHALL ใช้สีที่แตกต่างกันระหว่างข้อมูลจริงและข้อมูลทำนาย
3. THE Price Forecast Chart SHALL แสดง tooltip เมื่อ hover เหนือจุดข้อมูล
4. THE Price Forecast Chart SHALL แสดงช่วงความเชื่อมั่น (confidence interval) ของการทำนาย
5. THE Price Forecast Chart SHALL responsive และแสดงผลได้ดีบนมือถือ

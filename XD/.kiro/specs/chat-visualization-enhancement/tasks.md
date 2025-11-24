# Implementation Plan

- [x] 1. ปรับปรุง Backend Prompt System

  - สร้าง PromptBuilderService เพื่อสร้าง context ที่เหมาะสมตามบริบท
  - เพิ่ม intent recognition สำหรับวิเคราะห์ความตั้งใจของคำถาม
  - ปรับปรุง AGRI_PERSONA ให้เป็นธรรมชาติและลื่นไหลมากขึ้น
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 1.1 สร้าง PromptBuilderService


  - สร้างไฟล์ backend/app/services/prompt_builder_service.py
  - Implement build_context() method สำหรับสร้าง context
  - Implement analyze_intent() method สำหรับวิเคราะห์ความตั้งใจ
  - Implement format_response_instruction() method
  - เพิ่ม intent patterns สำหรับ price prediction, crop recommendation, water management
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 1.2 ปรับปรุง AGRI_PERSONA


  - แก้ไขไฟล์ backend/utils/constants.py
  - ลดการใช้ markdown formatting (**, __, etc.)
  - เพิ่มตัวอย่างการตอบที่เป็นธรรมชาติ
  - เพิ่มคำแนะนำการปรับความยาวคำตอบตามคำถาม
  - เพิ่มคำแนะนำการใช้อิโมจิแทน markdown
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.3 อัพเดท chat.py ให้ใช้ PromptBuilderService


  - แก้ไขไฟล์ backend/app/routers/chat.py
  - Import และใช้ PromptBuilderService
  - ปรับ context building ให้ใช้ service แทน
  - เพิ่ม conversation history tracking
  - _Requirements: 1.1, 3.1, 4.1, 4.2, 4.3_

- [x] 2. สร้าง Response Formatter และ Chart Data Handler


  - สร้าง ResponseFormatter class เพื่อจัดรูปแบบ response
  - เพิ่มการแยกข้อมูลกราฟจาก function result
  - อัพเดท chat endpoint ให้ส่งข้อมูลกราฟกลับไป
  - _Requirements: 2.1, 2.2, 5.1, 5.2, 5.3_

- [x] 2.1 สร้าง ResponseFormatter Service



  - สร้างไฟล์ backend/app/services/response_formatter_service.py
  - Implement format_with_chart() method
  - Implement extract_chart_data() method สำหรับ price forecast
  - เพิ่ม validation สำหรับ chart data
  - _Requirements: 2.1, 2.2, 5.3_

- [x] 2.2 อัพเดท price_forecast_service.py


  - แก้ไขไฟล์ backend/app/services/price_forecast_service.py
  - เพิ่ม method get_historical_data() เพื่อดึงข้อมูลย้อนหลัง
  - ปรับ forecast_price() ให้ return ทั้งข้อมูลย้อนหลังและทำนาย
  - เพิ่ม confidence interval calculation
  - _Requirements: 2.1, 2.2, 6.4_

- [x] 2.3 อัพเดท chat.py ให้ส่งข้อมูลกราฟ


  - แก้ไขไฟล์ backend/app/routers/chat.py
  - Import และใช้ ResponseFormatter
  - ปรับ response structure ให้รวม chart_data
  - เพิ่ม error handling สำหรับ chart data
  - _Requirements: 2.2, 2.3, 5.2, 5.3_

- [x] 3. สร้าง Frontend Chart Components


  - สร้าง ChartMessage component สำหรับแสดงข้อความพร้อมกราฟ
  - สร้าง PriceForecastChart component สำหรับแสดงกราฟทำนายราคา
  - อัพเดท ChatInterface ให้รองรับ chart messages
  - _Requirements: 2.3, 2.4, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 สร้าง PriceForecastChart Component


  - สร้างไฟล์ frontend/src/components/chat/PriceForecastChart.tsx
  - ใช้ Recharts library สำหรับแสดงกราฟ
  - แสดง line chart พร้อม historical และ forecast data
  - เพิ่ม bridge point เชื่อมต่อระหว่างข้อมูลจริงและทำนาย
  - แสดง confidence interval เป็น area chart
  - เพิ่ม tooltip แสดงรายละเอียดเมื่อ hover
  - ทำให้ responsive สำหรับมือถือ
  - _Requirements: 2.4, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.2 สร้าง ChartMessage Component


  - สร้างไฟล์ frontend/src/components/chat/ChartMessage.tsx
  - แสดงข้อความ text response
  - แสดง PriceForecastChart เมื่อมีข้อมูลกราฟ
  - เพิ่ม loading state
  - เพิ่ม error handling
  - _Requirements: 2.3, 6.5_

- [x] 3.3 อัพเดท ChatInterface


  - แก้ไขไฟล์ frontend/src/components/ChatInterface.tsx (หรือไฟล์ที่เกี่ยวข้อง)
  - Import ChartMessage component
  - ตรวจสอบ response ว่ามี chart_data หรือไม่
  - แสดง ChartMessage เมื่อมีข้อมูลกราฟ
  - แสดง TextMessage ปกติเมื่อไม่มีกราฟ
  - _Requirements: 2.3, 5.4_

- [ ] 4. ปรับปรุง Error Handling และ Logging
  - เพิ่ม comprehensive error handling ใน chat endpoint
  - เพิ่ม logging สำหรับ debugging
  - เพิ่ม fallback responses
  - _Requirements: 5.2, 5.3, 5.5_

- [ ] 4.1 ปรับปรุง Error Handling ใน chat.py
  - แก้ไขไฟล์ backend/app/routers/chat.py
  - เพิ่ม specific error handling สำหรับ Gemini API errors
  - เพิ่ม fallback responses ที่เป็นธรรมชาติ
  - เพิ่ม timeout protection
  - _Requirements: 5.2, 5.3, 5.5_

- [ ] 4.2 เพิ่ม Logging
  - เพิ่ม detailed logging ใน PromptBuilderService
  - เพิ่ม logging ใน ResponseFormatter
  - เพิ่ม logging สำหรับ function calls
  - Log intent recognition results
  - _Requirements: 5.3_

- [ ] 5. เพิ่ม Conversation History Tracking
  - อัพเดท database schema สำหรับเก็บ conversation history
  - เพิ่ม API endpoint สำหรับดึง conversation history
  - อัพเดท chat endpoint ให้ใช้ history ในการสร้าง context
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 5.1 อัพเดท Database Schema
  - แก้ไขไฟล์ backend/database.py
  - เพิ่ม conversation_history field ใน ChatSession model
  - เพิ่ม user_id foreign key ถ้ายังไม่มี
  - สร้าง migration script
  - _Requirements: 4.3_

- [ ] 5.2 อัพเดท chat.py ให้ track history
  - แก้ไขไฟล์ backend/app/routers/chat.py
  - ดึง conversation history จาก database
  - ส่ง history ไปยัง PromptBuilderService
  - บันทึก conversation history หลังจากตอบ
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 6. Testing และ Validation
  - เขียน integration tests สำหรับ chat endpoint
  - ทดสอบ chart rendering บน frontend
  - ทดสอบ error scenarios
  - ทดสอบ mobile responsiveness
  - _Requirements: All_

- [ ] 6.1 เขียน Backend Tests
  - สร้างไฟล์ backend/tests/test_chat_enhancement.py
  - Test PromptBuilderService.analyze_intent()
  - Test ResponseFormatter.extract_chart_data()
  - Test chat endpoint with various queries
  - Test error handling
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 6.2 เขียน Frontend Tests
  - สร้างไฟล์ frontend/src/components/chat/__tests__/PriceForecastChart.test.tsx
  - Test PriceForecastChart rendering
  - Test ChartMessage rendering
  - Test responsive behavior
  - _Requirements: 6.5_

- [ ] 6.3 Manual Testing
  - ทดสอบการสนทนาด้วยคำถามต่างๆ
  - ทดสอบการแสดงกราฟ
  - ทดสอบบนมือถือ
  - ทดสอบ error scenarios
  - _Requirements: All_

- [ ] 7. Documentation และ Deployment
  - อัพเดท API documentation
  - สร้าง user guide สำหรับ chat features
  - Deploy to staging environment
  - _Requirements: All_

- [ ] 7.1 อัพเดท Documentation
  - อัพเดทไฟล์ README.md
  - เพิ่ม API documentation สำหรับ chart_data response
  - เพิ่ม examples ของ chat queries
  - _Requirements: All_

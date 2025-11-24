# Implementation Plan

- [x] 1. อัพเดท User interface ใน useAuth hook


  - เพิ่มฟิลด์ province (optional) ใน User interface
  - ตรวจสอบว่า hook ยังคงทำงานได้ปกติกับข้อมูลเดิม
  - _Requirements: 2.3_



- [ ] 2. เพิ่ม auto-select province ในหน้า DashboardOverview
  - เพิ่ม useEffect เพื่อตั้งค่า selectedProvince จาก user.province
  - ตรวจสอบว่า province ที่เก็บไว้มีอยู่ในรายการจังหวัดจริง


  - จัดการกรณีที่ user ไม่มี province หรือไม่ได้ login
  - _Requirements: 1.2, 1.3, 1.4_

- [x] 3. ทดสอบ login flow



  - ทดสอบ login ด้วย user ที่มี province
  - ตรวจสอบว่า province ถูกเก็บใน localStorage
  - ตรวจสอบว่า useAuth hook อ่านข้อมูล province ได้ถูกต้อง
  - _Requirements: 1.1, 2.2, 2.4_

- [ ] 4. ทดสอบ Overview page behavior
  - ทดสอบ auto-select province เมื่อเปิดหน้า Overview
  - ทดสอบการเปลี่ยนจังหวัดด้วยตัวเอง
  - ทดสอบ refresh page และ navigation
  - ทดสอบกรณี edge cases (no province, invalid province, guest user)
  - _Requirements: 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4_

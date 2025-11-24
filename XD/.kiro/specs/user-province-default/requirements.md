# Requirements Document

## Introduction

ฟีเจอร์นี้จะทำให้หน้า Overview แสดงข้อมูลของจังหวัดที่ผู้ใช้อยู่เป็นค่าเริ่มต้นโดยอัตโนมัติ แทนที่จะต้องให้ผู้ใช้เลือกจังหวัดทุกครั้งที่เข้าหน้า Overview ระบบจะดึงข้อมูลจังหวัดจากโปรไฟล์ผู้ใช้และแสดงข้อมูลของจังหวัดนั้นทันที

## Glossary

- **Frontend**: ส่วนแสดงผลของแอปพลิเคชันที่ผู้ใช้โต้ตอบด้วย (React/TypeScript)
- **Backend**: ส่วนเซิร์ฟเวอร์ที่จัดการข้อมูลและ API (FastAPI/Python)
- **User Profile**: ข้อมูลส่วนตัวของผู้ใช้ที่เก็บในฐานข้อมูล รวมถึงจังหวัดที่อยู่
- **Overview Page**: หน้าแสดงภาพรวมข้อมูลเกษตรกรรมของจังหวัด (DashboardOverview component)
- **Auth System**: ระบบการยืนยันตัวตนและจัดการข้อมูลผู้ใช้
- **LocalStorage**: พื้นที่เก็บข้อมูลในเบราว์เซอร์ของผู้ใช้

## Requirements

### Requirement 1

**User Story:** ในฐานะผู้ใช้ที่ลงทะเบียนแล้ว ฉันต้องการให้หน้า Overview แสดงข้อมูลจังหวัดของฉันโดยอัตโนมัติ เพื่อที่ฉันจะได้ไม่ต้องเลือกจังหวัดทุกครั้งที่เข้าหน้านี้

#### Acceptance Criteria

1. WHEN ผู้ใช้เข้าสู่ระบบสำเร็จ, THE Auth System SHALL เก็บข้อมูล province ของผู้ใช้ใน LocalStorage พร้อมกับข้อมูลผู้ใช้อื่นๆ
2. WHEN ผู้ใช้เปิดหน้า Overview, THE Frontend SHALL ดึงข้อมูล province จาก LocalStorage และตั้งค่าเป็นจังหวัดที่เลือกโดยอัตโนมัติ
3. IF ผู้ใช้ไม่มีข้อมูล province ในโปรไฟล์, THEN THE Overview Page SHALL แสดงข้อความให้เลือกจังหวัดเหมือนเดิม
4. THE Overview Page SHALL โหลดข้อมูลแดชบอร์ดของจังหวัดที่ตั้งค่าไว้โดยอัตโนมัติ

### Requirement 2

**User Story:** ในฐานะผู้ใช้ ฉันต้องการให้ข้อมูล province ถูกเก็บไว้ในโปรไฟล์ของฉัน เพื่อให้ระบบสามารถใช้ข้อมูลนี้แสดงผลในหน้าต่างๆ ได้

#### Acceptance Criteria

1. WHEN ผู้ใช้ลงทะเบียนและระบุจังหวัด, THE Backend SHALL เก็บข้อมูล province ในฐานข้อมูล
2. WHEN ผู้ใช้เข้าสู่ระบบ, THE Backend SHALL ส่งข้อมูล province กลับมาพร้อมกับข้อมูลผู้ใช้อื่นๆ
3. THE User Profile interface ใน Frontend SHALL มีฟิลด์ province เพื่อเก็บข้อมูลจังหวัด
4. THE Auth System SHALL อัพเดทข้อมูล province ใน LocalStorage ทุกครั้งที่มีการเข้าสู่ระบบหรือลงทะเบียน

### Requirement 3

**User Story:** ในฐานะผู้ใช้ ฉันยังคงต้องการสามารถเปลี่ยนจังหวัดที่แสดงในหน้า Overview ได้ เพื่อดูข้อมูลของจังหวัดอื่นๆ

#### Acceptance Criteria

1. THE Overview Page SHALL ยังคงแสดง ProvinceSelector component ให้ผู้ใช้สามารถเปลี่ยนจังหวัดได้
2. WHEN ผู้ใช้เลือกจังหวัดใหม่จาก ProvinceSelector, THE Overview Page SHALL โหลดข้อมูลของจังหวัดที่เลือกใหม่
3. THE Overview Page SHALL ไม่บันทึกการเปลี่ยนแปลงจังหวัดที่เลือกลงในโปรไฟล์ผู้ใช้ (เป็นเพียงการเปลี่ยนชั่วคราว)
4. WHEN ผู้ใช้รีเฟรชหน้าหรือกลับมาที่หน้า Overview อีกครั้ง, THE Overview Page SHALL แสดงจังหวัดจากโปรไฟล์ผู้ใช้อีกครั้ง

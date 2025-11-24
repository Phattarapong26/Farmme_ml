# Implementation Plan

## Overview

แผนการดำเนินงานนี้แบ่งการปรับโครงสร้างเอกสารออกเป็น 4 phases หลัก โดยแต่ละ phase จะมีงานย่อยที่ชัดเจนและสามารถทำได้ทีละขั้นตอน งานที่มีเครื่องหมาย * คืองานเสริมที่ไม่จำเป็นต่อการทำงานหลัก

---

## Phase 1: Core Structure Setup

- [x] 1. สร้างโครงสร้างเอกสารใหม่



  - สร้างไฟล์เอกสารใหม่ 5 บท
  - สร้างโครงสร้างหัวข้อหลักในแต่ละบท
  - สร้างไฟล์ metadata สำหรับข้อมูลอาจารย์และวิชา



  - _Requirements: 1.1, 1.2, 1.3, 9.1_

- [x] 2. ปรับบทที่ 1: บทนำ


  - [x] 2.1 เพิ่มข้อมูลอาจารย์ที่ปรึกษา 3 คน

    - เพิ่ม section สำหรับข้อมูลอาจารย์
    - จัดรูปแบบให้เป็นมาตรฐานวิชาการ
    - _Requirements: 1.1_


  

  - [x] 2.2 เพิ่มข้อมูลวิชาที่เกี่ยวข้อง 3 วิชา

    - เพิ่ม section สำหรับรายชื่อวิชา
    - ระบุรหัสวิชาและชื่อวิชา

    - _Requirements: 1.2_
  


  - [ ] 2.3 ปรับประโยชน์ที่คาดว่าจะได้รับให้วัดได้จริง
    - ลบประโยชน์ที่วัดไม่ได้ (เช่น "เพิ่มรายได้ 15-30%")
    - แทนที่ด้วยประโยชน์ที่วัดได้ (เช่น "R² = 0.47", "MAE = 13.31")
    - เน้นประโยชน์ของแอปพลิเคชันที่ทำได้จริง
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 2.4 แปลงภาษาพูดเป็นภาษาเขียนในบทที่ 1


    - แปลงคำถาม "ควรปลูกเมื่อใด" เป็น "การกำหนดช่วงเวลาการเพาะปลูก"
    - แปลงคำถาม "ควรเลือกอะไร" เป็น "การเลือกชนิดพืชที่เหมาะสม"
    - ตรวจสอบและแก้ไขภาษาพูดทั้งหมด
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

---

## Phase 2: Restructure Theory and Methodology







- [x] 3. สร้างบทที่ 2 ใหม่: ทฤษฎีและงานวิจัยที่เกี่ยวข้อง

  - [x] 3.1 ย้ายเนื้อหาทฤษฎีจาก Chapter3_Background_RelatedWork.md

    - ย้าย Section 3.2-3.6 (ML, MOEA, Time Series, Bandits, Data Leakage)
    - ลบ Section 3.1 (Introduction/บทนำ)
    - จัดระเบียบเป็น Section 2.2 (ทฤษฎีที่เกี่ยวข้อง)
    - _Requirements: 2.1, 2.2, 2.6_

  
  - [x] 3.2 ย้ายงานวิจัยที่เกี่ยวข้อง

    - ย้าย Section 3.7 (Related Systems)
    - จัดระเบียบเป็น Section 2.3 (งานวิจัยที่เกี่ยวข้อง)
    - _Requirements: 2.1_

  
  - [x] 3.3 เพิ่มนิยามศัพท์เฉพาะในบทที่ 2

    - สร้าง Section 2.1 สำหรับนิยามศัพท์
    - ขยายความนิยามให้ยาวกว่าเดิม
    - รวมศัพท์เทคนิคทั้งหมดที่ใช้ในเอกสาร

    - _Requirements: 2.5_
  










  - [ ] 3.4 แปลง bullet points เป็นย่อหน้าในบทที่ 2
    - แปลงรายการทฤษฎีเป็นย่อหน้าที่ต่อเนื่อง
    - รักษา bullet points เฉพาะรายการขั้นตอนและสูตร
    - เขียนให้เป็นพารากราฟที่อ่านง่าย
    - _Requirements: 2.4, 8.1, 8.2, 8.3, 8.4_
  
  - [x] 3.5 ลบการอธิบายการนำไปใช้ออกจากบทที่ 2


    - ลบส่วนที่อธิบายว่าใช้ทฤษฎีอย่างไร
    - เก็บเฉพาะคำอธิบายทฤษฎีเท่านั้น
    - _Requirements: 2.6_

- [x] 4. สร้างบทที่ 3 ใหม่: การดำเนินงาน


  - [ ] 4.1 สร้างโครงสร้างบทที่ 3 ตามลำดับขั้นตอน
    - สร้าง Section 3.1: ภาพรวมกระบวนการวิจัย
    - สร้าง Section 3.2: Data Collection
    - สร้าง Section 3.3: EDA


    - สร้าง Section 3.4: Feature Engineering
    - สร้าง Section 3.5: Feature Selection
    - สร้าง Section 3.6: Model Training
    - สร้าง Section 3.7: Train/Test Split
    - สร้าง Section 3.8: Evaluation Metrics

    - สร้าง Section 3.9: Error Analysis

    - สร้าง Section 3.10: Application Development
    - _Requirements: 3.1_
  

  - [-] 4.2 ย้ายเนื้อหา Data Generation มาบทที่ 3

    - ย้ายจาก Chapter2_Data_Generation_Detailed.md
    - ใส่ใน Section 3.2 (Data Collection)
    - ระบุแหล่งที่มาของข้อมูล (Synthetic Data)
    - อธิบาย GPU-Accelerated Generation
    - _Requirements: 3.4_
  

  - [ ] 4.3 เขียน Section 3.3: EDA
    - อธิบายการวิเคราะห์เชิงสถิติ
    - อธิบาย Correlation Analysis
    - อธิบาย Temporal Patterns
    - _Requirements: 3.1_

  
  - [ ] 4.4 เขียน Section 3.4: Feature Engineering
    - อธิบายการทำ one-hot encoding (ระบุข้อมูลชุดใด)
    - อธิบาย Temporal Features
    - อธิบาย Cyclical Encoding
    - ระบุว่าใช้ทฤษฎีใดจากบทที่ 2
    - _Requirements: 3.2, 3.3_

  
  - [ ] 4.5 เขียน Section 3.5: Feature Selection
    - อธิบาย Feature Importance Analysis
    - อธิบาย Correlation-based Selection
    - อธิบาย Data Leakage Prevention

    - _Requirements: 3.1_
  
  - [ ] 4.6 เขียน Section 3.6: Model Training
    - ย้ายเนื้อหาจาก Chapter4-7 (Models)
    - อธิบาย Model A: Crop Recommendation (NSGA-II + XGBoost)
    - อธิบาย Model B: Planting Window (Logistic Regression)
    - อธิบาย Model C: Price Forecasting (XGBoost)
    - อธิบาย Model D: Harvest Timing (Thompson Sampling)
    - ระบุว่าใช้ทฤษฎีใดจากบทที่ 2 ในแต่ละโมเดล





    - _Requirements: 3.2, 3.6_
  
  - [ ] 4.7 เขียน Section 3.7: Train/Test Split
    - อธิบาย Temporal Split Strategy
    - ระบุ Split Ratio (70/30 หรือ 80/20)
    - อธิบาย Validation Strategy
    - _Requirements: 3.7_

  
  - [ ] 4.8 เขียน Section 3.8: Evaluation Metrics
    - ระบุตัววัดประสิทธิภาพแต่ละโมเดล
    - R² Score (Crop Recommendation)
    - F1 Score (Planting Window)
    - MAE (Price Forecasting)
    - Accuracy (Harvest Timing)

    - _Requirements: 3.8_
  
  - [ ] 4.9 เขียน Section 3.9: Error Analysis
    - อธิบาย Temporal Bias Analysis
    - อธิบาย Data Leakage Detection

    - อธิบาย Model Diagnostics
    - _Requirements: 3.1_
  
  - [x] 4.10 เขียน Section 3.10: Application Development

    - ย้ายเนื้อหาจาก Chapter8 (System Integration)
    - อธิบาย Backend Architecture
    - อธิบาย Frontend Design
    - อธิบาย API Integration
    - อธิบาย Deployment Strategy
    - _Requirements: 3.9_

---

## Phase 3: Results and Discussion

- [ ] 5. ปรับบทที่ 4: ผลการทดลอง
  - [ ] 5.1 สร้างโครงสร้างบทที่ 4
    - สร้าง Section 4.1: ภาพรวมผลการทดลอง
    - สร้าง Section 4.2: Model A Results (เน้นหลัก)
    - สร้าง Section 4.3: Model B-D Results (ถ้ามีเวลา)
    - สร้าง Section 4.4: แดชบอร์ด
    - สร้าง Section 4.5: สรุปตามวัตถุประสงค์
    - สร้าง Section 4.6: สรุปตามขอบเขต
    - _Requirements: 4.1_
  
  - [ ] 5.2 เขียน Section 4.2: Model A Crop Recommendation Results
    - ย้ายผลการทดลองจาก Chapter9
    - สร้างตารางเปรียบเทียบโมเดล
    - ระบุโมเดลที่ดีที่สุด (NSGA-II + XGBoost)
    - แสดง R² Score และ Metrics อื่นๆ
    - เพิ่ม Case Studies
    - _Requirements: 4.2, 4.6_
  
  - [ ] 5.3 เขียน Section 4.3: Model B-D Results (ถ้ามีเวลา)
    - สรุปผล Model B: Planting Window
    - สรุปผล Model C: Price Forecasting
    - สรุปผล Model D: Harvest Timing
    - _Requirements: 4.6_
  
  - [ ] 5.4 เขียน Section 4.4: แดชบอร์ด
    - เพิ่มภาพหน้าจอแดชบอร์ด
    - เขียนคำอธิบายการใช้งาน
    - _Requirements: 4.3_
  
  - [ ] 5.5 เขียน Section 4.5-4.6: สรุปตามวัตถุประสงค์และขอบเขต
    - เปรียบเทียบผลกับวัตถุประสงค์ในบทที่ 1
    - เปรียบเทียบผลกับขอบเขตในบทที่ 1
    - _Requirements: 4.4, 4.5_

- [x] 6. สร้างบทที่ 5: สรุปและอภิปรายผล




  - [x] 6.1 เขียน Section 5.1: สรุปผลการทดลอง

    - ย้ายเนื้อหาจาก Chapter10 (Discussion)
    - สรุปผลการทดลองทั้งหมด
    - _Requirements: 5.1_
  
  - [x] 6.2 เขียน Section 5.2: อภิปรายผล

    - อธิบายว่าทำไม XGBoost/NSGA-II ดีที่สุด
    - อ้างอิงงานวิจัยที่สนับสนุนผล
    - เปรียบเทียบกับงานอื่นที่คล้ายกัน
    - _Requirements: 5.2, 5.3_
  

  - [x] 6.3 เขียน Section 5.3: ข้อจำกัดของการวิจัย

    - ระบุ Synthetic Data Limitations
    - ระบุ Scope Limitations
    - ระบุ Technical Limitations
    - _Requirements: 5.4_
  
  - [x] 6.4 เขียน Section 5.4-5.5: ข้อเสนอแนะและงานในอนาคต

    - เขียนข้อเสนอแนะ
    - เขียนแนวทางการวิจัยในอนาคต
    - _Requirements: 5.5_

---

## Phase 4: Final Polish

- [x] 7. ปรับภาษาและรูปแบบทั้งเล่ม

  - [x] 7.1 แปลงภาษาพูดเป็นภาษาเขียนในทุกบท

    - ตรวจสอบบทที่ 2-5
    - แปลงคำถามและภาษาพูดทั้งหมด
    - ใช้คำศัพท์ทางวิชาการที่เหมาะสม
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 7.2 แปลง bullet points เป็นย่อหน้าในทุกบท

    - ตรวจสอบบทที่ 1-5
    - แปลงในส่วนที่เหมาะสม
    - รักษา bullets ที่จำเป็น (ขั้นตอน, รายการ)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 7.3 ตรวจสอบความสอดคล้องระหว่างบท

    - ตรวจสอบการอ้างอิงระหว่างบท
    - ตรวจสอบว่าวัตถุประสงค์สอดคล้องกับผล
    - ตรวจสอบว่าทฤษฎีถูกนำไปใช้
    - _Requirements: 9.2, 9.3, 9.4_

- [x] 8. จัดการบรรณานุกรม

  - [x] 8.1 รวบรวมเอกสารอ้างอิงทั้งหมด

    - สแกนเอกสารทั้งหมดหาการอ้างอิง
    - รวบรวมข้อมูลเอกสารอ้างอิง
    - _Requirements: 10.1_
  
  - [x] 8.2 จัดรูปแบบบรรณานุกรม

    - จัดรูปแบบตามมาตรฐาน APA หรือ IEEE
    - เรียงลำดับตามตัวอักษร
    - _Requirements: 10.2, 10.4_
  
  - [x] 8.3 ตรวจสอบความสมบูรณ์

    - ตรวจสอบว่าทุกการอ้างอิงมีในบรรณานุกรม
    - ตรวจสอบความซ้ำซ้อน
    - _Requirements: 10.3_

- [x] 9. Final Review และ Validation


  - [x] 9.1 ตรวจสอบโครงสร้างทั้งเล่ม

    - ตรวจสอบว่ามีครบ 5 บท
    - ตรวจสอบว่าแต่ละบทมี sections ครบ
    - _Requirements: 9.1_
  

  - [x] 9.2 ตรวจสอบเนื้อหาทางเทคนิค

    - ตรวจสอบความถูกต้องของข้อมูล
    - ตรวจสอบตัวเลขและสถิติ
    - _Requirements: 9.2, 9.3, 9.4_
  

  - [x] 9.3 ตรวจสอบภาษาและรูปแบบ

    - ตรวจสอบไวยากรณ์
    - ตรวจสอบความสม่ำเสมอของรูปแบบ
    - _Requirements: 6.4, 8.3_
  


  - [x] 9.4 สร้างเอกสารสรุปการเปลี่ยนแปลง

    - สร้างไฟล์ RESTRUCTURE_SUMMARY.md
    - สรุปการเปลี่ยนแปลงหลัก
    - ระบุสิ่งที่ปรับปรุง

---

## Notes

- งานที่มีเครื่องหมาย * คืองานเสริมที่ไม่จำเป็นต่อการทำงานหลัก
- แต่ละงานควรทำทีละขั้นตอนและตรวจสอบผลก่อนไปต่อ
- ควร backup เอกสารเดิมก่อนเริ่มแก้ไข
- ควรทำ git commit หลังจากเสร็จแต่ละ task หลัก

## Estimated Timeline

- Phase 1: 2-3 ชั่วโมง (Tasks 1-2)
- Phase 2: 4-6 ชั่วโมง (Tasks 3-4)
- Phase 3: 2-3 ชั่วโมง (Tasks 5-6)
- Phase 4: 1-2 ชั่วโมง (Tasks 7-9)

**Total**: 9-14 ชั่วโมง

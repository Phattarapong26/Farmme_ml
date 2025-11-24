# Design Document

## Overview

การออกแบบการปรับโครงสร้างเอกสารวิชาการ FarmMe จะเน้นการแปลงจากโครงสร้างแบบ model-centric (แยกตามโมเดล) ไปเป็น process-centric (แยกตามขั้นตอนการวิจัย) โดยรักษาเนื้อหาทางเทคนิคที่มีอยู่แล้วและจัดระเบียบใหม่ให้สอดคล้องกับมาตรฐานเอกสารวิชาการ

## Architecture

### โครงสร้างเอกสารใหม่

```
หน้าปก (Cover Page)
├── ชื่อเอกสาร
├── ชื่อผู้เขียน
├── อาจารย์ที่ปรึกษา 3 คน
└── วิชาที่เกี่ยวข้อง 3 วิชา

บทคัดย่อ (Abstract)

บทที่ 1: บทนำ (Introduction)
├── 1.1 ความเป็นมาและความสำคัญ
├── 1.2 วัตถุประสงค์
├── 1.3 ขอบเขต
├── 1.4 ประโยชน์ที่คาดว่าจะได้รับ (ปรับให้วัดได้จริง)
└── 1.5 โครงสร้างเอกสาร

บทที่ 2: ทฤษฎีและงานวิจัยที่เกี่ยวข้อง (Background and Related Work)
├── 2.1 นิยามศัพท์เฉพาะ (ขยายความ)
├── 2.2 ทฤษฎีที่เกี่ยวข้อง
│   ├── 2.2.1 Machine Learning Fundamentals
│   ├── 2.2.2 Multi-Objective Optimization (NSGA-II)
│   ├── 2.2.3 Gradient Boosting (XGBoost)
│   ├── 2.2.4 Time Series Forecasting
│   ├── 2.2.5 Multi-Armed Bandits (Thompson Sampling)
│   └── 2.2.6 Data Leakage Prevention
└── 2.3 งานวิจัยที่เกี่ยวข้อง
    ├── 2.3.1 Agricultural ML Systems
    ├── 2.3.2 Crop Recommendation Systems
    ├── 2.3.3 Price Forecasting Systems
    └── 2.3.4 Decision Support Systems

บทที่ 3: การดำเนินงาน (Methodology)
├── 3.1 ภาพรวมกระบวนการวิจัย
├── 3.2 การเก็บรวบรวมข้อมูล (Data Collection)
│   ├── แหล่งข้อมูล
│   ├── GPU-Accelerated Data Generation
│   └── Dataset Specifications
├── 3.3 การวิเคราะห์เชิงสำรวจ (Exploratory Data Analysis)
│   ├── Statistical Analysis
│   ├── Correlation Analysis
│   └── Temporal Patterns
├── 3.4 การสร้างฟีเจอร์ (Feature Engineering)
│   ├── One-hot Encoding (ระบุข้อมูลชุดใด)
│   ├── Temporal Features
│   ├── Cyclical Encoding
│   └── การใช้ทฤษฎีจากบทที่ 2
├── 3.5 การคัดเลือกฟีเจอร์ (Feature Selection)
│   ├── Feature Importance Analysis
│   ├── Correlation-based Selection
│   └── Data Leakage Prevention
├── 3.6 การสร้างและฝึกโมเดล (Model Training)
│   ├── Model A: Crop Recommendation (NSGA-II + XGBoost)
│   ├── Model B: Planting Window (Logistic Regression)
│   ├── Model C: Price Forecasting (XGBoost)
│   └── Model D: Harvest Timing (Thompson Sampling)
├── 3.7 การแบ่งข้อมูล (Train/Test Split)
│   ├── Temporal Split Strategy
│   ├── Split Ratio (70/30 หรือ 80/20)
│   └── Validation Strategy
├── 3.8 ตัววัดประสิทธิภาพ (Evaluation Metrics)
│   ├── R² Score (Crop Recommendation)
│   ├── F1 Score (Planting Window)
│   ├── MAE (Price Forecasting)
│   └── Accuracy (Harvest Timing)
├── 3.9 การวิเคราะห์ข้อผิดพลาด (Error Analysis)
│   ├── Temporal Bias Analysis
│   ├── Data Leakage Detection
│   └── Model Diagnostics
└── 3.10 การพัฒนาแอปพลิเคชัน (Application Development)
    ├── Backend Architecture
    ├── Frontend Design
    ├── API Integration
    └── Deployment Strategy

บทที่ 4: ผลการทดลอง (Experimental Results)
├── 4.1 ภาพรวมผลการทดลอง
├── 4.2 ผลการทดลอง Model A: Crop Recommendation (เน้นหลัก)
│   ├── ตารางเปรียบเทียบโมเดล
│   ├── โมเดลที่ดีที่สุด (NSGA-II + XGBoost)
│   ├── R² Score และ Metrics อื่นๆ
│   └── Case Studies
├── 4.3 ผลการทดลอง Model B-D (ถ้ามีเวลา)
│   ├── Model B: Planting Window Results
│   ├── Model C: Price Forecasting Results
│   └── Model D: Harvest Timing Results
├── 4.4 แดชบอร์ดและ User Interface
│   ├── ภาพหน้าจอแดชบอร์ด
│   └── คำอธิบายการใช้งาน
├── 4.5 การสรุปตามวัตถุประสงค์
│   └── เทียบกับวัตถุประสงค์ในบทที่ 1
└── 4.6 การสรุปตามขอบเขต
    └── เทียบกับขอบเขตในบทที่ 1

บทที่ 5: สรุปและอภิปรายผล (Conclusion and Discussion)
├── 5.1 สรุปผลการทดลอง
├── 5.2 อภิปรายผล
│   ├── ทำไม XGBoost/NSGA-II ดีที่สุด
│   ├── การอ้างอิงงานวิจัยที่สนับสนุน
│   └── การเปรียบเทียบกับงานอื่น
├── 5.3 ข้อจำกัดของการวิจัย
│   ├── Synthetic Data Limitations
│   ├── Scope Limitations
│   └── Technical Limitations
├── 5.4 ข้อเสนอแนะ
└── 5.5 งานวิจัยในอนาคต

บรรณานุกรม (References)
└── รายการเอกสารอ้างอิงทั้งหมด (APA/IEEE format)

ภาคผนวก (Appendices)
├── ภาคผนวก ก: รายละเอียดข้อมูล
├── ภาคผนวก ข: โค้ดตัวอย่าง
└── ภาคผนวก ค: ตารางเพิ่มเติม
```

## Components and Interfaces

### 1. Document Transformation Engine

**Purpose**: แปลงเอกสารจากโครงสร้างเดิมเป็นโครงสร้างใหม่

**Input**:
- Chapter1_Introduction.md (เดิม)
- Chapter2_Data_Generation_Detailed.md (เดิม)
- Chapter3_Background_RelatedWork.md (เดิม)
- Chapter4-11 (เดิม)

**Output**:
- Chapter1_Introduction_New.md (ปรับแก้)
- Chapter2_Theory_RelatedWork_New.md (ใหม่)
- Chapter3_Methodology_New.md (ใหม่)
- Chapter4_Results_New.md (ใหม่)
- Chapter5_Conclusion_Discussion_New.md (ใหม่)

**Transformation Rules**:
1. เก็บเนื้อหาทางเทคนิคไว้ทั้งหมด
2. จัดระเบียบใหม่ตามโครงสร้างที่กำหนด
3. แปลงภาษาพูดเป็นภาษาเขียน
4. แปลง bullet points เป็นย่อหน้าในส่วนที่เหมาะสม
5. ลบประโยชน์ที่วัดไม่ได้

### 2. Content Reorganizer

**Purpose**: จัดระเบียบเนื้อหาให้อยู่ในบทที่เหมาะสม

**Mapping Rules**:

**จาก Chapter3_Background_RelatedWork.md → Chapter2_Theory_RelatedWork_New.md**:
- Section 3.2-3.6 (ทฤษฎี) → Chapter 2 Section 2.2
- Section 3.7 (งานวิจัย) → Chapter 2 Section 2.3
- ลบ Section 3.1 (Introduction)

**จาก Chapter2_Data_Generation_Detailed.md → Chapter3_Methodology_New.md**:
- Section 2.1-2.13 → Chapter 3 Section 3.2 (Data Collection)
- เพิ่มคำอธิบายว่าใช้ทฤษฎีใดจากบทที่ 2

**จาก Chapter4-7 (Models) → Chapter3_Methodology_New.md**:
- Model implementations → Chapter 3 Section 3.6
- Feature engineering → Chapter 3 Section 3.4
- Evaluation metrics → Chapter 3 Section 3.8

**จาก Chapter9 (Results) → Chapter4_Results_New.md**:
- All experimental results → Chapter 4
- เน้น Model A (Crop Recommendation)
- เพิ่มตารางเปรียบเทียบ

**จาก Chapter10 (Discussion) → Chapter5_Conclusion_Discussion_New.md**:
- Key findings → Chapter 5 Section 5.1
- Discussion → Chapter 5 Section 5.2
- Limitations → Chapter 5 Section 5.3

### 3. Language Converter

**Purpose**: แปลงภาษาพูดเป็นภาษาเขียนทางวิชาการ

**Conversion Rules**:

| ภาษาพูด | ภาษาเขียน |
|---------|-----------|
| "ควรปลูกพืชชนิดใด" | "การเลือกชนิดพืชที่เหมาะสม" |
| "ควรปลูกเมื่อใด" | "การกำหนดช่วงเวลาการเพาะปลูก" |
| "ราคาที่คาดว่าจะได้รับ" | "การพยากรณ์ราคาผลผลิต" |
| "ควรเก็บเกี่ยวเมื่อใด" | "การกำหนดเวลาการเก็บเกี่ยว" |
| "เพิ่มรายได้" | "ปรับปรุงประสิทธิภาพการตัดสินใจ" |

**Style Guidelines**:
- ใช้ประโยคความเดียว (simple sentences) สำหรับความชัดเจน
- ใช้ประโยคความรวม (compound sentences) สำหรับความเชื่อมโยง
- หลีกเลี่ยงคำถาม
- ใช้ passive voice เมื่อเหมาะสม
- ใช้ศัพท์เทคนิคอย่างสม่ำเสมอ

### 4. Format Converter

**Purpose**: แปลง bullet points เป็นย่อหน้า

**Conversion Strategy**:

**Keep as Bullets**:
- รายการขั้นตอน (step-by-step procedures)
- รายการคุณสมบัติ (feature lists)
- รายการเปรียบเทียบ (comparison lists)

**Convert to Paragraphs**:
- คำอธิบายแนวคิด (conceptual explanations)
- การอภิปราย (discussions)
- การสรุป (summaries)
- ความเป็นมาและความสำคัญ (background and motivation)

**Example Transformation**:

Before (Bullets):
```markdown
**ปัญหาและความท้าทาย**:
- เกษตรกรต้องตัดสินใจด้วยข้อมูลไม่สมบูรณ์
- ขาดเครื่องมือพยากรณ์
- ราคาผันผวนสูง
```

After (Paragraph):
```markdown
เกษตรกรไทยเผชิญกับความท้าทายในการตัดสินใจเนื่องจากข้อมูลที่ไม่สมบูรณ์และการขาดเครื่องมือพยากรณ์ที่เหมาะสม นอกจากนี้ ราคาสินค้าเกษตรมีความผันผวนสูง ทำให้การวางแผนการผลิตและการตลาดเป็นไปได้ยาก
```

### 5. Benefits Validator

**Purpose**: ตรวจสอบและปรับประโยชน์ให้วัดได้จริง

**Validation Rules**:

**Remove (ไม่สามารถวัดได้)**:
- "เพิ่มรายได้ 15-30%" (ไม่มีการทดสอบจริง)
- "ลดความยากจน" (วัดไม่ได้ในขอบเขตโครงการ)
- "ความมั่นคงด้านอาหาร" (ผลกระทบระดับมหภาค)

**Keep (วัดได้จริง)**:
- "ระบบสามารถแนะนำพืชได้ด้วย R² = 0.47"
- "โมเดลพยากรณ์ราคาได้ด้วย MAE = 13.31 บาท"
- "ระบบตัดสินใจเก็บเกี่ยวได้ด้วยความแม่นยำ 68%"
- "แอปพลิเคชันสามารถประมวลผลได้ภายใน 2 วินาที"

**Replacement Strategy**:
```
เดิม: "เพิ่มรายได้ของเกษตรกร 15-30%"
ใหม่: "ระบบสามารถแนะนำพืชที่เหมาะสมโดยพิจารณาปัจจัยหลายด้าน ได้แก่ ผลตอบแทน ความเสี่ยง และความยั่งยืน"

เดิม: "ลดความเสี่ยงจากสภาพอากาศ"
ใหม่: "ระบบสามารถจำแนกช่วงเวลาปลูกที่เหมาะสมได้ด้วย F1 Score = 0.70-0.75"
```

### 6. Reference Manager

**Purpose**: จัดการบรรณานุกรม

**Features**:
- รวบรวมการอ้างอิงทั้งหมดจากเนื้อหา
- จัดรูปแบบตามมาตรฐาน APA หรือ IEEE
- ตรวจสอบความสมบูรณ์
- เรียงลำดับตามตัวอักษร

**Reference Format (APA)**:
```
Author, A. A., & Author, B. B. (Year). Title of article. Title of Journal, volume(issue), pages. DOI

Example:
Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. IEEE Transactions on Evolutionary Computation, 6(2), 182-197. https://doi.org/10.1109/4235.996017
```

## Data Models

### Document Structure Model

```typescript
interface Document {
  metadata: {
    title: string;
    authors: string[];
    advisors: string[]; // 3 คน
    courses: string[]; // 3 วิชา
    date: Date;
  };
  
  chapters: Chapter[];
  references: Reference[];
  appendices: Appendix[];
}

interface Chapter {
  number: number;
  title: string;
  sections: Section[];
}

interface Section {
  number: string; // e.g., "3.2.1"
  title: string;
  content: Content[];
}

interface Content {
  type: 'paragraph' | 'list' | 'table' | 'figure' | 'equation';
  text: string;
  metadata?: {
    language: 'formal' | 'informal';
    hasLeakage?: boolean;
    measurable?: boolean;
  };
}

interface Reference {
  id: string;
  authors: string[];
  year: number;
  title: string;
  journal?: string;
  conference?: string;
  pages?: string;
  doi?: string;
}
```

### Content Mapping Model

```typescript
interface ContentMapping {
  source: {
    file: string;
    chapter: number;
    section: string;
  };
  
  destination: {
    file: string;
    chapter: number;
    section: string;
  };
  
  transformations: Transformation[];
}

interface Transformation {
  type: 'move' | 'rewrite' | 'format' | 'delete';
  rules: string[];
}
```

## Error Handling

### Validation Checks

1. **Structure Validation**
   - ตรวจสอบว่าทุกบทมีครบตามโครงสร้าง
   - ตรวจสอบการอ้างอิงระหว่างบท
   - ตรวจสอบความสมบูรณ์ของเนื้อหา

2. **Content Validation**
   - ตรวจสอบภาษาเขียน (ไม่มีภาษาพูด)
   - ตรวจสอบประโยชน์ที่วัดได้
   - ตรวจสอบการอ้างอิงทฤษฎี

3. **Reference Validation**
   - ตรวจสอบว่าทุกการอ้างอิงมีในบรรณานุกรม
   - ตรวจสอบรูปแบบการอ้างอิง
   - ตรวจสอบความซ้ำซ้อน

### Error Recovery

- สร้าง backup ของเอกสารเดิมก่อนแปลง
- บันทึก log ของการแปลงทั้งหมด
- สามารถ rollback ได้ถ้าเกิดข้อผิดพลาด

## Testing Strategy

### Unit Testing

1. **Language Converter Tests**
   - ทดสอบการแปลงภาษาพูดเป็นภาษาเขียน
   - ทดสอบการรักษาความหมายเดิม

2. **Format Converter Tests**
   - ทดสอบการแปลง bullets เป็นย่อหน้า
   - ทดสอบการรักษา bullets ที่จำเป็น

3. **Benefits Validator Tests**
   - ทดสอบการตรวจจับประโยชน์ที่วัดไม่ได้
   - ทดสอบการแทนที่ด้วยประโยชน์ที่วัดได้

### Integration Testing

1. **End-to-End Transformation**
   - ทดสอบการแปลงเอกสารทั้งเล่ม
   - ตรวจสอบความสมบูรณ์ของผลลัพธ์

2. **Cross-Reference Testing**
   - ทดสอบการอ้างอิงระหว่างบท
   - ตรวจสอบความสอดคล้องของเนื้อหา

### Manual Review

1. **Content Review**
   - ตรวจสอบความถูกต้องของเนื้อหา
   - ตรวจสอบความเหมาะสมของภาษา

2. **Structure Review**
   - ตรวจสอบโครงสร้างทั้งเล่ม
   - ตรวจสอบความต่อเนื่องของเนื้อหา

## Implementation Priorities

### Phase 1: Core Structure (สำคัญที่สุด)
1. สร้างโครงสร้างบทใหม่ทั้ง 5 บท
2. ย้ายเนื้อหาหลักไปยังบทที่เหมาะสม
3. ปรับบทที่ 1 (เพิ่มอาจารย์, วิชา, ปรับประโยชน์)

### Phase 2: Content Transformation
1. แปลงบทที่ 2 (ทฤษฎี + งานวิจัย)
2. สร้างบทที่ 3 ใหม่ (การดำเนินงาน)
3. ปรับบทที่ 4 (ผลการทดลอง)
4. ปรับบทที่ 5 (สรุปและอภิปราย)

### Phase 3: Language and Format
1. แปลงภาษาพูดเป็นภาษาเขียน
2. แปลง bullets เป็นย่อหน้า
3. ปรับประโยชน์ให้วัดได้

### Phase 4: References and Polish
1. รวบรวมและจัดรูปแบบบรรณานุกรม
2. ตรวจสอบความสมบูรณ์
3. Final review

## Success Criteria

เอกสารที่ปรับโครงสร้างแล้วจะถือว่าสำเร็จเมื่อ:

1. ✅ มีโครงสร้าง 5 บทตามที่กำหนด
2. ✅ บทที่ 1 มีอาจารย์ 3 คน และวิชา 3 วิชา
3. ✅ บทที่ 2 แยกเป็นทฤษฎีและงานวิจัย ไม่มีบทนำ
4. ✅ บทที่ 3 อธิบายการดำเนินงานตามลำดับ
5. ✅ บทที่ 4 เน้นผลการทดลอง Crop Recommendation
6. ✅ บทที่ 5 มีการอภิปรายและอ้างอิงงานวิจัย
7. ✅ ใช้ภาษาเขียนทางวิชาการทั้งเล่ม
8. ✅ ประโยชน์ที่ระบุวัดได้จริงทั้งหมด
9. ✅ เนื้อหาเขียนเป็นย่อหน้าในส่วนที่เหมาะสม
10. ✅ มีบรรณานุกรมที่สมบูรณ์

## Timeline Estimate

- Phase 1: 2-3 ชั่วโมง
- Phase 2: 4-6 ชั่วโมง
- Phase 3: 2-3 ชั่วโมง
- Phase 4: 1-2 ชั่วโมง

**Total**: 9-14 ชั่วโมง (ประมาณ 2-3 วันทำงาน)

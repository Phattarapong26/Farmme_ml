# เอกสารวิชาการ FarmMe ML System

## สถานะ: กำลังสร้าง

เนื่องจากเอกสารมีความยาวมาก (มากกว่า 100 หน้า) จึงแบ่งออกเป็นส่วนๆ ดังนี้:

### ไฟล์ที่สร้างแล้ว:
1. ✅ `part1_cover_and_intro.md` - หน้าปก คำนำ สารบัญ
2. ✅ `chapter1.md` - บทที่ 1 บทนำ

### ไฟล์ที่กำลังสร้าง:
3. ⏳ `chapter2.md` - บทที่ 2 ทฤษฎีและงานวิจัยที่เกี่ยวข้อง
4. ⏳ `chapter3.md` - บทที่ 3 การดำเนินงาน
5. ⏳ `chapter4.md` - บทที่ 4 ผลลัพธ์
6. ⏳ `chapter5.md` - บทที่ 5 สรุป
7. ⏳ `appendix.md` - ภาคผนวก

## วิธีรวมเอกสารทั้งหมด

### วิธีที่ 1: ใช้ Python Script (แนะนำ)

```python
# รันคำสั่งนี้เพื่อสร้างเอกสารฉบับสมบูรณ์
python documentation/compile_document.py
```

### วิธีที่ 2: รวมด้วยตนเอง

1. เปิดไฟล์ทั้งหมดตามลำดับ
2. Copy เนื้อหาไปยัง Word Document
3. จัดรูปแบบตามต้องการ

### วิธีที่ 3: ใช้ Pandoc (สำหรับผู้ที่มี Pandoc)

```bash
pandoc part1_cover_and_intro.md chapter1.md chapter2.md chapter3.md chapter4.md chapter5.md appendix.md -o FarmMe_Academic_Document.docx
```

## โครงสร้างเอกสาร

### บทที่ 1: บทนำ
- ความเป็นมาและความสำคัญ
- วัตถุประสงค์
- ขอบเขต
- ประโยชน์ที่คาดว่าจะได้รับ
- นิยามศัพท์

### บทที่ 2: ทฤษฎีและงานวิจัยที่เกี่ยวข้อง
- Machine Learning Fundamentals
- XGBoost Algorithm
- Logistic Regression
- NSGA-II
- Thompson Sampling
- งานวิจัยที่เกี่ยวข้อง
- ชุดข้อมูลและการเตรียมข้อมูล
- Feature Engineering

### บทที่ 3: การดำเนินงาน
- สถาปัตยกรรมระบบ
- Model A: Crop Recommendation
- Model B: Planting Window
- Model C: Price Forecasting
- Model D: Harvest Decision
- Pipeline Integration
- Data Leakage Prevention

### บทที่ 4: ผลลัพธ์
- ผลการประเมินแต่ละโมเดล
- การเปรียบเทียบ Before/After
- แอปพลิเคชันและแดชบอร์ด
- การทดสอบกับผู้ใช้

### บทที่ 5: สรุป
- สรุปผลการดำเนินงาน
- ปัญหาและอุปสรรค
- ข้อเสนอแนะ

## ข้อมูลที่ใช้ในเอกสาร

เอกสารนี้อ้างอิงจากโค้ดและข้อมูลจริงใน:
- `REMEDIATION_PRODUCTION/` - โค้ดทั้งหมด
- `buildingModel.py/Dataset/` - ชุดข้อมูล
- `backend/` - API และ wrappers
- เอกสารต่างๆ ใน project

## สถิติโครงการ

- **จำนวนโมเดล**: 4 โมเดลหลัก
- **จำนวนพืช**: 46 ชนิด
- **จำนวนจังหวัด**: 77 จังหวัด
- **ข้อมูลการเพาะปลูก**: 6,226 records
- **ข้อมูลราคา**: 2,289,492 records
- **ข้อมูลสภาพอากาศ**: 56,287 records

## ผลการประเมิน

### Model A (Crop Recommendation)
- Algorithm: XGBoost
- R²: 0.47 (honest, no leakage)
- Use Case: แนะนำพืชที่เหมาะสม

### Model B (Planting Window)
- Algorithm: Logistic Regression
- F1-Score: 0.70-0.75
- Use Case: คาดการณ์ช่วงเวลาปลูก

### Model C (Price Forecasting)
- Algorithm: XGBoost + Weather + Economic
- MAE: 13.31 บาท
- Bias Reduction: 28.7%
- Use Case: พยากรณ์ราคา

### Model D (Harvest Decision)
- Algorithm: Thompson Sampling
- Decision Accuracy: ~68%
- Use Case: แนะนำเวลาเก็บเกี่ยว

## ติดต่อ

หากมีคำถามหรือต้องการข้อมูลเพิ่มเติม กรุณาติดต่อทีมพัฒนา

# Model B - Target และ Tables ที่ใช้

**Model:** Model B - Planting Window Prediction  
**Type:** Binary Classification  
**วัตถุประสงค์:** ทำนายว่าวันนี้เป็นช่วงเวลาที่ดีในการปลูกหรือไม่

---

## 🎯 Target (เป้าหมายการทำนาย)

### Target: **1 Target เดียว**

```python
Target: is_good_window (Binary: 0 or 1)

คำนวณจาก:
is_good_window = 1 if success_rate > 0.75 else 0

โดยที่:
- 1 (Good Window) = ช่วงเวลาดีในการปลูก (success_rate > 75%)
- 0 (Bad Window) = ช่วงเวลาไม่ดีในการปลูก (success_rate ≤ 75%)
```

### ตัวอย่าง:
```
success_rate = 0.85 → is_good_window = 1 (Good)
success_rate = 0.60 → is_good_window = 0 (Bad)
success_rate = 0.75 → is_good_window = 0 (Bad, ต้องมากกว่า 0.75)
```

---

## 📊 Tables ที่ใช้

### 1. **cultivation.csv** (หลัก)

**Columns ที่มี (18 columns):**
```
1. province                      - จังหวัด
2. crop_type                     - ชนิดพืช
3. crop_id                       - รหัสพืช
4. planting_date                 - วันที่ปลูก ✅ ใช้
5. harvest_date                  - วันที่เก็บเกี่ยว ❌ ไม่ใช้ (post-harvest)
6. planting_area_rai             - พื้นที่ปลูก
7. expected_yield_kg             - ผลผลิตที่คาดหวัง
8. actual_yield_kg               - ผลผลิตจริง ❌ ไม่ใช้ (post-harvest)
9. yield_efficiency              - ประสิทธิภาพผลผลิต ❌ ไม่ใช้ (post-harvest)
10. success_rate                 - อัตราความสำเร็จ ✅ ใช้สร้าง target
11. investment_cost              - ต้นทุนการลงทุน
12. farm_skill                   - ทักษะเกษตรกร
13. tech_adoption                - การใช้เทคโนโลยี
14. harvest_timing_adjustment    - การปรับเวลาเก็บเกี่ยว
15. extreme_event_damage         - ความเสียหายจากภัยพิบัติ
16. extreme_event_notes          - หมายเหตุภัยพิบัติ
17. weather_quality              - คุณภาพสภาพอากาศ
18. yield_multiplier             - ตัวคูณผลผลิต
```

**Columns ที่ Model B ใช้จริง:**
```
✅ planting_date      - วันที่ปลูก (สร้าง temporal features)
✅ success_rate       - สร้าง target (is_good_window)
❓ soil_type          - ประเภทดิน (ไม่มีใน cultivation.csv!)
❓ soil_ph            - ค่า pH ดิน (ไม่มีใน cultivation.csv!)
❓ soil_nutrients     - ธาตุอาหารในดิน (ไม่มีใน cultivation.csv!)
❓ days_to_maturity   - จำนวนวันเก็บเกี่ยว (ไม่มีใน cultivation.csv!)
✅ province           - จังหวัด
❓ season             - ฤดูกาล (ไม่มีใน cultivation.csv!)
```

**ปัญหา:** หลาย columns ที่ Model B ต้องการ **ไม่มีใน cultivation.csv!**

---

### 2. **weather.csv** (รอง)

**ไม่ได้ใช้จริง!** แม้จะ import แต่ไม่ได้นำมาใช้ใน features

**Columns ที่น่าจะมี:**
```
- province
- date
- temperature_celsius
- rainfall_mm
- humidity_percent
```

**ปัญหา:** Model B ไม่ได้ใช้ข้อมูล weather จริงๆ!

---

## 🔍 Features ที่ Model B ใช้จริง

### Input Features (8 features):

```python
1. soil_ph                    - ค่า pH ดิน (ไม่มีในข้อมูล!)
2. soil_nutrients             - ธาตุอาหารในดิน (ไม่มีในข้อมูล!)
3. days_to_maturity           - จำนวนวันเก็บเกี่ยว (ไม่มีในข้อมูล!)
4. plant_month                - เดือนที่ปลูก (จาก planting_date)
5. plant_quarter              - ไตรมาสที่ปลูก (จาก planting_date)
6. plant_day_of_year          - วันที่ในปี (จาก planting_date)
7. month_sin, month_cos       - Cyclic encoding ของเดือน
8. soil_type_encoded          - ประเภทดิน encoded (ไม่มีในข้อมูล!)
9. province_encoded           - จังหวัด encoded
10. season_encoded            - ฤดูกาล encoded (ไม่มีในข้อมูล!)
```

**ปัญหาใหญ่:** หลาย features **ไม่มีในข้อมูลจริง!**

---

## ⚠️ ปัญหาที่พบ

### 1. Missing Columns
```
❌ soil_type       - ไม่มีใน cultivation.csv
❌ soil_ph         - ไม่มีใน cultivation.csv
❌ soil_nutrients  - ไม่มีใน cultivation.csv
❌ days_to_maturity - ไม่มีใน cultivation.csv
❌ season          - ไม่มีใน cultivation.csv
```

**ผลกระทบ:**
- Model ไม่สามารถใช้ features เหล่านี้ได้
- Features ที่เหลือมีแค่ temporal features (เดือน, วัน)
- Model อาจไม่แม่นยำเพราะขาดข้อมูลสำคัญ

---

### 2. Weather Data ไม่ได้ใช้
```
❌ temperature_celsius  - ไม่ได้ใช้
❌ rainfall_mm          - ไม่ได้ใช้
❌ humidity_percent     - ไม่ได้ใช้
```

**ผลกระทบ:**
- ขาดข้อมูลสภาพอากาศที่สำคัญ
- ไม่สามารถทำนายตามสภาพอากาศได้

---

### 3. Target มาจาก success_rate
```
Target: is_good_window = (success_rate > 0.75)

ปัญหา:
- success_rate คำนวณจาก actual_yield_kg (post-harvest)
- เป็นข้อมูลหลังเก็บเกี่ยว ไม่ใช่ก่อนปลูก
- อาจมี data leakage
```

---

## 📋 Tables ที่ควรมีใน Database

### ถ้าต้องการให้ Model B ทำงานได้ดี ควรมี:

### 1. **crop_cultivation** (มีอยู่แล้ว)
```sql
CREATE TABLE crop_cultivation (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR,
    province VARCHAR,
    planting_date DATE,
    harvest_date DATE,
    yield_kg FLOAT,
    area_rai FLOAT,
    success_rate FLOAT,  -- สำหรับสร้าง target
    created_at TIMESTAMP
);
```

### 2. **weather_data** (มีอยู่แล้ว แต่ไม่ได้ใช้)
```sql
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    province VARCHAR,
    date DATE,
    temperature_celsius FLOAT,
    rainfall_mm FLOAT,
    humidity_percent FLOAT,
    created_at TIMESTAMP
);
```

### 3. **soil_data** (ไม่มี - ต้องเพิ่ม!)
```sql
CREATE TABLE soil_data (
    id SERIAL PRIMARY KEY,
    province VARCHAR,
    soil_type VARCHAR,
    soil_ph FLOAT,
    soil_nutrients FLOAT,
    created_at TIMESTAMP
);
```

### 4. **crop_characteristics** (มีอยู่แล้ว)
```sql
CREATE TABLE crop_characteristics (
    id SERIAL PRIMARY KEY,
    crop_type VARCHAR,
    growth_days INTEGER,  -- days_to_maturity
    water_requirement VARCHAR,
    soil_preference VARCHAR,
    seasonal_type VARCHAR,  -- season
    created_at TIMESTAMP
);
```

---

## 💡 สรุป

### Target:
- **1 Target:** `is_good_window` (Binary: 0 or 1)
- คำนวณจาก: `success_rate > 0.75`

### Tables ที่ใช้:
1. ✅ **cultivation.csv** - หลัก (มี 6,226 rows)
2. ⚠️ **weather.csv** - รอง (import แต่ไม่ได้ใช้)

### Tables ที่ขาด:
1. ❌ **soil_data** - ข้อมูลดิน (soil_type, soil_ph, soil_nutrients)
2. ❌ **crop_characteristics** - ลักษณะพืช (days_to_maturity, season)

### Features ที่ใช้จริง:
- **8 features** (ส่วนใหญ่เป็น temporal features จาก planting_date)
- ขาด soil, weather, crop characteristics

### ปัญหาหลัก:
1. ❌ Dataset เล็ก (6,226 samples)
2. ❌ Features น้อยและไม่ครบ (8 features)
3. ❌ ขาดข้อมูล soil, weather
4. ⚠️ Target อาจมี data leakage (จาก success_rate)
5. ⚠️ Recall = 100% น่าสงสัย

---

**สร้างโดย:** Kiro AI Assistant  
**วันที่:** 23 พฤศจิกายน 2568

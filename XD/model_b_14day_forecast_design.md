# 📋 Model B v2.0 - การทำนายความเหมาะสมรายวัน 14 วันล่วงหน้า

## 🎯 เป้าหมาย
ทำนายความเหมาะสมในการปลูกพืชเป็นรายวัน สำหรับ 14 วันข้างหน้า โดยใช้ข้อมูลที่มีอยู่แล้ว

---

## 📊 ข้อมูลที่มีอยู่

### 1. Weather Data (อดีต)
```
- date, province
- temperature_celsius
- rainfall_mm
- humidity_percent
- drought_index
```

### 2. Cultivation Data
```
- planting_date, harvest_date
- crop_type, province
- planting_area_rai
```

### 3. Crop Characteristics
```
- crop_type
- growth_days
- water_requirement
- soil_preference
- seasonal_type
```

---

## 💡 แนวคิดหลัก: Time Series Forecasting

### ปัญหาเดิม:
❌ Model B ปัจจุบันต้องการข้อมูลอากาศ 30 วันก่อนวันปลูก
❌ ไม่มีข้อมูลอากาศในอนาคต

### แนวทางใหม่:
✅ **ใช้ Time Series Pattern จากข้อมูลอดีต**
✅ **สร้าง Features ที่ช่วยทำนายแนวโน้ม**
✅ **ทำนายทีละวัน (Day-by-Day Prediction)**

---

## 🔧 Feature Engineering ใหม่

### 1️⃣ **Temporal Features (เวลา)**
```python
# วันที่ทำนาย
- target_date (วันที่ต้องการทำนาย)
- target_day_of_year (1-365)
- target_month (1-12)
- target_week_of_year (1-52)
- target_day_of_week (0-6)

# Cyclic encoding
- target_month_sin = sin(2π * month / 12)
- target_month_cos = cos(2π * month / 12)
- target_day_sin = sin(2π * day_of_year / 365)
- target_day_cos = cos(2π * day_of_year / 365)

# ระยะห่างจากวันปัจจุบัน
- days_ahead (1-14 วัน)
```

### 2️⃣ **Historical Weather Features (อากาศย้อนหลัง)**
```python
# ข้อมูล 7 วันล่าสุด (ก่อนวันทำนาย)
- temp_last_7d_mean
- temp_last_7d_std
- temp_last_7d_trend (slope)
- rainfall_last_7d_mean
- rainfall_last_7d_sum
- rainfall_last_7d_max
- rainy_days_last_7d

# ข้อมูล 30 วันล่าสุด
- temp_last_30d_mean
- temp_last_30d_std
- rainfall_last_30d_mean
- rainfall_last_30d_sum
- rainy_days_last_30d

# Trend (แนวโน้ม)
- temp_trend_7d (อุณหภูมิกำลังขึ้นหรือลง)
- rainfall_trend_7d (ฝนกำลังเพิ่มหรือลด)
```

### 3️⃣ **Seasonal Pattern Features (รูปแบบตามฤดู)**
```python
# ค่าเฉลี่ยตามเดือนจากข้อมูลย้อนหลัง
- temp_monthly_avg (อุณหภูมิเฉลี่ยของเดือนนั้นๆ)
- temp_monthly_std (ความผันแปร)
- rainfall_monthly_avg
- rainfall_monthly_std

# ค่าเฉลี่ยตามสัปดาห์ของปี
- temp_weekly_avg
- rainfall_weekly_avg

# ฤดูกาล
- season (winter/summer/rainy)
- season_encoded
```

### 4️⃣ **Lag Features (ข้อมูลล่าช้า)**
```python
# อากาศเมื่อ X วันก่อน
- temp_lag_1d (เมื่อวาน)
- temp_lag_3d (3 วันก่อน)
- temp_lag_7d (สัปดาห์ที่แล้ว)
- rainfall_lag_1d
- rainfall_lag_3d
- rainfall_lag_7d

# อากาศในช่วงเดียวกันของปีที่แล้ว
- temp_same_week_last_year
- rainfall_same_week_last_year
```

### 5️⃣ **Rolling Statistics (สถิติเคลื่อนที่)**
```python
# Moving averages
- temp_ma_3d (3-day moving average)
- temp_ma_7d (7-day moving average)
- rainfall_ma_3d
- rainfall_ma_7d

# Exponential moving average (ให้น้ำหนักกับข้อมูลล่าสุดมากกว่า)
- temp_ema_7d
- rainfall_ema_7d
```

### 6️⃣ **Crop-Specific Features (ลักษณะพืช)**
```python
- crop_type_encoded
- growth_days
- water_requirement_encoded
- soil_preference_encoded
- seasonal_type_encoded
```

### 7️⃣ **Location Features (พื้นที่)**
```python
- province_encoded
- province_latitude (ถ้ามี)
- province_longitude (ถ้ามี)
- province_elevation (ความสูงจากระดับน้ำทะเล)
```

### 8️⃣ **Interaction Features (ปฏิสัมพันธ์)**
```python
# ความสัมพันธ์ระหว่าง features
- temp_x_rainfall (อุณหภูมิ × ฝน)
- temp_deviation_from_monthly_avg (เบี่ยงเบนจากค่าเฉลี่ย)
- rainfall_deviation_from_monthly_avg
- is_rainy_season (0/1)
- is_dry_season (0/1)
```

---

## 🏗️ Model Architecture

### แนวทาง 1: Direct Multi-Step Forecasting
```
Input: Features ณ วันที่ t
Output: Predictions สำหรับ t+1, t+2, ..., t+14 (14 outputs)

Model: XGBoost MultiOutput Regressor
```

### แนวทาง 2: Recursive Forecasting (แนะนำ)
```
Input: Features ณ วันที่ t
Output: Prediction สำหรับ t+1

จากนั้นใช้ prediction เป็น input สำหรับ t+2
ทำซ้ำจนครบ 14 วัน

Model: XGBoost Classifier
```

### แนวทาง 3: Sequence-to-Sequence (Advanced)
```
Input: Sequence ของ 30 วันล่าสุด
Output: Sequence ของ 14 วันข้างหน้า

Model: LSTM / GRU
```

---

## 📐 Target Variable (ตัวแปรเป้าหมาย)

### Option 1: Binary Classification (แนะนำ)
```python
is_good_planting_day = 0 or 1

# กำหนดกฎ:
def is_good_day(temp, rainfall, season, crop_seasonal_type):
    score = 0
    
    # อุณหภูมิเหมาะสม
    if 22 <= temp <= 32:
        score += 2
    elif 18 <= temp <= 36:
        score += 1
    
    # ฝนเหมาะสม
    if 5 <= rainfall <= 50:
        score += 2
    elif rainfall < 100:
        score += 1
    
    # ฤดูกาลตรง
    if crop_seasonal_type == 'all_season':
        score += 2
    elif crop_seasonal_type == season:
        score += 2
    
    return int(score >= 4)
```

### Option 2: Multi-Class Classification
```python
planting_suitability = 0, 1, 2
# 0 = ไม่เหมาะ
# 1 = เหมาะปานกลาง
# 2 = เหมาะมาก
```

### Option 3: Regression
```python
suitability_score = 0.0 - 1.0
# คะแนนความเหมาะสม (ต่อเนื่อง)
```

---

## 🔄 Training Process

### 1. Data Preparation
```python
# สร้าง training samples
for each_date in historical_dates:
    for days_ahead in range(1, 15):  # 1-14 วัน
        target_date = each_date + timedelta(days=days_ahead)
        
        # สร้าง features จากข้อมูลก่อน each_date
        features = create_features(
            current_date=each_date,
            target_date=target_date,
            crop=crop,
            province=province
        )
        
        # Target จากข้อมูลจริงของ target_date
        target = is_good_planting_day(target_date)
        
        samples.append((features, target))
```

### 2. Train-Test Split
```python
# Time-based split (ไม่ใช่ random)
train_data = data[data['date'] < '2025-01-01']
test_data = data[data['date'] >= '2025-01-01']
```

### 3. Model Training
```python
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=pos_weight
)

model.fit(X_train, y_train)
```

---

## 📊 Evaluation Metrics

### 1. Overall Performance
```python
- Accuracy
- F1 Score
- Precision / Recall
- ROC-AUC
```

### 2. Performance by Forecast Horizon
```python
# แยกประเมินแต่ละวัน
for day in range(1, 15):
    metrics_day_n = evaluate(predictions[day])
    
# คาดว่า:
# - Day 1-3: F1 > 0.85 (แม่นยำสูง)
# - Day 4-7: F1 > 0.75 (แม่นยำดี)
# - Day 8-14: F1 > 0.65 (แม่นยำพอใช้)
```

### 3. Calibration
```python
# ตรวจสอบว่า confidence score สอดคล้องกับความแม่นยำจริงหรือไม่
calibration_curve(y_true, y_proba)
```

---

## 🎯 Expected Performance

### ความแม่นยำที่คาดหวัง:

| วันที่ทำนาย | F1 Score | Accuracy | หมายเหตุ |
|------------|----------|----------|----------|
| Day 1-3    | 0.85+    | 0.88+    | แม่นยำสูง (ใช้ข้อมูลล่าสุด) |
| Day 4-7    | 0.75+    | 0.80+    | แม่นยำดี (ใช้ trend) |
| Day 8-14   | 0.65+    | 0.70+    | แม่นยำพอใช้ (ใช้ seasonal pattern) |

### ปัจจัยที่ส่งผล:
✅ **ช่วงที่แม่นยำ:**
- ฤดูกาลชัดเจน (ฤดูหนาว, ฤดูร้อน)
- พืชที่ปลูกได้ตลอดปี
- พื้นที่ที่มีข้อมูลเยอะ

⚠️ **ช่วงที่ท้าทาย:**
- ช่วงเปลี่ยนฤดู
- สภาพอากาศผิดปกติ
- พื้นที่ที่มีข้อมูลน้อย

---

## 🚀 Implementation Plan

### Phase 1: Data Preparation (1-2 วัน)
```
✓ โหลดและทำความสะอาดข้อมูล
✓ สร้าง feature engineering functions
✓ สร้าง training dataset
✓ แบ่ง train/test
```

### Phase 2: Model Development (2-3 วัน)
```
✓ Train baseline model
✓ Feature selection
✓ Hyperparameter tuning
✓ Cross-validation
```

### Phase 3: Evaluation (1 วัน)
```
✓ ประเมินผลแต่ละวัน (1-14)
✓ วิเคราะห์ errors
✓ Calibration
```

### Phase 4: Integration (1 วัน)
```
✓ สร้าง API endpoint
✓ ทดสอบกับ frontend
✓ Documentation
```

---

## 💻 Code Structure

```
buildingModel.py/
├── Model_B_14Day/
│   ├── data_preparation.py      # โหลดและเตรียมข้อมูล
│   ├── feature_engineering.py   # สร้าง features
│   ├── model_training.py        # Train model
│   ├── model_evaluation.py      # ประเมินผล
│   └── forecaster.py            # ทำนาย 14 วัน
│
backend/models/
├── model_b_14day.pkl            # Model ที่ train แล้ว
├── model_b_14day_scaler.pkl     # Scaler
├── model_b_14day_metadata.json  # Metadata
└── model_b_14day_features.json  # Feature names
```

---

## 🎨 API Design

### Endpoint: `/api/forecast/14-day`

**Request:**
```json
{
  "crop_type": "พริก",
  "province": "เชียงใหม่",
  "start_date": "2025-11-26"
}
```

**Response:**
```json
{
  "success": true,
  "crop_type": "พริก",
  "province": "เชียงใหม่",
  "forecast_start": "2025-11-26",
  "forecast_end": "2025-12-09",
  "daily_predictions": [
    {
      "date": "2025-11-26",
      "day_ahead": 1,
      "is_good_day": true,
      "confidence": 0.92,
      "predicted_temp": 25.3,
      "predicted_rainfall": 12.5,
      "season": "winter",
      "recommendation": "เหมาะสมมาก"
    },
    {
      "date": "2025-11-27",
      "day_ahead": 2,
      "is_good_day": true,
      "confidence": 0.88,
      "predicted_temp": 26.1,
      "predicted_rainfall": 8.2,
      "season": "winter",
      "recommendation": "เหมาะสม"
    },
    // ... 12 วันถัดไป
  ],
  "summary": {
    "good_days": 10,
    "bad_days": 4,
    "best_days": ["2025-11-26", "2025-11-27", "2025-11-28"],
    "recommendation": "แนะนำให้ปลูกในช่วง 3 วันแรก"
  }
}
```

---

## ⚠️ ข้อควรระวัง

### 1. Data Leakage
```python
# ❌ ผิด: ใช้ข้อมูลอนาคต
features['temp_next_7d_mean'] = ...

# ✅ ถูก: ใช้เฉพาะข้อมูลอดีต
features['temp_last_7d_mean'] = ...
```

### 2. Overfitting
```python
# ใช้ regularization
# Cross-validation
# Early stopping
```

### 3. Concept Drift
```python
# สภาพอากาศเปลี่ยนแปลงตามกาลเวลา
# ควร retrain model เป็นระยะ (ทุก 3-6 เดือน)
```

---

## 📈 Success Criteria

### ✅ Model ถือว่าสำเร็จถ้า:
1. F1 Score (Day 1-7) > 0.75
2. F1 Score (Day 8-14) > 0.65
3. ไม่มี data leakage
4. Inference time < 1 วินาที
5. ใช้งานได้จริงกับ frontend

---

## 🎯 Next Steps

1. ✅ **อนุมัติแนวทาง** - ตรวจสอบว่าแนวทางนี้เหมาะสมหรือไม่
2. 🔧 **เริ่ม Implementation** - เขียนโค้ด feature engineering
3. 🤖 **Train Model** - Train และ evaluate
4. 🚀 **Deploy** - นำไปใช้งานจริง

---

**คิดว่าแนวทางนี้เหมาะสมไหมครับ? มีอะไรที่ต้องปรับเปลี่ยนหรือเพิ่มเติมไหม?** 🤔

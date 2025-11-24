# Backend Database Tables Summary

## 📊 Tables ที่ Backend ใช้งาน

### 1. **CropPrice** (crop_prices) - ใช้มากที่สุด ⭐⭐⭐
**คอลัมน์:**
- id (Primary Key)
- crop_type (String, indexed)
- province (String, indexed)
- price_per_kg (Float)
- date (DateTime, indexed)
- source (String, nullable)
- created_at, updated_at (DateTime)

**ใช้ใน:**
- ✅ `model_c_wrapper.py` - ดึงราคาปัจจุบันและข้อมูลย้อนหลัง 90 วัน
- ✅ `price_prediction_service.py` - ดึงข้อมูลราคาย้อนหลัง
- ✅ `planting_service.py` - วิเคราะห์ราคาย้อนหลัง
- ✅ `dashboard_service.py` - แสดงราคาล่าสุด, crop types, most profitable
- ✅ `forecast.py` - ดึงข้อมูลราคาสำหรับ forecast
- ✅ `model.py` - ดึงราคาเฉลี่ยและ trend
- ✅ `database.py` router - ดึงข้อมูลราคา
- ✅ `data_import.py` - import ข้อมูลราคา
- ✅ `dashboard.py` - ดึง provinces ที่มีข้อมูล

**Query patterns:**
```python
# ดึงราคาปัจจุบัน
db.query(CropPrice).filter(
    CropPrice.crop_type == crop_type,
    CropPrice.province == province
).order_by(desc(CropPrice.date)).first()

# ดึงข้อมูลย้อนหลัง 90 วัน
db.query(CropPrice.price_per_kg).filter(
    CropPrice.crop_type == crop_type,
    CropPrice.province == province
).order_by(desc(CropPrice.date)).limit(90).all()

# ดึงข้อมูลตามช่วงวันที่
db.query(CropPrice).filter(
    CropPrice.crop_type == crop_type,
    CropPrice.province == province,
    CropPrice.date >= start_date,
    CropPrice.date <= end_date
).order_by(CropPrice.date).all()
```

---

### 2. **WeatherData** (weather_data) - สำคัญ ⭐⭐
**คอลัมน์:**
- id (Primary Key)
- province (String, indexed)
- date (DateTime, indexed)
- temperature_celsius (Float)
- rainfall_mm (Float)
- source (String, nullable)
- created_at, updated_at (DateTime)

**ใช้ใน:**
- ✅ `dashboard_service.py` - ดึงสภาพอากาศล่าสุด
- ✅ `forecast.py` - ดึงข้อมูลอากาศสำหรับ forecast
- ✅ `database.py` router - ดึงข้อมูลอากาศ
- ✅ `data_import.py` - import ข้อมูลอากาศ

**Query patterns:**
```python
# ดึงอากาศล่าสุด
db.query(WeatherData).filter(
    WeatherData.province == province
).order_by(desc(WeatherData.date)).first()

# ดึงข้อมูลตามช่วงวันที่
db.query(WeatherData).filter(
    WeatherData.province == province,
    WeatherData.date >= start_date
).order_by(WeatherData.date).all()
```

---

### 3. **CropCharacteristics** (crop_characteristics) - ข้อมูลพืช ⭐⭐
**คอลัมน์:**
- id (Primary Key)
- crop_type (String, indexed, unique)
- growth_days (Integer)
- water_requirement (String)
- suitable_regions (String)
- soil_preference (String)
- investment_cost (Float)
- risk_level (String)
- seasonal_type (String)
- crop_category (String)
- created_at, updated_at (DateTime)

**ใช้ใน:**
- ✅ `forecast.py` - ดึงข้อมูลพืชสำหรับแสดงใน dropdown
- ✅ `database.py` router - ดึงรายการพืชทั้งหมด

**Query patterns:**
```python
# ดึงข้อมูลพืชทั้งหมด
db.query(CropCharacteristics).all()

# ดึงข้อมูลพืชเฉพาะ
db.query(CropCharacteristics).filter(
    CropCharacteristics.crop_type == crop_type
).first()
```

---

### 4. **User** (users) - ระบบ Authentication ⭐
**คอลัมน์:**
- id (Primary Key)
- email (String, unique, indexed)
- username (String, unique, indexed)
- password_hash (String)
- full_name (String)
- is_active (Boolean)
- province, water_availability, budget_level (String)
- experience_crops (Text - JSON)
- risk_tolerance, preference, soil_type (String)
- time_constraint (Integer)
- created_at, updated_at (DateTime)

**ใช้ใน:**
- ✅ `auth.py` - register, login, get user
- ✅ `user.py` - get profile, update email/password/profile
- ✅ `chat.py` - ดึง user profile

**Query patterns:**
```python
# Login
db.query(User).filter(User.email == email).first()

# Get user by ID
db.query(User).filter(User.id == user_id).first()

# Check existing user
db.query(User).filter(
    (User.email == email) | (User.username == username)
).first()
```

---

### 5. **ChatSession** (chat_sessions) - Chat History ⭐
**คอลัมน์:**
- id (Primary Key)
- session_id (String, unique, indexed)
- user_id (Integer, indexed)
- user_query (Text)
- gemini_response (Text)
- crop_id (Integer)
- forecast_data (Text - JSON)
- created_at (DateTime)

**ใช้ใน:**
- ✅ `database.py` router - ดึง chat sessions
- ✅ `chat.py` - ดึง recent chats

**Query patterns:**
```python
# Get recent sessions
db.query(ChatSession).order_by(
    ChatSession.created_at.desc()
).limit(limit).all()

# Get specific session
db.query(ChatSession).filter(
    ChatSession.session_id == session_id
).first()

# Get user's recent chats
db.query(ChatSession).filter(
    ChatSession.user_query.isnot(None)
).order_by(ChatSession.created_at.desc()).limit(5).all()
```

---

### 6. **CropPrediction** (crop_predictions) - Prediction History
**คอลัมน์:**
- id (Primary Key)
- crop_id (Integer, indexed)
- crop_type (String, indexed)
- province (String, indexed)
- predicted_price (Float)
- confidence (Float)
- price_history, weather_data, crop_info, calendar_data (Text - JSON)
- prediction (Float - legacy)
- created_at, updated_at (DateTime)

**ใช้ใน:**
- ✅ `database.py` router - ดึง recent predictions

**Query patterns:**
```python
# Get recent predictions
db.query(CropPrediction).order_by(
    CropPrediction.created_at.desc()
).all()
```

---

### 7. **ForecastData** (forecast_data) - Forecast Cache
**คอลัมน์:**
- id (Primary Key)
- crop_type (String, indexed)
- province (String, indexed)
- forecast_date (DateTime)
- temperature (Float)
- rainfall (Float)
- predicted_price (Float)
- created_at (DateTime)

**ใช้ใน:**
- ไม่พบการใช้งานใน backend ปัจจุบัน (อาจเป็น legacy)

---

### 8. **ProvinceData** (province_data) - ข้อมูลจังหวัด
**คอลัมน์:**
- id (Primary Key)
- province_name (String, indexed)
- region (String)
- climate_zone (String)
- created_at (DateTime)

**ใช้ใน:**
- ไม่พบการใช้งานใน backend ปัจจุบัน (อาจเป็น legacy)

---

### 9. **EconomicFactors** (economic_factors) - ปัจจัยเศรษฐกิจ
**คอลัมน์:**
- id (Primary Key)
- factor_name (String, indexed)
- value (Float)
- date (DateTime, indexed)
- created_at (DateTime)

**ใช้ใน:**
- ไม่พบการใช้งานใน backend ปัจจุบัน (อาจเป็น legacy)

---

### 10. **CropCultivation** (crop_cultivation) - ข้อมูลการปลูก
**คอลัมน์:**
- id (Primary Key)
- crop_name (String, indexed)
- province (String, indexed)
- planting_date (DateTime)
- harvest_date (DateTime)
- yield_kg (Float)
- area_rai (Float)
- created_at (DateTime)

**ใช้ใน:**
- ไม่พบการใช้งานใน backend ปัจจุบัน (อาจเป็น legacy)

---

## 📈 สรุปการใช้งาน

### Tables ที่ใช้งานจริง (Active):
1. ✅ **CropPrice** - ใช้มากที่สุด (ทุก service)
2. ✅ **WeatherData** - ใช้ใน forecast และ dashboard
3. ✅ **CropCharacteristics** - ใช้แสดงข้อมูลพืช
4. ✅ **User** - ระบบ authentication
5. ✅ **ChatSession** - chat history
6. ✅ **CropPrediction** - prediction history

### Tables ที่ไม่ค่อยใช้ (Legacy/Unused):
- ⚠️ **ForecastData** - ไม่พบการใช้งาน
- ⚠️ **ProvinceData** - ไม่พบการใช้งาน
- ⚠️ **EconomicFactors** - ไม่พบการใช้งาน
- ⚠️ **CropCultivation** - ไม่พบการใช้งาน

---

## 🔍 ข้อมูลที่จำเป็นต้องมีใน Database

### สำหรับ Model C Stratified:
1. **CropPrice** - ต้องมีข้อมูลย้อนหลังอย่างน้อย 90 วัน
   - crop_type (ชื่อพืช)
   - province (จังหวัด)
   - price_per_kg (ราคา)
   - date (วันที่)

### สำหรับ Forecast:
1. **CropPrice** - ราคาย้อนหลัง
2. **WeatherData** - อากาศย้อนหลัง
3. **CropCharacteristics** - ข้อมูลพืช

### สำหรับ Dashboard:
1. **CropPrice** - ราคาล่าสุด
2. **WeatherData** - อากาศล่าสุด

---

## 💡 คำแนะนำ

### ควรเก็บข้อมูล:
- ✅ CropPrice: อย่างน้อย 90-180 วันย้อนหลัง
- ✅ WeatherData: อย่างน้อย 30-90 วันย้อนหลัง
- ✅ CropCharacteristics: ข้อมูลพืชทั้งหมด

### อาจลบหรือ archive:
- ⚠️ ForecastData, ProvinceData, EconomicFactors, CropCultivation (ถ้าไม่ใช้)

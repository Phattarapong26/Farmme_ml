# Model B Wrapper - Changelog

## Version 2.0 - Production Ready (2025-11-26)

### 🎉 Major Improvements

#### Real Data Integration
- **Crop Characteristics**: โหลดจาก `crop_characteristics.csv` แทน hardcoded data
  - รองรับพืชทั้งหมดในระบบ (ไม่จำกัดแค่ 5 พืช)
  - ข้อมูล growth_days, soil_preference, seasonal_type จากฐานข้อมูลจริง

- **Province Mapping**: โหลดจาก `cultivation.csv` แทน hardcoded list
  - รองรับทุกจังหวัดที่มีข้อมูลการปลูก
  - Dynamic mapping ตามข้อมูลจริง

- **Weather Data**: ดึงข้อมูลจริง 30 วันย้อนหลังจาก `weather.csv`
  - อุณหภูมิเฉลี่ย (avg_temp_prev_30d)
  - ปริมาณฝนเฉลี่ย (avg_rainfall_prev_30d)
  - ปริมาณฝนรวม (total_rainfall_prev_30d)
  - จำนวนวันที่ฝนตก (rainy_days_prev_30d)

### 🛡️ Fallback Mechanism
- ถ้าไม่มีข้อมูลในช่วงวันที่ต้องการ จะใช้ค่าเฉลี่ยตามฤดูกาล
- Error handling ครบถ้วน ไม่ crash
- Logging ชัดเจนเมื่อใช้ fallback data

### ✅ API Testing
- ทดสอบผ่าน API endpoints:
  - `GET /api/planting/health` - ตรวจสอบสถานะ Model B
  - `POST /api/planting/window` - ทำนายช่วงเวลาปลูกวันเดียว
  - `POST /api/planting/calendar` - ทำนายปฏิทินการปลูกหลายเดือน

### 📊 Test Results
```
Test Case 1: พริก - เชียงใหม่ - ฤดูฝน (มิถุนายน)
- Result: แนะนำปลูก (99.97% confidence)
- Weather: อุณหภูมิ 29.0°C, ฝน 32.7mm
- Reason: อุณหภูมิเหมาะสม, ปริมาณฝนเหมาะสม, ช่วงฤดูฝน

Test Case 2: พริก - เชียงใหม่ - ฤดูหนาว (มกราคม)
- Result: ไม่แนะนำ (0.03% confidence)
- Weather: อุณหภูมิ 19.3°C, ฝน 0.2mm
- Reason: อุณหภูมิต่ำ, ฝนน้อย, ช่วงฤดูหนาว
```

### 🔧 Technical Details

#### Data Sources
```python
# Crop characteristics
dataset_path = 'buildingModel.py/Dataset/crop_characteristics.csv'
# Columns: crop_type, growth_days, soil_preference, seasonal_type

# Province mapping
dataset_path = 'buildingModel.py/Dataset/cultivation.csv'
# Columns: province, crop_type, planting_date, ...

# Weather data
dataset_path = 'buildingModel.py/Dataset/weather.csv'
# Columns: date, province, temperature_celsius, rainfall_mm, humidity_percent
```

#### Feature Engineering
- 17 features ครบถ้วนตาม design
- Temporal features: month_sin, month_cos, day_sin, day_cos
- Encoded features: crop_type, province, season, soil_preference, seasonal_type
- Weather features: 30-day historical data

### 📝 Breaking Changes
None - API interface เหมือนเดิม

### 🚀 Migration Guide
ไม่ต้องเปลี่ยนแปลงโค้ดที่เรียกใช้ Model B เลย เพียงแค่:
1. ตรวจสอบว่ามีไฟล์ dataset ครบ:
   - `buildingModel.py/Dataset/crop_characteristics.csv`
   - `buildingModel.py/Dataset/cultivation.csv`
   - `buildingModel.py/Dataset/weather.csv`
2. Restart API server

---

## Version 1.0 - Initial Release

### Features
- Binary classification สำหรับช่วงเวลาปลูก
- 17 features
- XGBoost model
- Mock weather data (seasonal averages)
- Hardcoded 5 crops และ 10 provinces

# Forecast Integration Plan - Model C Stratified

## 🔍 ปัญหาที่พบ

### 1. Service ใช้ Model เก่า
```python
# ❌ ปัจจุบัน (price_forecast_service.py):
model_path = "models/model_c_price_forecast.pkl"  # ไม่มีไฟล์นี้!

# ✅ ควรใช้:
from model_c_wrapper import model_c_wrapper  # Stratified models (R² = 0.76)
```

### 2. Frontend แสดง Fallback
```typescript
// RealForecastChart.tsx แสดง:
"⚠️ ใช้การพยากรณ์แบบ Trend-based (ML Model ไม่พร้อมใช้งาน)"

// เพราะ:
- model_c_price_forecast.pkl ไม่มี
- price_forecast_service.model_loaded = False
- ใช้ fallback trend แทน
```

### 3. Timeframe ไม่เหมาะสม
```typescript
// ปัจจุบัน:
const [timeFrame, setTimeFrame] = useState<TimeFrame>(90);  // Default 90 วัน

// ปัญหา:
- Model C แม่นสุดที่ 7 วัน (R² = 0.77, MAE = 2.17)
- 90 วัน แม่นยำลดลง
- User ไม่รู้ว่า 7 วันแม่นที่สุด
```

---

## 💡 แนวทางแก้ไข

### Phase 1: เชื่อม Model C Stratified (สำคัญที่สุด!)

#### 1.1 อัปเดต price_forecast_service.py
```python
# แทนที่การโหลด model เอง
# ใช้ model_c_wrapper แทน

from model_c_wrapper import model_c_wrapper

class PriceForecastService:
    def __init__(self):
        # ใช้ wrapper ที่มี stratified models
        self.model_wrapper = model_c_wrapper
        self.model_loaded = model_c_wrapper.model_loaded
        
    def forecast_price(self, province, crop_type, days_ahead, ...):
        # เรียกใช้ wrapper
        result = self.model_wrapper.predict_price(
            crop_type=crop_type,
            province=province,
            days_ahead=days_ahead
        )
        return result
```

**ประโยชน์:**
- ✅ ใช้ Model C Stratified (R² = 0.76)
- ✅ ใช้ 3 models (LOW, MEDIUM, HIGH)
- ✅ แม่นยำกว่า fallback มาก
- ✅ ไม่ต้อง train model ใหม่

#### 1.2 ทดสอบ Integration
```bash
# Test endpoint
curl -X POST http://localhost:8000/api/v2/model/predict-price-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "เชียงใหม่",
    "crop_type": "พริก",
    "days_ahead": 7
  }'

# ควรได้:
{
  "success": true,
  "forecast": [...],
  "model_used": "model_c_stratified",  # ไม่ใช่ fallback!
  "confidence_score": 0.85
}
```

---

### Phase 2: ปรับ Timeframe UI

#### 2.1 เปลี่ยน Default เป็น 7 วัน
```typescript
// RealForecastChart.tsx
const [timeFrame, setTimeFrame] = useState<TimeFrame>(7);  // เปลี่ยนจาก 90 → 7
```

#### 2.2 เพิ่ม UI Hint
```typescript
const timeFrameOptions = [
  { value: 7, label: '7 วัน', badge: '⭐ แม่นสุด' },  // เพิ่ม badge
  { value: 30, label: '30 วัน', badge: '✅ แม่น' },
  { value: 90, label: '90 วัน', badge: '⚠️ พอใช้' },
  { value: 180, label: '180 วัน', badge: '❌ ไม่แนะนำ' },
];
```

#### 2.3 แสดง Accuracy Info
```typescript
<div className="text-xs text-gray-600 mt-2">
  💡 ความแม่นยำ:
  - 7 วัน: R² = 0.77, MAE = 2.17 บาท (แม่นมาก!)
  - 30 วัน: R² = 0.34, MAE = 4.10 บาท (พอใช้)
  - 90+ วัน: ความแม่นยำลดลง
</div>
```

---

### Phase 3: ปรับปรุง Chart Display

#### 3.1 แสดง Confidence Interval
```typescript
// เพิ่มแถบความเชื่อมั่น (confidence band)
<Area
  type="monotone"
  dataKey="confidence_high"
  stroke="none"
  fill="#86efac"
  fillOpacity={0.2}
/>
```

#### 3.2 แสดง Model Info
```typescript
{mlForecast?.success && (
  <div className="bg-green-50 p-2 rounded">
    ✅ ใช้ ML Model: {mlForecast.model_used}
    📊 R²: {mlForecast.r2 || 0.76}
    📉 MAE: {mlForecast.mae || 6.97} บาท/กก.
  </div>
)}
```

---

## 📋 Implementation Checklist

### Phase 1: Model Integration (สำคัญที่สุด!)
- [ ] อัปเดต `price_forecast_service.py` ให้ใช้ `model_c_wrapper`
- [ ] ทดสอบ `/api/v2/model/predict-price-forecast` endpoint
- [ ] ตรวจสอบว่า frontend ได้ข้อมูลจริง (ไม่ใช่ fallback)
- [ ] ทดสอบกับพืชหลายชนิด (ราคาถูก, กลาง, แพง)

### Phase 2: UI Improvements
- [ ] เปลี่ยน default timeframe เป็น 7 วัน
- [ ] เพิ่ม badge "แม่นสุด" ที่ปุ่ม 7 วัน
- [ ] แสดง accuracy info สำหรับแต่ละ timeframe
- [ ] เพิ่ม tooltip อธิบายความแม่นยำ

### Phase 3: Chart Enhancements
- [ ] เพิ่ม confidence interval band
- [ ] แสดง model metrics (R², MAE)
- [ ] เพิ่ม legend อธิบายกราฟ
- [ ] ปรับสี/style ให้ชัดเจนขึ้น

---

## 🎯 Expected Results

### Before (ปัจจุบัน)
```
❌ Model: fallback_trend
❌ Accuracy: ไม่ทราบ
❌ Timeframe: 90 วัน (default)
❌ UI: ไม่มี hint ว่า 7 วันแม่นสุด
```

### After (หลังแก้ไข)
```
✅ Model: model_c_stratified (R² = 0.76)
✅ Accuracy: แสดงชัดเจน (R², MAE)
✅ Timeframe: 7 วัน (default) พร้อม badge "แม่นสุด"
✅ UI: มี hint และ confidence interval
```

---

## 📊 Performance by Timeframe

```
7 วัน:   R² = 0.77, MAE = 2.17 baht  ⭐ แม่นสุด!
30 วัน:  R² = 0.34, MAE = 4.10 baht  ✅ แม่น
90 วัน:  R² = 0.08, MAE = 24.01 baht ⚠️ พอใช้
180 วัน: ไม่แนะนำ                    ❌ ไม่แม่น
```

---

## 🚀 Next Steps

1. **เริ่มจาก Phase 1** (Model Integration) - สำคัญที่สุด!
2. ทดสอบให้แน่ใจว่า Model C Stratified ทำงาน
3. ทำ Phase 2 (UI) เพื่อให้ user รู้ว่า 7 วันแม่นสุด
4. ทำ Phase 3 (Chart) เพื่อปรับปรุง UX

---

**Priority**: 🔥 HIGH  
**Estimated Time**: 2-3 hours  
**Impact**: ⭐⭐⭐⭐⭐ (Very High)

**หมายเหตุ**: Phase 1 สำคัญที่สุด เพราะจะทำให้ frontend ใช้ Model C จริงแทน fallback!

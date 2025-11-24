# 📋 คู่มือ Endpoints ที่มีอยู่แล้วใน Farmme API

## 🎯 สรุปปัญหาและแนวทางแก้ไข

**ปัญหา:** Frontend ใช้ endpoints `/api/v2/planting-schedule/*` ที่ยังไม่ได้สร้าง  
**แนวทางแก้ไข:** ใช้ endpoints ที่มีอยู่แล้วและปรับ frontend ให้เข้ากัน

---

## 🔧 Endpoints ที่มีอยู่และใช้งานได้

### 1. 📅 **Planting Date Recommendation**
```
POST /recommend-planting-date
```

**Request Body:**
```json
{
  "crop_type": "ข่า",
  "province": "กรุงเทพมหานคร", 
  "growth_days": 180
}
```

**Response:**
```json
{
  "success": true,
  "best_planting_window": {
    "planting_date": "2024-12-01",
    "harvest_date": "2025-05-30",
    "predicted_price": 47.5,
    "confidence": 0.85
  },
  "ml_scenarios": [...],
  "recommendation": {
    "text": "ช่วงเวลานี้เหมาะสมมากสำหรับการเพาะปลูก!"
  }
}
```

### 2. 🌾 **Available Crops**
```
GET /api/v2/forecast/crops
```

**Response:**
```json
{
  "success": true,
  "crops": [
    {
      "crop_type": "ข่า",
      "crop_category": "สมุนไพร",
      "growth_days": 180,
      "suitable_regions": "ทั่วประเทศ"
    }
  ]
}
```

### 3. 🎯 **Crop Recommendations**
```
POST /api/v3/recommend-crops
```

**Request Body:**
```json
{
  "province": "กรุงเทพมหานคร",
  "water_availability": "ปานกลาง",
  "budget_level": "กลาง",
  "risk_tolerance": "ต่ำ",
  "experience_level": "ปานกลาง",
  "time_constraint": 90,
  "soil_type": "ดินร่วน",
  "preference": "ผักใบ",
  "season": "ร้อน",
  "top_n": 5
}
```

### 4. 💰 **Price Prediction**
```
POST /api/v3/predict-price
```

**Request Body:**
```json
{
  "province": "กรุงเทพมหานคร",
  "crop_type": "ข่า",
  "crop_category": "สมุนไพร",
  "month": 12,
  "year": 2024,
  "temperature_celsius": 28.0,
  "rainfall_mm": 100.0,
  "planting_area_rai": 10.0,
  "expected_yield_kg": 5000.0
}
```

---

## 🔄 การปรับ Frontend

### ✅ **อัปเดตแล้ว:** `usePlantingRecommendation.ts`

1. **usePlantingSchedule()** → ใช้ `/recommend-planting-date`
2. **useAvailableCrops()** → ใช้ `/api/v2/forecast/crops`  
3. **useCompareCrops()** → ใช้ `/api/v3/recommend-crops`

### 📝 **การใช้งานใน Frontend:**

```typescript
// 1. Get planting recommendations
const plantingMutation = usePlantingSchedule();
plantingMutation.mutate({
  province: "กรุงเทพมหานคร",
  crop_type: "ข่า",
  growth_days: 180,
  planting_area_rai: 10
});

// 2. Get available crops
const { data: cropsData } = useAvailableCrops();

// 3. Compare crops
const compareMutation = useCompareCrops();
compareMutation.mutate({
  province: "กรุงเทพมหานคร",
  crop_types: ["ข่า", "คะน้า", "พริก"],
  planting_date: "2024-12-01",
  planting_area_rai: 10
});
```

---

## 🧪 การทดสอบ

### รันเซิร์ฟเวอร์:
```bash
cd @backend
uvicorn main:app --reload
```

### ทดสอบ endpoints:
```bash
python test_planting_endpoint.py
```

---

## ⚠️ ข้อควรระวัง

1. **ML Models:** บาง endpoints อาจใช้เวลานานในการประมวลผล
2. **Error Handling:** ตรวจสอบ `success: false` ใน response
3. **Timeout:** ตั้ง timeout สำหรับ requests ที่ใช้ ML models
4. **Data Availability:** บางจังหวัด/พืชอาจไม่มีข้อมูลเพียงพอ

---

## 🎯 สถานะปัจจุบัน

✅ **ใช้งานได้:**
- `/recommend-planting-date` - แนะนำวันปลูก
- `/api/v2/forecast/crops` - รายการพืช
- `/api/v3/recommend-crops` - แนะนำพืช
- `/api/v3/predict-price` - ทำนายราคา

✅ **Frontend อัปเดตแล้ว:**
- `usePlantingRecommendation.ts` ปรับให้ใช้ endpoints ที่มีอยู่

🔄 **ต้องทดสอบ:**
- การทำงานของ ML models กับข้อมูลจริง
- Performance และ timeout handling
- Error cases และ fallback mechanisms

---

**📞 หากมีปัญหา:** ตรวจสอบ logs ใน console และ network tab ของ browser
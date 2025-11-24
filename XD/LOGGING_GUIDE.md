# 📊 Logging Guide - ML Models

**วันที่:** 24 พฤศจิกายน 2568  
**สถานะ:** ✅ IMPLEMENTED  
**ครอบคลุม:** All Models (A, B, C, D)

---

## 🎯 วัตถุประสงค์

เพิ่ม detailed logging เพื่อ:
1. ✅ ดูค่าที่ model ตอบกลับก่อนส่งไปยัง LLM
2. ✅ Debug และ troubleshoot ได้ง่าย
3. ✅ Monitor model performance
4. ✅ วิเคราะห์ usage patterns

---

## 📝 Logging Format

### ทุก Function Call จะ Log:

**1. Function Execution:**
```
🔧 Executing function: [function_name]
📥 Function args: {args}
```

**2. Model Response:**
```
📤 Function result (before LLM):
   Success: True/False
   [Model-specific details]
```

---

## 🤖 Model-Specific Logging

### Model A - Crop Recommendation 🌾

```
🌾 Model A (Crop Recommendation) Response:
   Province: เชียงใหม่
   Budget: medium
   Water: sufficient
   Recommendations: 5 crops
   1. พริก (score: 0.85)
   2. มะเขือเทศ (score: 0.82)
   3. ข้าว (score: 0.78)
```

**ข้อมูลที่ Log:**
- Province
- Budget level
- Water availability
- Number of recommendations
- Top 3 crops with scores

---

### Model B - Planting Window 🌱

```
🌱 Model B Response:
   Crop: พริก
   Province: เชียงใหม่
   Date: 2024-11-24
   Is Good: True
   Confidence: 99.92%
   Recommendation: แนะนำให้ปลูกในช่วงนี้ (เหมาะสมมาก)
   Reason: อุณหภูมิเหมาะสม (25.0°C), ปริมาณฝนเหมาะสม (20.0mm), ช่วงฤดูหนาว
```

**ข้อมูลที่ Log:**
- Crop type
- Province
- Planting date
- Is good window (True/False)
- Confidence score
- Recommendation text
- Reason/explanation

---

### Model B - Planting Calendar 📅

```
📅 Model B Calendar Response:
   Crop: พริก
   Province: เชียงใหม่
   Months Analyzed: 12
   Good Windows: 10
   Summary: พบ 10 เดือนที่เหมาะสมจาก 12 เดือน (83%)
```

**ข้อมูลที่ Log:**
- Crop type
- Province
- Number of months analyzed
- Number of good windows
- Summary text

---

### Model C - Price Prediction 💰

```
💰 Model C (Price Prediction) Response:
   Crop: พริก
   Province: เชียงใหม่
   Days Ahead: 30
   Predictions: 4 timeframes
   Current Price: 35.50 บาท/กก.
   - 7d: 36.20 บาท/กก. (confidence: 85.0%)
   - 30d: 38.50 บาท/กก. (confidence: 72.0%)
   - 90d: 42.00 บาท/กก. (confidence: 58.0%)
```

**ข้อมูลที่ Log:**
- Crop type
- Province
- Days ahead
- Number of predictions
- Current price
- First 3 predictions with confidence

---

### Model D - Water Management 💧

```
💧 Model D (Water Management) Response:
   Crop: พริก
   Province: เชียงใหม่
   Soil Type: ดินร่วน
   Current Rainfall: 50.0 mm
   Recommendation: รดน้ำเพิ่ม 2 ครั้งต่อสัปดาห์
   Water Needed: 500 L
```

**ข้อมูลที่ Log:**
- Crop type
- Province
- Soil type
- Current rainfall
- Recommendation
- Water needed

---

### Harvest Decision 🌾

```
🌾 Harvest Decision Response:
   Crop: พริก
   Province: เชียงใหม่
   Current Price: 35.50 บาท/กก.
   Action: รอเก็บเกี่ยว
   Confidence: 75.0%
   Reason: ราคาคาดว่าจะสูงขึ้นในอีก 7-14 วัน
```

**ข้อมูลที่ Log:**
- Crop type
- Province
- Current price
- Recommended action
- Confidence
- Reason

---

## 📍 ตำแหน่งของ Logs

### 1. Terminal Output
เมื่อรัน server ด้วย:
```bash
uvicorn backend.app.main:app --reload
```

จะเห็น logs แบบนี้:
```
INFO:gemini_functions:🔧 Executing function: check_planting_window
INFO:gemini_functions:📥 Function args: {'crop_type': 'พริก', 'province': 'เชียงใหม่', 'planting_date': '2024-11-24'}
INFO:gemini_functions:🌱 Model B Response:
INFO:gemini_functions:   Crop: พริก
INFO:gemini_functions:   Province: เชียงใหม่
INFO:gemini_functions:   Date: 2024-11-24
INFO:gemini_functions:   Is Good: True
INFO:gemini_functions:   Confidence: 99.92%
```

### 2. Log Files
Logs จะถูกเขียนไปที่:
```
backend/logs/
├── app.log
├── model_a.log
├── model_b.log
├── model_c.log
└── model_d.log
```

---

## 🔍 วิธีดู Logs

### 1. Real-time Monitoring
```bash
# ดู logs แบบ real-time
tail -f backend/logs/app.log

# หรือใน Windows
Get-Content backend/logs/app.log -Wait
```

### 2. Filter by Model
```bash
# ดูเฉพาะ Model B
grep "Model B" backend/logs/app.log

# ดูเฉพาะ Model C
grep "Model C" backend/logs/app.log
```

### 3. Filter by Function
```bash
# ดูเฉพาะ function calls
grep "Executing function" backend/logs/app.log

# ดูเฉพาะ results
grep "Function result" backend/logs/app.log
```

---

## 🧪 ทดสอบ Logging

### Test Script
```python
# test_logging.py
import requests

# Test Model B
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "query": "วันนี้เหมาะปลูกพริกในเชียงใหม่ไหม",
        "crop_id": 1,
        "price_history": [30, 32, 31],
        "weather": [100, 28],
        "crop_info": [1, 2, 1],
        "calendar": [0, 0, 1]
    }
)

print(response.json())
```

**Expected Terminal Output:**
```
INFO:gemini_functions:🔧 Executing function: check_planting_window
INFO:gemini_functions:📥 Function args: {'crop_type': 'พริก', 'province': 'เชียงใหม่'}
INFO:gemini_functions:🌱 Model B Response:
INFO:gemini_functions:   Crop: พริก
INFO:gemini_functions:   Province: เชียงใหม่
INFO:gemini_functions:   Date: 2024-11-24
INFO:gemini_functions:   Is Good: True
INFO:gemini_functions:   Confidence: 99.92%
INFO:gemini_functions:   Recommendation: แนะนำให้ปลูกในช่วงนี้ (เหมาะสมมาก)
INFO:gemini_functions:   Reason: อุณหภูมิเหมาะสม (25.0°C), ปริมาณฝนเหมาะสม (20.0mm)
INFO:gemini_functions:📤 Function result (before LLM):
INFO:gemini_functions:   Success: True
INFO:gemini_functions:   Is Good Window: True
INFO:gemini_functions:   Confidence: 99.92%
INFO:gemini_functions:   Recommendation: แนะนำให้ปลูกในช่วงนี้ (เหมาะสมมาก)
```

---

## 📊 Log Analysis

### ตัวอย่างการวิเคราะห์:

**1. นับจำนวน function calls:**
```bash
grep "Executing function" backend/logs/app.log | wc -l
```

**2. ดู function ที่ถูกเรียกบ่อยที่สุด:**
```bash
grep "Executing function" backend/logs/app.log | sort | uniq -c | sort -nr
```

**3. ดู error rate:**
```bash
grep "Success: False" backend/logs/app.log | wc -l
```

**4. ดู average confidence:**
```bash
grep "Confidence:" backend/logs/app.log | awk '{print $3}' | sed 's/%//' | awk '{sum+=$1; count++} END {print sum/count "%"}'
```

---

## 🎯 Benefits

### 1. Debugging ✅
- เห็นค่าที่ model ตอบกลับทันที
- ตรวจสอบว่า function ถูกเรียกหรือไม่
- Debug parameter issues

### 2. Monitoring ✅
- ติดตาม model performance
- เห็น confidence scores
- วิเคราะห์ usage patterns

### 3. Troubleshooting ✅
- หา error ได้เร็ว
- เห็น flow ของ data
- วิเคราะห์ปัญหา

### 4. Analytics ✅
- นับจำนวน requests
- วิเคราะห์ popular functions
- ดู success rate

---

## 🔧 Configuration

### Log Level
แก้ไขใน `backend/app/main.py`:
```python
import logging

# Set log level
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Rotation
เพิ่ม log rotation:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'backend/logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

## ✅ Summary

**Logging Coverage:**
- ✅ Model A (Crop Recommendation)
- ✅ Model B (Planting Window)
- ✅ Model B (Planting Calendar)
- ✅ Model C (Price Prediction)
- ✅ Model D (Water Management)
- ✅ Harvest Decision
- ✅ All function calls

**Information Logged:**
- ✅ Function name
- ✅ Input parameters
- ✅ Model responses
- ✅ Success/failure status
- ✅ Confidence scores
- ✅ Recommendations

**Benefits:**
- ✅ Easy debugging
- ✅ Performance monitoring
- ✅ Usage analytics
- ✅ Error tracking

---

**ตอนนี้คุณสามารถดูค่าที่ทุก model ตอบกลับผ่าน terminal ได้แล้ว!** 🎉

---

**Created by:** Kiro AI Assistant  
**Date:** 24 พฤศจิกายน 2568  
**Status:** ✅ IMPLEMENTED

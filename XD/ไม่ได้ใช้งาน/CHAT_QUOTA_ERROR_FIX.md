# Chat Quota Error Fix

## 🔍 ปัญหา:

Chat แสดงข้อความ: **"ขออภัย เกิดข้อผิดพลาดในการประมวลผล"**

## 🎯 สาเหตุ:

**Gemini API Quota Exceeded!**

```
quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
```

Free tier มีข้อจำกัด:
- **15 requests per minute** (RPM)
- **1 million tokens per day**
- **1,500 requests per day**

## ✅ การแก้ไข:

### 1. เปลี่ยนไปใช้ Model ที่เสถียรกว่า
```python
models_to_try = [
    ("gemini-1.5-flash", True),   # Stable model (แนะนำ)
    ("gemini-1.5-pro", True),     # Pro model (quota สูงกว่า)
    ("gemini-1.5-flash", False),  # Fallback
]
```

### 2. เพิ่ม Retry Logic
```python
max_retries = 2
while retry_count <= max_retries:
    try:
        response = gemini_model.generate_content(...)
        break
    except Exception as e:
        if "quota" in str(e).lower():
            time.sleep(2)  # Wait before retry
            retry_count += 1
        else:
            raise
```

### 3. Error Handling ที่ดีขึ้น
```python
except Exception as e:
    logger.error(f"❌ Chat error: {e}", exc_info=True)
    return {
        "gemini_answer": f"ขออภัย เกิดข้อผิดพลาด: {type(e).__name__}",
        "error": str(e),
        "error_type": type(e).__name__
    }
```

---

## 🔧 วิธีแก้ปัญหา Quota:

### Option 1: รอให้ Quota Reset
- Quota จะ reset ทุก **1 นาที** (RPM)
- หรือทุก **1 วัน** (daily limit)

### Option 2: Upgrade เป็น Paid Plan
- ไปที่ https://ai.google.dev/pricing
- Paid plan มี quota สูงกว่ามาก:
  - **1,000 RPM** (vs 15 RPM)
  - **4 million tokens/day** (vs 1 million)

### Option 3: ใช้ Model C แทน (แนะนำ)
Model C **ไม่ต้องใช้ API key** และ **ไม่มี quota limit**:

```python
from model_c_wrapper import model_c_wrapper

result = model_c_wrapper.predict_price(
    crop_type='พริก',
    province='เชียงใหม่',
    days_ahead=30
)

if result.get('success'):
    response = format_model_c_response(result)
else:
    response = result.get('message')
```

### Option 4: Implement Caching
Cache คำตอบที่ซ้ำๆ เพื่อลด API calls:

```python
from cache import cache

# Check cache first
cached_response = cache.get(f"chat_{query_hash}")
if cached_response:
    return cached_response

# Call Gemini only if not cached
response = gemini_model.generate_content(...)

# Cache the response
cache.set(f"chat_{query_hash}", response, ttl_hours=1)
```

---

## 📊 Quota Limits:

### Free Tier:
- ✅ 15 requests/minute
- ✅ 1 million tokens/day
- ✅ 1,500 requests/day

### Paid Tier (Pay-as-you-go):
- ✅ 1,000 requests/minute
- ✅ 4 million tokens/day
- ✅ Unlimited requests/day
- 💰 $0.075 per 1M input tokens
- 💰 $0.30 per 1M output tokens

---

## 💡 คำแนะนำ:

1. **ระยะสั้น**: รอ quota reset (1 นาที)
2. **ระยะกลาง**: ใช้ caching + rate limiting
3. **ระยะยาว**: 
   - Upgrade เป็น paid plan
   - หรือใช้ Model C แทน Gemini
   - หรือใช้ทั้งสอง (Gemini สำหรับคำถามทั่วไป, Model C สำหรับทำนายราคา)

---

## 🚀 Status:

✅ **แก้ไขแล้ว**:
- เปลี่ยนไปใช้ `gemini-1.5-flash` (เสถียรกว่า)
- เพิ่ม retry logic สำหรับ quota errors
- เพิ่ม error handling ที่ชัดเจน
- แสดง error message ที่เข้าใจง่าย

⏳ **รอ Quota Reset**: ~1 นาที

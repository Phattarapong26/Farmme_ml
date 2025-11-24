# 🧪 คู่มือทดสอบ Backend บน Render

## 📋 ข้อมูล Render IP Ranges

Render ใช้ IP ranges เหล่านี้:
- `74.220.52.0/24` (74.220.52.0 - 74.220.52.255)
- `74.220.60.0/24` (74.220.60.0 - 74.220.60.255)

**สำคัญ**: ถ้าใช้ Supabase หรือ Database ที่มี IP Whitelist ต้องเพิ่ม IP ranges เหล่านี้

---

## 🔧 ตั้งค่า Database Whitelist

### Supabase
1. ไปที่: https://app.supabase.com/project/[your-project]/settings/database
2. ที่ **Connection Pooling** → **Allowed IP addresses**
3. เพิ่ม:
   ```
   74.220.52.0/24
   74.220.60.0/24
   ```
4. กด **Save**

### PostgreSQL/Other Databases
เพิ่ม IP ranges เหล่านี้ใน firewall rules หรือ security groups

---

## 🧪 วิธีทดสอบ Backend

### วิธีที่ 1: ใช้ Python Script (แนะนำ)

```bash
cd XD
python test_render_deployment.py
```

**อย่าลืม**: แก้ `RENDER_URL` ในไฟล์ให้เป็น URL จริงของคุณ

### วิธีที่ 2: ใช้ Browser

เปิด URL เหล่านี้ใน browser:

1. **Ping**: https://farmme-backend.onrender.com/ping
   - ควรเห็น: `{"status":"ok","timestamp":...}`

2. **Root**: https://farmme-backend.onrender.com/
   - ควรเห็นข้อมูล API

3. **Health**: https://farmme-backend.onrender.com/health
   - ควรเห็นสถานะระบบ

4. **API Docs**: https://farmme-backend.onrender.com/docs
   - ถ้าเปิด DEBUG จะเห็น Swagger UI

### วิธีที่ 3: ใช้ curl/PowerShell

**PowerShell**:
```powershell
# Test ping
Invoke-RestMethod -Uri "https://farmme-backend.onrender.com/ping"

# Test root
Invoke-RestMethod -Uri "https://farmme-backend.onrender.com/"

# Test planting recommendation
$body = @{
    crop_type = "ข้าว"
    province = "เชียงใหม่"
    growth_days = 120
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    top_n = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://farmme-backend.onrender.com/recommend-planting-date" -Method Post -Body $body -ContentType "application/json"
```

**curl** (ถ้าติดตั้งแล้ว):
```bash
curl https://farmme-backend.onrender.com/ping
curl https://farmme-backend.onrender.com/
```

---

## 🐛 แก้ปัญหาที่พบบ่อย

### 1. Timeout / Service Unavailable (503)
**สาเหตุ**: Render Free Plan จะ sleep หลังไม่ใช้งาน 15 นาที

**วิธีแก้**:
- รอ 30-60 วินาที แล้วลองใหม่
- ครั้งแรกที่ wake up จะใช้เวลานาน

### 2. Database Connection Error
**สาเหตุ**: IP ของ Render ไม่ได้อยู่ใน whitelist

**วิธีแก้**:
- เพิ่ม IP ranges: `74.220.52.0/24` และ `74.220.60.0/24`
- ตรวจสอบ `DATABASE_URL` ถูกต้อง

### 3. Internal Server Error (500)
**สาเหตุ**: Environment variables ไม่ครบหรือผิด

**วิธีแก้**:
1. ไปที่ Render Dashboard → Environment tab
2. ตรวจสอบว่ามีครบ:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
   - `ENVIRONMENT=production`
   - `ALLOWED_ORIGINS`

### 4. CORS Error (จาก Frontend)
**สาเหตุ**: Frontend URL ไม่ได้อยู่ใน ALLOWED_ORIGINS

**วิธีแก้**:
- เพิ่ม `ALLOWED_ORIGINS=https://phattarapong26.github.io`
- ถ้ามีหลาย URL ใช้ comma คั่น

### 5. Model Loading Error
**สาเหตุ**: ไฟล์ model ใหญ่เกินไป หรือไม่มีใน repo

**วิธีแก้**:
- ตรวจสอบว่าไฟล์ `.pkl` อยู่ใน `backend/models/`
- ถ้าไฟล์ใหญ่เกิน 100MB ต้องใช้ Git LFS หรือ external storage

---

## 📊 ตรวจสอบ Logs

### ดู Logs บน Render
1. ไปที่ Render Dashboard
2. เลือก service ของคุณ
3. ไปที่ **Logs** tab
4. ดู error messages

### ตัวอย่าง Log ที่ดี:
```
🚀 Starting Farmme API...
✅ Database tables initialized successfully
✅ Database connection verified
✅ Metrics collection started
✅ Farmme API startup complete
```

### ตัวอย่าง Log ที่มีปัญหา:
```
❌ Failed to initialize database: connection refused
❌ Database connection failed: could not connect to server
```

---

## ✅ Checklist ก่อนทดสอบ

- [ ] Push code ขึ้น GitHub แล้ว
- [ ] สร้าง Web Service บน Render แล้ว
- [ ] ตั้งค่า Environment Variables ครบถ้วน
- [ ] เพิ่ม Render IP ใน Database whitelist
- [ ] Deployment status เป็น "Live" (สีเขียว)
- [ ] รอ service wake up แล้ว (ถ้า sleep อยู่)

---

## 🎯 Expected Results

### Ping Endpoint
```json
{
  "status": "ok",
  "timestamp": 1700000000.123
}
```

### Root Endpoint
```json
{
  "message": "Farmme API",
  "version": "1.0.0",
  "environment": "production",
  "status": "running",
  "docs": "disabled"
}
```

### Health Endpoint
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-11-24T10:00:00"
}
```

---

## 📞 ติดปัญหา?

1. ตรวจสอบ Logs บน Render Dashboard
2. ตรวจสอบ Environment Variables
3. ตรวจสอบ Database connection
4. ลองรัน `test_render_deployment.py` เพื่อดู error details
5. ถ้ายังไม่ได้ ลอง Manual Deploy ใหม่

---

## 🚀 Next Steps

เมื่อ Backend ทำงานได้แล้ว:

1. อัพเดท Frontend API URL
2. Test การเชื่อมต่อระหว่าง Frontend-Backend
3. Test features ต่างๆ บนหน้าเว็บ
4. Monitor performance และ logs

---

**หมายเหตุ**: Render Free Plan มีข้อจำกัด:
- Sleep หลังไม่ใช้งาน 15 นาที
- 750 hours/month (พอสำหรับ 1 service)
- Cold start ใช้เวลา 30-60 วินาที

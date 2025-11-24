# 🚀 คู่มือ Deploy Farmme ML

## 📋 สิ่งที่ต้องเตรียม

1. ✅ Git for Windows ติดตั้งแล้ว
2. ✅ GitHub Account: Phattarapong26
3. ✅ Repository: https://github.com/Phattarapong26/Farmme_ml
4. ✅ Render Account (สมัครฟรีที่ https://render.com)
5. ✅ Supabase Database URL
6. ✅ Gemini API Key

---

## 🌐 Part 1: Deploy Frontend ไปที่ GitHub Pages

### ขั้นตอนที่ 1: Push Code ขึ้น GitHub

```bash
cd XD
git add .
git commit -m "Setup deployment for frontend and backend"
git push origin main
```

### ขั้นตอนที่ 2: เปิดใช้งาน GitHub Pages

1. ไปที่: https://github.com/Phattarapong26/Farmme_ml/settings/pages
2. ที่ **Source** เลือก: **GitHub Actions**
3. กด **Save**

### ขั้นตอนที่ 3: รอ Deployment

1. ไปที่: https://github.com/Phattarapong26/Farmme_ml/actions
2. รอให้ workflow "Deploy to GitHub Pages" รันเสร็จ (2-3 นาที)
3. เว็บจะพร้อมใช้งานที่: **https://phattarapong26.github.io/Farmme_ml/**

---

## 🔧 Part 2: Deploy Backend ไปที่ Render

### ขั้นตอนที่ 1: สร้าง Web Service บน Render

1. ไปที่: https://dashboard.render.com
2. กด **New +** → เลือก **Web Service**
3. เชื่อมต่อ GitHub repository: `Phattarapong26/Farmme_ml`
4. ตั้งค่าดังนี้:

```
Name: farmme-backend
Region: Singapore
Branch: main
Root Directory: (ว่างไว้)
Runtime: Python 3
Build Command: cd backend && pip install --upgrade pip && pip install -r requirements.txt
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. เลือก **Free Plan**
6. กด **Create Web Service**

### ขั้นตอนที่ 2: ตั้งค่า Environment Variables

ไปที่ **Environment** tab และเพิ่ม:

```
DATABASE_URL = postgresql://[your-supabase-url]
GEMINI_API_KEY = [your-gemini-api-key]
ENVIRONMENT = production
DEBUG = false
LOG_LEVEL = INFO
ALLOWED_ORIGINS = https://phattarapong26.github.io,http://localhost:8080
```

### ขั้นตอนที่ 3: Deploy

1. กด **Manual Deploy** → **Deploy latest commit**
2. รอ 5-10 นาที (ครั้งแรกจะนานหน่อย)
3. เมื่อเสร็จจะได้ URL เช่น: `https://farmme-backend.onrender.com`

---

## 🔐 Part 3: ตั้งค่า Database Whitelist (สำคัญ!)

### เพิ่ม Render IP ใน Supabase

Render ใช้ IP ranges เหล่านี้:
- `74.220.52.0/24`
- `74.220.60.0/24`

**ขั้นตอน**:
1. ไปที่ Supabase Dashboard: https://app.supabase.com
2. เลือก Project ของคุณ
3. ไปที่ **Settings** → **Database**
4. ที่ **Connection Pooling** หรือ **Network Restrictions**
5. เพิ่ม IP addresses:
   ```
   74.220.52.0/24
   74.220.60.0/24
   ```
6. กด **Save**

**หมายเหตุ**: ถ้าไม่เพิ่ม IP เหล่านี้ Backend จะเชื่อมต่อ Database ไม่ได้!

---

## 🔗 Part 4: เชื่อมต่อ Frontend กับ Backend

### อัพเดท Frontend Config

แก้ไฟล์ `frontend/src/config/api.ts` (หรือไฟล์ที่เก็บ API URL):

```typescript
const API_URL = import.meta.env.PROD 
  ? 'https://farmme-backend.onrender.com'
  : 'http://localhost:8000';

export default API_URL;
```

### Push การเปลี่ยนแปลง

```bash
git add .
git commit -m "Update API URL for production"
git push origin main
```

รอ GitHub Actions deploy ใหม่อีกครั้ง

---

## ✅ ตรวจสอบการทำงาน

### ทดสอบ Backend (แนะนำ)

รันสคริปต์ทดสอบ:
```bash
cd XD
python test_render_deployment.py
```

หรือทดสอบด้วย Browser:

### Frontend
- เปิด: https://phattarapong26.github.io/Farmme_ml/
- ตรวจสอบว่าหน้าเว็บโหลดได้

### Backend
- เปิด: https://farmme-backend.onrender.com/ping
- ควรเห็น: `{"status":"ok","timestamp":...}`

### API Docs (ถ้าเปิด DEBUG)
- เปิด: https://farmme-backend.onrender.com/docs

**ดูคู่มือทดสอบเพิ่มเติม**: `RENDER_TESTING_GUIDE.md`

---

## 🐛 แก้ปัญหาที่พบบ่อย

### Frontend ไม่โหลด CSS/JS
- ตรวจสอบ `vite.config.ts` ว่า `base: '/Farmme_ml/'` ถูกต้อง

### Backend Error 500
- ตรวจสอบ Logs ใน Render Dashboard
- ตรวจสอบ Environment Variables ครบถ้วน

### CORS Error
- เพิ่ม Frontend URL ใน `ALLOWED_ORIGINS`
- Format: `https://phattarapong26.github.io`

### Database Connection Failed
- ตรวจสอบ `DATABASE_URL` ถูกต้อง
- ตรวจสอบ Supabase ยังใช้งานได้

---

## 📝 หมายเหตุ

- **Free Plan ของ Render** จะ sleep หลังไม่มีการใช้งาน 15 นาที
- ครั้งแรกที่เข้าจะใช้เวลา 30-60 วินาที ในการ wake up
- ถ้าต้องการ uptime 100% ต้องอัพเกรดเป็น Paid Plan

---

## 🎉 เสร็จสิ้น!

Frontend: https://phattarapong26.github.io/Farmme_ml/
Backend: https://farmme-backend.onrender.com

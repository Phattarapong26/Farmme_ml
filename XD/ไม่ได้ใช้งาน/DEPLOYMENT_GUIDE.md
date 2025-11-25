# 🚀 คู่มือการ Deploy FarmMe

## 📋 สิ่งที่ต้องเตรียม

### ✅ ที่มีอยู่แล้ว
- [x] GitHub Repository: `https://github.com/Phattarapong26/XD.git`
- [x] Supabase Database (PostgreSQL)
- [x] Gemini API Key
- [x] Frontend (React + Vite)
- [x] Backend (FastAPI + Python)

### 📦 ที่ต้องสร้างใหม่
- [ ] Render Account (สำหรับ Backend)
- [ ] GitHub Pages Settings (สำหรับ Frontend)

---

## 🎯 Part 1: Deploy Backend ไป Render.com

### Step 1: สร้าง Render Account
1. ไปที่ https://render.com
2. Sign up ด้วย GitHub account
3. เชื่อมต่อกับ GitHub repository

### Step 2: สร้าง Web Service
1. คลิก **New +** → **Web Service**
2. เลือก repository: `Phattarapong26/XD`
3. ตั้งค่าดังนี้:

**Basic Settings:**
```
Name: farmme-backend
Region: Singapore
Branch: main
Root Directory: (ว่างไว้)
Environment: Python 3
```

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 3: ตั้งค่า Environment Variables

คลิก **Advanced** → **Add Environment Variable** แล้วเพิ่ม:

| Key | Value | หมายเหตุ |
|-----|-------|---------|
| `DATABASE_URL` | `postgresql://postgres.[ref]:[password]@...pooler.supabase.com:6543/postgres` | จาก Supabase Settings → Database → Connection pooling |
| `GEMINI_API_KEY` | `your_gemini_api_key` | API key ของคุณ |
| `ENVIRONMENT` | `production` | |
| `PYTHON_VERSION` | `3.11.0` | |
| `DEBUG` | `False` | |

**⚠️ สำคัญ:** ใช้ Connection Pooling URL (port 6543) ไม่ใช่ Direct Connection (port 5432)

### Step 4: Deploy
1. คลิก **Create Web Service**
2. รอ 5-10 นาที
3. เมื่อเสร็จจะได้ URL: `https://farmme-backend.onrender.com`

### Step 5: ทดสอบ Backend
```bash
# ทดสอบ health check
curl https://farmme-backend.onrender.com/health

# ดู API docs
เปิดเบราว์เซอร์: https://farmme-backend.onrender.com/docs
```

---

## 🌐 Part 2: Deploy Frontend ไป GitHub Pages

### Step 1: เปิดใช้งาน GitHub Pages
1. ไปที่ GitHub repository: https://github.com/Phattarapong26/XD
2. ไปที่ **Settings** → **Pages**
3. ตั้งค่า:
   - **Source**: GitHub Actions
   - **Branch**: (ไม่ต้องเลือก เพราะใช้ Actions)

### Step 2: เพิ่ม Secret สำหรับ API URL
1. ไปที่ **Settings** → **Secrets and variables** → **Actions**
2. คลิก **New repository secret**
3. เพิ่ม:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://farmme-backend.onrender.com`

### Step 3: Push Code ไป GitHub
```bash
# เช็คสถานะ
git status

# เพิ่มไฟล์ทั้งหมด
git add .

# Commit
git commit -m "Add deployment configuration for GitHub Pages and Render"

# Push
git push origin main
```

### Step 4: รอ Deployment
1. ไปที่ **Actions** tab ใน GitHub
2. ดู workflow "Deploy to GitHub Pages" กำลังทำงาน
3. เมื่อเสร็จ (สีเขียว ✓) จะได้ URL: `https://phattarapong26.github.io/XD/`

---

## 🔧 Part 3: อัพเดท CORS ใน Backend

หลังจาก deploy แล้ว ต้องอัพเดท CORS ใน backend:

### ไฟล์: `backend/app/main.py`

เพิ่ม frontend URL ใน CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "https://phattarapong26.github.io",  # เพิ่มบรรทัดนี้
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

จากนั้น:
```bash
git add backend/app/main.py
git commit -m "Update CORS for GitHub Pages"
git push origin main
```

Render จะ auto-deploy ใหม่อัตโนมัติ

---

## ✅ ตรวจสอบว่า Deploy สำเร็จ

### Frontend
- เปิด: `https://phattarapong26.github.io/XD/`
- ควรเห็นหน้า Intro แล้วเด้งไปหน้าหลัก
- ทดสอบฟีเจอร์ต่างๆ

### Backend
- เปิด: `https://farmme-backend.onrender.com/docs`
- ควรเห็น API documentation
- ทดสอบ API endpoints

---

## ⚠️ ข้อควรระวัง

### Render Free Tier
- **Cold Start**: หลังไม่มีคนใช้ 15 นาที server จะ sleep
- **First Request**: ครั้งแรกหลัง sleep จะช้า 30-60 วินาที
- **Solution**: ใช้ UptimeRobot ping ทุก 10 นาที

### GitHub Pages
- **Cache**: อาจต้องรอ 1-2 นาทีถึงจะเห็นการเปลี่ยนแปลง
- **Base Path**: ใช้ `/XD/` เป็น base path (ตั้งค่าใน vite.config.ts แล้ว)

---

## 🔄 การอัพเดทในอนาคต

### อัพเดท Frontend
```bash
# แก้ไขโค้ด
git add .
git commit -m "Update frontend"
git push origin main
# GitHub Actions จะ deploy อัตโนมัติ
```

### อัพเดท Backend
```bash
# แก้ไขโค้ด
git add .
git commit -m "Update backend"
git push origin main
# Render จะ deploy อัตโนมัติ
```

---

## 📊 Monitoring

### Render Dashboard
- ดู Logs: https://dashboard.render.com
- ดู Metrics: CPU, Memory usage
- ดู Events: Deployment history

### GitHub Actions
- ดู Workflow runs: https://github.com/Phattarapong26/XD/actions
- ดู Deployment status

---

## 🆘 Troubleshooting

### ปัญหา: Frontend ไม่เชื่อมต่อ Backend
**แก้ไข:**
1. เช็ค CORS ใน backend
2. เช็ค `VITE_API_BASE_URL` ใน GitHub Secrets
3. เช็ค Network tab ใน browser DevTools

### ปัญหา: Backend ช้ามาก
**แก้ไข:**
1. Cold start ปกติ (ครั้งแรก)
2. ใช้ UptimeRobot keep alive
3. พิจารณา upgrade Render plan

### ปัญหา: Database connection error
**แก้ไข:**
1. เช็ค `DATABASE_URL` ใน Render
2. ใช้ Connection Pooling URL (port 6543)
3. เช็ค Supabase database status

---

## 🎉 สรุป

หลังจาก deploy เสร็จ คุณจะมี:

✅ **Frontend**: `https://phattarapong26.github.io/XD/`
✅ **Backend**: `https://farmme-backend.onrender.com`
✅ **Database**: Supabase (PostgreSQL)
✅ **Auto Deploy**: Push to GitHub = Auto deploy ทั้ง Frontend และ Backend

**ทุกอย่างพร้อมใช้งาน! 🚀**

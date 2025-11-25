# FarmMe Project Setup Guide

คู่มือการติดตั้งและใช้งานโปรเจค FarmMe สำหรับสมาชิกในทีม

## 📋 สิ่งที่ต้องเตรียม

- Python 3.8+
- Node.js 16+
- Git
- Internet connection

## 🚀 Quick Start (สำหรับสมาชิกทีม)

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd XD
```

### 2. ตั้งค่า Backend

```bash
cd backend

# สร้าง virtual environment
python -m venv .venv

# เปิดใช้งาน virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# คัดลอกไฟล์ .env.example
copy .env.example .env

# แก้ไขไฟล์ .env ด้วย credentials ที่ได้รับจากทีม
```

### 3. อัพเดท .env File

แก้ไขไฟล์ `backend/.env` ด้วยข้อมูลเหล่านี้:

```env
# Database (Supabase - ใช้ร่วมกันทั้งทีม)
DATABASE_URL=postgresql://postgres:Zx0966566414@db.inhanxxglxnjbugppulg.supabase.co:5432/postgres

# Redis Cache
REDIS_URL=redis://default:mqnXR9U01fIHWAjd9t5sHRCV24n1onmx@redis-15456.c8.us-east-1-4.ec2.redns.redis-cloud.com:15456

# Gemini API (ขอ API key ของตัวเองจาก https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_api_key_here

# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

### 4. ทดสอบการเชื่อมต่อ

```bash
# ทดสอบ Supabase connection
python scripts/test_supabase_connection.py
```

ถ้าเห็น ✅ Connection Successful แสดงว่าพร้อมใช้งาน!

### 5. รัน Backend

```bash
python run.py
```

Backend จะรันที่: http://localhost:8000
API Docs: http://localhost:8000/docs

### 6. ตั้งค่า Frontend

```bash
cd ../frontend

# ติดตั้ง dependencies
npm install

# รัน development server
npm run dev
```

Frontend จะรันที่: http://localhost:5173

## 📊 Database (Supabase)

### ข้อดีของการใช้ Supabase

✅ **ไม่ต้อง import ข้อมูล** - ข้อมูลมีอยู่แล้วบน cloud  
✅ **ข้อมูลเดียวกัน** - ทุกคนเห็นข้อมูลเดียวกัน  
✅ **ไม่ต้องติดตั้ง PostgreSQL** - ใช้ cloud database  
✅ **Sync อัตโนมัติ** - การเปลี่ยนแปลงเห็นได้ทันที  

### ข้อมูลที่มีอยู่

- **Crop Prices**: 2.3 ล้าน records
- **Weather Data**: 56,000+ records
- **Crop Cultivation**: 6,000+ records
- **Crop Characteristics**: 50 crops

### ดู Database

เข้าไปดูได้ที่: https://supabase.com/dashboard/project/inhanxxglxnjbugppulg

## 🔑 Credentials (สำหรับทีม)

### Supabase Database
- **Host**: db.inhanxxglxnjbugppulg.supabase.co
- **Port**: 5432
- **Database**: postgres
- **User**: postgres
- **Password**: Zx0966566414

### Redis Cache
- **URL**: redis://default:mqnXR9U01fIHWAjd9t5sHRCV24n1onmx@redis-15456.c8.us-east-1-4.ec2.redns.redis-cloud.com:15456

### Gemini API
- แต่ละคนต้องสมัคร API key ของตัวเอง
- ฟรี: https://makersuite.google.com/app/apikey

## 🛠️ Development Workflow

### การทำงานกับ Git

```bash
# ดึงการเปลี่ยนแปลงล่าสุด
git pull origin main

# สร้าง branch ใหม่สำหรับ feature
git checkout -b feature/your-feature-name

# เพิ่มไฟล์ที่แก้ไข
git add .

# Commit
git commit -m "Add: your feature description"

# Push ขึ้น GitHub
git push origin feature/your-feature-name

# สร้าง Pull Request บน GitHub
```

### ไฟล์ที่ไม่ควร Commit

❌ `.env` - มี passwords และ API keys  
❌ `__pycache__/` - Python cache  
❌ `node_modules/` - Node dependencies  
❌ `*.db` - Database files  
❌ `.venv/` - Virtual environment  
❌ `*.log` - Log files  

ไฟล์เหล่านี้อยู่ใน `.gitignore` แล้ว

## 📁 โครงสร้างโปรเจค

```
XD/
├── backend/                    # FastAPI Backend
│   ├── app/                   # Application code
│   │   ├── routers/          # API endpoints
│   │   └── services/         # Business logic
│   ├── scripts/              # Utility scripts
│   │   ├── migrate_to_supabase.py
│   │   ├── test_supabase_connection.py
│   │   └── ...
│   ├── database.py           # Database config
│   ├── config.py             # App config
│   ├── run.py                # Start server
│   ├── .env                  # Environment variables (ไม่ commit)
│   ├── .env.example          # Template (commit ได้)
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── buildingModel.py/         # ML Models & Training
│   ├── Dataset/              # Training data (ไม่ commit)
│   └── ...
│
├── REMEDIATION_PRODUCTION/   # Production models
│   └── trained_models/
│
├── .gitignore                # Git ignore rules
├── README.md                 # Project overview
└── SETUP_GUIDE.md           # This file
```

## 🧪 Testing

### ทดสอบ Backend

```bash
cd backend

# ทดสอบ connection
python scripts/test_supabase_connection.py

# ทดสอบ API (ต้องรัน server ก่อน)
# เปิด browser: http://localhost:8000/docs
```

### ทดสอบ Frontend

```bash
cd frontend
npm run dev
# เปิด browser: http://localhost:5173
```

## 🐛 Troubleshooting

### Backend ไม่เริ่ม

**Error**: `ModuleNotFoundError`
```bash
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

**Error**: `Connection failed`
```bash
# ตรวจสอบ .env file
# ตรวจสอบ internet connection
python scripts/test_supabase_connection.py
```

### Frontend ไม่เริ่ม

**Error**: `Cannot find module`
```bash
# ลบ node_modules และติดตั้งใหม่
rm -rf node_modules
npm install
```

**Error**: `Port 5173 already in use`
```bash
# หยุด process ที่ใช้ port นั้นอยู่
# หรือเปลี่ยน port ใน vite.config.ts
```

### Database Connection Issues

**Error**: `Tenant or user not found`
- ตรวจสอบ DATABASE_URL ใน .env
- ตรวจสอบ password ถูกต้อง

**Error**: `Too many connections`
- รอสักครู่แล้วลองใหม่
- หรือ restart backend

## 📚 เอกสารเพิ่มเติม

- [Backend README](backend/README.md) - Backend documentation
- [Supabase Migration Guide](backend/SUPABASE_MIGRATION_GUIDE.md) - Migration details
- [API Documentation](backend/API_DOCUMENTATION.md) - API reference

## 💡 Tips

### สำหรับ Backend Development

1. ใช้ virtual environment เสมอ
2. ติดตั้ง dependencies ใหม่เมื่อมีการอัพเดท requirements.txt
3. ทดสอบ API ผ่าน http://localhost:8000/docs
4. ดู logs เพื่อ debug

### สำหรับ Frontend Development

1. ใช้ React DevTools
2. ตรวจสอบ Network tab ใน browser
3. ดู console สำหรับ errors
4. Hot reload ทำงานอัตโนมัติ

### สำหรับ Database

1. ไม่ต้อง import ข้อมูล - ใช้ Supabase
2. ดูข้อมูลผ่าน Supabase Dashboard
3. ระวังการแก้ไขข้อมูลโดยตรง - อาจกระทบทีม
4. ใช้ API endpoints แทนการแก้ database โดยตรง

## 🤝 การทำงานร่วมกัน

### Communication

- แจ้งทีมก่อนแก้ไข database schema
- สร้าง Pull Request สำหรับ features ใหม่
- Review code ของกันและกัน
- ใช้ Issues บน GitHub สำหรับ bugs

### Best Practices

1. **Pull ก่อนเริ่มงาน**: `git pull origin main`
2. **สร้าง branch ใหม่**: `git checkout -b feature/xxx`
3. **Commit บ่อยๆ**: แต่ละ commit ควรมีความหมาย
4. **Test ก่อน push**: ตรวจสอบว่าโค้ดทำงาน
5. **Write clear commit messages**: อธิบายว่าทำอะไร

## 🆘 ขอความช่วยเหลือ

ถ้ามีปัญหา:

1. ตรวจสอบ error message
2. ดูใน Troubleshooting section
3. ค้นหาใน Issues บน GitHub
4. ถามทีม
5. สร้าง Issue ใหม่พร้อม error details

## 📞 Contact

- **Project Lead**: [ชื่อ]
- **Backend Team**: [ชื่อ]
- **Frontend Team**: [ชื่อ]
- **ML Team**: [ชื่อ]

---

**Happy Coding! 🚀**

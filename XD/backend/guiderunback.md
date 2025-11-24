# 🚀 วิธีรัน Backend

## Option 1: ใช้ run.py (แนะนำ)
```bash
./venv_new/bin/python run.py
```

## Option 2: ใช้ uvicorn โดยตรง
```bash
./venv_new/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Option 3: ใช้ python -m
```bash
./venv_new/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ตรวจสอบว่ารันสำเร็จ
- เปิด browser: http://localhost:8000
- ดู API docs: http://localhost:8000/docs
- Test health: http://localhost:8000/health

## หยุดการทำงาน
กด `CTRL+C`
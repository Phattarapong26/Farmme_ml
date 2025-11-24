# Git Setup Instructions

## ขั้นตอนการ Push โปรเจคขึ้น GitHub

### 1. ติดตั้ง Git (ถ้ายังไม่มี)

**ดาวน์โหลด Git:**
- ไปที่: https://git-scm.com/download/win
- ดาวน์โหลดและติดตั้ง
- เลือก "Use Git from the Windows Command Prompt" ตอนติดตั้ง
- Restart terminal หลังติดตั้ง

**ตรวจสอบว่าติดตั้งสำเร็จ:**
```bash
git --version
```

### 2. Setup Git Repository

**วิธีที่ 1: ใช้ Batch File (แนะนำ - ง่ายที่สุด)**

Double-click ไฟล์:
```
setup_git.bat
```

จากนั้น double-click:
```
push_to_github.bat
```

**วิธีที่ 2: รันคำสั่งเอง**

เปิด Command Prompt หรือ PowerShell ในโฟลเดอร์โปรเจค:

```bash
# 1. Initialize Git
git init

# 2. Configure user
git config user.name "Phattarapong26"
git config user.email "phattarapong26@example.com"

# 3. Add remote
git remote add origin https://github.com/Phattarapong26/app.git

# 4. Add all files
git add .

# 5. Commit
git commit -m "Initial commit: FarmMe project with Supabase migration"

# 6. Set main branch
git branch -M main

# 7. Push to GitHub
git push -u origin main
```

### 3. GitHub Credentials

เมื่อ push จะถูกถามข้อมูล:

**Username:**
```
Phattarapong26
```

**Password (Personal Access Token):**
```
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
```

⚠️ **หมายเหตุ:** ใช้ Personal Access Token แทน password ปกติ

### 4. ตรวจสอบว่า Push สำเร็จ

เปิด browser ไปที่:
```
https://github.com/Phattarapong26/app
```

คุณควรเห็นไฟล์ทั้งหมดของโปรเจค

## 📁 ไฟล์ที่จะถูก Push

### ✅ จะถูก Push:
- Source code ทั้งหมด (backend, frontend)
- Documentation (README, SETUP_GUIDE, etc.)
- Configuration files (.gitignore, requirements.txt, package.json)
- Migration scripts
- .env.example (template)

### ❌ จะไม่ถูก Push (ตาม .gitignore):
- .env (มี passwords!)
- node_modules/
- .venv/
- __pycache__/
- *.db, *.log
- Dataset/*.csv (ไฟล์ใหญ่)

## 🔄 การอัพเดทโค้ดในอนาคต

หลังจาก push ครั้งแรกแล้ว ถ้ามีการแก้ไขโค้ด:

```bash
# 1. ดูไฟล์ที่เปลี่ยนแปลง
git status

# 2. เพิ่มไฟล์ที่แก้ไข
git add .

# 3. Commit พร้อมข้อความ
git commit -m "Update: describe what you changed"

# 4. Push ขึ้น GitHub
git push
```

## 🆘 Troubleshooting

### ปัญหา: Git command not found

**แก้ไข:**
1. ติดตั้ง Git จาก https://git-scm.com/download/win
2. Restart terminal
3. ลองรันคำสั่งใหม่

### ปัญหา: Authentication failed

**แก้ไข:**
1. ตรวจสอบ username: `Phattarapong26`
2. ตรวจสอบ token: `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`
3. ตรวจสอบว่า token ยังไม่หมดอายุ
4. ตรวจสอบว่า token มี permissions: `repo` (full control)

### ปัญหา: Repository not found

**แก้ไข:**
1. ตรวจสอบว่าสร้าง repository แล้วที่ GitHub
2. ตรวจสอบชื่อ repository: `app`
3. ตรวจสอบ URL: `https://github.com/Phattarapong26/app.git`

### ปัญหา: Large files

**แก้ไข:**
1. ตรวจสอบว่า .gitignore ครบถ้วน
2. ไฟล์ใหญ่ (>100MB) ต้องใช้ Git LFS
3. หรือเก็บไว้ที่อื่น (Google Drive, Supabase Storage)

## 📝 Git Best Practices

### Commit Messages

ใช้รูปแบบนี้:
```
Add: เพิ่ม feature ใหม่
Update: แก้ไขโค้ดที่มีอยู่
Fix: แก้ bug
Remove: ลบโค้ดหรือไฟล์
Refactor: ปรับปรุงโค้ดโดยไม่เปลี่ยนการทำงาน
Docs: อัพเดท documentation
```

ตัวอย่าง:
```bash
git commit -m "Add: Supabase migration scripts"
git commit -m "Fix: Database connection timeout issue"
git commit -m "Update: README with setup instructions"
```

### Branching Strategy

สำหรับทีม:
```bash
# สร้าง branch ใหม่สำหรับ feature
git checkout -b feature/your-feature-name

# ทำงานและ commit
git add .
git commit -m "Add: your feature"

# Push branch
git push origin feature/your-feature-name

# สร้าง Pull Request บน GitHub
# หลังจาก merge แล้ว กลับไป main
git checkout main
git pull origin main
```

## 🔐 Security Reminders

⚠️ **สิ่งที่ต้องระวัง:**

1. **ไม่ commit .env file** - มี passwords และ API keys
2. **ไม่ commit database files** - ข้อมูลส่วนตัว
3. **ไม่ commit large files** - ใช้ Git LFS หรือเก็บที่อื่น
4. **ไม่ commit node_modules/** - ใหญ่เกินไป
5. **ไม่ commit .venv/** - virtual environment

✅ **ตรวจสอบก่อน commit:**
```bash
git status
git diff
```

## 📞 ติดต่อ

ถ้ามีปัญหา:
1. ดู error message
2. ค้นหาใน Google
3. ถามทีม
4. สร้าง Issue บน GitHub

---

**Repository:** https://github.com/Phattarapong26/app

**Happy Coding! 🚀**

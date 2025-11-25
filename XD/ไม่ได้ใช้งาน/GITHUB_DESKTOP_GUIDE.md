# 🖥️ คู่มือใช้ GitHub Desktop สำหรับ Deploy

## � ขขั้นตอนการ Commit และ Push

### 1️⃣ เปิด GitHub Desktop

เปิดโปรแกรม GitHub Desktop และเลือก repository: **XD**

---

### 2️⃣ ดูไฟล์ที่เปลี่ยนแปลง

ใน GitHub Desktop คุณจะเห็น:

**✅ ไฟล์ที่ควร Commit (ติ๊กถูกไว้):**
```
✓ .github/workflows/deploy.yml          (ไฟล์ใหม่)
✓ frontend/vite.config.ts               (แก้ไข)
✓ frontend/src/pages/Intro.tsx          (แก้ไข)
✓ frontend/src/config/api.ts            (ไฟล์ใหม่)
✓ frontend/.env.example                 (ไฟล์ใหม่)
✓ backend/config.py                     (แก้ไข)
✓ DEPLOYMENT_GUIDE.md                   (ไฟล์ใหม่)
✓ READY_TO_DEPLOY.md                    (ไฟล์ใหม่)
✓ WHAT_TO_COMMIT.md                     (ไฟล์ใหม่)
✓ GITHUB_DESKTOP_GUIDE.md               (ไฟล์ใหม่)
```

**❌ ไฟล์ที่ไม่ควร Commit (เอาติ๊กออก!):**
```
✗ backend/.env                          ⚠️ อันตราย! มี API keys
✗ SECURITY_ALERT.md                     (ลบหลังอ่านแล้ว)
✗ test_*.py                             (ไฟล์ test - ไม่จำเป็น)
✗ *_SUMMARY.md                          (ไฟล์ summary - ไม่จำเป็น)
✗ check_*.py                            (ไฟล์ check - ไม่จำเป็น)
```

---

### 3️⃣ เลือกไฟล์ที่จะ Commit

#### วิธีที่ 1: Commit ทั้งหมด (ง่ายที่สุด)
1. ดูว่าไม่มี `backend/.env` ในรายการ
2. ถ้ามี ให้ **เอาติ๊กออก** (uncheck)
3. ติ๊กไฟล์อื่นๆ ทั้งหมด

#### วิธีที่ 2: Commit เฉพาะไฟล์สำคัญ (ปลอดภัยที่สุด)
1. กด **Deselect All** (เอาติ๊กออกทั้งหมด)
2. ติ๊กเฉพาะไฟล์เหล่านี้:
   - `.github/workflows/deploy.yml`
   - `frontend/vite.config.ts`
   - `frontend/src/pages/Intro.tsx`
   - `frontend/src/config/api.ts`
   - `frontend/.env.example`
   - `backend/config.py`
   - `DEPLOYMENT_GUIDE.md`
   - `READY_TO_DEPLOY.md`
   - `WHAT_TO_COMMIT.md`
   - `GITHUB_DESKTOP_GUIDE.md`

---

### 4️⃣ เขียน Commit Message

ในช่อง **Summary** (ด้านล่างซ้าย):
```
Add deployment configuration for GitHub Pages and Render
```

ในช่อง **Description** (ถ้าต้องการ):
```
- Add GitHub Actions workflow for auto-deploy
- Add API configuration file
- Update vite config for GitHub Pages base path
- Update Intro page with Thai-English text
- Update CORS to allow GitHub Pages
- Add comprehensive deployment guides
```

---

### 5️⃣ Commit

1. คลิกปุ่ม **Commit to main** (ด้านล่างซ้าย)
2. รอสักครู่ จะเห็นข้อความ "No local changes"

---

### 6️⃣ Push to GitHub

1. คลิกปุ่ม **Push origin** (ด้านบนขวา)
2. รอจนกว่าจะเสร็จ (แถบสีน้ำเงินเต็ม)
3. เสร็จแล้ว! 🎉

---

## 🔍 ตรวจสอบหลัง Push

### เช็คใน GitHub Desktop
- ไม่มี changes ค้างอยู่
- History แสดง commit ล่าสุด

### เช็คใน GitHub.com
1. เปิด: https://github.com/Phattarapong26/XD
2. ดู commit ล่าสุด
3. ไปที่ **Actions** tab
4. ดู workflow "Deploy to GitHub Pages" กำลังทำงาน

---

## ⚠️ สิ่งที่ต้องระวัง

### 🚨 ห้ามติ๊กไฟล์เหล่านี้!

```
❌ backend/.env                    # มี API keys และ passwords
❌ frontend/.env                   # ถ้ามี
❌ *.db                            # Database files
❌ node_modules/                   # Dependencies (ใหญ่มาก)
❌ __pycache__/                    # Python cache
```

### ✅ ถ้าเห็นไฟล์เหล่านี้ใน GitHub Desktop

**ปกติ:** ไฟล์เหล่านี้ไม่ควรปรากฏเลย เพราะอยู่ใน `.gitignore`

**ถ้าเห็น:** แสดงว่า `.gitignore` ไม่ทำงาน หรือไฟล์ถูก track ไปแล้วก่อนหน้า

**แก้ไข:**
1. เอาติ๊กออก (uncheck)
2. ไม่ commit ไฟล์นั้น
3. ถ้าจำเป็น ให้ untrack ไฟล์นั้นออกจาก git

---

## 🎯 หลังจาก Push แล้ว

### 1. ตั้งค่า GitHub Pages
1. ไปที่: https://github.com/Phattarapong26/XD/settings/pages
2. ตั้งค่า **Source**: GitHub Actions
3. บันทึก

### 2. เพิ่ม GitHub Secret
1. ไปที่: https://github.com/Phattarapong26/XD/settings/secrets/actions
2. คลิก **New repository secret**
3. เพิ่ม:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend.onrender.com` (จะได้หลัง deploy backend)
4. คลิก **Add secret**

### 3. Deploy Backend ไป Render
ทำตามขั้นตอนใน `DEPLOYMENT_GUIDE.md`

---

## 💡 Tips สำหรับ GitHub Desktop

### ดู Changes ก่อน Commit
- คลิกที่ไฟล์แต่ละไฟล์
- ดูว่ามีการเปลี่ยนแปลงอะไรบ้าง
- ตรวจสอบว่าไม่มี API keys หรือ passwords

### Undo Commit (ถ้า commit ผิด)
1. ไปที่ **History** tab
2. คลิกขวาที่ commit ล่าสุด
3. เลือก **Undo commit**
4. แก้ไขแล้ว commit ใหม่

### Discard Changes (ถ้าไม่ต้องการเปลี่ยนแปลง)
1. คลิกขวาที่ไฟล์
2. เลือก **Discard changes**
3. ไฟล์จะกลับไปเป็นเหมือนเดิม

---

## 📸 ภาพประกอบ (ตำแหน่งต่างๆ)

```
┌─────────────────────────────────────────────────────────┐
│ GitHub Desktop                                    [Push origin] │
├─────────────────────────────────────────────────────────┤
│ Changes (10)                                            │
│                                                         │
│ ✓ .github/workflows/deploy.yml          +100 lines    │
│ ✓ frontend/vite.config.ts               +1 -0         │
│ ✓ frontend/src/pages/Intro.tsx          +9 -9         │
│ ✓ frontend/src/config/api.ts            +20 lines     │
│ ✓ backend/config.py                     +1 -0         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Summary (required)                                      │
│ Add deployment configuration                            │
│                                                         │
│ Description                                             │
│ - Add GitHub Actions workflow                           │
│ - Update configs for deployment                         │
│                                                         │
│                                    [Commit to main]     │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist

ก่อน Commit:
- [ ] ไม่มี `backend/.env` ในรายการ
- [ ] ไม่มี API keys หรือ passwords ในไฟล์ที่จะ commit
- [ ] เขียน commit message แล้ว
- [ ] เลือกไฟล์ที่ต้องการ commit แล้ว

หลัง Push:
- [ ] เช็ค GitHub.com ว่า push สำเร็จ
- [ ] เช็ค Actions tab ว่า workflow ทำงาน
- [ ] ตั้งค่า GitHub Pages
- [ ] เพิ่ม GitHub Secret
- [ ] Deploy backend ไป Render

---

## 🎉 สรุป

**ใช้ GitHub Desktop ง่ายมาก!**

1. เปิด GitHub Desktop
2. เลือกไฟล์ที่จะ commit (ระวัง backend/.env)
3. เขียน commit message
4. คลิก "Commit to main"
5. คลิก "Push origin"
6. เสร็จ! 🚀

**ไม่ต้องกังวลเรื่อง command line เลย!** 😊

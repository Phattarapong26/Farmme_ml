# 🚨 SECURITY ALERT - ต้องดำเนินการทันที!

## ⚠️ ข้อมูล Sensitive ที่ถูกเปิดเผย

คุณได้แชร์ข้อมูลที่ sensitive ในการสนทนา ซึ่งอาจถูกบันทึกไว้:

1. **Gemini API Key**: `AIzaSyBOhVXgPhixsj4jJ5aI62Xa9iq6AE74pH0`
2. **Database Password**: `Zx0966566414`
3. **Supabase Host**: `db.inhanxxglxnjbugppulg.supabase.co`

## 🔒 ต้องทำทันที (ตามลำดับความสำคัญ)

### 1️⃣ เปลี่ยน Gemini API Key (สำคัญที่สุด!)

1. ไปที่: https://makersuite.google.com/app/apikey
2. **Revoke** (ยกเลิก) API key เดิม: `AIzaSyBOhVXgPhixsj4jJ5aI62Xa9iq6AE74pH0`
3. สร้าง API key ใหม่
4. อัพเดทใน `backend/.env`:
   ```
   GEMINI_API_KEY=<new_key_here>
   ```

### 2️⃣ เปลี่ยน Database Password (แนะนำ)

1. ไปที่ Supabase Dashboard: https://supabase.com/dashboard
2. ไปที่ Settings → Database → Database Password
3. คลิก "Generate new password"
4. Copy password ใหม่
5. อัพเดทใน `backend/.env`:
   ```
   DATABASE_URL=postgresql://postgres:<new_password>@db.inhanxxglxnjbugppulg.supabase.co:5432/postgres
   ```

### 3️⃣ ตรวจสอบ .gitignore

ตรวจสอบว่า `backend/.env` อยู่ใน `.gitignore` แล้ว (ควรอยู่แล้ว):

```bash
# ตรวจสอบ
cat .gitignore | grep ".env"
```

ถ้ายังไม่มี ให้เพิ่ม:
```
backend/.env
.env
*.env
```

### 4️⃣ ตรวจสอบ Git History

ตรวจสอบว่าไม่เคย commit ไฟล์ `.env`:

```bash
git log --all --full-history -- backend/.env
```

ถ้าเคย commit ไว้ ต้องลบออกจาก history:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all
```

## ✅ หลังจากเปลี่ยนแล้ว

### สำหรับ Development (Local)
อัพเดทไฟล์ `backend/.env`:
```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres:<NEW_PASSWORD>@db.inhanxxglxnjbugppulg.supabase.co:5432/postgres

# Gemini AI
GEMINI_API_KEY=<NEW_API_KEY>

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
DEBUG=True
```

### สำหรับ Production (Render)
อัพเดท Environment Variables ใน Render Dashboard:
1. ไปที่ https://dashboard.render.com
2. เลือก service ของคุณ
3. ไปที่ Environment
4. อัพเดท:
   - `DATABASE_URL` (ใช้ Connection Pooling URL)
   - `GEMINI_API_KEY` (ใช้ key ใหม่)

## 📝 Best Practices ต่อไป

### ❌ อย่าทำ:
- อย่าแชร์ไฟล์ `.env` ในที่สาธารณะ
- อย่า commit `.env` เข้า git
- อย่าแชร์ API keys ในแชท/email/slack
- อย่าใส่ credentials ใน code

### ✅ ควรทำ:
- ใช้ `.env.example` เป็น template (ไม่มีค่าจริง)
- เก็บ credentials ใน environment variables
- ใช้ secrets management (GitHub Secrets, Render Environment Variables)
- Rotate (เปลี่ยน) API keys เป็นประจำ

## 🔐 Connection Pooling URL สำหรับ Production

สำหรับ Render ให้ใช้ Connection Pooling URL แทน:

```
postgresql://postgres.<ref>:<password>@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

หา URL นี้ได้จาก:
1. Supabase Dashboard → Settings → Database
2. Connection string → Connection pooling
3. Mode: Transaction
4. Copy URL

## 📞 ติดต่อ Support

ถ้ามีปัญหา:
- **Supabase**: https://supabase.com/dashboard/support
- **Google AI**: https://support.google.com/

---

**หมายเหตุ**: ไฟล์นี้ควรถูกลบหลังจากดำเนินการเสร็จแล้ว เพราะมีข้อมูล sensitive

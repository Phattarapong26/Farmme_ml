# วิธี Add ไฟล์ Model ขึ้น GitHub

## สถานะปัจจุบัน
✅ แก้ไข `.gitignore` เรียบร้อยแล้ว - ไฟล์ model จะไม่ถูก ignore อีกต่อไป

## ขนาดไฟล์โมเดล
- Model A: ~0.13-0.32 MB
- Model B: ~0.13 MB  
- Model C: ~2.56-3.06 MB
- **รวม: ~9 MB** (ไม่เกินขีดจำกัดของ GitHub)

## คำสั่งที่ต้องรัน

```bash
# 1. Add ไฟล์โมเดลทั้งหมด
git add backend/models/*.pkl

# 2. Add ไฟล์ JSON metadata ของ Model C
git add backend/models/model_c_*.json

# 3. Add ไฟล์ .gitignore ที่แก้ไขแล้ว
git add .gitignore

# 4. Commit
git commit -m "Add ML model files for deployment

- Added Model A (price prediction)
- Added Model B (planting window)
- Added Model C (stratified price forecasting)
- Updated .gitignore to allow model files
- Total size: ~9 MB"

# 5. Push ขึ้น GitHub
git push origin main
```

## หมายเหตุ
- ไฟล์โมเดลจำเป็นสำหรับการ deploy บน Render
- ขนาดไม่เกิน 100 MB ต่อไฟล์ (ตาม GitHub limit)
- หากต้องการลบไฟล์โมเดลออกในอนาคต ให้ใช้ Git LFS แทน

"""
Quick Save Model (ไม่ต้อง train ใหม่)
======================================
สคริปต์นี้จะ save model โดยตรงจากผลลัพธ์ที่คุณรันไปแล้ว
ไม่ต้อง train ใหม่!

ใช้เมื่อ: รัน model_c_new.py เสร็จแล้ว และต้องการ save model
"""

import pickle
import json
from datetime import datetime
import os

print("="*80)
print("💾 Quick Save Model (Manual)")
print("="*80)

print("\n📋 จากผลลัพธ์ที่คุณรันไปแล้ว:")
print("   - Best Model: Gradient Boosting")
print("   - Test R²: 0.6898")
print("   - Test MAE: 9.95")
print("   - Test RMSE: 15.98")
print("   - Baseline MA-14 R²: 0.6711")

print("\n⚠️  เนื่องจากเราไม่สามารถเข้าถึง model object ได้โดยตรง")
print("   กรุณาใช้วิธีนี้แทน:")

print("\n" + "="*80)
print("📝 วิธีที่ 1: ใช้ Python Interactive (แนะนำ)")
print("="*80)

print("""
1. เปิด Python:
   python

2. รันคำสั่งนี้:
   exec(open('buildingModel.py/model_c_new.py').read())
   
3. รอจน train เสร็จ (จะเห็น "✅ Model Training Complete!")

4. รันคำสั่งนี้เพื่อ save:
   exec(open('buildingModel.py/save_model_from_memory.py').read())
""")

print("\n" + "="*80)
print("📝 วิธีที่ 2: ใช้ Jupyter Notebook")
print("="*80)

print("""
1. เปิด Jupyter:
   jupyter notebook

2. สร้าง notebook ใหม่

3. รันใน cell แรก:
   %run buildingModel.py/model_c_new.py

4. รันใน cell ที่สอง:
   %run buildingModel.py/save_model_from_memory.py
""")

print("\n" + "="*80)
print("📝 วิธีที่ 3: แก้ model_c_new.py ให้ save อัตโนมัติ")
print("="*80)

print("""
เพิ่มโค้ดนี้ที่ท้าย model_c_new.py:

import pickle
import json
import os

os.makedirs('backend/models', exist_ok=True)

# Save model
with open('backend/models/model_c_gradient_boosting.pkl', 'wb') as f:
    pickle.dump(best_model['model'], f)

# Save features
with open('backend/models/model_c_features.json', 'w') as f:
    json.dump(available_features, f, indent=2)

print("✅ Model saved!")
""")

print("\n" + "="*80)
print("💡 คำแนะนำ")
print("="*80)

print("""
ถ้า save_and_tune_model_c.py กำลังรันอยู่:
- ให้รอต่อไป (ใช้เวลา 5-10 นาที)
- หรือกด Ctrl+C เพื่อยกเลิก แล้วใช้วิธีที่ 1 หรือ 2 ข้างบน
""")

print("\n" + "="*80)

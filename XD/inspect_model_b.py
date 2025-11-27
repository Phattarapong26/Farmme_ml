# -*- coding: utf-8 -*-
"""
ตรวจสอบโครงสร้างของ Model B
"""

import pickle
from pathlib import Path

model_path = Path("XD/backend/models/model_b_xgboost.pkl")

print("=" * 80)
print("ตรวจสอบโครงสร้าง Model B")
print("=" * 80)

with open(model_path, 'rb') as f:
    model_b = pickle.load(f)

print(f"\nประเภท: {type(model_b)}")

if isinstance(model_b, dict):
    print("\n📦 Model B เป็น Dictionary ที่มี keys:")
    for key in model_b.keys():
        print(f"   - {key}: {type(model_b[key])}")
    
    # ลองดูข้อมูลในแต่ละ key
    print("\n📊 รายละเอียดแต่ละ key:")
    for key, value in model_b.items():
        print(f"\n   {key}:")
        if hasattr(value, '__dict__'):
            print(f"      Type: {type(value).__name__}")
            if hasattr(value, 'n_features_in_'):
                print(f"      Features: {value.n_features_in_}")
            if hasattr(value, 'feature_names_in_'):
                print(f"      Feature names: {value.feature_names_in_}")
        else:
            print(f"      Value: {value}")

print("\n" + "=" * 80)

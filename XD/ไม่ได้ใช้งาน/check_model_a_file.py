# -*- coding: utf-8 -*-
"""
ตรวจสอบไฟล์ Model A ว่ามีปัญหาอะไร
"""

import pickle
import sys
from pathlib import Path

model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl")

print("=" * 80)
print("🔍 ตรวจสอบไฟล์ Model A")
print("=" * 80)

print(f"\n📁 Model Path: {model_path}")
print(f"   Exists: {model_path.exists()}")
print(f"   Size: {model_path.stat().st_size if model_path.exists() else 0} bytes")

if not model_path.exists():
    print("\n❌ ไฟล์ไม่มีอยู่!")
    sys.exit(1)

print("\n🔧 กำลังโหลด Model...")

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"✅ โหลดสำเร็จ!")
    print(f"\n📊 Model Information:")
    print(f"   Type: {type(model).__name__}")
    print(f"   Module: {type(model).__module__}")
    
    # Check attributes
    attrs = dir(model)
    important_attrs = ['n_features_in_', 'predict', 'feature_importances_', 'n_estimators']
    
    print(f"\n🔍 Attributes:")
    for attr in important_attrs:
        has_attr = hasattr(model, attr)
        print(f"   {attr}: {'✅' if has_attr else '❌'}")
        if has_attr:
            value = getattr(model, attr)
            if not callable(value):
                print(f"      Value: {value}")
    
    # Try to predict
    print(f"\n🧪 ทดสอบ Prediction:")
    try:
        import numpy as np
        
        # Get number of features
        if hasattr(model, 'n_features_in_'):
            n_features = model.n_features_in_
            print(f"   Features Required: {n_features}")
            
            # Create dummy data
            X_test = np.random.rand(1, n_features)
            prediction = model.predict(X_test)
            
            print(f"   ✅ Prediction สำเร็จ!")
            print(f"   Result: {prediction[0]:.2f}")
        else:
            print(f"   ⚠️ Model ไม่มี n_features_in_ attribute")
            
    except Exception as e:
        print(f"   ❌ Prediction ล้มเหลว: {e}")
    
    print(f"\n✅ Model A ใช้งานได้!")
    
except Exception as e:
    print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    print(f"\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

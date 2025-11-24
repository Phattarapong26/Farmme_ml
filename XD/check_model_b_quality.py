# -*- coding: utf-8 -*-
"""
ตรวจสอบคุณภาพ Model B
ดูว่า train เร็วเกินไปหรือไม่ และใช้งานได้จริงหรือไม่
"""

import pickle
import json
from pathlib import Path

print("=" * 80)
print("🔍 ตรวจสอบคุณภาพ Model B")
print("=" * 80)

# 1. ตรวจสอบขนาดไฟล์
print("\n📁 ขนาดไฟล์ Model:")
model_files = [
    "model_b_xgboost.pkl",
    "model_b_temporal_gb.pkl",
    "model_b_logistic.pkl"
]

for model_file in model_files:
    path = Path(f"REMEDIATION_PRODUCTION/trained_models/{model_file}")
    if path.exists():
        size = path.stat().st_size
        print(f"   {model_file}: {size:,} bytes ({size/1024:.2f} KB)")
    else:
        print(f"   {model_file}: ❌ ไม่มี")

# 2. ตรวจสอบ Evaluation Results
print("\n📊 ผลการประเมิน:")
eval_path = Path("REMEDIATION_PRODUCTION/trained_models/model_b_evaluation.json")
if eval_path.exists():
    with open(eval_path, 'r') as f:
        results = json.load(f)
    
    print(f"\n   Dataset Size:")
    print(f"   - Total: {results.get('dataset_size', {}).get('total', 'N/A')} samples")
    print(f"   - Train: {results.get('dataset_size', {}).get('train', 'N/A')} samples")
    print(f"   - Test: {results.get('dataset_size', {}).get('test', 'N/A')} samples")
    
    print(f"\n   Best Model: {results.get('best_model', 'N/A')}")
    
    for model_name, metrics in results.get('models', {}).items():
        print(f"\n   {model_name}:")
        print(f"   - F1: {metrics.get('f1', 'N/A'):.4f}")
        print(f"   - Precision: {metrics.get('precision', 'N/A'):.4f}")
        print(f"   - Recall: {metrics.get('recall', 'N/A'):.4f}")
        print(f"   - ROC-AUC: {metrics.get('roc_auc', 'N/A'):.4f}")
else:
    print("   ❌ ไม่พบไฟล์ evaluation")

# 3. โหลดและทดสอบ Model
print("\n🧪 ทดสอบโหลด Model:")
for model_file in model_files:
    path = Path(f"REMEDIATION_PRODUCTION/trained_models/{model_file}")
    if path.exists():
        try:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            
            print(f"\n   {model_file}:")
            print(f"   - Type: {type(model).__name__}")
            
            # ตรวจสอบ attributes
            if hasattr(model, 'model'):
                print(f"   - Has model: ✅")
                print(f"   - Model type: {type(model.model).__name__}")
            
            if hasattr(model, 'scaler'):
                print(f"   - Has scaler: ✅")
            
            # ลอง predict
            import numpy as np
            X_test = np.random.rand(1, 8)  # 8 features
            
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(X_test)
                    print(f"   - Prediction: {pred[0]} ✅")
                else:
                    print(f"   - ❌ ไม่มี predict method")
            except Exception as e:
                print(f"   - ❌ Prediction failed: {e}")
                
        except Exception as e:
            print(f"   ❌ โหลดไม่ได้: {e}")

# 4. วิเคราะห์ปัญหา
print("\n" + "=" * 80)
print("🔍 วิเคราะห์:")
print("=" * 80)

# อ่าน evaluation results อีกครั้ง
if eval_path.exists():
    with open(eval_path, 'r') as f:
        results = json.load(f)
    
    total_samples = results.get('dataset_size', {}).get('total', 0)
    train_samples = results.get('dataset_size', {}).get('train', 0)
    
    print(f"\n1. ขนาด Dataset:")
    print(f"   Total: {total_samples} samples")
    print(f"   Train: {train_samples} samples")
    
    if total_samples < 10000:
        print(f"   ⚠️ Dataset เล็ก! (< 10,000 samples)")
        print(f"   → Model train เร็วเพราะข้อมูลน้อย")
    else:
        print(f"   ✅ Dataset ขนาดพอใช้")
    
    print(f"\n2. จำนวน Features:")
    print(f"   Features: 8 features")
    print(f"   ⚠️ Features น้อย! (Model A ใช้ 19 features)")
    print(f"   → Model train เร็วเพราะ features น้อย")
    
    print(f"\n3. Algorithm:")
    best_model = results.get('best_model', '')
    if 'logistic' in best_model.lower():
        print(f"   Best: Logistic Regression")
        print(f"   ⚠️ Algorithm ง่าย! (Linear model)")
        print(f"   → Train เร็วเพราะเป็น linear model")
    
    print(f"\n4. Performance:")
    best_metrics = results.get('models', {}).get(best_model, {})
    f1 = best_metrics.get('f1', 0)
    recall = best_metrics.get('recall', 0)
    
    print(f"   F1: {f1:.4f}")
    print(f"   Recall: {recall:.4f}")
    
    if recall >= 0.99:
        print(f"   ⚠️ Recall สูงผิดปกติ! (= {recall:.4f})")
        print(f"   → อาจ overfit หรือ data leakage")
    
    if f1 > 0.85:
        print(f"   ⚠️ F1 สูงผิดปกติ! (= {f1:.4f})")
        print(f"   → ควรตรวจสอบ data leakage")

print("\n" + "=" * 80)
print("💡 สรุป:")
print("=" * 80)
print("""
Model B train เร็วเพราะ:
1. Dataset เล็ก (6,226 samples vs Model A ที่ใช้ 1.4M samples)
2. Features น้อย (8 features vs Model A ที่ใช้ 19 features)
3. Algorithm ง่าย (Logistic Regression เป็น linear model)

⚠️ ปัญหาที่พบ:
1. Recall = 1.0000 (100%) → น่าสงสัย data leakage
2. F1 = 0.8683 สูงผิดปกติ
3. Dataset เล็กเกินไป

✅ แนะนำ:
1. ตรวจสอบ data leakage (features ที่รั่วไหล)
2. ใช้ dataset ใหญ่ขึ้น
3. ทดสอบกับข้อมูลจริง
""")

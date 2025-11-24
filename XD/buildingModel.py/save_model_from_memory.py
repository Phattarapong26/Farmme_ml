"""
Save Model from Memory
======================
สคริปต์นี้ใช้ save model ที่ train ไว้แล้วใน memory
ต้องรันหลังจาก model_c_new.py ใน Python session เดียวกัน

Usage:
1. รัน model_c_new.py ให้เสร็จก่อน
2. แล้วรันสคริปต์นี้ใน session เดียวกัน
"""

import pickle
import json
from datetime import datetime
import os

print("="*80)
print("💾 Save Model from Memory")
print("="*80)

# ตรวจสอบว่ามี variables จาก model_c_new.py หรือไม่
try:
    _ = best_model
    _ = available_features
    _ = baseline_r2_2
    _ = train_df
    _ = test_df
    print("\n✅ Found trained model in memory!")
except NameError as e:
    print(f"\n❌ Error: {e}")
    print("\n⚠️  This script must be run AFTER model_c_new.py in the same Python session")
    print("\nHow to use:")
    print("1. Run model_c_new.py first")
    print("2. Then run this script in the same session")
    print("\nExample (in Python/IPython):")
    print("   exec(open('buildingModel.py/model_c_new.py').read())")
    print("   exec(open('buildingModel.py/save_model_from_memory.py').read())")
    exit(1)

# ============================================================================
# Save Model
# ============================================================================
print("\n" + "="*80)
print("💾 Saving Model")
print("="*80)

os.makedirs('backend/models', exist_ok=True)

# Save model
model_path = 'backend/models/model_c_gradient_boosting.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(best_model['model'], f)
print(f"\n✅ Model saved: {model_path}")

# Save feature list
features_path = 'backend/models/model_c_features.json'
with open(features_path, 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"✅ Features saved: {features_path}")

# Save metadata
metadata = {
    'model_name': 'Gradient Boosting',
    'test_r2': float(best_model['test_r2']),
    'test_mae': float(best_model['test_mae']),
    'test_rmse': float(best_model['test_rmse']),
    'baseline_ma14_r2': float(baseline_r2_2),
    'gap_vs_baseline': float(best_model['test_r2'] - baseline_r2_2),
    'train_date_range': f"{train_df['date'].min()} to {train_df['date'].max()}",
    'test_date_range': f"{test_df['date'].min()} to {test_df['date'].max()}",
    'n_features': len(available_features),
    'trained_at': datetime.now().isoformat()
}

metadata_path = 'backend/models/model_c_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✅ Metadata saved: {metadata_path}")

print("\n" + "="*80)
print("🎉 Summary")
print("="*80)

print(f"\n📊 Model Performance:")
print(f"   - Test R²: {best_model['test_r2']:.4f}")
print(f"   - Test MAE: {best_model['test_mae']:.2f}")
print(f"   - Test RMSE: {best_model['test_rmse']:.2f}")
print(f"   - Baseline MA-14 R²: {baseline_r2_2:.4f}")
print(f"   - Improvement: {(best_model['test_r2'] - baseline_r2_2):.4f}")

print(f"\n📁 Files saved:")
print(f"   - {model_path}")
print(f"   - {features_path}")
print(f"   - {metadata_path}")

print(f"\n📝 Next Steps:")
print(f"   1. ✅ Model saved successfully")
print(f"   2. 🔄 Update backend/model_c_wrapper.py")
print(f"   3. 🧪 Test the wrapper")
print(f"   4. (Optional) Run save_and_tune_model_c.py for hyperparameter tuning")

print("\n" + "="*80)
print("✅ Done!")
print("="*80)

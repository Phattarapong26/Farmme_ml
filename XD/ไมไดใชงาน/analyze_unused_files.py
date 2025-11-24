"""
Analyze and categorize files for Model C
=========================================
แยกไฟล์ที่ใช้งานจริง vs ไฟล์ที่ไม่ได้ใช้แล้ว
"""

import os
from pathlib import Path

print("="*80)
print("📊 Analyzing Model C Files")
print("="*80)

# ============================================================================
# Files ที่ใช้งานจริง (PRODUCTION)
# ============================================================================
production_files = {
    "Models (backend/models/)": [
        "model_c_stratified_low_final.pkl",
        "model_c_stratified_medium_final.pkl",
        "model_c_stratified_high_final.pkl",
        "model_c_stratified_thresholds_final.json",
        "model_c_stratified_features_final.json",
        "model_c_stratified_metadata_final.json",
    ],
    "Code (backend/)": [
        "model_c_wrapper.py",
    ],
    "Tests": [
        "test_model_c_stratified.py",
    ],
    "Documentation": [
        "MODEL_C_FINAL_SUMMARY.md",
        "MODEL_C_DEPLOYMENT_GUIDE.md",
    ],
    "Visualizations (buildingModel.py/)": [
        "actual_vs_predicted_overall.png",
        "actual_vs_predicted_by_range.png",
        "actual_vs_predicted_crops.png",
    ]
}

# ============================================================================
# Files ที่ไม่ได้ใช้แล้ว (ARCHIVE)
# ============================================================================
unused_files = {
    "Training Scripts (buildingModel.py/)": [
        "model_c_new.py",  # เวอร์ชันแรก (ไม่มี stratified)
        "save_and_tune_model_c.py",  # hyperparameter tuning (ไม่ได้ใช้)
        "quick_save_model.py",  # quick save (ไม่ได้ใช้)
        "save_model_only.py",  # save only (ไม่ได้ใช้)
        "train_model_c_final.py",  # ใช้แล้ว (train เสร็จแล้ว)
        "model_c_stratified.py",  # test version (ใช้แล้ว)
        "data_cleaning_and_features.py",  # ทดสอบ features (ไม่ได้ผล)
        "model_c_with_log_transform.py",  # log transform (ไม่ได้ผล)
        "quick_test_log_transform.py",  # test log (ไม่ได้ผล)
    ],
    "Visualization Scripts (buildingModel.py/)": [
        "plot_actual_vs_predicted.py",  # ใช้แล้ว (สร้างกราฟเสร็จแล้ว)
        "visualize_model_c_fix.py",  # ใช้แล้ว (สร้างกราฟเสร็จแล้ว)
        "visualize_predictions.py",  # old version
    ],
    "Old Tests": [
        "test_model_c.py",  # test single model (ไม่ใช้แล้ว)
        "test_model_predictions.py",  # old test
        "test_wrapper.py",  # general test (ไม่เฉพาะ Model C)
    ],
    "Documentation (buildingModel.py/)": [
        "feedbackmodel_c.md",  # feedback (เก็บไว้อ้างอิง)
        "MODEL_C_FIX_SUMMARY.md",  # technical details (เก็บไว้อ้างอิง)
        "คำตอบ_Model_C.md",  # Thai explanation (เก็บไว้อ้างอิง)
    ],
    "Old Visualizations (buildingModel.py/)": [
        "model_c_fix_comparison.png",  # comparison chart (เก็บไว้อ้างอิง)
        "model_c_stratified_performance.png",  # performance chart (เก็บไว้อ้างอิง)
    ]
}

# ============================================================================
# Print Analysis
# ============================================================================
print("\n" + "="*80)
print("✅ FILES ที่ใช้งานจริง (PRODUCTION)")
print("="*80)

for category, files in production_files.items():
    print(f"\n📁 {category}:")
    for file in files:
        print(f"   ✅ {file}")

print("\n" + "="*80)
print("📦 FILES ที่ไม่ได้ใช้แล้ว (ARCHIVE)")
print("="*80)

total_unused = 0
for category, files in unused_files.items():
    print(f"\n📁 {category}:")
    for file in files:
        print(f"   📦 {file}")
        total_unused += 1

print(f"\n📊 Summary:")
print(f"   Production files: {sum(len(files) for files in production_files.values())}")
print(f"   Archive files: {total_unused}")

# ============================================================================
# Generate Move Commands
# ============================================================================
print("\n" + "="*80)
print("📝 Commands to Archive Files")
print("="*80)

print("\n# 1. Create archive folder")
print("mkdir ไม่ได้ใช้งาน")
print("mkdir ไม่ได้ใช้งาน\\buildingModel.py")

print("\n# 2. Move training scripts")
for file in unused_files["Training Scripts (buildingModel.py/)"]:
    print(f"move buildingModel.py\\{file} ไม่ได้ใช้งาน\\buildingModel.py\\")

print("\n# 3. Move visualization scripts")
for file in unused_files["Visualization Scripts (buildingModel.py/)"]:
    print(f"move buildingModel.py\\{file} ไม่ได้ใช้งาน\\buildingModel.py\\")

print("\n# 4. Move old tests")
for file in unused_files["Old Tests"]:
    print(f"move {file} ไม่ได้ใช้งาน\\")

print("\n# 5. Move documentation (keep for reference)")
for file in unused_files["Documentation (buildingModel.py/)"]:
    print(f"move buildingModel.py\\{file} ไม่ได้ใช้งาน\\buildingModel.py\\")

print("\n# 6. Move old visualizations")
for file in unused_files["Old Visualizations (buildingModel.py/)"]:
    print(f"move buildingModel.py\\{file} ไม่ได้ใช้งาน\\buildingModel.py\\")

print("\n" + "="*80)
print("✅ Analysis Complete!")
print("="*80)

# ไม่ได้ใช้งาน (Archived Files)

## 📦 Folder นี้คืออะไร?

Folder นี้เก็บไฟล์ที่**ไม่ได้ใช้งานแล้ว**สำหรับ Model C แต่เก็บไว้เพื่อ:
- อ้างอิงในอนาคต
- ดูประวัติการพัฒนา
- กรณีต้องการ rollback

## ⚠️ คำเตือน

**ไฟล์ในนี้ไม่ได้ใช้ในระบบ Production!**

ถ้าต้องการใช้งานระบบ ให้ใช้ไฟล์ใน:
- `backend/models/model_c_stratified_*_final.*`
- `backend/model_c_wrapper.py`
- `test_model_c_stratified.py`

## 📁 โครงสร้าง

```
ไม่ได้ใช้งาน/
├── README.md (ไฟล์นี้)
├── analyze_unused_files.py (script วิเคราะห์ไฟล์)
├── buildingModel.py/
│   ├── Training Scripts (ใช้แล้ว)
│   │   ├── model_c_new.py
│   │   ├── save_and_tune_model_c.py
│   │   ├── quick_save_model.py
│   │   ├── save_model_only.py
│   │   ├── train_model_c_final.py
│   │   ├── model_c_stratified.py
│   │   ├── data_cleaning_and_features.py
│   │   ├── model_c_with_log_transform.py
│   │   └── quick_test_log_transform.py
│   │
│   ├── Documentation (เก็บไว้อ้างอิง)
│   │   ├── feedbackmodel_c.md
│   │   ├── MODEL_C_FIX_SUMMARY.md
│   │   └── คำตอบ_Model_C.md
│   │
│   └── Visualizations (เก็บไว้อ้างอิง)
│       ├── model_c_fix_comparison.png
│       └── model_c_stratified_performance.png
│
└── Old Tests (ไม่ใช้แล้ว)
    ├── test_model_c.py
    ├── test_model_predictions.py
    └── test_wrapper.py
```

## 📊 สรุปไฟล์

### Training Scripts (9 files)
ไฟล์ที่ใช้ train models - **ใช้แล้ว ไม่ต้องรันอีก**

- `model_c_new.py` - เวอร์ชันแรก (single model)
- `save_and_tune_model_c.py` - hyperparameter tuning
- `train_model_c_final.py` - ✅ ใช้ train models ที่ใช้งานจริง
- `model_c_stratified.py` - test version
- `data_cleaning_and_features.py` - ทดสอบ features (ไม่ได้ผล)
- `model_c_with_log_transform.py` - log transform (ไม่ได้ผล)
- อื่นๆ - quick save scripts

### Documentation (3 files)
เอกสารเก่า - **เก็บไว้อ้างอิง**

- `feedbackmodel_c.md` - feedback จากการทดสอบ
- `MODEL_C_FIX_SUMMARY.md` - รายละเอียดการแก้ไข
- `คำตอบ_Model_C.md` - อธิบายภาษาไทย

### Visualizations (2 files)
กราฟเก่า - **เก็บไว้อ้างอิง**

- `model_c_fix_comparison.png` - เปรียบเทียบ single vs stratified
- `model_c_stratified_performance.png` - performance by range

### Old Tests (3 files)
Test scripts เก่า - **ไม่ใช้แล้ว**

- `test_model_c.py` - test single model
- `test_model_predictions.py` - old test
- `test_wrapper.py` - general test

## ✅ ไฟล์ที่ใช้งานจริง (อยู่นอก folder นี้)

### Models
```
backend/models/
├── model_c_stratified_low_final.pkl
├── model_c_stratified_medium_final.pkl
├── model_c_stratified_high_final.pkl
├── model_c_stratified_thresholds_final.json
├── model_c_stratified_features_final.json
└── model_c_stratified_metadata_final.json
```

### Code
```
backend/
└── model_c_wrapper.py
```

### Tests
```
test_model_c_stratified.py
```

### Documentation
```
MODEL_C_FINAL_SUMMARY.md
MODEL_C_DEPLOYMENT_GUIDE.md
```

### Visualizations
```
buildingModel.py/
├── actual_vs_predicted_overall.png
├── actual_vs_predicted_by_range.png
└── actual_vs_predicted_crops.png
```

## 🔄 ถ้าต้องการใช้ไฟล์ในนี้

1. **อ่านเอกสาร**: ดู documentation files เพื่อเข้าใจประวัติ
2. **ดูกราฟ**: ดู visualization files เพื่อเปรียบเทียบ
3. **อ้างอิง code**: ดู training scripts เพื่อเข้าใจวิธีการ train

**⚠️ อย่า deploy ไฟล์ในนี้!**

## 📅 Archive Date

**Date**: November 23, 2025  
**Reason**: Model C v7.0.0 (Stratified) deployed to production  
**Status**: Archived for reference only

---

**หมายเหตุ**: ถ้าต้องการ train model ใหม่ ให้ใช้:
```bash
python buildingModel.py/train_model_c_final.py
```
(แต่ไฟล์นี้อยู่ใน archive แล้ว ต้อง copy ออกมาก่อน)

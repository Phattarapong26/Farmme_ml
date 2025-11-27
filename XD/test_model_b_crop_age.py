# -*- coding: utf-8 -*-
"""
ทดสอบ Model B - ตรวจสอบว่าแต่ละพืชในแต่ละจังหวัดแนะนำวัยต่างกันหรือไม่
Test Model B to see if it recommends different crop ages for different crops and provinces
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path

# Load Model B
model_path = Path("XD/backend/models/model_b_xgboost.pkl")

print("=" * 80)
print("ทดสอบ Model B - การแนะนำวัยของพืชในแต่ละจังหวัด")
print("=" * 80)

try:
    with open(model_path, 'rb') as f:
        model_b_dict = pickle.load(f)
    
    # Extract model and scaler from dictionary
    model_b = model_b_dict['model']
    scaler_b = model_b_dict['scaler']
    
    print(f"✅ โหลด Model B สำเร็จ: {model_path}")
    print(f"   ประเภท Model: {type(model_b).__name__}")
    print(f"   Version: {model_b_dict.get('version', 'N/A')}")
    print(f"   Trained at: {model_b_dict.get('trained_at', 'N/A')}")
    
    if hasattr(model_b, 'n_features_in_'):
        print(f"   จำนวน Features: {model_b.n_features_in_}")
    
    if hasattr(scaler_b, 'feature_names_in_'):
        print(f"   Feature Names: {list(scaler_b.feature_names_in_)}")
    
except Exception as e:
    print(f"❌ ไม่สามารถโหลด Model B: {e}")
    exit(1)

print("\n" + "=" * 80)

# Load crop characteristics
crop_file = Path("XD/buildingModel.py/Dataset/crop_characteristics.csv")
crops_df = pd.read_csv(crop_file, encoding='utf-8')

# เลือกพืชที่จะทดสอบ (หลากหลายประเภท)
test_crops = [
    'ข้าวโพดเลี้ยงสัตว์',
    'มะเขือเทศ',
    'พริก',
    'แตงโม',
    'กระเทียม',
    'คะน้า',
    'ถั่วเหลือง',
    'ขมิ้น'
]

# เลือกจังหวัดที่จะทดสอบ (หลากหลายภูมิภาค)
test_provinces = [
    'เชียงใหม่',  # ภาคเหนือ
    'นครราชสีมา',  # ภาคตะวันออกเฉียงเหนือ
    'สุพรรณบุรี',  # ภาคกลาง
    'สงขลา'  # ภาคใต้
]

# วัยของพืชที่จะทดสอบ (เป็นวัน)
test_ages = [0, 15, 30, 45, 60, 90, 120]

print("\n📊 ทดสอบการทำนายของ Model B")
print("-" * 80)

results = []

for crop_name in test_crops:
    # หาข้อมูลพืช
    crop_data = crops_df[crops_df['crop_type'] == crop_name]
    
    if crop_data.empty:
        print(f"⚠️  ไม่พบข้อมูลพืช: {crop_name}")
        continue
    
    crop_row = crop_data.iloc[0]
    growth_days = crop_row['growth_days']
    
    print(f"\n🌱 พืช: {crop_name} (อายุเก็บเกี่ยว: {growth_days} วัน)")
    print("-" * 80)
    
    for province in test_provinces:
        print(f"\n   📍 จังหวัด: {province}")
        
        # ทดสอบแต่ละวัย
        for age in test_ages:
            # ข้ามวัยที่เกินอายุเก็บเกี่ยว
            if age > growth_days + 30:
                continue
            
            try:
                # สร้าง features สำหรับ Model B (17 features)
                # Features: growth_days, avg_temp_prev_30d, avg_rainfall_prev_30d,
                #           total_rainfall_prev_30d, rainy_days_prev_30d, plant_month,
                #           plant_quarter, plant_day_of_year, month_sin, month_cos,
                #           day_sin, day_cos, crop_type_encoded, province_encoded,
                #           season_encoded, soil_preference_encoded, seasonal_type_encoded
                
                # สมมติค่าเริ่มต้น
                current_month = 1  # มกราคม
                plant_quarter = 1
                plant_day_of_year = 15
                
                # คำนวณ sin/cos สำหรับ cyclical features
                import math
                month_sin = math.sin(2 * math.pi * current_month / 12)
                month_cos = math.cos(2 * math.pi * current_month / 12)
                day_sin = math.sin(2 * math.pi * plant_day_of_year / 365)
                day_cos = math.cos(2 * math.pi * plant_day_of_year / 365)
                
                # Encode categorical features (ใช้ค่าเริ่มต้น)
                # ในการใช้งานจริงควรใช้ LabelEncoder ที่ train ไว้
                crop_type_encoded = hash(crop_name) % 100
                province_encoded = hash(province) % 77  # มี 77 จังหวัด
                
                # Season encoding
                season_map = {'winter': 0, 'summer': 1, 'rainy': 2}
                if current_month in [11, 12, 1, 2]:
                    season = 'winter'
                elif current_month in [3, 4, 5]:
                    season = 'summer'
                else:
                    season = 'rainy'
                season_encoded = season_map[season]
                
                # Soil preference encoding
                soil_map = {
                    'ดินร่วน': 0, 'ดินร่วนปนทราย': 1, 'ดินร่วนปนเหนียว': 2,
                    'ดินทราย': 3, 'ดินเหนียว': 4
                }
                soil_preference_encoded = soil_map.get(crop_row['soil_preference'], 0)
                
                # Seasonal type encoding
                seasonal_map = {
                    'ได้ทุกฤดู': 0, 'ได้ตลอดปี': 0, 'หนาว': 1, 'ร้อน': 2,
                    'ฝน': 3, 'ร้อน-ฝน': 4
                }
                seasonal_type_encoded = seasonal_map.get(crop_row['seasonal_type'], 0)
                
                # สร้าง feature vector (17 features)
                features = np.array([[
                    float(growth_days),  # growth_days
                    float(28.0),  # avg_temp_prev_30d (default)
                    float(5.0),  # avg_rainfall_prev_30d (default)
                    float(150.0),  # total_rainfall_prev_30d (default)
                    float(10),  # rainy_days_prev_30d (default)
                    float(current_month),  # plant_month
                    float(plant_quarter),  # plant_quarter
                    float(plant_day_of_year),  # plant_day_of_year
                    float(month_sin),  # month_sin
                    float(month_cos),  # month_cos
                    float(day_sin),  # day_sin
                    float(day_cos),  # day_cos
                    float(crop_type_encoded),  # crop_type_encoded
                    float(province_encoded),  # province_encoded
                    float(season_encoded),  # season_encoded
                    float(soil_preference_encoded),  # soil_preference_encoded
                    float(seasonal_type_encoded),  # seasonal_type_encoded
                ]], dtype=np.float64)
                
                # Scale features
                features_scaled = scaler_b.transform(features)
                
                # ทำนาย (Model B ทำนาย class ไม่ใช่ค่าต่อเนื่อง)
                prediction = model_b.predict(features_scaled)[0]
                
                # ถ้า Model B เป็น classifier อาจต้องใช้ predict_proba
                if hasattr(model_b, 'predict_proba'):
                    proba = model_b.predict_proba(features_scaled)[0]
                    # ใช้ probability ของ class ที่ทำนาย
                    prediction_value = proba[int(prediction)]
                else:
                    prediction_value = prediction
                
                # เก็บผลลัพธ์
                results.append({
                    'crop': crop_name,
                    'province': province,
                    'age_days': age,
                    'growth_days': growth_days,
                    'age_percent': round(age / growth_days * 100, 1) if growth_days > 0 else 0,
                    'prediction': int(prediction),
                    'prediction_value': round(prediction_value, 4)
                })
                
                # แสดงผล
                age_percent = age / growth_days * 100 if growth_days > 0 else 0
                print(f"      วัย {age:3d} วัน ({age_percent:5.1f}%) → Class: {int(prediction)}, Prob: {prediction_value:.4f}")
                
            except Exception as e:
                print(f"      ❌ Error at age {age}: {e}")
                continue

print("\n" + "=" * 80)
print("📈 สรุปผลการทดสอบ")
print("=" * 80)

# แปลงเป็น DataFrame เพื่อวิเคราะห์
results_df = pd.DataFrame(results)

if not results_df.empty:
    print("\n1️⃣  การเปลี่ยนแปลงตามวัยของพืช (ในจังหวัดเดียวกัน)")
    print("-" * 80)
    
    for crop_name in test_crops:
        crop_results = results_df[results_df['crop'] == crop_name]
        if crop_results.empty:
            continue
        
        print(f"\n   🌱 {crop_name}:")
        
        for province in test_provinces:
            prov_results = crop_results[crop_results['province'] == province]
            if prov_results.empty:
                continue
            
            predictions = prov_results['prediction'].values
            pred_values = prov_results['prediction_value'].values
            if len(predictions) > 1:
                # นับจำนวน class ที่แตกต่างกัน
                unique_classes = len(set(predictions))
                variation = predictions.max() - predictions.min()
                print(f"      {province:15s}: Class ต่ำสุด={int(predictions.min())}, "
                      f"Class สูงสุด={int(predictions.max())}, "
                      f"จำนวน Class={unique_classes}, "
                      f"Prob Range={pred_values.min():.4f}-{pred_values.max():.4f}")
    
    print("\n2️⃣  การเปลี่ยนแปลงตามจังหวัด (วัยเดียวกัน)")
    print("-" * 80)
    
    for crop_name in test_crops:
        crop_results = results_df[results_df['crop'] == crop_name]
        if crop_results.empty:
            continue
        
        print(f"\n   🌱 {crop_name}:")
        
        # เลือกวัยกลางๆ (30 วัน)
        age_results = crop_results[crop_results['age_days'] == 30]
        if not age_results.empty:
            print(f"      วัย 30 วัน:")
            for _, row in age_results.iterrows():
                print(f"         {row['province']:15s}: Class={int(row['prediction'])}, Prob={row['prediction_value']:.4f}")
            
            predictions = age_results['prediction'].values
            if len(predictions) > 1:
                unique_classes = len(set(predictions))
                variation = predictions.max() - predictions.min()
                print(f"      → จำนวน Class ที่แตกต่าง: {unique_classes}, ความแตกต่าง: {variation}")
    
    print("\n3️⃣  สรุปภาพรวม")
    print("-" * 80)
    
    # ตรวจสอบว่า Model B แนะนำวัยต่างกันหรือไม่
    age_sensitive = False
    province_sensitive = False
    
    for crop_name in test_crops:
        crop_results = results_df[results_df['crop'] == crop_name]
        if crop_results.empty:
            continue
        
        # ตรวจสอบความแตกต่างตามวัย
        for province in test_provinces:
            prov_results = crop_results[crop_results['province'] == province]
            if len(prov_results) > 1:
                predictions = prov_results['prediction'].values
                unique_classes = len(set(predictions))
                if unique_classes > 1:  # ถ้ามี class ที่แตกต่างกัน
                    age_sensitive = True
        
        # ตรวจสอบความแตกต่างตามจังหวัด
        for age in test_ages:
            age_results = crop_results[crop_results['age_days'] == age]
            if len(age_results) > 1:
                predictions = age_results['prediction'].values
                unique_classes = len(set(predictions))
                if unique_classes > 1:  # ถ้ามี class ที่แตกต่างกัน
                    province_sensitive = True
    
    print(f"\n   ✓ Model B {'มี' if age_sensitive else 'ไม่มี'}ความไวต่อวัยของพืช")
    print(f"   ✓ Model B {'มี' if province_sensitive else 'ไม่มี'}ความไวต่อจังหวัด")
    
    if age_sensitive:
        print("\n   → Model B แนะนำ Class ที่แตกต่างกันตามวัยของพืช")
        print("      (หมายความว่า Model B สามารถแยกแยะวัยของพืชได้)")
    else:
        print("\n   → Model B แนะนำ Class เดียวกันไม่ว่าพืชจะอายุเท่าไหร่")
        print("      (หมายความว่า Model B ไม่ได้ใช้วัยของพืชในการตัดสินใจ)")
    
    if province_sensitive:
        print("   → Model B แนะนำ Class ที่แตกต่างกันตามจังหวัด")
        print("      (หมายความว่า Model B คำนึงถึงพื้นที่ปลูก)")
    else:
        print("   → Model B แนะนำ Class เดียวกันทุกจังหวัด")
        print("      (หมายความว่า Model B ไม่ได้คำนึงถึงพื้นที่ปลูก)")
    
    # บันทึกผลลัพธ์
    output_file = Path("XD/test_model_b_results.csv")
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n   💾 บันทึกผลลัพธ์ไปที่: {output_file}")

else:
    print("\n❌ ไม่มีผลลัพธ์ที่จะวิเคราะห์")

print("\n" + "=" * 80)
print("✅ ทดสอบเสร็จสิ้น")
print("=" * 80)

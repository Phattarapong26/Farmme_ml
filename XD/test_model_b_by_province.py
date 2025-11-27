# -*- coding: utf-8 -*-
"""
ทดสอบ Model B - เปรียบเทียบความเหมาะสมในแต่ละจังหวัด
ดูว่าพืชเดียวกันในจังหวัดต่างกัน Model แนะนำอย่างไร
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import math

print("=" * 80)
print("🗺️  ทดสอบ Model B - เปรียบเทียบแต่ละจังหวัด")
print("=" * 80)

# Load Model B
model_path = Path("XD/backend/models/model_b_xgboost.pkl")

with open(model_path, 'rb') as f:
    model_b_dict = pickle.load(f)

model_b = model_b_dict['model']
scaler_b = model_b_dict['scaler']

print(f"\n✅ โหลด Model B สำเร็จ")

# Load crop characteristics
crop_file = Path("XD/buildingModel.py/Dataset/crop_characteristics.csv")
crops_df = pd.read_csv(crop_file, encoding='utf-8')

# Load weather data เพื่อดูค่าเฉลี่ยของแต่ละจังหวัด
weather_file = Path("XD/buildingModel.py/Dataset/weather.csv")
weather_df = pd.read_csv(weather_file, parse_dates=['date'])

print("\n" + "=" * 80)
print("🌱 ทดสอบพืช: พริก, มะเขือเทศ, ข้าวโพด")
print("📍 จังหวัด: 10 จังหวัดทั่วประเทศ")
print("=" * 80)

# เลือกพืชทดสอบ
test_crops = ['พริก', 'มะเขือเทศ', 'ข้าวโพดเลี้ยงสัตว์']

# เลือกจังหวัดทดสอบ (ครอบคลุมทุกภูมิภาค)
test_provinces = [
    'เชียงใหม่',      # ภาคเหนือ
    'เชียงราย',       # ภาคเหนือ
    'นครราชสีมา',    # ภาคตะวันออกเฉียงเหนือ
    'อุบลราชธานี',    # ภาคตะวันออกเฉียงเหนือ
    'กรุงเทพมหานคร',  # ภาคกลาง
    'สุพรรณบุรี',     # ภาคกลาง
    'ชลบุรี',         # ภาคตะวันออก
    'ระยอง',          # ภาคตะวันออก
    'สงขลา',          # ภาคใต้
    'ภูเก็ต',         # ภาคใต้
]

# คำนวณค่าเฉลี่ยอากาศของแต่ละจังหวัด
print("\n📊 ค่าเฉลี่ยอากาศของแต่ละจังหวัด:")
print("-" * 80)

province_stats = {}
for province in test_provinces:
    province_weather = weather_df[weather_df['province'] == province]
    if len(province_weather) > 0:
        stats = {
            'avg_temp': province_weather['temperature_celsius'].mean(),
            'avg_rainfall': province_weather['rainfall_mm'].mean(),
            'total_rainfall': province_weather['rainfall_mm'].sum() / 2,  # 2 ปี
        }
        province_stats[province] = stats
        print(f"{province:20s}: อุณหภูมิ {stats['avg_temp']:.1f}°C, "
              f"ฝน {stats['avg_rainfall']:.1f} mm/วัน")

# ฟังก์ชันสร้าง features
def create_features_for_province(crop_data, province, province_stats):
    """สร้าง features สำหรับจังหวัดและพืชที่กำหนด"""
    
    # ใช้ค่าเฉลี่ยของจังหวัด
    if province in province_stats:
        avg_temp = province_stats[province]['avg_temp']
        avg_rainfall = province_stats[province]['avg_rainfall']
    else:
        avg_temp = 28.0
        avg_rainfall = 100.0
    
    # ประมาณการฝนรวมและวันที่ฝนตก
    total_rainfall = avg_rainfall * 30
    rainy_days = min(int(avg_rainfall / 10), 30)
    
    # Temporal features (ใช้เดือนมกราคม)
    current_month = 1
    plant_quarter = 1
    plant_day_of_year = 15
    
    # Cyclic encoding
    month_sin = math.sin(2 * math.pi * current_month / 12)
    month_cos = math.cos(2 * math.pi * current_month / 12)
    day_sin = math.sin(2 * math.pi * plant_day_of_year / 365)
    day_cos = math.cos(2 * math.pi * plant_day_of_year / 365)
    
    # Encode categorical
    crop_type_encoded = hash(crop_data['crop_type']) % 100
    province_encoded = hash(province) % 77
    
    # Season (มกราคม = ฤดูหนาว)
    season = 'winter'
    season_map = {'winter': 0, 'summer': 1, 'rainy': 2}
    season_encoded = season_map[season]
    
    # Soil and seasonal type
    soil_map = {
        'ดินร่วน': 0, 'ดินร่วนปนทราย': 1, 'ดินร่วนปนเหนียว': 2,
        'ดินทราย': 3, 'ดินเหนียว': 4
    }
    soil_preference_encoded = soil_map.get(crop_data['soil_preference'], 0)
    
    seasonal_map = {
        'ได้ทุกฤดู': 0, 'ได้ตลอดปี': 0, 'หนาว': 1, 'ร้อน': 2,
        'ฝน': 3, 'ร้อน-ฝน': 4
    }
    seasonal_type_encoded = seasonal_map.get(crop_data['seasonal_type'], 0)
    
    # สร้าง feature vector (17 features)
    features = np.array([[
        float(crop_data['growth_days']),
        float(avg_temp),
        float(avg_rainfall),
        float(total_rainfall),
        float(rainy_days),
        float(current_month),
        float(plant_quarter),
        float(plant_day_of_year),
        float(month_sin),
        float(month_cos),
        float(day_sin),
        float(day_cos),
        float(crop_type_encoded),
        float(province_encoded),
        float(season_encoded),
        float(soil_preference_encoded),
        float(seasonal_type_encoded),
    ]], dtype=np.float64)
    
    return features, avg_temp, avg_rainfall

# ทดสอบแต่ละพืช
results = []

for crop_name in test_crops:
    crop_data = crops_df[crops_df['crop_type'] == crop_name]
    
    if crop_data.empty:
        print(f"\n⚠️  ไม่พบข้อมูลพืช: {crop_name}")
        continue
    
    crop_row = crop_data.iloc[0]
    
    print(f"\n" + "=" * 80)
    print(f"🌱 พืช: {crop_name}")
    print(f"   Growth days: {crop_row['growth_days']}")
    print(f"   Seasonal type: {crop_row['seasonal_type']}")
    print(f"   Water requirement: {crop_row['water_requirement']}")
    print("=" * 80)
    
    crop_results = []
    
    for province in test_provinces:
        # สร้าง features
        features, avg_temp, avg_rainfall = create_features_for_province(
            crop_row, province, province_stats
        )
        
        # ทำนาย
        features_scaled = scaler_b.transform(features)
        prediction = model_b.predict(features_scaled)[0]
        proba = model_b.predict_proba(features_scaled)[0]
        
        # แปลผล
        if prediction == 1:
            result = "✅ เหมาะปลูก"
            confidence = proba[1]
            emoji = "✅"
        else:
            result = "❌ ไม่เหมาะปลูก"
            confidence = proba[0]
            emoji = "❌"
        
        print(f"{emoji} {province:20s}: {result:20s} "
              f"(ความมั่นใจ: {confidence:5.1%}) "
              f"[อุณหภูมิ: {avg_temp:5.1f}°C, ฝน: {avg_rainfall:5.1f} mm]")
        
        crop_results.append({
            'crop': crop_name,
            'province': province,
            'prediction': int(prediction),
            'confidence': confidence,
            'avg_temp': avg_temp,
            'avg_rainfall': avg_rainfall,
            'result': result
        })
    
    results.extend(crop_results)

# สรุปผล
print("\n" + "=" * 80)
print("📊 สรุปผลการทดสอบ")
print("=" * 80)

results_df = pd.DataFrame(results)

for crop_name in test_crops:
    crop_results = results_df[results_df['crop'] == crop_name]
    
    if crop_results.empty:
        continue
    
    print(f"\n🌱 {crop_name}:")
    print("-" * 80)
    
    # นับจำนวนจังหวัดที่เหมาะและไม่เหมาะ
    good_provinces = crop_results[crop_results['prediction'] == 1]
    bad_provinces = crop_results[crop_results['prediction'] == 0]
    
    print(f"   ✅ เหมาะปลูก: {len(good_provinces)}/{len(crop_results)} จังหวัด")
    if len(good_provinces) > 0:
        for _, row in good_provinces.iterrows():
            print(f"      - {row['province']:20s} (ความมั่นใจ: {row['confidence']:.1%})")
    
    print(f"\n   ❌ ไม่เหมาะปลูก: {len(bad_provinces)}/{len(crop_results)} จังหวัด")
    if len(bad_provinces) > 0:
        for _, row in bad_provinces.iterrows():
            print(f"      - {row['province']:20s} (ความมั่นใจ: {row['confidence']:.1%})")
    
    # วิเคราะห์ความแตกต่าง
    if len(good_provinces) > 0 and len(bad_provinces) > 0:
        print(f"\n   📈 วิเคราะห์:")
        print(f"      อุณหภูมิเฉลี่ย (เหมาะ): {good_provinces['avg_temp'].mean():.1f}°C")
        print(f"      อุณหภูมิเฉลี่ย (ไม่เหมาะ): {bad_provinces['avg_temp'].mean():.1f}°C")
        print(f"      ฝนเฉลี่ย (เหมาะ): {good_provinces['avg_rainfall'].mean():.1f} mm")
        print(f"      ฝนเฉลี่ย (ไม่เหมาะ): {bad_provinces['avg_rainfall'].mean():.1f} mm")

# วิเคราะห์ภาพรวม
print("\n" + "=" * 80)
print("🔍 วิเคราะห์ภาพรวม")
print("=" * 80)

# ตรวจสอบว่า Model มีความไวต่อจังหวัดหรือไม่
print("\n1️⃣  ความไวต่อจังหวัด:")
print("-" * 80)

for crop_name in test_crops:
    crop_results = results_df[results_df['crop'] == crop_name]
    if crop_results.empty:
        continue
    
    unique_predictions = crop_results['prediction'].nunique()
    good_count = (crop_results['prediction'] == 1).sum()
    bad_count = (crop_results['prediction'] == 0).sum()
    
    print(f"\n   {crop_name}:")
    print(f"      จำนวน Class ที่แตกต่าง: {unique_predictions}")
    print(f"      เหมาะปลูก: {good_count} จังหวัด")
    print(f"      ไม่เหมาะปลูก: {bad_count} จังหวัด")
    
    if unique_predictions > 1:
        print(f"      ✅ Model สามารถแยกแยะจังหวัดได้")
    else:
        print(f"      ❌ Model แนะนำเหมือนกันทุกจังหวัด")

# ตรวจสอบปัจจัยที่ส่งผล
print("\n2️⃣  ปัจจัยที่ส่งผลต่อการทำนาย:")
print("-" * 80)

# เปรียบเทียบจังหวัดที่เหมาะ vs ไม่เหมาะ
good_all = results_df[results_df['prediction'] == 1]
bad_all = results_df[results_df['prediction'] == 0]

if len(good_all) > 0 and len(bad_all) > 0:
    print(f"\n   จังหวัดที่เหมาะปลูก:")
    print(f"      อุณหภูมิเฉลี่ย: {good_all['avg_temp'].mean():.1f}°C "
          f"(ช่วง: {good_all['avg_temp'].min():.1f}-{good_all['avg_temp'].max():.1f}°C)")
    print(f"      ฝนเฉลี่ย: {good_all['avg_rainfall'].mean():.1f} mm "
          f"(ช่วง: {good_all['avg_rainfall'].min():.1f}-{good_all['avg_rainfall'].max():.1f} mm)")
    
    print(f"\n   จังหวัดที่ไม่เหมาะปลูก:")
    print(f"      อุณหภูมิเฉลี่ย: {bad_all['avg_temp'].mean():.1f}°C "
          f"(ช่วง: {bad_all['avg_temp'].min():.1f}-{bad_all['avg_temp'].max():.1f}°C)")
    print(f"      ฝนเฉลี่ย: {bad_all['avg_rainfall'].mean():.1f} mm "
          f"(ช่วง: {bad_all['avg_rainfall'].min():.1f}-{bad_all['avg_rainfall'].max():.1f} mm)")
    
    print(f"\n   💡 สรุป:")
    temp_diff = abs(good_all['avg_temp'].mean() - bad_all['avg_temp'].mean())
    rain_diff = abs(good_all['avg_rainfall'].mean() - bad_all['avg_rainfall'].mean())
    
    if temp_diff > 5:
        print(f"      ✅ อุณหภูมิมีผลต่อการทำนาย (ต่างกัน {temp_diff:.1f}°C)")
    else:
        print(f"      ⚠️  อุณหภูมิมีผลน้อย (ต่างกันแค่ {temp_diff:.1f}°C)")
    
    if rain_diff > 10:
        print(f"      ✅ ฝนมีผลต่อการทำนาย (ต่างกัน {rain_diff:.1f} mm)")
    else:
        print(f"      ⚠️  ฝนมีผลน้อย (ต่างกันแค่ {rain_diff:.1f} mm)")

# บันทึกผลลัพธ์
output_file = Path("XD/model_b_province_comparison.csv")
results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n💾 บันทึกผลลัพธ์ไปที่: {output_file}")

print("\n" + "=" * 80)
print("✅ ทดสอบเสร็จสิ้น")
print("=" * 80)

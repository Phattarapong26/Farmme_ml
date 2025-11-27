# -*- coding: utf-8 -*-
"""
ทดสอบวัตถุประสงค์ของ Model B
Model B = Planting Window Classifier (ตรวจสอบว่าช่วงเวลานั้นเหมาะปลูกหรือไม่)
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import math

print("=" * 80)
print("🎯 ทดสอบวัตถุประสงค์ของ Model B")
print("=" * 80)

# Load Model B
model_path = Path("XD/backend/models/model_b_xgboost.pkl")

with open(model_path, 'rb') as f:
    model_b_dict = pickle.load(f)

model_b = model_b_dict['model']
scaler_b = model_b_dict['scaler']

print(f"\n✅ โหลด Model B สำเร็จ")
print(f"   Version: {model_b_dict.get('version', 'N/A')}")
print(f"   Trained at: {model_b_dict.get('trained_at', 'N/A')}")

# ตรวจสอบ classes
if hasattr(model_b, 'classes_'):
    print(f"\n📊 Classes ที่ Model ทำนาย:")
    print(f"   {model_b.classes_}")
    print(f"   → Class 0 = ไม่เหมาะปลูก (Bad Window)")
    print(f"   → Class 1 = เหมาะปลูก (Good Window)")

print("\n" + "=" * 80)
print("🧪 ทดสอบการทำนาย: ช่วงเวลาที่เหมาะปลูก vs ไม่เหมาะปลูก")
print("=" * 80)

# Load crop characteristics
crop_file = Path("XD/buildingModel.py/Dataset/crop_characteristics.csv")
crops_df = pd.read_csv(crop_file, encoding='utf-8')

# เลือกพืชทดสอบ
test_crop = 'พริก'
crop_data = crops_df[crops_df['crop_type'] == test_crop].iloc[0]

print(f"\n🌱 พืชทดสอบ: {test_crop}")
print(f"   Growth days: {crop_data['growth_days']}")
print(f"   Seasonal type: {crop_data['seasonal_type']}")

# ทดสอบหลายสถานการณ์
scenarios = [
    {
        'name': '🌞 ฤดูร้อน - อากาศร้อนมาก ฝนน้อย',
        'avg_temp': 38.0,
        'avg_rainfall': 5.0,
        'total_rainfall': 150.0,
        'rainy_days': 3,
        'season': 'summer',
        'expected': 'ไม่เหมาะ (ร้อนเกินไป)'
    },
    {
        'name': '🌧️ ฤดูฝน - ฝนตกหนักมาก',
        'avg_temp': 28.0,
        'avg_rainfall': 250.0,
        'total_rainfall': 7500.0,
        'rainy_days': 28,
        'season': 'rainy',
        'expected': 'ไม่เหมาะ (ฝนมากเกินไป)'
    },
    {
        'name': '❄️ ฤดูหนาว - อากาศเย็นมาก',
        'avg_temp': 15.0,
        'avg_rainfall': 2.0,
        'total_rainfall': 60.0,
        'rainy_days': 1,
        'season': 'winter',
        'expected': 'ไม่เหมาะ (เย็นเกินไป)'
    },
    {
        'name': '✅ สภาพอากาศเหมาะสม - อุณหภูมิดี ฝนพอดี',
        'avg_temp': 28.0,
        'avg_rainfall': 50.0,
        'total_rainfall': 1500.0,
        'rainy_days': 10,
        'season': 'rainy',
        'expected': 'เหมาะ'
    },
    {
        'name': '✅ ฤดูหนาว - อากาศเย็นสบาย ฝนน้อย',
        'avg_temp': 25.0,
        'avg_rainfall': 20.0,
        'total_rainfall': 600.0,
        'rainy_days': 5,
        'season': 'winter',
        'expected': 'เหมาะ'
    },
    {
        'name': '⚠️ แห้งแล้ง - ไม่มีฝนเลย',
        'avg_temp': 32.0,
        'avg_rainfall': 0.0,
        'total_rainfall': 0.0,
        'rainy_days': 0,
        'season': 'summer',
        'expected': 'ไม่เหมาะ (แห้งแล้ง)'
    },
]

results = []

for scenario in scenarios:
    print(f"\n{scenario['name']}")
    print(f"   อุณหภูมิเฉลี่ย: {scenario['avg_temp']}°C")
    print(f"   ฝนเฉลี่ย: {scenario['avg_rainfall']} mm/วัน")
    print(f"   ฝนรวม: {scenario['total_rainfall']} mm")
    print(f"   วันที่ฝนตก: {scenario['rainy_days']} วัน")
    print(f"   ฤดูกาล: {scenario['season']}")
    
    # สร้าง features
    current_month = 1
    plant_quarter = 1
    plant_day_of_year = 15
    
    month_sin = math.sin(2 * math.pi * current_month / 12)
    month_cos = math.cos(2 * math.pi * current_month / 12)
    day_sin = math.sin(2 * math.pi * plant_day_of_year / 365)
    day_cos = math.cos(2 * math.pi * plant_day_of_year / 365)
    
    crop_type_encoded = hash(test_crop) % 100
    province_encoded = hash('เชียงใหม่') % 77
    
    season_map = {'winter': 0, 'summer': 1, 'rainy': 2}
    season_encoded = season_map[scenario['season']]
    
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
        float(scenario['avg_temp']),
        float(scenario['avg_rainfall']),
        float(scenario['total_rainfall']),
        float(scenario['rainy_days']),
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
    
    # Scale และทำนาย
    features_scaled = scaler_b.transform(features)
    prediction = model_b.predict(features_scaled)[0]
    proba = model_b.predict_proba(features_scaled)[0]
    
    # แปลผล
    if prediction == 1:
        result = "✅ เหมาะปลูก (Good Window)"
        confidence = proba[1]
    else:
        result = "❌ ไม่เหมาะปลูก (Bad Window)"
        confidence = proba[0]
    
    print(f"\n   🎯 ผลทำนาย: {result}")
    print(f"   📊 ความมั่นใจ: {confidence:.2%}")
    print(f"   📝 คาดหวัง: {scenario['expected']}")
    
    # เก็บผลลัพธ์
    results.append({
        'scenario': scenario['name'],
        'prediction': int(prediction),
        'confidence': confidence,
        'expected': scenario['expected']
    })

# สรุปผล
print("\n" + "=" * 80)
print("📊 สรุปผลการทดสอบ")
print("=" * 80)

results_df = pd.DataFrame(results)

print("\n1️⃣  การทำนายของ Model B:")
print("-" * 80)
for _, row in results_df.iterrows():
    status = "✅" if row['prediction'] == 1 else "❌"
    print(f"{status} {row['scenario']}")
    print(f"   ทำนาย: {'เหมาะปลูก' if row['prediction'] == 1 else 'ไม่เหมาะปลูก'} "
          f"(ความมั่นใจ: {row['confidence']:.2%})")
    print(f"   คาดหวัง: {row['expected']}")
    print()

print("\n2️⃣  วัตถุประสงค์ของ Model B:")
print("-" * 80)
print("""
Model B = Planting Window Classifier (ตัวจำแนกช่วงเวลาที่เหมาะปลูก)

🎯 วัตถุประสงค์:
   ทำนายว่าช่วงเวลาใดเหมาะสมสำหรับการปลูกพืชหรือไม่
   โดยพิจารณาจาก:
   - สภาพอากาศ (อุณหภูมิ, ฝน)
   - ฤดูกาล
   - ลักษณะพืช
   - พื้นที่ปลูก

📊 Output:
   - Class 0 = ไม่เหมาะปลูก (Bad Window)
   - Class 1 = เหมาะปลูก (Good Window)
   - Confidence Score (ความมั่นใจ)

💡 การใช้งาน:
   - ตรวจสอบว่าวันนี้เหมาะปลูกหรือไม่
   - ดูปฏิทินการปลูกตลอดทั้งปี
   - เปรียบเทียบช่วงเวลาที่เหมาะสม
   - แนะนำช่วงเวลาที่ดีที่สุด

❌ ไม่ใช่:
   - ไม่ได้ทำนายวัยของพืช (crop age)
   - ไม่ได้ทำนายผลผลิต (yield)
   - ไม่ได้ทำนาย ROI
""")

print("\n3️⃣  ข้อสังเกต:")
print("-" * 80)

# นับจำนวน class ที่ทำนาย
class_counts = results_df['prediction'].value_counts()
print(f"\nการกระจายของการทำนาย:")
print(f"   Class 0 (ไม่เหมาะ): {class_counts.get(0, 0)} ครั้ง")
print(f"   Class 1 (เหมาะ): {class_counts.get(1, 0)} ครั้ง")

if class_counts.get(1, 0) == len(results_df):
    print(f"\n⚠️  Model ทำนาย Class 1 (เหมาะปลูก) ทุกกรณี!")
    print(f"   → Model อาจมีปัญหา:")
    print(f"      - Data imbalance (ข้อมูลไม่สมดุล)")
    print(f"      - Overfitting")
    print(f"      - Features ไม่เพียงพอ")
elif class_counts.get(0, 0) == len(results_df):
    print(f"\n⚠️  Model ทำนาย Class 0 (ไม่เหมาะปลูก) ทุกกรณี!")
    print(f"   → Model อาจมีปัญหาเช่นกัน")
else:
    print(f"\n✅ Model สามารถแยกแยะได้")
    print(f"   → Model ทำงานตามที่ออกแบบไว้")

print("\n" + "=" * 80)
print("✅ ทดสอบเสร็จสิ้น")
print("=" * 80)

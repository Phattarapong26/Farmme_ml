# -*- coding: utf-8 -*-
"""
ทดสอบ Model B - การทำนายรายสัปดาห์ในอนาคต
และข้อจำกัดเรื่องข้อมูลพยากรณ์อากาศ
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import math

print("=" * 80)
print("📅 Model B - การทำนายรายสัปดาห์ในอนาคต")
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

# Load weather data
weather_file = Path("XD/buildingModel.py/Dataset/weather.csv")
weather_df = pd.read_csv(weather_file, parse_dates=['date'])

print(f"\n📊 ข้อมูลที่มี:")
print(f"   Weather data: {weather_df['date'].min()} ถึง {weather_df['date'].max()}")
print(f"   จำนวนวัน: {(weather_df['date'].max() - weather_df['date'].min()).days} วัน")

# ตั้งค่าการทดสอบ
test_crop = 'พริก'
test_province = 'เชียงใหม่'
crop_data = crops_df[crops_df['crop_type'] == test_crop].iloc[0]

print(f"\n🌱 พืชทดสอบ: {test_crop}")
print(f"📍 จังหวัด: {test_province}")

print("\n" + "=" * 80)
print("🔍 ข้อจำกัดของ Model B")
print("=" * 80)

print("""
Model B ต้องการข้อมูลอากาศ 30 วันก่อนวันปลูก:
   - อุณหภูมิเฉลี่ย 30 วัน (avg_temp_prev_30d)
   - ฝนเฉลี่ย 30 วัน (avg_rainfall_prev_30d)
   - ฝนรวม 30 วัน (total_rainfall_prev_30d)
   - จำนวนวันที่ฝนตก (rainy_days_prev_30d)

⚠️ ปัญหา:
   1. ไม่มีข้อมูลพยากรณ์อากาศในอนาคต
   2. ข้อมูลอากาศที่มีเป็นข้อมูลในอดีตเท่านั้น
   3. การพยากรณ์อากาศแม่นยำได้แค่ 7-14 วัน
""")

print("\n" + "=" * 80)
print("💡 วิธีแก้ปัญหา: ใช้ข้อมูลทางสถิติ")
print("=" * 80)

print("""
แทนที่จะใช้ข้อมูลพยากรณ์อากาศ เราสามารถใช้:

1️⃣  ข้อมูลสถิติย้อนหลัง (Historical Average)
   - คำนวณค่าเฉลี่ยของแต่ละเดือนจากข้อมูลหลายปี
   - เช่น: เดือนมกราคมในเชียงใหม่มีอุณหภูมิเฉลี่ย 25°C
   
2️⃣  ข้อมูลตามฤดูกาล (Seasonal Pattern)
   - ฤดูหนาว: อุณหภูมิต่ำ, ฝนน้อย
   - ฤดูร้อน: อุณหภูมิสูง, ฝนน้อย
   - ฤดูฝน: อุณหภูมิปานกลาง, ฝนมาก

3️⃣  ข้อมูลพยากรณ์อากาศระยะสั้น (7-14 วัน)
   - ใช้ API เช่น OpenWeatherMap, WeatherAPI
   - แม่นยำสำหรับ 1-2 สัปดาห์แรก
   - หลังจากนั้นใช้ข้อมูลสถิติ
""")

print("\n" + "=" * 80)
print("🧪 ทดสอบ: ทำนาย 8 สัปดาห์ข้างหน้า (ใช้ข้อมูลสถิติ)")
print("=" * 80)

# คำนวณค่าเฉลี่ยตามเดือนจากข้อมูลย้อนหลัง
print("\n📊 คำนวณค่าเฉลี่ยตามเดือน...")

weather_province = weather_df[weather_df['province'] == test_province].copy()
weather_province['month'] = weather_province['date'].dt.month

monthly_stats = weather_province.groupby('month').agg({
    'temperature_celsius': 'mean',
    'rainfall_mm': 'mean',
}).round(2)

print(f"\n   ค่าเฉลี่ยรายเดือนใน{test_province}:")
print(monthly_stats)

# ฟังก์ชันสร้าง features
def create_features_for_date(planting_date, crop_data, province, monthly_stats):
    """สร้าง features สำหรับวันที่กำหนด โดยใช้ข้อมูลสถิติ"""
    
    month = planting_date.month
    
    # ใช้ค่าเฉลี่ยของเดือนนั้นๆ
    if month in monthly_stats.index:
        avg_temp = monthly_stats.loc[month, 'temperature_celsius']
        avg_rainfall = monthly_stats.loc[month, 'rainfall_mm']
    else:
        avg_temp = 28.0
        avg_rainfall = 100.0
    
    # ประมาณการฝนรวมและวันที่ฝนตก
    total_rainfall = avg_rainfall * 30
    rainy_days = min(int(avg_rainfall / 10), 30)  # ประมาณการ
    
    # Temporal features
    plant_month = planting_date.month
    plant_quarter = (plant_month - 1) // 3 + 1
    plant_day_of_year = planting_date.timetuple().tm_yday
    
    # Cyclic encoding
    month_sin = math.sin(2 * math.pi * plant_month / 12)
    month_cos = math.cos(2 * math.pi * plant_month / 12)
    day_sin = math.sin(2 * math.pi * plant_day_of_year / 365)
    day_cos = math.cos(2 * math.pi * plant_day_of_year / 365)
    
    # Encode categorical
    crop_type_encoded = hash(test_crop) % 100
    province_encoded = hash(province) % 77
    
    # Season
    if month in [11, 12, 1, 2]:
        season = 'winter'
    elif month in [3, 4, 5]:
        season = 'summer'
    else:
        season = 'rainy'
    
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
    
    # สร้าง feature vector
    features = np.array([[
        float(crop_data['growth_days']),
        float(avg_temp),
        float(avg_rainfall),
        float(total_rainfall),
        float(rainy_days),
        float(plant_month),
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
    
    return features, avg_temp, avg_rainfall, season

# ทำนาย 8 สัปดาห์ข้างหน้า
print(f"\n📅 ทำนาย 8 สัปดาห์ข้างหน้า (เริ่มจากวันนี้):")
print("-" * 80)

today = datetime.now()
results = []

for week in range(8):
    # วันเริ่มต้นของสัปดาห์
    week_start = today + timedelta(weeks=week)
    week_end = week_start + timedelta(days=6)
    
    # ใช้วันกลางสัปดาห์สำหรับการทำนาย
    mid_week = week_start + timedelta(days=3)
    
    # สร้าง features
    features, avg_temp, avg_rainfall, season = create_features_for_date(
        mid_week, crop_data, test_province, monthly_stats
    )
    
    # ทำนาย
    features_scaled = scaler_b.transform(features)
    prediction = model_b.predict(features_scaled)[0]
    proba = model_b.predict_proba(features_scaled)[0]
    
    # แปลผล
    if prediction == 1:
        result = "✅ เหมาะปลูก"
        confidence = proba[1]
        emoji = "🌱"
    else:
        result = "❌ ไม่เหมาะปลูก"
        confidence = proba[0]
        emoji = "⚠️"
    
    print(f"\n{emoji} สัปดาห์ที่ {week + 1}: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}")
    print(f"   วันกลางสัปดาห์: {mid_week.strftime('%d/%m/%Y')} ({season})")
    print(f"   อุณหภูมิเฉลี่ย: {avg_temp:.1f}°C")
    print(f"   ฝนเฉลี่ย: {avg_rainfall:.1f} mm/วัน")
    print(f"   {result} (ความมั่นใจ: {confidence:.1%})")
    
    results.append({
        'week': week + 1,
        'start_date': week_start.strftime('%Y-%m-%d'),
        'end_date': week_end.strftime('%Y-%m-%d'),
        'mid_date': mid_week.strftime('%Y-%m-%d'),
        'season': season,
        'avg_temp': avg_temp,
        'avg_rainfall': avg_rainfall,
        'prediction': int(prediction),
        'confidence': confidence,
        'result': result
    })

# สรุปผล
print("\n" + "=" * 80)
print("📊 สรุปผลการทำนาย 8 สัปดาห์")
print("=" * 80)

results_df = pd.DataFrame(results)

good_weeks = results_df[results_df['prediction'] == 1]
bad_weeks = results_df[results_df['prediction'] == 0]

print(f"\n✅ สัปดาห์ที่เหมาะปลูก: {len(good_weeks)} สัปดาห์")
if len(good_weeks) > 0:
    for _, row in good_weeks.iterrows():
        print(f"   - สัปดาห์ที่ {row['week']}: {row['start_date']} ({row['season']})")

print(f"\n❌ สัปดาห์ที่ไม่เหมาะปลูก: {len(bad_weeks)} สัปดาห์")
if len(bad_weeks) > 0:
    for _, row in bad_weeks.iterrows():
        print(f"   - สัปดาห์ที่ {row['week']}: {row['start_date']} ({row['season']})")

# บันทึกผลลัพธ์
output_file = Path("XD/model_b_weekly_forecast.csv")
results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n💾 บันทึกผลลัพธ์ไปที่: {output_file}")

print("\n" + "=" * 80)
print("💡 คำแนะนำสำหรับการใช้งานจริง")
print("=" * 80)

print("""
1️⃣  สำหรับ 1-2 สัปดาห์แรก:
   ✅ ใช้ข้อมูลพยากรณ์อากาศจริง (Weather API)
   - OpenWeatherMap (ฟรี 7 วัน)
   - WeatherAPI (ฟรี 14 วัน)
   - ความแม่นยำสูง

2️⃣  สำหรับ 3-8 สัปดาห์:
   ⚠️ ใช้ข้อมูลสถิติย้อนหลัง
   - ค่าเฉลี่ยรายเดือน
   - แม่นยำน้อยกว่า แต่ใช้ได้สำหรับการวางแผนคร่าวๆ

3️⃣  สำหรับระยะยาว (2-3 เดือน):
   📊 ใช้ข้อมูลตามฤดูกาล
   - ดูแนวโน้มตามฤดู
   - เหมาะสำหรับการวางแผนระยะยาว

4️⃣  อัปเดตการทำนายเป็นประจำ:
   🔄 ทำนายใหม่ทุกสัปดาห์
   - เมื่อมีข้อมูลอากาศใหม่
   - ปรับแผนตามสถานการณ์จริง

⚠️ ข้อควรระวัง:
   - การทำนายระยะยาวมีความไม่แน่นอนสูง
   - ควรใช้เป็นแนวทางเท่านั้น ไม่ใช่คำตอบสุดท้าย
   - ติดตามข่าวสภาพอากาศอย่างสม่ำเสมอ
""")

print("\n" + "=" * 80)
print("✅ ทดสอบเสร็จสิ้น")
print("=" * 80)

"""
Check Model A for Data Leakage
Verify that no post-outcome features are used
"""

import sys
sys.path.insert(0, 'REMEDIATION_PRODUCTION')

from Model_A_Fixed.data_loader_clean import DataLoaderClean
from config import Config

print("\n" + "="*80)
print("MODEL A - DATA LEAKAGE CHECK".center(80))
print("="*80)

# Load data
loader = DataLoaderClean()
cultivation = loader.load_cultivation_clean()
farmers = loader.load_farmer_profiles()
crops = loader.load_crop_characteristics()
weather = loader.load_weather()
price = loader.load_price_data()

df = loader.create_training_data(cultivation, farmers, crops, weather, price)

print("\n📊 FEATURES IN TRAINING DATA:")
print("-" * 80)
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n🚫 FORBIDDEN FEATURES (Post-Outcome):")
print("-" * 80)
for feature in Config.FORBIDDEN_FEATURES_MODEL_A:
    print(f"  - {feature}")

print("\n✅ LEAKAGE CHECK:")
print("-" * 80)
leakage_found = False
for feature in Config.FORBIDDEN_FEATURES_MODEL_A:
    if feature in df.columns:
        print(f"  ❌ {feature}: FOUND IN DATA (LEAKAGE!)")
        leakage_found = True
    else:
        print(f"  ✅ {feature}: Not in data (clean)")

print("\n" + "="*80)
if leakage_found:
    print("❌ DATA LEAKAGE DETECTED!".center(80))
    print("Model A is using post-outcome features".center(80))
else:
    print("✅ NO DATA LEAKAGE".center(80))
    print("Model A uses only pre-planting features".center(80))
print("="*80)

print("\n📝 EXPLANATION:")
print("-" * 80)
print("Model A is a RECOMMENDATION system that predicts expected ROI")
print("BEFORE planting. It should only use:")
print("  ✅ Farm characteristics (size, soil, location)")
print("  ✅ Crop characteristics (growth days, water needs, investment)")
print("  ✅ Farmer profile (experience, budget)")
print("  ✅ Historical market data (prices, demand)")
print("\nIt should NOT use:")
print("  ❌ actual_yield_kg (measured AFTER harvest)")
print("  ❌ success_rate (measured AFTER harvest)")
print("  ❌ harvest_timing_adjustment (measured AFTER harvest)")
print("  ❌ yield_efficiency (measured AFTER harvest)")

print("\n🎯 CURRENT TARGET VARIABLE:")
print("-" * 80)
print(f"  Target: expected_roi_percent")
print(f"  Mean: {df['expected_roi_percent'].mean():.2f}%")
print(f"  Std: {df['expected_roi_percent'].std():.2f}%")
print(f"  Note: This is EXPECTED ROI (estimated before planting)")
print(f"        NOT actual ROI (measured after harvest)")

print("\n" + "="*80)

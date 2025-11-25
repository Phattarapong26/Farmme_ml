# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

dataset_dir = Path("buildingModel.py/Dataset")

print("=" * 80)
print("CULTIVATION DATA ANALYSIS")
print("=" * 80)
print()

# Load cultivation data
cultivation = pd.read_csv(dataset_dir / "cultivation.csv", encoding='utf-8')

print(f"Total cultivation records: {len(cultivation):,}")
print()

# Check for missing values
print("Missing values per column:")
missing = cultivation.isnull().sum()
missing_pct = (missing / len(cultivation) * 100).round(2)
for col in cultivation.columns:
    if missing[col] > 0:
        print(f"  {col:30s}: {missing[col]:>6,} ({missing_pct[col]:>6.2f}%)")

print()

# Check data distribution
print("Data distribution:")
print(f"  Date range: {cultivation['planting_date'].min()} to {cultivation['planting_date'].max()}")
print(f"  Unique crops: {cultivation['crop_type'].nunique()}")
print(f"  Unique provinces: {cultivation['province'].nunique()}")
print(f"  Unique farmers: {cultivation['farmer_id'].nunique() if 'farmer_id' in cultivation.columns else 'N/A'}")
print()

# Check if we can expand data
print("Potential for data expansion:")
print()

# 1. Check weather data
weather = pd.read_csv(dataset_dir / "weather.csv", encoding='utf-8')
print(f"1. Weather data: {len(weather):,} records")
print(f"   Provinces: {weather['province'].nunique()}")
print(f"   Date range: {weather['date'].min()} to {weather['date'].max()}")
print()

# 2. Check price data  
price = pd.read_csv(dataset_dir / "price.csv", encoding='utf-8')
print(f"2. Price data: {len(price):,} records")
print(f"   Crops: {price['crop_type'].nunique()}")
print(f"   Provinces: {price['province'].nunique()}")
print()

# 3. Potential synthetic data
print("3. Synthetic data generation potential:")
print(f"   Current: {len(cultivation):,} records")
print(f"   Possible combinations (crops × provinces): {cultivation['crop_type'].nunique() * cultivation['province'].nunique():,}")
print()

# Check actual yield distribution
print("Actual yield statistics:")
if 'actual_yield_kg' in cultivation.columns:
    print(f"  Mean: {cultivation['actual_yield_kg'].mean():.2f} kg")
    print(f"  Std: {cultivation['actual_yield_kg'].std():.2f} kg")
    print(f"  Min: {cultivation['actual_yield_kg'].min():.2f} kg")
    print(f"  Max: {cultivation['actual_yield_kg'].max():.2f} kg")
    print(f"  Missing: {cultivation['actual_yield_kg'].isnull().sum()}")

print()
print("=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print()
print("Options to increase training data:")
print("  1. ✓ Use ALL 6,226 records (currently using all)")
print("  2. ✓ Generate synthetic data based on weather + price patterns")
print("  3. ✓ Use data augmentation (add noise, interpolation)")
print("  4. ✓ Cross-validation to maximize data usage")
print()

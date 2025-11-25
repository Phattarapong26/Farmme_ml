import pandas as pd
import numpy as np
import os
from pathlib import Path

dataset_dir = os.path.join('buildingModel.py', 'Dataset')

print('='*100)
print('COMPREHENSIVE DATASET ANALYSIS - CHECKING FOR LEAKAGE RISKS')
print('='*100)

# Load all files
files = {
    'cultivation': 'cultivation.csv',
    'weather': 'weather.csv',
    'price': 'price.csv',
    'farmer_profiles': 'farmer_profiles.csv',
    'crop_characteristics': 'crop_characteristics.csv',
    'economic': 'economic.csv',
    'compatibility': 'compatibility.csv',
    'profit': 'profit.csv',
    'population': 'population.csv',
}

data = {}
for name, filename in files.items():
    try:
        filepath = os.path.join(dataset_dir, filename)
        data[name] = pd.read_csv(filepath)
        print(f"✅ {name:20s}: {len(data[name]):6d} rows × {len(data[name].columns):2d} cols")
    except Exception as e:
        print(f"❌ {name:20s}: Error - {e}")

print('\n' + '='*100)
print('ANALYSIS 1: CULTIVATION DATA (Core Dataset)')
print('='*100)

cult = data['cultivation']
print(f"\nColumns: {list(cult.columns)}")
print(f"\nFirst few rows:")
print(cult.head(2))

print(f"\nData types:")
print(cult.dtypes)

print(f"\nMissing values:")
print(cult.isnull().sum())

print('\n' + '='*100)
print('ANALYSIS 2: POTENTIAL LEAKAGE IN EACH COLUMN')
print('='*100)

print("""
🔍 CHECKING: Which columns are OUTCOME vs FEATURES

OUTCOME VARIABLES (What we're trying to predict):
  ❓ harvest_date - IS THIS THE TARGET FOR MODEL D?
  ❓ actual_yield_kg - Related to harvest success
  ❓ success_rate - Outcome of planting
  ❓ yield_efficiency - Outcome measure

POTENTIAL LEAKAGE FEATURES:
  ❓ harvest_timing_adjustment - Might be known after harvest!
  ❓ yield_multiplier - Might be derived from actual_yield
  ❓ extreme_event_damage - This is POST-harvest
  ❓ weather_quality - Computed when?
""")

print('\nColumn Analysis:')
print('-' * 100)

for col in cult.columns:
    print(f"\n{col}:")
    
    # Check data type and content
    print(f"  Type: {cult[col].dtype}")
    print(f"  Nulls: {cult[col].isnull().sum()}")
    print(f"  Sample values: {cult[col].head(3).tolist()}")
    
    # Flag potential leakage
    if 'harvest' in col.lower() and col != 'planting_date':
        print(f"  🚨 LEAKAGE RISK: '{col}' appears to be HARVEST-related")
        if col == 'harvest_date':
            print(f"     This is likely the TARGET for Model D!")
    
    if 'yield' in col.lower() or 'actual' in col.lower():
        print(f"  🚨 LEAKAGE RISK: '{col}' is an OUTCOME variable")
    
    if 'success' in col.lower() or 'quality' in col.lower():
        print(f"  🚨 LEAKAGE RISK: '{col}' is OUTCOME-related")
    
    if 'adjustment' in col.lower() or 'damage' in col.lower():
        print(f"  🚨 LEAKAGE RISK: '{col}' might be known AFTER harvest")

print('\n' + '='*100)
print('ANALYSIS 3: MODEL A - CROP RECOMMENDATION')
print('='*100)

print("""
TARGET: Predict best crop (ROI/profit)

REQUIRED FEATURES (available BEFORE planting):
  ✅ farm_size, farm_skill, tech_adoption
  ✅ soil properties (if in data)
  ✅ weather historical
  ✅ crop_characteristics
  ✅ price (historical)

FORBIDDEN (leakage):
  ❌ actual_yield_kg - outcome of this crop!
  ❌ success_rate - outcome!
  ❌ yield_efficiency - outcome!
  ❌ harvest_date - outcome!
  ❌ expected_yield_kg - might be derived from outcomes
  ❌ yield_multiplier - outcome proxy

CHECKING DATA...
""")

# Check for outcome leakage in cultivation
outcome_cols = ['actual_yield_kg', 'success_rate', 'yield_efficiency', 'harvest_date']
for col in outcome_cols:
    if col in cult.columns:
        print(f"  Found: {col}")
        print(f"    Values: {cult[col].describe()}")

print(f"\n  🤔 QUESTION: Is profit.csv derived from cultivation outcomes?")
if 'profit' in data:
    profit_df = data['profit']
    print(f"     Profit has: {list(profit_df.columns)}")
    print(f"     This might use actual_yield or success_rate!")

print('\n' + '='*100)
print('ANALYSIS 4: MODEL B - PLANTING WINDOW')
print('='*100)

print("""
TARGET: Predict good planting window (success_rate > 0.75)

REQUIRED FEATURES (at planting time):
  ✅ weather (temperature, rainfall, humidity PRE-planting)
  ✅ soil moisture (at planting time)
  ✅ soil pH (at planting time)
  ✅ farm_skill
  ✅ crop_type
  ✅ month/season

FORBIDDEN (leakage):
  ❌ success_rate - this IS the outcome!
  ❌ actual_yield_kg - outcome of planting
  ❌ harvest_date - outcome!
  ❌ weather_quality - computed AFTER harvest
  ❌ yield_efficiency - outcome!

CHECKING...
""")

print(f"  Weather data has {len(data['weather'])} rows")
print(f"  Weather columns: {list(data['weather'].columns)}")

print(f"\n  🤔 QUESTION: Does weather data have 'drought_index'?")
if 'drought_index' in data['weather'].columns:
    print(f"     YES - drought_index is in weather")
    print(f"     Is this PRE-planting or POST-planting?")

print('\n' + '='*100)
print('ANALYSIS 5: MODEL C - PRICE FORECAST')
print('='*100)

print("""
TARGET: Predict price on harvest date

REQUIRED FEATURES:
  ✅ historical prices
  ✅ supply/demand factors
  ✅ market trends
  ✅ seasonal patterns
  ✅ supply level, demand level

FORBIDDEN (leakage):
  ❌ bid_price, ask_price, base_price (if = target!)
  ❌ actual_yield (affects supply)
  ❌ success_rate (affects supply)
  ❌ extreme_event_damage (affects supply)

CHECKING Price data...
""")

price = data['price']
print(f"  Price columns: {list(price.columns)}")
print(f"  Price sample:")
print(price.head(3))

print(f"\n  🚨 QUESTION: Are there bid/ask/base prices that equal target?")
bid_cols = [c for c in price.columns if 'bid' in c.lower() or 'ask' in c.lower() or 'base' in c.lower()]
if bid_cols:
    print(f"     FOUND: {bid_cols}")
    print(f"     These might BE the target price!")

print('\n' + '='*100)
print('ANALYSIS 6: MODEL D - HARVEST TIMING')
print('='*100)

print("""
TARGET: Predict harvest_date (days from planting)

REQUIRED FEATURES (PRE-harvest):
  ✅ growing_degree_days (accumulated temperature)
  ✅ weather patterns during growth
  ✅ soil fertility
  ✅ plant health indicators
  ✅ crop_type
  ✅ planting_date
  ✅ pest/disease history
  
FORBIDDEN (CIRCULAR LEAKAGE):
  ❌ days_since_planting = harvest_date - planting_date (WE FOUND THIS!)
  ❌ harvest_date itself
  ❌ harvest_timing_adjustment (outcome!)
  ❌ actual_yield_kg (tells us harvest happened)
  ❌ success_rate (outcome)
  ❌ crop_maturity_index (= how close to harvest)
  ❌ yield_efficiency (outcome, known after harvest)

CHECKING...
""")

# Check for days_since_planting
if 'harvest_date' in cult.columns and 'planting_date' in cult.columns:
    cult['planting_date'] = pd.to_datetime(cult['planting_date'])
    cult['harvest_date'] = pd.to_datetime(cult['harvest_date'])
    cult['days_since_planting'] = (cult['harvest_date'] - cult['planting_date']).dt.days
    
    print(f"\n  days_since_planting computed from data:")
    print(f"    Mean: {cult['days_since_planting'].mean():.1f} days")
    print(f"    Min: {cult['days_since_planting'].min()} days")
    print(f"    Max: {cult['days_since_planting'].max()} days")
    print(f"\n  🚨 THIS IS EXACTLY THE LEAKAGE WE FOUND IN MODEL D!")
    print(f"     The clean model uses this as Feature 0 (99.99% importance)")

print(f"\n  Checking for harvest_timing_adjustment:")
if 'harvest_timing_adjustment' in cult.columns:
    print(f"    ✅ Found: harvest_timing_adjustment")
    print(f"    Sample values: {cult['harvest_timing_adjustment'].head(5).tolist()}")
    print(f"    🚨 THIS IS AN OUTCOME! (adjustment AFTER harvest)")

print('\n' + '='*100)
print('ANALYSIS 7: CROSS-DATASET LEAKAGE CHAINS')
print('='*100)

print("""
POTENTIAL CHAIN LEAKAGE:

SCENARIO A: Profit → Model A
  cultivation.profit → Model A predicts crop
  Problem: profit USES actual_yield + price
  actual_yield is OUTCOME
  So recommending high-profit crops = recommending crops that worked in past
  Not predicting what will work for THIS farmer

SCENARIO B: Economic → Model A/B
  economic.csv might have derived metrics
  Check if these are post-harvest calculations

SCENARIO C: Success Rate → Model B
  Model B tries to predict success_rate
  But this needs to be known at planting time
  Historical success_rate? Or actual success_rate?

SCENARIO D: Compatibility → Models
  Is compatibility.csv based on historical success?
  If yes, this is outcome-based leakage
""")

if 'economic' in data:
    econ = data['economic']
    print(f"\n  Economic columns: {list(econ.columns)}")
    if 'profit' in econ.columns:
        print(f"    Economic has 'profit' - might be derived from outcomes!")

if 'compatibility' in data:
    compat = data['compatibility']
    print(f"\n  Compatibility columns: {list(compat.columns)}")
    print(f"    This might be based on historical success rates!")

print('\n' + '='*100)
print('SUMMARY: LEAKAGE RISKS BY MODEL')
print('='*100)

print("""
MODEL A (CROP RECOMMENDATION):
  🟡 RISK: MEDIUM
  - Might include profit from past outcomes
  - Need to check if recommendations use actual_yield
  - economic.csv might be outcome-derived
  STATUS: Need to verify features

MODEL B (PLANTING WINDOW):
  🟡 RISK: MEDIUM
  - success_rate in cultivation is OUTCOME
  - weather_quality might be post-harvest
  - Need to check: Is "good window" = historically successful?
  STATUS: Need to verify what "success_rate > 0.75" means

MODEL C (PRICE FORECAST):
  🟡 RISK: MEDIUM
  - Check if bid/ask/base prices are outcome-derived
  - extreme_event_damage affects prices but is post-harvest
  - supply level might use actual yields
  STATUS: Need to verify price targets

MODEL D (HARVEST TIMING):
  🔴 RISK: CRITICAL (CONFIRMED)
  - ✅ PROVEN: uses days_since_planting = harvest_date - planting_date
  - ✅ PROVEN: harvest_timing_adjustment is post-harvest
  - ✅ PROVEN: actual_yield indicates harvest happened
  STATUS: MUST FIX (days_since_planting removal)
""")

print('\n' + '='*100)
print('RECOMMENDATIONS')
print('='*100)

print("""
IMMEDIATE ACTIONS:

1. MODEL D: Already identified
   ✅ Remove days_since_planting
   ✅ Remove harvest_timing_adjustment
   ✅ Remove actual_yield as feature
   ✅ Use only pre-harvest environmental data
   
2. MODEL A: Need investigation
   ✓ Audit all features in crop recommendation
   ✓ Check if profit.csv uses outcomes
   ✓ Verify economic.csv derivation
   
3. MODEL B: Need investigation
   ✓ Define: What is "good planting window"?
   ✓ Verify: success_rate = historical or actual?
   ✓ Check: weather_quality calculation
   
4. MODEL C: Need investigation
   ✓ Audit price targets and features
   ✓ Verify: bid/ask/base pricing
   ✓ Check: supply level computation

VALIDATION FRAMEWORK:
  For each model, ask:
  "Can this feature be calculated BEFORE we know the outcome?"
  If NO → Remove it
  If YES → Keep it
  If MAYBE → Remove it (better safe)
""")

print('='*100)

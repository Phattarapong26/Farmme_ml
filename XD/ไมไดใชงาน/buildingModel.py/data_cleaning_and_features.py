"""
Data Cleaning + Feature Engineering for Model C
================================================
1. วิเคราะห์ปัญหาข้อมูล
2. ทำ Data Cleaning อย่างระมัดระวัง
3. เพิ่ม Features สำหรับจัดการความผันผวน
4. Train และเปรียบเทียบผล
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🔍 Data Cleaning + Feature Engineering for Model C")
print("="*80)

# ============================================================================
# STEP 1: Load and Analyze Data
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 1: Loading and Analyzing Data")
print("="*80)

df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df = df.sample(frac=0.1, random_state=42).copy()  # Use 10% for speed
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

print(f"\n✅ Loaded {len(df):,} rows (10% sample for testing)")
print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
print(f"   Crops: {df['crop_type'].nunique()}")
print(f"   Provinces: {df['province'].nunique()}")

# Analyze price distribution
print(f"\n📊 Price Distribution:")
print(f"   Min:    {df['price_per_kg'].min():.2f} baht/kg")
print(f"   Max:    {df['price_per_kg'].max():.2f} baht/kg")
print(f"   Mean:   {df['price_per_kg'].mean():.2f} baht/kg")
print(f"   Median: {df['price_per_kg'].median():.2f} baht/kg")
print(f"   Std:    {df['price_per_kg'].std():.2f} baht/kg")

# ============================================================================
# STEP 2: Data Quality Analysis
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 2: Data Quality Analysis")
print("="*80)

# Check for data errors
print("\n🔍 Checking for data errors...")

# 1. Invalid prices
invalid_prices = df[df['price_per_kg'] <= 0]
print(f"\n❌ Invalid prices (<= 0): {len(invalid_prices):,} rows ({len(invalid_prices)/len(df)*100:.2f}%)")
if len(invalid_prices) > 0:
    print(f"   Examples: {invalid_prices['price_per_kg'].head().tolist()}")

# 2. Suspiciously low prices
very_low_prices = df[(df['price_per_kg'] > 0) & (df['price_per_kg'] < 1)]
print(f"\n⚠️  Very low prices (< 1 baht): {len(very_low_prices):,} rows ({len(very_low_prices)/len(df)*100:.2f}%)")
if len(very_low_prices) > 0:
    print(f"   Examples: {very_low_prices['price_per_kg'].head().tolist()}")
    print(f"   Crops: {very_low_prices['crop_type'].unique()[:5].tolist()}")

# 3. Suspiciously high prices
very_high_prices = df[df['price_per_kg'] > 500]
print(f"\n⚠️  Very high prices (> 500 baht): {len(very_high_prices):,} rows ({len(very_high_prices)/len(df)*100:.2f}%)")
if len(very_high_prices) > 0:
    print(f"   Examples: {very_high_prices['price_per_kg'].head().tolist()}")
    print(f"   Crops: {very_high_prices['crop_type'].unique()[:5].tolist()}")

# 4. Missing values
print(f"\n📊 Missing Values:")
missing = df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False)
if len(missing) > 0:
    for col, count in missing.items():
        pct = count / len(df) * 100
        print(f"   {col}: {count:,} ({pct:.2f}%)")
else:
    print(f"   ✅ No missing values!")

# ============================================================================
# STEP 3: Data Cleaning
# ============================================================================
print("\n" + "="*80)
print("🧹 STEP 3: Data Cleaning")
print("="*80)

df_original = df.copy()
rows_before = len(df)

# Rule 1: Remove invalid prices (<= 0)
df = df[df['price_per_kg'] > 0]
removed_invalid = rows_before - len(df)
print(f"\n✅ Removed invalid prices (<= 0): {removed_invalid:,} rows")

# Rule 2: Remove suspiciously low prices (< 1 baht)
rows_before = len(df)
df = df[df['price_per_kg'] >= 1]
removed_low = rows_before - len(df)
print(f"✅ Removed very low prices (< 1 baht): {removed_low:,} rows")

# Rule 3: Investigate very high prices (> 500 baht)
# ไม่ลบทิ้ง แต่ตรวจสอบว่าเป็นพืชพิเศษหรือไม่
high_price_crops = df[df['price_per_kg'] > 500]['crop_type'].value_counts()
if len(high_price_crops) > 0:
    print(f"\n📊 Crops with prices > 500 baht:")
    for crop, count in high_price_crops.head(10).items():
        avg_price = df[df['crop_type'] == crop]['price_per_kg'].mean()
        print(f"   {crop}: {count} occurrences, avg = {avg_price:.2f} baht")
    
    # ถ้าเป็นพืชที่ราคาเฉลี่ยสูงจริงๆ → เก็บไว้
    # ถ้าเป็น outlier ผิดปกติ → ลบ
    # ใช้กฎ: ถ้าราคา > 3 * ราคาเฉลี่ยของพืชนั้น → น่าจะผิดพลาด
    
    rows_before = len(df)
    crop_avg_prices = df.groupby('crop_type')['price_per_kg'].mean()
    
    def is_extreme_outlier(row):
        crop_avg = crop_avg_prices.get(row['crop_type'], 50)
        return row['price_per_kg'] > crop_avg * 3
    
    extreme_outliers = df.apply(is_extreme_outlier, axis=1)
    df = df[~extreme_outliers]
    removed_extreme = rows_before - len(df)
    print(f"\n✅ Removed extreme outliers (> 3x crop average): {removed_extreme:,} rows")

total_removed = len(df_original) - len(df)
print(f"\n📊 Total rows removed: {total_removed:,} ({total_removed/len(df_original)*100:.2f}%)")
print(f"   Remaining: {len(df):,} rows ({len(df)/len(df_original)*100:.2f}%)")

# ============================================================================
# STEP 4: Remove Leaky Features
# ============================================================================
print("\n" + "="*80)
print("🔒 STEP 4: Removing Leaky Features")
print("="*80)

LEAKY_FEATURES = ['future_price_7d', 'price_next_day', 'bid_price', 'ask_price', 'base_price', 'spread_pct']
existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
if existing_leaky:
    df = df.drop(columns=existing_leaky)
    print(f"✅ Removed: {existing_leaky}")

# ============================================================================
# STEP 5: Create Target
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 5: Creating Target Variable")
print("="*80)

df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)
print(f"✅ Target created: price 7 days ahead")

# ============================================================================
# STEP 6: Create Basic Features
# ============================================================================
print("\n" + "="*80)
print("📈 STEP 6: Creating Basic Features")
print("="*80)

grouped = df.groupby(['province', 'crop_type'])

# Price lags
for lag in [7, 14, 21, 30]:
    df[f'price_lag_{lag}'] = grouped['price_per_kg'].shift(lag)
print(f"✅ Created price lags: 7, 14, 21, 30 days")

# Moving averages
for window in [7, 14, 30]:
    df[f'price_ma_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).mean()
    )
    df[f'price_std_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).std()
    )
print(f"✅ Created moving averages and std: 7, 14, 30 days")

# Momentum
df['price_momentum_7d'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']
df['price_momentum_30d'] = (df['price_lag_7'] - df['price_lag_30']) / df['price_lag_30']
print(f"✅ Created momentum features")

# ============================================================================
# STEP 7: Create NEW Features (Volatility & Trend)
# ============================================================================
print("\n" + "="*80)
print("🆕 STEP 7: Creating NEW Features (Volatility & Trend)")
print("="*80)

# 1. Volatility features (ช่วยจัดการความผันผวน)
print("\n📊 Creating volatility features...")

# Coefficient of Variation (CV) = std / mean
df['price_cv_7d'] = df['price_std_7'] / df['price_ma_7']
df['price_cv_14d'] = df['price_std_14'] / df['price_ma_14']
df['price_cv_30d'] = df['price_std_30'] / df['price_ma_30']
print(f"   ✅ Coefficient of Variation (CV)")

# Max/Min price ratio (faster alternative)
df['price_range_7d'] = grouped['price_per_kg'].transform(
    lambda x: x.shift(7).rolling(7, min_periods=1).max() - x.shift(7).rolling(7, min_periods=1).min()
)
df['price_range_14d'] = grouped['price_per_kg'].transform(
    lambda x: x.shift(7).rolling(14, min_periods=1).max() - x.shift(7).rolling(14, min_periods=1).min()
)
print(f"   ✅ Price range (max-min)")

# 2. Trend features (ช่วยจับทิศทาง)
print("\n📊 Creating trend features...")

# Price trend (slope)
df['price_trend_7d'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']
df['price_trend_30d'] = (df['price_lag_7'] - df['price_lag_30']) / df['price_lag_30']
print(f"   ✅ Price trend")

# Price acceleration (change in momentum)
df['price_acceleration'] = df['price_momentum_7d'] - grouped['price_momentum_7d'].shift(7)
print(f"   ✅ Price acceleration")

# 3. Relative price features (เปรียบเทียบกับค่าเฉลี่ย)
print("\n📊 Creating relative price features...")

# Distance from moving average
df['price_distance_ma_7d'] = (df['price_lag_7'] - df['price_ma_7']) / df['price_ma_7']
df['price_distance_ma_30d'] = (df['price_lag_7'] - df['price_ma_30']) / df['price_ma_30']
print(f"   ✅ Distance from moving average")

# Z-score (standardized price)
df['price_zscore_30d'] = (df['price_lag_7'] - df['price_ma_30']) / df['price_std_30']
print(f"   ✅ Z-score")

# 4. Seasonal features (ช่วยจับ pattern ตามฤดูกาล)
print("\n📊 Creating seasonal features...")

df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['dayofyear'] = df['date'].dt.dayofyear
df['weekday'] = df['date'].dt.weekday

# Cyclical encoding for month (ป้องกัน discontinuity)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
print(f"   ✅ Seasonal features with cyclical encoding")

print(f"\n✅ Total NEW features created: 15")

# ============================================================================
# STEP 8: Select Features
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 8: Selecting Features")
print("="*80)

# Basic features
basic_features = [
    'price_lag_7', 'price_lag_14', 'price_lag_21', 'price_lag_30',
    'price_ma_7', 'price_ma_14', 'price_ma_30',
    'price_std_7', 'price_std_14', 'price_std_30',
    'price_momentum_7d', 'price_momentum_30d',
]

# NEW features
new_features = [
    # Volatility
    'price_cv_7d', 'price_cv_14d', 'price_cv_30d',
    'price_range_7d', 'price_range_14d',
    # Trend
    'price_trend_7d', 'price_trend_30d', 'price_acceleration',
    # Relative
    'price_distance_ma_7d', 'price_distance_ma_30d', 'price_zscore_30d',
    # Seasonal
    'month', 'quarter', 'month_sin', 'month_cos',
]

all_features = basic_features + new_features
available_features = [col for col in all_features if col in df.columns]

print(f"\n✅ Selected features:")
print(f"   Basic features: {len(basic_features)}")
print(f"   NEW features: {len(new_features)}")
print(f"   Total: {len(available_features)}")

# ============================================================================
# STEP 9: Prepare Data
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 9: Preparing Data")
print("="*80)

# Remove rows with missing values
df_clean = df[['crop_type', 'province', 'target_price_7d'] + available_features].copy()

# Replace inf values with NaN
df_clean = df_clean.replace([np.inf, -np.inf], np.nan)

# Drop NaN
rows_before = len(df_clean)
df_clean = df_clean.dropna()
rows_after = len(df_clean)

print(f"\n✅ Removed rows with missing/inf values: {rows_before - rows_after:,}")
print(f"   Remaining: {rows_after:,} rows")

# Time-series split
split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx]
test_df = df_clean.iloc[split_idx:]

print(f"\n✅ Train/Test split:")
print(f"   Train: {len(train_df):,} rows")
print(f"   Test:  {len(test_df):,} rows")

# ============================================================================
# STEP 10: Define Price Ranges
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 10: Defining Price Ranges")
print("="*80)

price_percentiles = train_df['target_price_7d'].quantile([0.33, 0.67])
low_threshold = price_percentiles[0.33]
high_threshold = price_percentiles[0.67]

print(f"\n📊 Price Range Thresholds:")
print(f"   Low:    < {low_threshold:.2f} baht/kg")
print(f"   Medium: {low_threshold:.2f} - {high_threshold:.2f} baht/kg")
print(f"   High:   > {high_threshold:.2f} baht/kg")

# Categorize
train_df['price_category'] = pd.cut(
    train_df['target_price_7d'],
    bins=[0, low_threshold, high_threshold, float('inf')],
    labels=['low', 'medium', 'high']
)

test_df['price_category'] = pd.cut(
    test_df['target_price_7d'],
    bins=[0, low_threshold, high_threshold, float('inf')],
    labels=['low', 'medium', 'high']
)

# ============================================================================
# STEP 11: Train Models
# ============================================================================
print("\n" + "="*80)
print("🤖 STEP 11: Training Models with NEW Features")
print("="*80)

models = {}
results = {}

for category in ['low', 'medium', 'high']:
    print(f"\n🔄 Training {category.upper()} model...")
    
    train_cat = train_df[train_df['price_category'] == category]
    test_cat = test_df[test_df['price_category'] == category]
    
    if len(train_cat) < 100:
        print(f"   ⚠️  Insufficient data, skipping...")
        continue
    
    X_train_cat = train_cat[available_features]
    y_train_cat = train_cat['target_price_7d']
    X_test_cat = test_cat[available_features]
    y_test_cat = test_cat['target_price_7d']
    
    # Train model (same parameters as before)
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.1,
        random_state=42,
        verbose=0
    )
    
    model.fit(X_train_cat, y_train_cat)
    
    # Evaluate
    y_pred_test = model.predict(X_test_cat)
    test_mae = mean_absolute_error(y_test_cat, y_pred_test)
    test_r2 = r2_score(y_test_cat, y_pred_test)
    
    models[category] = model
    results[category] = {
        'test_mae': test_mae,
        'test_r2': test_r2,
        'test_samples': len(test_cat)
    }
    
    print(f"   ✅ Test MAE: {test_mae:.2f}, R²: {test_r2:.4f} ({len(test_cat):,} samples)")

# ============================================================================
# STEP 12: Evaluate Combined Performance
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 12: Evaluating Combined Performance")
print("="*80)

test_df['y_pred_new'] = np.nan

for category in ['low', 'medium', 'high']:
    if category in models:
        mask = test_df['price_category'] == category
        X_test_cat = test_df.loc[mask, available_features]
        test_df.loc[mask, 'y_pred_new'] = models[category].predict(X_test_cat)

test_df_eval = test_df.dropna(subset=['y_pred_new'])

new_mae = mean_absolute_error(test_df_eval['target_price_7d'], test_df_eval['y_pred_new'])
new_rmse = np.sqrt(mean_squared_error(test_df_eval['target_price_7d'], test_df_eval['y_pred_new']))
new_r2 = r2_score(test_df_eval['target_price_7d'], test_df_eval['y_pred_new'])

print(f"\n✅ NEW Model Performance (with cleaning + features):")
print(f"   MAE:  {new_mae:.2f} baht/kg")
print(f"   RMSE: {new_rmse:.2f} baht/kg")
print(f"   R²:   {new_r2:.4f}")

# ============================================================================
# STEP 13: Compare with Original
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 13: Comparison with Original Model")
print("="*80)

# Original results (from previous run)
original_r2 = 0.7589
original_mae = 6.97
original_rmse = 14.09

print(f"\n📊 Comparison:")
print(f"   {'Metric':<10} {'Original':<15} {'NEW':<15} {'Change':<15}")
print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
print(f"   {'R²':<10} {original_r2:<15.4f} {new_r2:<15.4f} {new_r2-original_r2:+15.4f}")
print(f"   {'MAE':<10} {original_mae:<15.2f} {new_mae:<15.2f} {original_mae-new_mae:+15.2f}")
print(f"   {'RMSE':<10} {original_rmse:<15.2f} {new_rmse:<15.2f} {original_rmse-new_rmse:+15.2f}")

improvement_r2 = ((new_r2 - original_r2) / original_r2) * 100
improvement_mae = ((original_mae - new_mae) / original_mae) * 100

print(f"\n📈 Improvement:")
print(f"   R² improvement: {improvement_r2:+.2f}%")
print(f"   MAE improvement: {improvement_mae:+.2f}%")

if new_r2 > original_r2:
    print(f"\n✅ NEW model is BETTER!")
else:
    print(f"\n⚠️  Original model is still better")

# Performance by category
print(f"\n📊 Performance by Price Range:")
print(f"   {'Category':<10} {'Original R²':<15} {'NEW R²':<15} {'Change':<15}")
print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")

original_results = {
    'low': 0.7722,
    'medium': 0.3370,
    'high': 0.0814
}

for cat in ['low', 'medium', 'high']:
    if cat in results:
        orig = original_results[cat]
        new = results[cat]['test_r2']
        change = new - orig
        print(f"   {cat.upper():<10} {orig:<15.4f} {new:<15.4f} {change:+15.4f}")

# ============================================================================
# STEP 14: Feature Importance
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 14: Feature Importance Analysis")
print("="*80)

for category in ['low', 'medium', 'high']:
    if category not in models:
        continue
    
    print(f"\n📊 {category.upper()} Model - Top 10 Features:")
    
    importances = models[category].feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': available_features,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    for idx, row in feature_importance_df.head(10).iterrows():
        is_new = row['Feature'] in new_features
        marker = "🆕" if is_new else "  "
        print(f"   {marker} {row['Feature']:<30} {row['Importance']:.4f}")

# ============================================================================
# STEP 15: Save Models
# ============================================================================
print("\n" + "="*80)
print("💾 STEP 15: Saving Models")
print("="*80)

if new_r2 > original_r2:
    print("\n✅ NEW model is better! Saving...")
    
    os.makedirs('backend/models', exist_ok=True)
    
    for category, model in models.items():
        model_path = f'backend/models/model_c_cleaned_{category}.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"   ✅ Saved: {model_path}")
    
    # Save features
    with open('backend/models/model_c_cleaned_features.json', 'w') as f:
        json.dump(available_features, f, indent=2)
    print(f"   ✅ Saved: model_c_cleaned_features.json")
    
    # Save thresholds
    thresholds = {
        'low_threshold': float(low_threshold),
        'high_threshold': float(high_threshold)
    }
    with open('backend/models/model_c_cleaned_thresholds.json', 'w') as f:
        json.dump(thresholds, f, indent=2)
    print(f"   ✅ Saved: model_c_cleaned_thresholds.json")
    
    # Save metadata
    metadata = {
        'model_name': 'Gradient Boosting (Cleaned + New Features)',
        'data_cleaning': {
            'removed_invalid': int(removed_invalid),
            'removed_low': int(removed_low),
            'removed_extreme': int(removed_extreme),
            'total_removed': int(total_removed)
        },
        'new_features': new_features,
        'overall_test_r2': float(new_r2),
        'overall_test_mae': float(new_mae),
        'overall_test_rmse': float(new_rmse),
        'improvement_over_original': {
            'r2_change': float(new_r2 - original_r2),
            'r2_pct': float(improvement_r2),
            'mae_change': float(original_mae - new_mae),
            'mae_pct': float(improvement_mae)
        },
        'model_performance': {
            cat: {
                'test_r2': float(results[cat]['test_r2']),
                'test_mae': float(results[cat]['test_mae'])
            }
            for cat in results.keys()
        },
        'trained_at': datetime.now().isoformat()
    }
    
    with open('backend/models/model_c_cleaned_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Saved: model_c_cleaned_metadata.json")
else:
    print("\n⚠️  Original model is still better, not saving")

# ============================================================================
# STEP 16: Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 SUMMARY")
print("="*80)

print(f"\n📊 Data Cleaning:")
print(f"   Removed {total_removed:,} rows ({total_removed/len(df_original)*100:.2f}%)")
print(f"   - Invalid prices: {removed_invalid:,}")
print(f"   - Very low prices: {removed_low:,}")
print(f"   - Extreme outliers: {removed_extreme:,}")

print(f"\n📊 Feature Engineering:")
print(f"   Added {len(new_features)} new features")
print(f"   - Volatility features: 5")
print(f"   - Trend features: 3")
print(f"   - Relative features: 3")
print(f"   - Seasonal features: 4")

print(f"\n📊 Model Performance:")
print(f"   Original R²: {original_r2:.4f}")
print(f"   NEW R²:      {new_r2:.4f}")
print(f"   Change:      {new_r2-original_r2:+.4f} ({improvement_r2:+.2f}%)")

if new_r2 > original_r2:
    print(f"\n✅ SUCCESS! Model improved by {improvement_r2:.2f}%")
else:
    print(f"\n⚠️  Model did not improve")
    print(f"   Possible reasons:")
    print(f"   - New features not helpful")
    print(f"   - Need hyperparameter tuning")
    print(f"   - Need more sophisticated features")

print("\n" + "="*80)
print("✅ Done!")
print("="*80)

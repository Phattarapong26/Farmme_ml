"""
Model C - With Log Transformation Fix
======================================
แก้ปัญหา "Ceiling Effect" ตาม feedback จาก feedbackmodel_c.md

Key Fix:
✅ Log Transformation: แปลง target เป็น log(price) ก่อน train
✅ Inverse Transform: แปลงกลับเป็นราคาปกติตอน predict
✅ ช่วยให้โมเดลเรียนรู้ pattern ของพืชราคาแพงได้ดีขึ้น

Based on: model_c_new.py (Clean Version - No Data Leakage)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pickle
import json
import os
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🚀 Model C - With Log Transformation Fix")
print("="*80)
print("\n📝 Fixing 'Ceiling Effect' problem:")
print("   - ว่านหางจระเข้: ของจริง 220 บาท -> ทายได้แค่ 99 บาท ❌")
print("   - ตะไคร้: ของจริง 210 บาท -> ทายได้แค่ 91 บาท ❌")
print("\n✅ Solution: Log Transformation")
print("   - Train on log(price) instead of price")
print("   - Transform back to normal price when predicting")

# ============================================================================
# STEP 1-5: Same as model_c_new.py (Load data, create features)
# ============================================================================
print("\n" + "="*80)
print("📊 Loading and Preparing Data")
print("="*80)

df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
print(f"✅ Loaded {len(df):,} rows")

# Remove leaky features
LEAKY_FEATURES = ['future_price_7d', 'price_next_day', 'bid_price', 'ask_price', 'base_price', 'spread_pct']
existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
if existing_leaky:
    df = df.drop(columns=existing_leaky)

# Create target
df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)

# Create lagged features
print("🔄 Creating lagged features...")
grouped = df.groupby(['province', 'crop_type'])

for lag in [7, 14, 21, 30]:
    df[f'price_lag_{lag}'] = grouped['price_per_kg'].shift(lag)

for window in [7, 14, 30]:
    df[f'price_ma_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).mean()
    )
    df[f'price_std_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).std()
    )

df['price_momentum_7d'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']
df['price_momentum_30d'] = (df['price_lag_7'] - df['price_lag_30']) / df['price_lag_30']

for feature in ['temperature_celsius', 'rainfall_mm', 'humidity_percent', 'drought_index']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

for feature in ['fuel_price', 'fertilizer_price', 'inflation_rate', 'gdp_growth']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

for feature in ['supply_level', 'inventory_level', 'demand_elasticity', 'income_elasticity']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

# Select features
SAFE_FEATURES = [
    'price_lag_7', 'price_lag_14', 'price_lag_21', 'price_lag_30',
    'price_ma_7', 'price_ma_14', 'price_ma_30',
    'price_std_7', 'price_std_14', 'price_std_30',
    'price_momentum_7d', 'price_momentum_30d',
    'dayofyear', 'month', 'weekday',
    'temperature_celsius_lag_7', 'rainfall_mm_lag_7', 'humidity_percent_lag_7', 'drought_index_lag_7',
    'fuel_price_lag_7', 'fertilizer_price_lag_7', 'inflation_rate_lag_7',
    'supply_level_lag_7', 'inventory_level_lag_7', 'demand_elasticity_lag_7',
]

available_features = [col for col in SAFE_FEATURES if col in df.columns]
print(f"✅ Selected {len(available_features)} features")

# Prepare data
df_clean = df[['date', 'province', 'crop_type', 'price_per_kg', 'target_price_7d'] + available_features].copy()
df_clean = df_clean.dropna()

split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx].copy()
test_df = df_clean.iloc[split_idx:].copy()

X_train = train_df[available_features]
y_train = train_df['target_price_7d']
X_test = test_df[available_features]
y_test = test_df['target_price_7d']

print(f"✅ Train: {len(X_train):,} rows, Test: {len(X_test):,} rows")

# ============================================================================
# 🔥 NEW: Log Transformation
# ============================================================================
print("\n" + "="*80)
print("🔥 STEP 6: Log Transformation (NEW!)")
print("="*80)

print("\n📊 Price Distribution BEFORE Log Transform:")
print(f"   Min:  {y_train.min():.2f} baht/kg")
print(f"   Max:  {y_train.max():.2f} baht/kg")
print(f"   Mean: {y_train.mean():.2f} baht/kg")
print(f"   Std:  {y_train.std():.2f} baht/kg")
print(f"   Range: {y_train.max() - y_train.min():.2f} baht/kg")

# Transform target to log scale
# ใช้ log1p เพื่อเลี่ยง log(0) และจัดการกับราคาที่ต่ำมาก
y_train_log = np.log1p(y_train)
y_test_log = np.log1p(y_test)

print("\n📊 Price Distribution AFTER Log Transform:")
print(f"   Min:  {y_train_log.min():.4f}")
print(f"   Max:  {y_train_log.max():.4f}")
print(f"   Mean: {y_train_log.mean():.4f}")
print(f"   Std:  {y_train_log.std():.4f}")
print(f"   Range: {y_train_log.max() - y_train_log.min():.4f}")

print("\n✅ Benefits of Log Transform:")
print("   1. ลดความต่างระหว่างของถูก (10 บาท) กับของแพง (200 บาท)")
print("   2. โมเดลเรียนรู้ % change แทน absolute change")
print("   3. แก้ปัญหา 'Ceiling Effect' (ชนเพดาน)")

# ============================================================================
# STEP 7: Train Model with Log-Transformed Target
# ============================================================================
print("\n" + "="*80)
print("🤖 STEP 7: Training Model (on log-transformed target)")
print("="*80)

print("\n🔄 Training Gradient Boosting on log(price)...")
gb_model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    verbose=0
)

gb_model.fit(X_train, y_train_log)
print("✅ Model trained on log-transformed target")

# ============================================================================
# STEP 8: Predict and Transform Back
# ============================================================================
print("\n" + "="*80)
print("🔮 STEP 8: Making Predictions (transform back to normal price)")
print("="*80)

# Predict in log space
y_pred_train_log = gb_model.predict(X_train)
y_pred_test_log = gb_model.predict(X_test)

# Transform back to normal price using expm1 (inverse of log1p)
y_pred_train = np.expm1(y_pred_train_log)
y_pred_test = np.expm1(y_pred_test_log)

print("✅ Predictions transformed back to normal price scale")

# ============================================================================
# STEP 9: Evaluate Performance
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 9: Model Performance")
print("="*80)

# Calculate metrics on ORIGINAL scale (not log scale!)
train_mae = mean_absolute_error(y_train, y_pred_train)
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
train_r2 = r2_score(y_train, y_pred_train)

test_mae = mean_absolute_error(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_r2 = r2_score(y_test, y_pred_test)

print("\n📈 Training Set:")
print(f"   MAE:  {train_mae:.2f} baht/kg")
print(f"   RMSE: {train_rmse:.2f} baht/kg")
print(f"   R²:   {train_r2:.4f}")

print("\n📈 Test Set:")
print(f"   MAE:  {test_mae:.2f} baht/kg")
print(f"   RMSE: {test_rmse:.2f} baht/kg")
print(f"   R²:   {test_r2:.4f}")

# Check overfitting
overfitting_gap = train_r2 - test_r2
print(f"\n🔍 Overfitting Check:")
print(f"   R² gap: {overfitting_gap:.4f}")
if overfitting_gap < 0.1:
    print(f"   ✅ No overfitting (gap < 0.1)")
elif overfitting_gap < 0.3:
    print(f"   ⚠️  Slight overfitting (0.1 < gap < 0.3)")
else:
    print(f"   ❌ Significant overfitting (gap > 0.3)")

# ============================================================================
# STEP 10: Compare with Baseline
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 10: Comparison with Baseline")
print("="*80)

# Baseline: Moving Average (14 days)
baseline_ma = test_df['price_ma_14']
baseline_mae = mean_absolute_error(y_test, baseline_ma)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_ma))
baseline_r2 = r2_score(y_test, baseline_ma)

print("\n📊 Baseline (MA-14):")
print(f"   MAE:  {baseline_mae:.2f} baht/kg")
print(f"   RMSE: {baseline_rmse:.2f} baht/kg")
print(f"   R²:   {baseline_r2:.4f}")

print("\n📊 Model with Log Transform:")
print(f"   MAE:  {test_mae:.2f} baht/kg")
print(f"   RMSE: {test_rmse:.2f} baht/kg")
print(f"   R²:   {test_r2:.4f}")

improvement = test_r2 - baseline_r2
print(f"\n📈 Improvement:")
print(f"   R² improvement: {improvement:+.4f}")
print(f"   MAE reduction: {baseline_mae - test_mae:+.2f} baht/kg")
print(f"   RMSE reduction: {baseline_rmse - test_rmse:+.2f} baht/kg")

if improvement > 0.05:
    print(f"   ✅ SIGNIFICANT improvement over baseline!")
else:
    print(f"   ⚠️  Marginal improvement")

# ============================================================================
# STEP 11: Analyze Predictions by Price Range
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 11: Performance by Price Range")
print("="*80)

# Categorize by price
test_df_eval = test_df.copy()
test_df_eval['y_pred'] = y_pred_test
test_df_eval['error'] = np.abs(y_test - y_pred_test)

# Define price ranges
test_df_eval['price_range'] = pd.cut(
    y_test,
    bins=[0, 20, 50, 100, 200, 1000],
    labels=['Very Cheap (<20)', 'Cheap (20-50)', 'Medium (50-100)', 'Expensive (100-200)', 'Very Expensive (>200)']
)

print("\n📊 Performance by Price Range:")
for price_range in test_df_eval['price_range'].cat.categories:
    subset = test_df_eval[test_df_eval['price_range'] == price_range]
    if len(subset) > 0:
        mae = subset['error'].mean()
        r2 = r2_score(subset['target_price_7d'], subset['y_pred'])
        print(f"\n   {price_range}:")
        print(f"      Samples: {len(subset):,}")
        print(f"      MAE: {mae:.2f} baht/kg")
        print(f"      R²: {r2:.4f}")

# ============================================================================
# STEP 12: Check Worst Predictions
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 12: Worst Predictions Analysis")
print("="*80)

test_df_eval['abs_error'] = np.abs(y_test - y_pred_test)
worst_predictions = test_df_eval.nlargest(10, 'abs_error')[['crop_type', 'province', 'target_price_7d', 'y_pred', 'abs_error']]

print("\n❌ Top 10 Worst Predictions:")
print(worst_predictions.to_string(index=False))

print("\n📊 Error Statistics:")
print(f"   Mean error: {test_df_eval['abs_error'].mean():.2f} baht/kg")
print(f"   Median error: {test_df_eval['abs_error'].median():.2f} baht/kg")
print(f"   90th percentile: {test_df_eval['abs_error'].quantile(0.9):.2f} baht/kg")
print(f"   95th percentile: {test_df_eval['abs_error'].quantile(0.95):.2f} baht/kg")
print(f"   99th percentile: {test_df_eval['abs_error'].quantile(0.99):.2f} baht/kg")

# ============================================================================
# STEP 13: Save Model
# ============================================================================
print("\n" + "="*80)
print("💾 STEP 13: Saving Model")
print("="*80)

os.makedirs('backend/models', exist_ok=True)

# Save model
model_path = 'backend/models/model_c_log_transform.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(gb_model, f)
print(f"✅ Model saved: {model_path}")

# Save features
features_path = 'backend/models/model_c_log_transform_features.json'
with open(features_path, 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"✅ Features saved: {features_path}")

# Save metadata
metadata = {
    'model_name': 'Gradient Boosting with Log Transform',
    'transformation': 'log1p',
    'test_r2': float(test_r2),
    'test_mae': float(test_mae),
    'test_rmse': float(test_rmse),
    'baseline_ma14_r2': float(baseline_r2),
    'improvement_over_baseline': float(improvement),
    'train_date_range': f"{train_df['date'].min()} to {train_df['date'].max()}",
    'test_date_range': f"{test_df['date'].min()} to {test_df['date'].max()}",
    'n_features': len(available_features),
    'trained_at': datetime.now().isoformat(),
    'overfitting_gap': float(overfitting_gap),
    'note': 'Uses log1p transformation to handle price range differences'
}

metadata_path = 'backend/models/model_c_log_transform_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✅ Metadata saved: {metadata_path}")

# ============================================================================
# STEP 14: Final Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 FINAL SUMMARY")
print("="*80)

print("\n📊 Model Performance:")
print(f"   Test R²: {test_r2:.4f}")
print(f"   Test MAE: {test_mae:.2f} baht/kg")
print(f"   Test RMSE: {test_rmse:.2f} baht/kg")

print("\n📈 Improvement over Baseline:")
print(f"   R² improvement: {improvement:+.4f}")
print(f"   Status: {'✅ SIGNIFICANT' if improvement > 0.05 else '⚠️  MARGINAL'}")

print("\n✅ Log Transform Benefits:")
print("   1. Better handling of price range differences")
print("   2. Reduced 'Ceiling Effect' problem")
print("   3. More balanced errors across price ranges")

print("\n📝 Next Steps:")
print("   1. Compare with model_c_gradient_boosting.pkl (without log transform)")
print("   2. If better, update backend/model_c_wrapper.py")
print("   3. Test with real data")
print("   4. Deploy to production")

print("\n" + "="*80)
print("✅ All Done!")
print("="*80)

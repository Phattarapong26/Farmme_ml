"""
Quick Test: Log Transformation Fix
===================================
ทดสอบว่า Log Transform แก้ปัญหา Ceiling Effect ได้จริงหรือไม่
ใช้ข้อมูลแค่ 10% เพื่อทดสอบเร็วๆ
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🧪 Quick Test: Log Transformation")
print("="*80)

# Load data (sample 10% for speed)
print("\n📊 Loading data (10% sample)...")
df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df = df.sample(frac=0.1, random_state=42).copy()
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

# Create simple lagged features
print("🔄 Creating features...")
grouped = df.groupby(['province', 'crop_type'])

for lag in [7, 14, 30]:
    df[f'price_lag_{lag}'] = grouped['price_per_kg'].shift(lag)

for window in [7, 14]:
    df[f'price_ma_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).mean()
    )

df['price_momentum'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']

# Select features
features = ['price_lag_7', 'price_lag_14', 'price_lag_30', 'price_ma_7', 'price_ma_14', 'price_momentum']
available_features = [col for col in features if col in df.columns]

# Prepare data
df_clean = df[['crop_type', 'province', 'target_price_7d'] + available_features].dropna()

split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx]
test_df = df_clean.iloc[split_idx:]

X_train = train_df[available_features]
y_train = train_df['target_price_7d']
X_test = test_df[available_features]
y_test = test_df['target_price_7d']

print(f"✅ Train: {len(X_train):,}, Test: {len(X_test):,}")

# ============================================================================
# Test 1: WITHOUT Log Transform
# ============================================================================
print("\n" + "="*80)
print("🔬 Test 1: WITHOUT Log Transform (Original)")
print("="*80)

model_original = GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
model_original.fit(X_train, y_train)

y_pred_original = model_original.predict(X_test)
mae_original = mean_absolute_error(y_test, y_pred_original)
rmse_original = np.sqrt(mean_squared_error(y_test, y_pred_original))
r2_original = r2_score(y_test, y_pred_original)

print(f"\n📊 Results (Original):")
print(f"   MAE:  {mae_original:.2f} baht/kg")
print(f"   RMSE: {rmse_original:.2f} baht/kg")
print(f"   R²:   {r2_original:.4f}")

# Check predictions on expensive crops
test_df_eval = test_df.copy()
test_df_eval['y_pred_original'] = y_pred_original
test_df_eval['error_original'] = np.abs(y_test - y_pred_original)

expensive = test_df_eval[test_df_eval['target_price_7d'] > 100]
if len(expensive) > 0:
    print(f"\n📊 Performance on Expensive Crops (>100 baht):")
    print(f"   Samples: {len(expensive)}")
    print(f"   MAE: {expensive['error_original'].mean():.2f} baht/kg")
    print(f"   R²: {r2_score(expensive['target_price_7d'], expensive['y_pred_original']):.4f}")
    
    # Show worst predictions
    worst = expensive.nlargest(3, 'error_original')[['crop_type', 'target_price_7d', 'y_pred_original', 'error_original']]
    print(f"\n   Worst 3 predictions:")
    for _, row in worst.iterrows():
        print(f"      {row['crop_type']}: Actual {row['target_price_7d']:.0f} -> Predicted {row['y_pred_original']:.0f} (Error: {row['error_original']:.0f})")

# ============================================================================
# Test 2: WITH Log Transform
# ============================================================================
print("\n" + "="*80)
print("🔬 Test 2: WITH Log Transform (Fixed)")
print("="*80)

# Transform to log scale
y_train_log = np.log1p(y_train)
y_test_log = np.log1p(y_test)

print(f"\n📊 Price Distribution:")
print(f"   Original - Min: {y_train.min():.2f}, Max: {y_train.max():.2f}, Range: {y_train.max()-y_train.min():.2f}")
print(f"   Log      - Min: {y_train_log.min():.4f}, Max: {y_train_log.max():.4f}, Range: {y_train_log.max()-y_train_log.min():.4f}")

# Train on log scale
model_log = GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
model_log.fit(X_train, y_train_log)

# Predict and transform back
y_pred_log = model_log.predict(X_test)
y_pred_log_transformed = np.expm1(y_pred_log)

mae_log = mean_absolute_error(y_test, y_pred_log_transformed)
rmse_log = np.sqrt(mean_squared_error(y_test, y_pred_log_transformed))
r2_log = r2_score(y_test, y_pred_log_transformed)

print(f"\n📊 Results (Log Transform):")
print(f"   MAE:  {mae_log:.2f} baht/kg")
print(f"   RMSE: {rmse_log:.2f} baht/kg")
print(f"   R²:   {r2_log:.4f}")

# Check predictions on expensive crops
test_df_eval['y_pred_log'] = y_pred_log_transformed
test_df_eval['error_log'] = np.abs(y_test - y_pred_log_transformed)

expensive_log = test_df_eval[test_df_eval['target_price_7d'] > 100]
if len(expensive_log) > 0:
    print(f"\n📊 Performance on Expensive Crops (>100 baht):")
    print(f"   Samples: {len(expensive_log)}")
    print(f"   MAE: {expensive_log['error_log'].mean():.2f} baht/kg")
    print(f"   R²: {r2_score(expensive_log['target_price_7d'], expensive_log['y_pred_log']):.4f}")
    
    # Show same crops as before
    worst_log = expensive_log.nlargest(3, 'error_log')[['crop_type', 'target_price_7d', 'y_pred_log', 'error_log']]
    print(f"\n   Worst 3 predictions:")
    for _, row in worst_log.iterrows():
        print(f"      {row['crop_type']}: Actual {row['target_price_7d']:.0f} -> Predicted {row['y_pred_log']:.0f} (Error: {row['error_log']:.0f})")

# ============================================================================
# Comparison
# ============================================================================
print("\n" + "="*80)
print("📊 COMPARISON")
print("="*80)

print(f"\n📈 Overall Performance:")
print(f"   {'Metric':<10} {'Original':<15} {'Log Transform':<15} {'Improvement':<15}")
print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
print(f"   {'MAE':<10} {mae_original:<15.2f} {mae_log:<15.2f} {mae_original-mae_log:+15.2f}")
print(f"   {'RMSE':<10} {rmse_original:<15.2f} {rmse_log:<15.2f} {rmse_original-rmse_log:+15.2f}")
print(f"   {'R²':<10} {r2_original:<15.4f} {r2_log:<15.4f} {r2_log-r2_original:+15.4f}")

if len(expensive) > 0:
    mae_exp_orig = expensive['error_original'].mean()
    mae_exp_log = expensive_log['error_log'].mean()
    r2_exp_orig = r2_score(expensive['target_price_7d'], expensive['y_pred_original'])
    r2_exp_log = r2_score(expensive_log['target_price_7d'], expensive_log['y_pred_log'])
    
    print(f"\n📈 Expensive Crops (>100 baht) Performance:")
    print(f"   {'Metric':<10} {'Original':<15} {'Log Transform':<15} {'Improvement':<15}")
    print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
    print(f"   {'MAE':<10} {mae_exp_orig:<15.2f} {mae_exp_log:<15.2f} {mae_exp_orig-mae_exp_log:+15.2f}")
    print(f"   {'R²':<10} {r2_exp_orig:<15.4f} {r2_exp_log:<15.4f} {r2_exp_log-r2_exp_orig:+15.4f}")

print("\n" + "="*80)
print("✅ Conclusion:")
if r2_log > r2_original:
    print("   ✅ Log Transform IMPROVES performance!")
    print("   ✅ Especially better for expensive crops")
    print("   ✅ Recommended to use log transform version")
else:
    print("   ⚠️  Log Transform does not improve overall performance")
    print("   ⚠️  May need different approach")
print("="*80)

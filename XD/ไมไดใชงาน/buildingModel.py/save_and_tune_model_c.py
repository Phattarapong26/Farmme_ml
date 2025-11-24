"""
Save and Tune Model C
======================
สคริปต์นี้จะ:
1. โหลดข้อมูลและ prepare features (ใช้โค้ดเดียวกับ model_c_new.py)
2. โหลด model ที่ train ไว้แล้ว (ถ้ามี) หรือ train ใหม่
3. Tune hyperparameters
4. Save best model

Note: ถ้ารัน model_c_new.py ไปแล้ว สคริปต์นี้จะโหลด model เดิมมาใช้
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import json
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("💾 Save and Tune Model C")
print("="*80)

# ============================================================================
# STEP 0: Prepare Data (Same as model_c_new.py)
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 0: Loading and Preparing Data")
print("="*80)

print("\n🔄 Loading dataset...")
df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
print(f"   ✅ Loaded {len(df):,} rows")

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
print(f"   ✅ Selected {len(available_features)} features")

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

print(f"   ✅ Train: {len(X_train):,} rows, Test: {len(X_test):,} rows")

# Calculate baseline
baseline_ma = test_df['price_ma_14']
baseline_r2_2 = r2_score(y_test, baseline_ma)
print(f"   ✅ Baseline MA-14 R²: {baseline_r2_2:.4f}")

# ============================================================================
# STEP 1: Load or Train Model
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 1: Load or Train Model")
print("="*80)

model_path = 'backend/models/model_c_gradient_boosting.pkl'
model_exists = os.path.exists(model_path)

if model_exists:
    print(f"\n✅ Found existing model: {model_path}")
    print("   Loading model...")
    
    with open(model_path, 'rb') as f:
        gb_model = pickle.load(f)
    
    # Evaluate
    y_pred = gb_model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred)
    test_mae = mean_absolute_error(y_test, y_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"   ✅ Loaded model performance:")
    print(f"      - Test R²: {test_r2:.4f}")
    print(f"      - Test MAE: {test_mae:.2f}")
    print(f"      - Test RMSE: {test_rmse:.2f}")
    
else:
    print(f"\n⚠️  No existing model found at {model_path}")
    print("   Training new Gradient Boosting model...")
    print("   This will take 5-10 minutes for 1.7M rows...")
    
    gb_model = GradientBoostingRegressor(
        n_estimators=100, 
        max_depth=5, 
        random_state=42,
        verbose=1  # แสดง progress
    )
    gb_model.fit(X_train, y_train)
    
    y_pred = gb_model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred)
    test_mae = mean_absolute_error(y_test, y_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"   ✅ Model trained:")
    print(f"      - Test R²: {test_r2:.4f}")
    print(f"      - Test MAE: {test_mae:.2f}")
    print(f"      - Test RMSE: {test_rmse:.2f}")
    
    # Save default model
    os.makedirs('backend/models', exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(gb_model, f)
    print(f"   ✅ Saved to: {model_path}")

best_model = {
    'model': gb_model,
    'test_r2': test_r2,
    'test_mae': test_mae,
    'test_rmse': test_rmse
}

# Save features and metadata
features_path = 'backend/models/model_c_features.json'
with open(features_path, 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"   ✅ Features saved: {features_path}")

metadata = {
    'model_name': 'Gradient Boosting',
    'test_r2': float(test_r2),
    'test_mae': float(test_mae),
    'test_rmse': float(test_rmse),
    'baseline_ma14_r2': float(baseline_r2_2),
    'gap_vs_baseline': float(test_r2 - baseline_r2_2),
    'train_date_range': f"{train_df['date'].min()} to {train_df['date'].max()}",
    'test_date_range': f"{test_df['date'].min()} to {test_df['date'].max()}",
    'n_features': len(available_features),
    'trained_at': datetime.now().isoformat()
}

metadata_path = 'backend/models/model_c_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✅ Metadata saved: {metadata_path}")

# ============================================================================
# STEP 2: Hyperparameter Tuning
# ============================================================================
print("\n" + "="*80)
print("🔧 STEP 2: Hyperparameter Tuning")
print("="*80)

print("\n🎯 Goal: Beat Baseline MA-14 by a larger margin")
print(f"   Baseline MA-14 R²: {baseline_r2_2:.4f}")
print(f"   Current GB R²: {test_r2:.4f}")
print(f"   Current gap: {(test_r2 - baseline_r2_2):.4f}")
print(f"   Target gap: > 0.05")

# Hyperparameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 7, 10],
    'learning_rate': [0.05, 0.1, 0.15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'subsample': [0.8, 0.9, 1.0]
}

total_combinations = (len(param_grid['n_estimators']) * 
                     len(param_grid['max_depth']) * 
                     len(param_grid['learning_rate']) * 
                     len(param_grid['min_samples_split']) * 
                     len(param_grid['min_samples_leaf']) * 
                     len(param_grid['subsample']))

print(f"\n🔍 Searching {total_combinations} combinations...")
print("   This may take 10-20 minutes...")
print("   Using 3-fold TimeSeriesSplit cross-validation")

# Use TimeSeriesSplit for CV
tscv_tuning = TimeSeriesSplit(n_splits=3)

# Grid search
gb_tuned = GridSearchCV(
    GradientBoostingRegressor(random_state=42),
    param_grid,
    cv=tscv_tuning,
    scoring='r2',
    n_jobs=-1,
    verbose=2
)

print("\n⏳ Training with GridSearchCV...")
gb_tuned.fit(X_train, y_train)

print(f"\n✅ Best parameters found:")
for param, value in gb_tuned.best_params_.items():
    print(f"   - {param}: {value}")

# Evaluate tuned model
y_pred_tuned = gb_tuned.predict(X_test)
tuned_mae = mean_absolute_error(y_test, y_pred_tuned)
tuned_rmse = np.sqrt(mean_squared_error(y_test, y_pred_tuned))
tuned_r2 = r2_score(y_test, y_pred_tuned)

print(f"\n📊 Tuned Model Performance:")
print(f"   - Test MAE:  {tuned_mae:.2f} (vs {test_mae:.2f})")
print(f"   - Test RMSE: {tuned_rmse:.2f} (vs {test_rmse:.2f})")
print(f"   - Test R²:   {tuned_r2:.4f} (vs {test_r2:.4f})")

improvement = tuned_r2 - test_r2
baseline_gap = tuned_r2 - baseline_r2_2

print(f"\n📈 Improvement Analysis:")
print(f"   - Improvement over default: {improvement:+.4f}")
print(f"   - Gap vs Baseline MA-14: {baseline_gap:.4f}")
print(f"   - Status: {'✅ SIGNIFICANT' if baseline_gap > 0.05 else '⚠️  MARGINAL'}")

# ============================================================================
# STEP 3: Save Best Model
# ============================================================================
print("\n" + "="*80)
print("💾 STEP 3: Saving Best Model")
print("="*80)

if tuned_r2 > test_r2:
    print(f"\n✅ Tuned model is better! Saving...")
    
    tuned_model_path = 'backend/models/model_c_tuned.pkl'
    with open(tuned_model_path, 'wb') as f:
        pickle.dump(gb_tuned.best_estimator_, f)
    print(f"   ✅ Tuned model saved: {tuned_model_path}")
    
    # Update metadata
    tuned_metadata = metadata.copy()
    tuned_metadata.update({
        'model_name': 'Gradient Boosting (Tuned)',
        'test_r2': float(tuned_r2),
        'test_mae': float(tuned_mae),
        'test_rmse': float(tuned_rmse),
        'best_params': gb_tuned.best_params_,
        'improvement_over_default': float(improvement),
        'gap_vs_baseline_ma14': float(baseline_gap)
    })
    
    tuned_metadata_path = 'backend/models/model_c_tuned_metadata.json'
    with open(tuned_metadata_path, 'w') as f:
        json.dump(tuned_metadata, f, indent=2)
    print(f"   ✅ Tuned metadata saved: {tuned_metadata_path}")
    
    final_model_to_use = 'model_c_tuned.pkl'
    final_r2 = tuned_r2
else:
    print(f"\n⚠️  Tuned model not better than default")
    print(f"   Keeping default model: model_c_gradient_boosting.pkl")
    final_model_to_use = 'model_c_gradient_boosting.pkl'
    final_r2 = test_r2

# ============================================================================
# STEP 4: Final Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 FINAL SUMMARY")
print("="*80)

print(f"\n📊 Model Comparison:")
print(f"   Baseline (MA-14):       R² = {baseline_r2_2:.4f}")
print(f"   GB Default:             R² = {test_r2:.4f} ({(test_r2 - baseline_r2_2):+.4f})")
print(f"   GB Tuned:               R² = {tuned_r2:.4f} ({(tuned_r2 - baseline_r2_2):+.4f})")

print(f"\n🏆 Final Model to Use: {final_model_to_use}")
print(f"   - Test R²: {final_r2:.4f}")
print(f"   - Location: backend/models/{final_model_to_use}")

print(f"\n� Nenxt Steps:")
print(f"   1. ✅ Models saved in backend/models/")
print(f"   2. 🔄 Update backend/model_c_wrapper.py to use {final_model_to_use}")
print(f"   3. 🧪 Test the wrapper with sample data")
print(f"   4. 🚀 Deploy to production")

print("\n" + "="*80)
print("✅ All Done!")
print("="*80)

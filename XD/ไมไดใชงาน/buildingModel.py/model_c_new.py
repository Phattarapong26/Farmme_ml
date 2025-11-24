"""
Model C - Clean Version (No Data Leakage)
==========================================
Based on feedback from dataserRevirew.md

Key Improvements:
1. ✅ Remove all leaky features (future_price_7d, price_next_day, etc.)
2. ✅ Use only lagged features (minimum lag = forecast horizon)
3. ✅ Proper time-series split (no shuffle)
4. ✅ TimeSeriesSplit for cross-validation
5. ✅ Compare with baseline models

Target: Predict price 7 days ahead using ONLY past data
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("="*80)
print("🚀 Model C - Clean Version (No Data Leakage)")
print("="*80)

df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

print(f"\n📊 Dataset Info:")
print(f"   - Total rows: {len(df):,}")
print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
print(f"   - Columns: {len(df.columns)}")

# ============================================================================
# STEP 2: Remove Leaky Features
# ============================================================================
print("\n" + "="*80)
print("🔧 STEP 2: Removing Leaky Features")
print("="*80)

# Features ที่ต้องลบทิ้ง (มี future information)
LEAKY_FEATURES = [
    'future_price_7d',      # นี่คือ target เอง!
    'price_next_day',       # รู้ future
    'bid_price',            # มี current price info
    'ask_price',            # มี current price info
    'base_price',           # มี current price info
    'spread_pct',           # คำนวณจาก bid/ask
]

# ลบ leaky features ถ้ามีในข้อมูล
existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
if existing_leaky:
    print(f"\n❌ Removing leaky features: {existing_leaky}")
    df = df.drop(columns=existing_leaky)

# ============================================================================
# STEP 3: Create Target Variable (7-day ahead price)
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 3: Creating Target Variable")
print("="*80)

# Target = ราคา 7 วันข้างหน้า
df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)

print(f"\n✅ Target created: price 7 days ahead")
print(f"   - Non-null targets: {df['target_price_7d'].notna().sum():,}")
print(f"   - Null targets: {df['target_price_7d'].isna().sum():,}")

# ============================================================================
# STEP 4: Create ONLY Lagged Features (No Future Info!)
# ============================================================================
print("\n" + "="*80)
print("📈 STEP 4: Creating Lagged Features (Safe)")
print("="*80)

# Group by province and crop_type for proper lagging
grouped = df.groupby(['province', 'crop_type'])

# Price lags (minimum lag = 7 days, ต้องมากกว่า forecast horizon)
LAG_PERIODS = [7, 14, 21, 30]
for lag in LAG_PERIODS:
    df[f'price_lag_{lag}'] = grouped['price_per_kg'].shift(lag)
    print(f"   ✅ Created price_lag_{lag}")

# Rolling statistics (using past data only)
ROLLING_WINDOWS = [7, 14, 30]
for window in ROLLING_WINDOWS:
    df[f'price_ma_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).mean()
    )
    df[f'price_std_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).std()
    )
    print(f"   ✅ Created price_ma_{window} and price_std_{window}")

# Price momentum (using lagged data)
df['price_momentum_7d'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']
df['price_momentum_30d'] = (df['price_lag_7'] - df['price_lag_30']) / df['price_lag_30']
print(f"   ✅ Created price momentum features")

# Weather lags
WEATHER_FEATURES = ['temperature_celsius', 'rainfall_mm', 'humidity_percent', 'drought_index']
for feature in WEATHER_FEATURES:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

# Economic indicators lags
ECONOMIC_FEATURES = ['fuel_price', 'fertilizer_price', 'inflation_rate', 'gdp_growth']
for feature in ECONOMIC_FEATURES:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

# Supply/Demand lags
SUPPLY_DEMAND = ['supply_level', 'inventory_level', 'demand_elasticity', 'income_elasticity']
for feature in SUPPLY_DEMAND:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

print(f"\n✅ Total features created: {len([col for col in df.columns if 'lag' in col or 'ma' in col or 'std' in col or 'momentum' in col])}")

# ============================================================================
# STEP 5: Select Features (No Leakage!)
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 5: Feature Selection")
print("="*80)

# Features ที่ปลอดภัย (ไม่มี future info)
SAFE_FEATURES = [
    # Lagged prices
    'price_lag_7', 'price_lag_14', 'price_lag_21', 'price_lag_30',
    
    # Rolling statistics
    'price_ma_7', 'price_ma_14', 'price_ma_30',
    'price_std_7', 'price_std_14', 'price_std_30',
    
    # Momentum
    'price_momentum_7d', 'price_momentum_30d',
    
    # Time features (always safe)
    'dayofyear', 'month', 'weekday',
    
    # Lagged weather
    'temperature_celsius_lag_7', 'rainfall_mm_lag_7', 'humidity_percent_lag_7', 'drought_index_lag_7',
    
    # Lagged economic
    'fuel_price_lag_7', 'fertilizer_price_lag_7', 'inflation_rate_lag_7',
    
    # Lagged supply/demand
    'supply_level_lag_7', 'inventory_level_lag_7', 'demand_elasticity_lag_7',
]

# เลือกเฉพาะ features ที่มีในข้อมูล
available_features = [col for col in SAFE_FEATURES if col in df.columns]
print(f"\n✅ Selected {len(available_features)} safe features")
print(f"   Features: {available_features[:10]}...")

# ============================================================================
# STEP 6: Prepare Data (Time-Series Split, NO SHUFFLE!)
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 6: Preparing Data (Time-Series Split)")
print("="*80)

# Remove rows with missing target or features
df_clean = df[['date', 'province', 'crop_type', 'price_per_kg', 'target_price_7d'] + available_features].copy()
df_clean = df_clean.dropna()

print(f"\n✅ Clean dataset:")
print(f"   - Rows: {len(df_clean):,}")
print(f"   - Features: {len(available_features)}")

# TIME-SERIES SPLIT (NO SHUFFLE!)
split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx].copy()
test_df = df_clean.iloc[split_idx:].copy()

print(f"\n✅ Time-series split:")
print(f"   - Train: {len(train_df):,} rows ({train_df['date'].min()} to {train_df['date'].max()})")
print(f"   - Test:  {len(test_df):,} rows ({test_df['date'].min()} to {test_df['date'].max()})")
print(f"   - ⚠️  NO SHUFFLE! Test data is strictly AFTER train data")

# Verify no data leakage (check median date instead of min/max due to multiple provinces)
train_median_date = train_df['date'].median()
test_median_date = test_df['date'].median()
print(f"   📅 Train median date: {train_median_date}")
print(f"   📅 Test median date: {test_median_date}")
if test_median_date > train_median_date:
    print(f"   ✅ Verified: Test data is generally AFTER train data")
else:
    print(f"   ⚠️  Warning: Some temporal overlap due to multiple provinces/crops")

X_train = train_df[available_features]
y_train = train_df['target_price_7d']
X_test = test_df[available_features]
y_test = test_df['target_price_7d']

# ============================================================================
# STEP 7: Baseline Models
# ============================================================================
print("\n" + "="*80)
print("📏 STEP 7: Baseline Models")
print("="*80)

# Baseline 1: Last known price (7 days ago)
baseline_last_price = test_df['price_lag_7']
baseline_mae_1 = mean_absolute_error(y_test, baseline_last_price)
baseline_rmse_1 = np.sqrt(mean_squared_error(y_test, baseline_last_price))
baseline_r2_1 = r2_score(y_test, baseline_last_price)

print(f"\n📊 Baseline 1: Last Price (7 days ago)")
print(f"   - MAE:  {baseline_mae_1:.2f}")
print(f"   - RMSE: {baseline_rmse_1:.2f}")
print(f"   - R²:   {baseline_r2_1:.4f}")

# Baseline 2: Moving average (14 days)
baseline_ma = test_df['price_ma_14']
baseline_mae_2 = mean_absolute_error(y_test, baseline_ma)
baseline_rmse_2 = np.sqrt(mean_squared_error(y_test, baseline_ma))
baseline_r2_2 = r2_score(y_test, baseline_ma)

print(f"\n📊 Baseline 2: Moving Average (14 days)")
print(f"   - MAE:  {baseline_mae_2:.2f}")
print(f"   - RMSE: {baseline_rmse_2:.2f}")
print(f"   - R²:   {baseline_r2_2:.4f}")

# ============================================================================
# STEP 8: Train Models
# ============================================================================
print("\n" + "="*80)
print("🤖 STEP 8: Training ML Models")
print("="*80)

models = {
    'Ridge': Ridge(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\n🔄 Training {name}...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Metrics
    train_mae = mean_absolute_error(y_train, y_pred_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_r2 = r2_score(y_train, y_pred_train)
    
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_r2 = r2_score(y_test, y_pred_test)
    
    results[name] = {
        'model': model,
        'train_mae': train_mae,
        'train_rmse': train_rmse,
        'train_r2': train_r2,
        'test_mae': test_mae,
        'test_rmse': test_rmse,
        'test_r2': test_r2,
        'predictions': y_pred_test
    }
    
    print(f"   ✅ {name} Results:")
    print(f"      Train - MAE: {train_mae:.2f}, RMSE: {train_rmse:.2f}, R²: {train_r2:.4f}")
    print(f"      Test  - MAE: {test_mae:.2f}, RMSE: {test_rmse:.2f}, R²: {test_r2:.4f}")
    
    # Check for overfitting
    if train_r2 - test_r2 > 0.3:
        print(f"      ⚠️  Warning: Possible overfitting (R² gap: {train_r2 - test_r2:.4f})")

# ============================================================================
# STEP 9: Model Comparison
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 9: Model Comparison")
print("="*80)

comparison_df = pd.DataFrame({
    'Model': ['Baseline (Last Price)', 'Baseline (MA-14)'] + list(results.keys()),
    'Test MAE': [baseline_mae_1, baseline_mae_2] + [r['test_mae'] for r in results.values()],
    'Test RMSE': [baseline_rmse_1, baseline_rmse_2] + [r['test_rmse'] for r in results.values()],
    'Test R²': [baseline_r2_1, baseline_r2_2] + [r['test_r2'] for r in results.values()]
})

print("\n" + comparison_df.to_string(index=False))

# Find best model
best_model_name = max(results.keys(), key=lambda k: results[k]['test_r2'])
best_model = results[best_model_name]

print(f"\n🏆 Best Model: {best_model_name}")
print(f"   - Test R²: {best_model['test_r2']:.4f}")
print(f"   - Test MAE: {best_model['test_mae']:.2f}")
print(f"   - Test RMSE: {best_model['test_rmse']:.2f}")

# ============================================================================
# STEP 10: Feature Importance (for tree-based models)
# ============================================================================
if best_model_name in ['Random Forest', 'Gradient Boosting']:
    print("\n" + "="*80)
    print("🔍 STEP 10: Feature Importance")
    print("="*80)
    
    importances = best_model['model'].feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': available_features,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    print("\n📊 Top 15 Most Important Features:")
    print(feature_importance_df.head(15).to_string(index=False))
    
    # Check for suspicious importance
    if feature_importance_df.iloc[0]['Importance'] > 0.9:
        print(f"\n⚠️  Warning: Feature '{feature_importance_df.iloc[0]['Feature']}' has very high importance ({feature_importance_df.iloc[0]['Importance']:.4f})")
        print(f"    This might indicate data leakage! Please verify.")

# ============================================================================
# STEP 11: Cross-Validation (TimeSeriesSplit)
# ============================================================================
print("\n" + "="*80)
print("🔄 STEP 11: Time-Series Cross-Validation")
print("="*80)

tscv = TimeSeriesSplit(n_splits=5)
cv_scores = []

print(f"\nPerforming 5-fold time-series CV on {best_model_name}...")

for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train), 1):
    X_cv_train, X_cv_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
    
    # Train
    cv_model = models[best_model_name].__class__(**models[best_model_name].get_params())
    cv_model.fit(X_cv_train, y_cv_train)
    
    # Validate
    y_cv_pred = cv_model.predict(X_cv_val)
    cv_r2 = r2_score(y_cv_val, y_cv_pred)
    cv_mae = mean_absolute_error(y_cv_val, y_cv_pred)
    
    cv_scores.append({'fold': fold, 'r2': cv_r2, 'mae': cv_mae})
    print(f"   Fold {fold}: R² = {cv_r2:.4f}, MAE = {cv_mae:.2f}")

cv_df = pd.DataFrame(cv_scores)
print(f"\n✅ Cross-Validation Results:")
print(f"   - Mean R²:  {cv_df['r2'].mean():.4f} (±{cv_df['r2'].std():.4f})")
print(f"   - Mean MAE: {cv_df['mae'].mean():.2f} (±{cv_df['mae'].std():.2f})")

# ============================================================================
# STEP 12: Final Evaluation
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 12: Final Evaluation")
print("="*80)

price_range = y_test.max() - y_test.min()
rmse_pct = (best_model['test_rmse'] / price_range) * 100

print(f"\n📊 Final Metrics:")
print(f"   - Test R²: {best_model['test_r2']:.4f}")
print(f"   - Test MAE: {best_model['test_mae']:.2f}")
print(f"   - Test RMSE: {best_model['test_rmse']:.2f} ({rmse_pct:.1f}% of price range)")
print(f"   - Price Range: {y_test.min():.2f} - {y_test.max():.2f}")

# Success criteria
print(f"\n✅ Success Criteria Check:")
print(f"   - R² > 0.3: {'✅ PASS' if best_model['test_r2'] > 0.3 else '❌ FAIL'} ({best_model['test_r2']:.4f})")
print(f"   - RMSE < 15% of range: {'✅ PASS' if rmse_pct < 15 else '❌ FAIL'} ({rmse_pct:.1f}%)")
print(f"   - No overfitting (R² gap < 0.3): {'✅ PASS' if abs(best_model['train_r2'] - best_model['test_r2']) < 0.3 else '❌ FAIL'}")

print("\n" + "="*80)
print("✅ Model Training Complete!")
print("="*80)

# ============================================================================
# STEP 13: Save Best Model
# ============================================================================
print("\n" + "="*80)
print("💾 STEP 13: Saving Best Model")
print("="*80)

import pickle
import json

# Save model
model_path = 'backend/models/model_c_gradient_boosting.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(best_model['model'], f)
print(f"\n✅ Model saved: {model_path}")

# Save feature list
features_path = 'backend/models/model_c_features.json'
with open(features_path, 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"✅ Features saved: {features_path}")

# Save metadata
metadata = {
    'model_name': best_model_name,
    'test_r2': float(best_model['test_r2']),
    'test_mae': float(best_model['test_mae']),
    'test_rmse': float(best_model['test_rmse']),
    'cv_mean_r2': float(cv_df['r2'].mean()),
    'cv_std_r2': float(cv_df['r2'].std()),
    'train_date_range': f"{train_df['date'].min()} to {train_df['date'].max()}",
    'test_date_range': f"{test_df['date'].min()} to {test_df['date'].max()}",
    'n_features': len(available_features),
    'trained_at': datetime.now().isoformat()
}

metadata_path = 'backend/models/model_c_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✅ Metadata saved: {metadata_path}")

# ============================================================================
# STEP 14: Hyperparameter Tuning (Optional)
# ============================================================================
print("\n" + "="*80)
print("🔧 STEP 14: Hyperparameter Tuning")
print("="*80)

from sklearn.model_selection import GridSearchCV

print("\n🎯 Goal: Beat Baseline MA-14 (R² = 0.6711) by a larger margin")
print(f"   Current GB R²: {best_model['test_r2']:.4f}")
print(f"   Improvement needed: {(best_model['test_r2'] - baseline_r2_2):.4f} → Target: > 0.05")

# Hyperparameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 7, 10],
    'learning_rate': [0.05, 0.1, 0.15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'subsample': [0.8, 0.9, 1.0]
}

print(f"\n🔍 Searching {len(param_grid['n_estimators']) * len(param_grid['max_depth']) * len(param_grid['learning_rate']) * len(param_grid['min_samples_split']) * len(param_grid['min_samples_leaf']) * len(param_grid['subsample'])} combinations...")
print("   This may take a while...")

# Use TimeSeriesSplit for CV
tscv_tuning = TimeSeriesSplit(n_splits=3)

# Grid search
gb_tuned = GridSearchCV(
    GradientBoostingRegressor(random_state=42),
    param_grid,
    cv=tscv_tuning,
    scoring='r2',
    n_jobs=-1,
    verbose=1
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
print(f"   - Test MAE:  {tuned_mae:.2f} (vs {best_model['test_mae']:.2f})")
print(f"   - Test RMSE: {tuned_rmse:.2f} (vs {best_model['test_rmse']:.2f})")
print(f"   - Test R²:   {tuned_r2:.4f} (vs {best_model['test_r2']:.4f})")

improvement = tuned_r2 - best_model['test_r2']
baseline_gap = tuned_r2 - baseline_r2_2

print(f"\n📈 Improvement Analysis:")
print(f"   - Improvement over default: {improvement:+.4f}")
print(f"   - Gap vs Baseline MA-14: {baseline_gap:.4f}")
print(f"   - Status: {'✅ SIGNIFICANT' if baseline_gap > 0.05 else '⚠️  MARGINAL'}")

# Save tuned model if better
if tuned_r2 > best_model['test_r2']:
    print(f"\n💾 Saving tuned model (better performance)...")
    
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
    print(f"\n⚠️  Tuned model not better, keeping default model")
    final_model_to_use = 'model_c_gradient_boosting.pkl'
    final_r2 = best_model['test_r2']

# ============================================================================
# STEP 15: Final Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 FINAL SUMMARY")
print("="*80)

print(f"\n📊 Model Comparison:")
print(f"   Baseline (Last Price):  R² = {baseline_r2_1:.4f}")
print(f"   Baseline (MA-14):       R² = {baseline_r2_2:.4f}")
print(f"   GB Default:             R² = {best_model['test_r2']:.4f} ({(best_model['test_r2'] - baseline_r2_2):.4f} better)")
print(f"   GB Tuned:               R² = {tuned_r2:.4f} ({(tuned_r2 - baseline_r2_2):.4f} better)")

print(f"\n🏆 Final Model to Use: {final_model_to_use}")
print(f"   - Test R²: {final_r2:.4f}")
print(f"   - Location: backend/models/{final_model_to_use}")

print(f"\n📝 Next Steps:")
print(f"   1. Update backend/model_c_wrapper.py to use {final_model_to_use}")
print(f"   2. Test the wrapper with sample data")
print(f"   3. Deploy to production")

print("\n" + "="*80)
print("✅ All Done!")
print("="*80)

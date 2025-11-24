"""
Model C - Stratified by Price Range
====================================
แก้ปัญหา Ceiling Effect ด้วยการแยก train model ต่างหากสำหรับแต่ละช่วงราคา

Strategy:
1. แบ่งพืชออกเป็น 3 กลุ่มตามราคา: ถูก, กลาง, แพง
2. Train model แยกสำหรับแต่ละกลุ่ม
3. ตอน predict ใช้ model ที่เหมาะสมกับช่วงราคา

Benefits:
✅ แต่ละ model เรียนรู้ pattern ของช่วงราคาตัวเอง
✅ ไม่มีปัญหา "ของถูกดึง loss function"
✅ แก้ปัญหา Ceiling Effect โดยตรง
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🚀 Model C - Stratified by Price Range")
print("="*80)

# ============================================================================
# Load and Prepare Data (same as before)
# ============================================================================
print("\n📊 Loading data (10% sample for testing)...")
df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df = df.sample(frac=0.1, random_state=42).copy()  # Use 10% for speed
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

# Create features
print("🔄 Creating features...")
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

# Select features
features = [
    'price_lag_7', 'price_lag_14', 'price_lag_21', 'price_lag_30',
    'price_ma_7', 'price_ma_14', 'price_ma_30',
    'price_std_7', 'price_std_14', 'price_std_30',
    'price_momentum_7d', 'price_momentum_30d'
]
available_features = [col for col in features if col in df.columns]

# Prepare data
df_clean = df[['crop_type', 'province', 'target_price_7d'] + available_features].dropna()

split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx]
test_df = df_clean.iloc[split_idx:]

print(f"✅ Train: {len(train_df):,}, Test: {len(test_df):,}")

# ============================================================================
# Define Price Ranges
# ============================================================================
print("\n" + "="*80)
print("📊 Defining Price Ranges")
print("="*80)

# Analyze price distribution
price_percentiles = train_df['target_price_7d'].quantile([0.33, 0.67])
low_threshold = price_percentiles[0.33]
high_threshold = price_percentiles[0.67]

print(f"\n📊 Price Range Thresholds:")
print(f"   Low:    < {low_threshold:.2f} baht/kg")
print(f"   Medium: {low_threshold:.2f} - {high_threshold:.2f} baht/kg")
print(f"   High:   > {high_threshold:.2f} baht/kg")

# Categorize training data
train_df['price_category'] = pd.cut(
    train_df['target_price_7d'],
    bins=[0, low_threshold, high_threshold, float('inf')],
    labels=['low', 'medium', 'high']
)

# Categorize test data
test_df['price_category'] = pd.cut(
    test_df['target_price_7d'],
    bins=[0, low_threshold, high_threshold, float('inf')],
    labels=['low', 'medium', 'high']
)

print(f"\n📊 Training Data Distribution:")
for cat in ['low', 'medium', 'high']:
    count = (train_df['price_category'] == cat).sum()
    pct = count / len(train_df) * 100
    print(f"   {cat.capitalize()}: {count:,} samples ({pct:.1f}%)")

print(f"\n📊 Test Data Distribution:")
for cat in ['low', 'medium', 'high']:
    count = (test_df['price_category'] == cat).sum()
    pct = count / len(test_df) * 100
    print(f"   {cat.capitalize()}: {count:,} samples ({pct:.1f}%)")

# ============================================================================
# Train Separate Models for Each Price Range
# ============================================================================
print("\n" + "="*80)
print("🤖 Training Separate Models")
print("="*80)

models = {}
results = {}

for category in ['low', 'medium', 'high']:
    print(f"\n🔄 Training model for {category.upper()} price range...")
    
    # Filter data for this category
    train_cat = train_df[train_df['price_category'] == category]
    test_cat = test_df[test_df['price_category'] == category]
    
    if len(train_cat) < 100:
        print(f"   ⚠️  Insufficient data ({len(train_cat)} samples), skipping...")
        continue
    
    X_train_cat = train_cat[available_features]
    y_train_cat = train_cat['target_price_7d']
    X_test_cat = test_cat[available_features]
    y_test_cat = test_cat['target_price_7d']
    
    # Train model
    model = GradientBoostingRegressor(
        n_estimators=50,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train_cat, y_train_cat)
    
    # Evaluate
    y_pred_train = model.predict(X_train_cat)
    y_pred_test = model.predict(X_test_cat)
    
    train_mae = mean_absolute_error(y_train_cat, y_pred_train)
    train_r2 = r2_score(y_train_cat, y_pred_train)
    test_mae = mean_absolute_error(y_test_cat, y_pred_test)
    test_r2 = r2_score(y_test_cat, y_pred_test)
    
    models[category] = model
    results[category] = {
        'train_samples': len(train_cat),
        'test_samples': len(test_cat),
        'train_mae': train_mae,
        'train_r2': train_r2,
        'test_mae': test_mae,
        'test_r2': test_r2,
        'predictions': y_pred_test
    }
    
    print(f"   ✅ {category.upper()} Model:")
    print(f"      Train: MAE={train_mae:.2f}, R²={train_r2:.4f}")
    print(f"      Test:  MAE={test_mae:.2f}, R²={test_r2:.4f}")

# ============================================================================
# Evaluate Combined Performance
# ============================================================================
print("\n" + "="*80)
print("📊 Combined Performance")
print("="*80)

# Combine predictions from all models
test_df['y_pred_stratified'] = np.nan

for category in ['low', 'medium', 'high']:
    if category in models:
        mask = test_df['price_category'] == category
        X_test_cat = test_df.loc[mask, available_features]
        test_df.loc[mask, 'y_pred_stratified'] = models[category].predict(X_test_cat)

# Remove rows without predictions
test_df_eval = test_df.dropna(subset=['y_pred_stratified'])

# Calculate overall metrics
y_test_all = test_df_eval['target_price_7d']
y_pred_all = test_df_eval['y_pred_stratified']

overall_mae = mean_absolute_error(y_test_all, y_pred_all)
overall_rmse = np.sqrt(mean_squared_error(y_test_all, y_pred_all))
overall_r2 = r2_score(y_test_all, y_pred_all)

print(f"\n📊 Overall Performance (Stratified Models):")
print(f"   MAE:  {overall_mae:.2f} baht/kg")
print(f"   RMSE: {overall_rmse:.2f} baht/kg")
print(f"   R²:   {overall_r2:.4f}")

# Performance by category
print(f"\n📊 Performance by Price Range:")
for category in ['low', 'medium', 'high']:
    if category in results:
        print(f"\n   {category.upper()}:")
        print(f"      Test MAE: {results[category]['test_mae']:.2f} baht/kg")
        print(f"      Test R²:  {results[category]['test_r2']:.4f}")

# ============================================================================
# Compare with Single Model
# ============================================================================
print("\n" + "="*80)
print("📊 Comparison with Single Model")
print("="*80)

# Train single model on all data
print("\n🔄 Training single model (baseline)...")
X_train_all = train_df[available_features]
y_train_all = train_df['target_price_7d']
X_test_all = test_df[available_features]
y_test_all = test_df['target_price_7d']

model_single = GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=42)
model_single.fit(X_train_all, y_train_all)

y_pred_single = model_single.predict(X_test_all)
mae_single = mean_absolute_error(y_test_all, y_pred_single)
rmse_single = np.sqrt(mean_squared_error(y_test_all, y_pred_single))
r2_single = r2_score(y_test_all, y_pred_single)

print(f"\n📊 Single Model Performance:")
print(f"   MAE:  {mae_single:.2f} baht/kg")
print(f"   RMSE: {rmse_single:.2f} baht/kg")
print(f"   R²:   {r2_single:.4f}")

print(f"\n📈 Comparison:")
print(f"   {'Metric':<10} {'Single Model':<15} {'Stratified':<15} {'Improvement':<15}")
print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
print(f"   {'MAE':<10} {mae_single:<15.2f} {overall_mae:<15.2f} {mae_single-overall_mae:+15.2f}")
print(f"   {'RMSE':<10} {rmse_single:<15.2f} {overall_rmse:<15.2f} {rmse_single-overall_rmse:+15.2f}")
print(f"   {'R²':<10} {r2_single:<15.4f} {overall_r2:<15.4f} {overall_r2-r2_single:+15.4f}")

# Check performance on expensive crops
test_df['y_pred_single'] = y_pred_single
expensive_single = test_df[test_df['target_price_7d'] > high_threshold]
expensive_stratified = test_df_eval[test_df_eval['target_price_7d'] > high_threshold]

if len(expensive_single) > 0 and len(expensive_stratified) > 0:
    mae_exp_single = mean_absolute_error(
        expensive_single['target_price_7d'],
        expensive_single['y_pred_single']
    )
    mae_exp_stratified = mean_absolute_error(
        expensive_stratified['target_price_7d'],
        expensive_stratified['y_pred_stratified']
    )
    
    r2_exp_single = r2_score(
        expensive_single['target_price_7d'],
        expensive_single['y_pred_single']
    )
    r2_exp_stratified = r2_score(
        expensive_stratified['target_price_7d'],
        expensive_stratified['y_pred_stratified']
    )
    
    print(f"\n📈 Expensive Crops (>{high_threshold:.0f} baht) Performance:")
    print(f"   {'Metric':<10} {'Single Model':<15} {'Stratified':<15} {'Improvement':<15}")
    print(f"   {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
    print(f"   {'MAE':<10} {mae_exp_single:<15.2f} {mae_exp_stratified:<15.2f} {mae_exp_single-mae_exp_stratified:+15.2f}")
    print(f"   {'R²':<10} {r2_exp_single:<15.4f} {r2_exp_stratified:<15.4f} {r2_exp_stratified-r2_exp_single:+15.4f}")

# ============================================================================
# Save Models
# ============================================================================
print("\n" + "="*80)
print("💾 Saving Models")
print("="*80)

os.makedirs('backend/models', exist_ok=True)

# Save stratified models
for category, model in models.items():
    model_path = f'backend/models/model_c_stratified_{category}.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Saved {category} model: {model_path}")

# Save thresholds
thresholds = {
    'low_threshold': float(low_threshold),
    'high_threshold': float(high_threshold),
    'categories': ['low', 'medium', 'high']
}

thresholds_path = 'backend/models/model_c_stratified_thresholds.json'
with open(thresholds_path, 'w') as f:
    json.dump(thresholds, f, indent=2)
print(f"✅ Saved thresholds: {thresholds_path}")

# Save features
features_path = 'backend/models/model_c_stratified_features.json'
with open(features_path, 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"✅ Saved features: {features_path}")

# Save metadata
metadata = {
    'model_name': 'Gradient Boosting (Stratified by Price Range)',
    'strategy': 'separate_models_per_price_range',
    'overall_test_r2': float(overall_r2),
    'overall_test_mae': float(overall_mae),
    'overall_test_rmse': float(overall_rmse),
    'single_model_r2': float(r2_single),
    'improvement_over_single': float(overall_r2 - r2_single),
    'price_ranges': {
        'low': f'< {low_threshold:.2f}',
        'medium': f'{low_threshold:.2f} - {high_threshold:.2f}',
        'high': f'> {high_threshold:.2f}'
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

metadata_path = 'backend/models/model_c_stratified_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✅ Saved metadata: {metadata_path}")

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 FINAL SUMMARY")
print("="*80)

print(f"\n✅ Stratified Approach:")
print(f"   - Trained {len(models)} separate models")
print(f"   - Overall R²: {overall_r2:.4f}")
print(f"   - Overall MAE: {overall_mae:.2f} baht/kg")

if overall_r2 > r2_single:
    improvement_pct = ((overall_r2 - r2_single) / r2_single) * 100
    print(f"\n✅ IMPROVEMENT over single model:")
    print(f"   - R² improvement: {overall_r2 - r2_single:+.4f} ({improvement_pct:+.1f}%)")
    print(f"   - Recommended approach: STRATIFIED")
else:
    print(f"\n⚠️  Single model performs better")
    print(f"   - Consider using single model instead")

print("\n📝 Next Steps:")
print("   1. If stratified is better, update model_c_wrapper.py")
print("   2. Test with full dataset (not just 10% sample)")
print("   3. Deploy to production")

print("\n" + "="*80)
print("✅ All Done!")
print("="*80)

"""
Train Model C - Final Version (Stratified Models)
==================================================
Train stratified models on FULL dataset (100%)
This will take longer but give better results
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
print("🚀 Training Model C - Final Version (Stratified Models)")
print("="*80)
print("\n⚠️  This will train on FULL dataset (100%)")
print("   Estimated time: 10-15 minutes")
print("   Press Ctrl+C to cancel\n")

# ============================================================================
# Load and Prepare Data
# ============================================================================
print("📊 Loading FULL dataset...")
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
print("\n📊 Defining Price Ranges...")
price_percentiles = train_df['target_price_7d'].quantile([0.33, 0.67])
low_threshold = price_percentiles[0.33]
high_threshold = price_percentiles[0.67]

print(f"   Low:    < {low_threshold:.2f} baht/kg")
print(f"   Medium: {low_threshold:.2f} - {high_threshold:.2f} baht/kg")
print(f"   High:   > {high_threshold:.2f} baht/kg")

# Categorize data
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
# Train Models
# ============================================================================
print("\n🤖 Training Separate Models...")
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
    
    # Train with more estimators for better performance
    model = GradientBoostingRegressor(
        n_estimators=200,  # More trees
        max_depth=7,       # Deeper trees
        learning_rate=0.1,
        random_state=42,
        verbose=1
    )
    
    print(f"   Training on {len(train_cat):,} samples...")
    model.fit(X_train_cat, y_train_cat)
    
    # Evaluate
    y_pred_test = model.predict(X_test_cat)
    test_mae = mean_absolute_error(y_test_cat, y_pred_test)
    test_r2 = r2_score(y_test_cat, y_pred_test)
    
    models[category] = model
    results[category] = {
        'test_mae': test_mae,
        'test_r2': test_r2
    }
    
    print(f"   ✅ Test MAE: {test_mae:.2f}, R²: {test_r2:.4f}")

# ============================================================================
# Evaluate Combined Performance
# ============================================================================
print("\n📊 Evaluating Combined Performance...")
test_df['y_pred_stratified'] = np.nan

for category in ['low', 'medium', 'high']:
    if category in models:
        mask = test_df['price_category'] == category
        X_test_cat = test_df.loc[mask, available_features]
        test_df.loc[mask, 'y_pred_stratified'] = models[category].predict(X_test_cat)

test_df_eval = test_df.dropna(subset=['y_pred_stratified'])

overall_mae = mean_absolute_error(test_df_eval['target_price_7d'], test_df_eval['y_pred_stratified'])
overall_rmse = np.sqrt(mean_squared_error(test_df_eval['target_price_7d'], test_df_eval['y_pred_stratified']))
overall_r2 = r2_score(test_df_eval['target_price_7d'], test_df_eval['y_pred_stratified'])

print(f"\n✅ Overall Performance:")
print(f"   MAE:  {overall_mae:.2f} baht/kg")
print(f"   RMSE: {overall_rmse:.2f} baht/kg")
print(f"   R²:   {overall_r2:.4f}")

# ============================================================================
# Save Models
# ============================================================================
print("\n💾 Saving Models...")
os.makedirs('backend/models', exist_ok=True)

for category, model in models.items():
    model_path = f'backend/models/model_c_stratified_{category}_final.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Saved: {model_path}")

# Save thresholds
thresholds = {
    'low_threshold': float(low_threshold),
    'high_threshold': float(high_threshold),
    'categories': ['low', 'medium', 'high']
}

with open('backend/models/model_c_stratified_thresholds_final.json', 'w') as f:
    json.dump(thresholds, f, indent=2)
print(f"✅ Saved: model_c_stratified_thresholds_final.json")

# Save features
with open('backend/models/model_c_stratified_features_final.json', 'w') as f:
    json.dump(available_features, f, indent=2)
print(f"✅ Saved: model_c_stratified_features_final.json")

# Save metadata
metadata = {
    'model_name': 'Gradient Boosting (Stratified by Price Range) - FINAL',
    'strategy': 'separate_models_per_price_range',
    'dataset_size': len(df_clean),
    'train_size': len(train_df),
    'test_size': len(test_df),
    'overall_test_r2': float(overall_r2),
    'overall_test_mae': float(overall_mae),
    'overall_test_rmse': float(overall_rmse),
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
    'hyperparameters': {
        'n_estimators': 200,
        'max_depth': 7,
        'learning_rate': 0.1
    },
    'trained_at': datetime.now().isoformat()
}

with open('backend/models/model_c_stratified_metadata_final.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"✅ Saved: model_c_stratified_metadata_final.json")

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "="*80)
print("🎉 TRAINING COMPLETE!")
print("="*80)

print(f"\n✅ Models trained on {len(df_clean):,} samples")
print(f"✅ Overall R²: {overall_r2:.4f}")
print(f"✅ Overall MAE: {overall_mae:.2f} baht/kg")

print(f"\n📊 Performance by Price Range:")
for cat in ['low', 'medium', 'high']:
    if cat in results:
        print(f"   {cat.upper()}: R²={results[cat]['test_r2']:.4f}, MAE={results[cat]['test_mae']:.2f}")

print(f"\n📝 Next Steps:")
print(f"   1. Update backend/model_c_wrapper.py to use these models")
print(f"   2. Test with: python test_model_c.py")
print(f"   3. Deploy to production")

print("\n" + "="*80)
print("✅ All Done!")
print("="*80)

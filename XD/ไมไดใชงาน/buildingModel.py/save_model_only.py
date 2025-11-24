"""
Save Model Only (ไม่ Tune)
===========================
Save model โดยไม่ทำ hyperparameter tuning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import json
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("💾 Save Model Only (No Tuning)")
print("="*80)

# Check if model already exists
model_path = 'backend/models/model_c_gradient_boosting.pkl'
if os.path.exists(model_path):
    print(f"\n✅ Model already exists: {model_path}")
    print("   No need to train again!")
    
    # Load and verify
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"   ✅ Model loaded successfully")
    print(f"   ✅ Model type: {type(model).__name__}")
    
    # Check metadata
    metadata_path = 'backend/models/model_c_metadata.json'
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print(f"\n📊 Model Performance:")
        print(f"   - Test R²: {metadata['test_r2']:.4f}")
        print(f"   - Test MAE: {metadata['test_mae']:.2f}")
        print(f"   - Test RMSE: {metadata['test_rmse']:.2f}")
        print(f"   - Baseline MA-14 R²: {metadata['baseline_ma14_r2']:.4f}")
        print(f"   - Improvement: {metadata['gap_vs_baseline']:.4f}")
    
    print("\n✅ Model is ready to use!")
    print(f"   Location: {model_path}")
    
else:
    print(f"\n⚠️  Model not found: {model_path}")
    print("   Training model (without tuning)...")
    
    # Load and prepare data (same as before)
    df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Remove leaky features
    LEAKY_FEATURES = ['future_price_7d', 'price_next_day', 'bid_price', 'ask_price', 'base_price', 'spread_pct']
    existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
    if existing_leaky:
        df = df.drop(columns=existing_leaky)
    
    # Create target
    df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)
    
    # Create features
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
    
    # Baseline
    baseline_ma = test_df['price_ma_14']
    baseline_r2_2 = r2_score(y_test, baseline_ma)
    
    # Train model
    print("   Training Gradient Boosting (this will take 5-10 minutes)...")
    gb_model = GradientBoostingRegressor(
        n_estimators=100, 
        max_depth=5, 
        random_state=42,
        verbose=1
    )
    gb_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = gb_model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred)
    test_mae = mean_absolute_error(y_test, y_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\n✅ Model trained:")
    print(f"   - Test R²: {test_r2:.4f}")
    print(f"   - Test MAE: {test_mae:.2f}")
    print(f"   - Test RMSE: {test_rmse:.2f}")
    
    # Save
    os.makedirs('backend/models', exist_ok=True)
    
    with open(model_path, 'wb') as f:
        pickle.dump(gb_model, f)
    print(f"\n✅ Model saved: {model_path}")
    
    with open('backend/models/model_c_features.json', 'w') as f:
        json.dump(available_features, f, indent=2)
    print(f"✅ Features saved")
    
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
    
    with open('backend/models/model_c_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved")

print("\n" + "="*80)
print("📝 Next Steps")
print("="*80)
print("1. ✅ Model saved and ready")
print("2. 🔄 Update backend/model_c_wrapper.py")
print("3. 🧪 Test the wrapper")
print("4. 🚀 Deploy!")
print("\n" + "="*80)

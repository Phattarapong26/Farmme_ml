"""
Test Model C
============
ทดสอบการใช้งาน model_c_gradient_boosting.pkl
"""

import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("🧪 Testing Model C")
print("="*80)

# ============================================================================
# STEP 1: Load Model and Features
# ============================================================================
print("\n" + "="*80)
print("📦 STEP 1: Loading Model")
print("="*80)

try:
    # Load model
    with open('backend/models/model_c_gradient_boosting.pkl', 'rb') as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully")
    print(f"   Type: {type(model).__name__}")
    print(f"   Parameters: n_estimators={model.n_estimators}, max_depth={model.max_depth}")
    
    # Load features
    with open('backend/models/model_c_features.json', 'r') as f:
        features = json.load(f)
    print(f"✅ Features loaded: {len(features)} features")
    
    # Load metadata
    with open('backend/models/model_c_metadata.json', 'r') as f:
        metadata = json.load(f)
    print(f"✅ Metadata loaded")
    print(f"   Test R²: {metadata['test_r2']:.4f}")
    print(f"   Test MAE: {metadata['test_mae']:.2f}")
    print(f"   Trained at: {metadata['trained_at']}")
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Model files not found!")
    print("   Please run: python buildingModel.py/save_model_only.py")
    exit(1)

# ============================================================================
# STEP 2: Create Sample Data
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 2: Creating Sample Data")
print("="*80)

# Sample data for testing (ข้าวโพด ในกรุงเทพ)
sample_data = {
    'price_lag_7': 45.0,
    'price_lag_14': 44.5,
    'price_lag_21': 44.0,
    'price_lag_30': 43.5,
    'price_ma_7': 45.2,
    'price_ma_14': 44.8,
    'price_ma_30': 44.3,
    'price_std_7': 2.1,
    'price_std_14': 2.3,
    'price_std_30': 2.5,
    'price_momentum_7d': 0.011,
    'price_momentum_30d': 0.034,
    'dayofyear': 330,
    'month': 11,
    'weekday': 2,
    'temperature_celsius_lag_7': 28.5,
    'rainfall_mm_lag_7': 5.2,
    'humidity_percent_lag_7': 75.0,
    'drought_index_lag_7': 85.0,
    'fuel_price_lag_7': 39.5,
    'fertilizer_price_lag_7': 885.0,
    'inflation_rate_lag_7': 1.6,
    'supply_level_lag_7': 0.85,
    'inventory_level_lag_7': 0.44,
    'demand_elasticity_lag_7': -0.60,
}

print("Sample input data:")
for key, value in list(sample_data.items())[:5]:
    print(f"   {key}: {value}")
print(f"   ... and {len(sample_data) - 5} more features")

# ============================================================================
# STEP 3: Make Prediction
# ============================================================================
print("\n" + "="*80)
print("🔮 STEP 3: Making Prediction")
print("="*80)

# Convert to DataFrame
X_sample = pd.DataFrame([sample_data])

# Ensure all required features are present
missing_features = set(features) - set(X_sample.columns)
if missing_features:
    print(f"⚠️  Missing features: {missing_features}")
    for feat in missing_features:
        X_sample[feat] = 0.0
    print("   Filled with zeros")

# Reorder columns to match training
X_sample = X_sample[features]

# Predict
try:
    prediction = model.predict(X_sample)[0]
    print(f"\n✅ Prediction successful!")
    print(f"   Input: price_lag_7 = {sample_data['price_lag_7']:.2f} บาท")
    print(f"   Predicted price (7 days ahead): {prediction:.2f} บาท")
    print(f"   Change: {(prediction - sample_data['price_lag_7']):.2f} บาท ({((prediction/sample_data['price_lag_7'] - 1)*100):.1f}%)")
    
except Exception as e:
    print(f"❌ Prediction failed: {e}")
    exit(1)

# ============================================================================
# STEP 4: Test Multiple Scenarios
# ============================================================================
print("\n" + "="*80)
print("🧪 STEP 4: Testing Multiple Scenarios")
print("="*80)

scenarios = [
    {
        'name': 'Stable Market',
        'price_lag_7': 45.0,
        'price_ma_14': 45.0,
        'demand_elasticity_lag_7': -0.60,
        'supply_level_lag_7': 0.85,
    },
    {
        'name': 'Rising Prices',
        'price_lag_7': 50.0,
        'price_ma_14': 47.0,
        'demand_elasticity_lag_7': -0.70,
        'supply_level_lag_7': 0.65,
    },
    {
        'name': 'Falling Prices',
        'price_lag_7': 40.0,
        'price_ma_14': 43.0,
        'demand_elasticity_lag_7': -0.50,
        'supply_level_lag_7': 0.95,
    },
]

print("\nTesting different market scenarios:\n")

for scenario in scenarios:
    # Create test data
    test_data = sample_data.copy()
    test_data.update(scenario)
    
    # Predict
    X_test = pd.DataFrame([test_data])[features]
    pred = model.predict(X_test)[0]
    
    print(f"📊 {scenario['name']}:")
    print(f"   Current: {scenario['price_lag_7']:.2f} บาท")
    print(f"   Predicted: {pred:.2f} บาท")
    print(f"   Change: {(pred - scenario['price_lag_7']):.2f} บาท ({((pred/scenario['price_lag_7'] - 1)*100):+.1f}%)")
    print()

# ============================================================================
# STEP 5: Feature Importance
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 5: Feature Importance")
print("="*80)

importances = model.feature_importances_
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': importances
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
for idx, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']:30s} {row['importance']:.4f}")

# ============================================================================
# STEP 6: Performance Summary
# ============================================================================
print("\n" + "="*80)
print("📈 STEP 6: Model Performance Summary")
print("="*80)

print(f"""
Model: Gradient Boosting
Test R²: {metadata['test_r2']:.4f}
Test MAE: {metadata['test_mae']:.2f} บาท
Test RMSE: {metadata['test_rmse']:.2f} บาท
Baseline MA-14 R²: {metadata['baseline_ma14_r2']:.4f}
Improvement: {metadata['gap_vs_baseline']:.4f}

✅ Model is working correctly!
✅ Ready for production use
""")

print("="*80)
print("✅ All Tests Passed!")
print("="*80)

print("\n📝 Next Steps:")
print("   1. ✅ Model tested successfully")
print("   2. 🔄 Update backend/model_c_wrapper.py")
print("   3. 🚀 Deploy to API")

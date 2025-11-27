#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Test: Algorithm Comparison
Tests if the 3-algorithm comparison works correctly
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

print("="*80)
print("🧪 ALGORITHM COMPARISON TEST")
print("="*80)

# Create synthetic data
print("\n📊 Creating synthetic test data...")
np.random.seed(42)
n_samples = 1000

X_train = pd.DataFrame({
    'price_lag_7': np.random.uniform(20, 80, n_samples),
    'price_ma_7': np.random.uniform(20, 80, n_samples),
    'price_std_7': np.random.uniform(1, 10, n_samples),
    'month': np.random.randint(1, 13, n_samples),
    'dayofyear': np.random.randint(1, 366, n_samples)
})

# Target = weighted combination of features + noise
y_train = (
    0.7 * X_train['price_lag_7'] + 
    0.2 * X_train['price_ma_7'] + 
    0.1 * X_train['price_std_7'] +
    np.random.normal(0, 3, n_samples)
)

X_test = pd.DataFrame({
    'price_lag_7': np.random.uniform(20, 80, 200),
    'price_ma_7': np.random.uniform(20, 80, 200),
    'price_std_7': np.random.uniform(1, 10, 200),
    'month': np.random.randint(1, 13, 200),
    'dayofyear': np.random.randint(1, 366, 200)
})

y_test = (
    0.7 * X_test['price_lag_7'] + 
    0.2 * X_test['price_ma_7'] + 
    0.1 * X_test['price_std_7'] +
    np.random.normal(0, 3, 200)
)

print(f"✅ Train: {len(X_train)} samples, Test: {len(X_test)} samples")

# Test algorithms
algorithms = {
    'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=100, random_state=42),
    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
}

if XGBOOST_AVAILABLE:
    algorithms['XGBoost'] = xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
else:
    print("\n⚠️  XGBoost not available (install with: pip install xgboost)")

print("\n" + "="*80)
print("🤖 TESTING ALGORITHMS")
print("="*80)

results = {}

for name, model in algorithms.items():
    print(f"\n🔄 Testing {name}...")
    
    try:
        import time
        start = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start
        
        start = time.time()
        y_pred = model.predict(X_test)
        predict_time = time.time() - start
        
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'mae': mae,
            'r2': r2,
            'train_time': train_time,
            'predict_time': predict_time
        }
        
        print(f"   ✅ MAE: {mae:.2f}, R²: {r2:.4f}")
        print(f"   ⏱️  Train: {train_time:.3f}s, Predict: {predict_time:.3f}s")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")

# Show comparison
print("\n" + "="*80)
print("📊 COMPARISON RESULTS")
print("="*80)
print(f"\n{'Algorithm':<25} {'MAE':>10} {'R²':>10} {'Train(s)':>12} {'Predict(s)':>12}")
print("-" * 75)

for name, metrics in results.items():
    print(f"{name:<25} "
          f"{metrics['mae']:>10.2f} "
          f"{metrics['r2']:>10.4f} "
          f"{metrics['train_time']:>12.3f} "
          f"{metrics['predict_time']:>12.3f}")

# Select best
if results:
    best = min(results.items(), key=lambda x: x[1]['mae'])
    print("\n" + "="*80)
    print(f"🏆 WINNER: {best[0]}")
    print("="*80)
    print(f"   MAE: {best[1]['mae']:.2f}")
    print(f"   R²:  {best[1]['r2']:.4f}")
    print("\n✅ Algorithm comparison working correctly!")
else:
    print("\n❌ No algorithms tested successfully")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
print("\n💡 Next step: Run the full training script:")
print("   python buildingModel.py/train_model_c_v8_improved.py")

"""
Check Model C Version in Production
"""

import pickle

# Check production model
model_path = "REMEDIATION_PRODUCTION/models_production/model_c_price_forecast.pkl"

with open(model_path, 'rb') as f:
    model_data = pickle.load(f)

print("\n" + "="*80)
print("MODEL C PRODUCTION VERSION CHECK".center(80))
print("="*80)

print(f"\nModel Path: {model_path}")
print(f"\nModel Info:")
print(f"   Name: {model_data['model_name']}")
print(f"   Version: {model_data['version']}")
print(f"   Features: {len(model_data['feature_names'])}")
print(f"   Trained: {model_data['trained_date']}")
print(f"   Dataset Size: {model_data['dataset_size']:,}")
print(f"   Split Type: {model_data['split_type']}")

print(f"\nTest Metrics:")
print(f"   R2:   {model_data['metrics']['test']['r2']:.4f}")
print(f"   RMSE: {model_data['metrics']['test']['rmse']:.2f} baht/kg")
print(f"   MAE:  {model_data['metrics']['test']['mae']:.2f} baht/kg")
print(f"   MAPE: {model_data['metrics']['test']['mape']:.2f}%")

if 'features_included' in model_data:
    print(f"\nFeatures Included:")
    for feat in model_data['features_included']:
        print(f"   + {feat}")

if 'features_excluded' in model_data:
    print(f"\nFeatures Excluded:")
    for feat in model_data['features_excluded']:
        print(f"   - {feat}")

if 'note' in model_data:
    print(f"\nNote: {model_data['note']}")

# Check for price lag features
price_lag_features = [f for f in model_data['feature_names'] if 'price_per_kg' in f and ('lag' in f or 'rolling' in f or 'momentum' in f)]

print(f"\nPrice Lag Features: {len(price_lag_features)}")
if price_lag_features:
    print("   Sample:")
    for feat in price_lag_features[:5]:
        print(f"      - {feat}")

# Check for overfitting features
overfitting_features = [f for f in model_data['feature_names'] if any(x in f for x in ['bid_price', 'ask_price', 'base_price', 'spread_pct'])]

print(f"\nOverfitting Features: {len(overfitting_features)}")
if overfitting_features:
    print("   WARNING: Found overfitting features!")
    for feat in overfitting_features:
        print(f"      - {feat}")
else:
    print("   OK: No overfitting features found")

print("\n" + "="*80)
if model_data['version'] == '2.0_proper_time_series' and len(price_lag_features) > 0 and len(overfitting_features) == 0:
    print("STATUS: CORRECT VERSION - READY FOR PRODUCTION".center(80))
else:
    print("STATUS: NEEDS UPDATE".center(80))
print("="*80)

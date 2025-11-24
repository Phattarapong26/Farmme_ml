#!/usr/bin/env python3
"""Check what features Model B was trained with"""

import pickle
import sys
from pathlib import Path

# Add REMEDIATION_PRODUCTION to path
sys.path.insert(0, str(Path(__file__).parent / "REMEDIATION_PRODUCTION"))

model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_b_logistic.pkl")

with open(model_path, 'rb') as f:
    model_data = pickle.load(f)

print("\n" + "="*80)
print("MODEL B - TRAINED FEATURES")
print("="*80)

if hasattr(model_data, 'model'):
    model = model_data.model
    scaler = model_data.scaler
else:
    model = model_data
    scaler = None

print(f"\nModel type: {type(model)}")

if hasattr(model, 'feature_names_in_'):
    print(f"\nFeatures trained ({len(model.feature_names_in_)}):")
    for i, feat in enumerate(model.feature_names_in_, 1):
        print(f"  {i}. {feat}")
else:
    print("\n⚠️ No feature_names_in_ attribute")

if scaler and hasattr(scaler, 'feature_names_in_'):
    print(f"\nScaler features ({len(scaler.feature_names_in_)}):")
    for i, feat in enumerate(scaler.feature_names_in_, 1):
        print(f"  {i}. {feat}")

print("\n" + "="*80)

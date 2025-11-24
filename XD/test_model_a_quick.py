# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path('backend')))

from model_a_wrapper import model_a_wrapper

print("=" * 60)
print("Model A Quick Test")
print("=" * 60)
print(f"Model Loaded: {model_a_wrapper.model_loaded}")
print(f"Model Type: {type(model_a_wrapper.model).__name__}")
print(f"Model Path: {model_a_wrapper.model_path}")
if hasattr(model_a_wrapper, 'n_features'):
    print(f"Features: {model_a_wrapper.n_features}")

if model_a_wrapper.model_loaded:
    print("\nTesting get_recommendations...")
    result = model_a_wrapper.get_recommendations(
        province="เชียงใหม่",
        soil_type="ดินร่วน",
        water_availability="น้ำฝน"
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Model Used: {result.get('model_used')}")
    print(f"Recommendations: {len(result.get('recommendations', []))}")
    
    if result.get('recommendations'):
        print("\nTop 3:")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"  {i}. {rec['crop_type']} (Score: {rec['suitability_score']:.2f}, ROI: {rec.get('predicted_roi', 'N/A')}%)")
    
    print("\nModel A is READY!")
else:
    print("\nModel A NOT loaded!")

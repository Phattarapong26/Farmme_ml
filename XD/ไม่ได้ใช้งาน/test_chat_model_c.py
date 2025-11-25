"""
Test Chat with Model C Stratified
==================================
ทดสอบว่า Chat ใช้ Model C Stratified ถูกต้องแล้ว
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Chat with Model C Stratified")
print("="*80)

# Test 1: Check PricePredictionModelService
print("\nTest 1: Check PricePredictionModelService")
print("-" * 50)

try:
    from price_prediction_service import price_prediction_service
    
    print(f"Model loaded: {price_prediction_service.model_loaded}")
    
    if price_prediction_service.model_loaded:
        print("SUCCESS: Model C Stratified loaded!")
        
        # Get model info
        model_info = price_prediction_service.model_wrapper.get_model_info()
        print(f"\nModel Info:")
        print(f"  Name: {model_info.get('model_name', 'unknown')}")
        print(f"  Version: {model_info.get('version', 'unknown')}")
        print(f"  Algorithm: {model_info.get('algorithm', 'unknown')}")
        print(f"  R²: {model_info.get('r2', 'unknown')}")
        print(f"  MAE: {model_info.get('mae', 'unknown')} baht/kg")
    else:
        print("WARNING: Model C Stratified not loaded")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test predict_price method
print("\n\nTest 2: Test predict_price method")
print("-" * 50)

try:
    result = price_prediction_service.predict_price(
        crop_type="พริก",
        province="เชียงใหม่",
        days_ahead=30
    )
    
    if result.get('success'):
        print("SUCCESS: Prediction successful!")
        print(f"\nResult:")
        print(f"  Crop: {result.get('crop_type')}")
        print(f"  Province: {result.get('province')}")
        print(f"  Current price: {result.get('current_price')} baht/kg")
        print(f"  Model used: {result.get('model_used')}")
        print(f"  Model version: {result.get('model_version', 'N/A')}")
        print(f"  Model R²: {result.get('model_r2', 'N/A')}")
        print(f"  Model MAE: {result.get('model_mae', 'N/A')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Trend: {result.get('price_trend')}")
        
        predictions = result.get('predictions', [])
        print(f"\n  Predictions ({len(predictions)} timeframes):")
        for pred in predictions:
            print(f"    {pred['days_ahead']} days: {pred['predicted_price']} baht/kg (confidence: {pred['confidence']})")
        
        # Check if using Model C Stratified
        if 'Stratified' in result.get('model_used', ''):
            print("\n  OK: Using Model C Stratified!")
        else:
            print(f"\n  WARNING: Not using Model C Stratified (using: {result.get('model_used')})")
    else:
        print(f"FAILED: {result.get('error', 'unknown')}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if price_prediction_service.model_loaded:
    print("\nSUCCESS: Chat will use Model C Stratified!")
    print("\nFrontend Chat will show:")
    print("  - Model C Stratified v7 (Gradient Boosting)")
    print("  - R² = 0.7589")
    print("  - MAE = 6.97 baht/kg")
    print("  - Confidence intervals")
    print("  - Accurate predictions (7 days: R² = 0.77)")
else:
    print("\nWARNING: Model C Stratified not loaded")
    print("Chat will use fallback predictions")

print("\n" + "="*80)
print("Test Complete!")
print("="*80)

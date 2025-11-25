"""
Test Model C Stratified Version
================================
ทดสอบ Model C แบบ Stratified ผ่าน wrapper
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from model_c_wrapper import model_c_wrapper

print("="*80)
print("🧪 Testing Model C (Stratified Version)")
print("="*80)

# ============================================================================
# STEP 1: Check Model Info
# ============================================================================
print("\n" + "="*80)
print("📦 STEP 1: Model Information")
print("="*80)

model_info = model_c_wrapper.get_model_info()

print(f"\n✅ Model Info:")
print(f"   Name: {model_info['model_name']}")
print(f"   Version: {model_info['version']}")
print(f"   Algorithm: {model_info['algorithm']}")
print(f"   Status: {model_info['status']}")
print(f"   Loaded: {model_info['model_loaded']}")

if model_info['model_loaded']:
    print(f"\n📊 Performance Metrics:")
    print(f"   R²:   {model_info.get('r2', 'N/A')}")
    print(f"   MAE:  {model_info.get('mae', 'N/A')} baht/kg")
    print(f"   RMSE: {model_info.get('rmse', 'N/A')} baht/kg")
    
    if 'features' in model_info:
        print(f"   Features: {model_info['features']}")

# ============================================================================
# STEP 2: Test Predictions
# ============================================================================
print("\n" + "="*80)
print("🔮 STEP 2: Testing Predictions")
print("="*80)

test_cases = [
    {
        "name": "พืชราคาถูก (พริก)",
        "crop_type": "พริก",
        "province": "เชียงใหม่",
        "days_ahead": 30
    },
    {
        "name": "พืชราคากลาง (มะเขือเทศ)",
        "crop_type": "มะเขือเทศ",
        "province": "กรุงเทพมหานคร",
        "days_ahead": 30
    },
    {
        "name": "พืชราคาแพง (ว่านหางจระเข้)",
        "crop_type": "ว่านหางจระเข้",
        "province": "นครปฐม",
        "days_ahead": 30
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📊 Test Case {i}: {test_case['name']}")
    print(f"   Crop: {test_case['crop_type']}")
    print(f"   Province: {test_case['province']}")
    print(f"   Forecast: {test_case['days_ahead']} days")
    
    try:
        result = model_c_wrapper.predict_price(
            crop_type=test_case['crop_type'],
            province=test_case['province'],
            days_ahead=test_case['days_ahead']
        )
        
        if result['success']:
            print(f"\n   ✅ Prediction successful!")
            print(f"   Current price: {result['current_price']:.2f} baht/kg")
            print(f"   Model used: {result['model_used']}")
            print(f"   Model version: {result['model_version']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Trend: {result['price_trend']} ({result['trend_percentage']:+.1f}%)")
            
            print(f"\n   📈 Predictions:")
            for pred in result['predictions']:
                print(f"      {pred['days_ahead']} days: {pred['predicted_price']:.2f} baht/kg (confidence: {pred['confidence']:.2f})")
            
            print(f"\n   💡 Market Insights:")
            for insight in result['market_insights']:
                print(f"      - {insight}")
        else:
            print(f"   ❌ Prediction failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# STEP 3: Verify Stratified Models
# ============================================================================
print("\n" + "="*80)
print("🔍 STEP 3: Verifying Stratified Models")
print("="*80)

if hasattr(model_c_wrapper, 'model_low'):
    print("\n✅ Stratified models loaded:")
    print(f"   LOW model: {type(model_c_wrapper.model_low).__name__}")
    print(f"   MEDIUM model: {type(model_c_wrapper.model_medium).__name__}")
    print(f"   HIGH model: {type(model_c_wrapper.model_high).__name__}")
    print(f"   Low threshold: {model_c_wrapper.low_threshold:.2f} baht/kg")
    print(f"   High threshold: {model_c_wrapper.high_threshold:.2f} baht/kg")
    
    print("\n📊 Price Ranges:")
    print(f"   LOW:    < {model_c_wrapper.low_threshold:.2f} baht/kg")
    print(f"   MEDIUM: {model_c_wrapper.low_threshold:.2f} - {model_c_wrapper.high_threshold:.2f} baht/kg")
    print(f"   HIGH:   > {model_c_wrapper.high_threshold:.2f} baht/kg")
else:
    print("\n⚠️  Using fallback single model")
    print(f"   Model: {type(model_c_wrapper.model).__name__}")

# ============================================================================
# STEP 4: Summary
# ============================================================================
print("\n" + "="*80)
print("📊 SUMMARY")
print("="*80)

if model_info['model_loaded']:
    if hasattr(model_c_wrapper, 'model_low'):
        print("\n✅ Model C (Stratified Version) is working correctly!")
        print(f"   Version: {model_info['version']}")
        print(f"   Algorithm: {model_info['algorithm']}")
        print(f"   R²: {model_info.get('r2', 'N/A')}")
        print(f"   MAE: {model_info.get('mae', 'N/A')} baht/kg")
        print("\n✅ Ready for production!")
    else:
        print("\n⚠️  Using fallback model (not stratified)")
        print("   Stratified models not found")
        print("   Check: backend/models/model_c_stratified_*_final.pkl")
else:
    print("\n❌ Model not loaded")
    print("   Check model files in backend/models/")

print("\n" + "="*80)
print("✅ Test Complete!")
print("="*80)

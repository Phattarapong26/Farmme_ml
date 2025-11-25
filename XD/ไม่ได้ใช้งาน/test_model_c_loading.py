"""
Test Model C Stratified Loading
================================
ทดสอบว่า Model C Stratified โหลดได้หรือไม่
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("🧪 Testing Model C Stratified Loading")
print("="*80)

# Test 1: Import model_c_wrapper
print("\n📦 Test 1: Import model_c_wrapper")
print("-" * 50)

try:
    from model_c_wrapper import model_c_wrapper
    print("✅ model_c_wrapper imported successfully")
except Exception as e:
    print(f"❌ Failed to import model_c_wrapper: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Check if models are loaded
print("\n🔍 Test 2: Check Model Loading Status")
print("-" * 50)

print(f"Model loaded: {model_c_wrapper.model_loaded}")

if model_c_wrapper.model_loaded:
    print("✅ Model C Stratified loaded successfully!")
    
    # Get model info
    model_info = model_c_wrapper.get_model_info()
    print(f"\n📊 Model Information:")
    print(f"   Name: {model_info.get('model_name', 'unknown')}")
    print(f"   Version: {model_info.get('version', 'unknown')}")
    print(f"   Algorithm: {model_info.get('algorithm', 'unknown')}")
    print(f"   R²: {model_info.get('r2', 'unknown')}")
    print(f"   MAE: {model_info.get('mae', 'unknown')} baht/kg")
    
    # Check stratified models
    print(f"\n🎯 Stratified Models:")
    print(f"   LOW model: {'✅ Loaded' if model_c_wrapper.model_low else '❌ Not loaded'}")
    print(f"   MEDIUM model: {'✅ Loaded' if model_c_wrapper.model_medium else '❌ Not loaded'}")
    print(f"   HIGH model: {'✅ Loaded' if model_c_wrapper.model_high else '❌ Not loaded'}")
    
else:
    print("❌ Model C Stratified NOT loaded")
    print("\n🔍 Checking model files...")
    
    models_dir = backend_dir / "models"
    print(f"   Models directory: {models_dir}")
    print(f"   Directory exists: {models_dir.exists()}")
    
    if models_dir.exists():
        print(f"\n📁 Files in models directory:")
        for file in models_dir.iterdir():
            print(f"      - {file.name}")
    
    print("\n❌ Model files missing or corrupted!")
    print("   Please check:")
    print("   1. backend/models/model_c_stratified_low.pkl")
    print("   2. backend/models/model_c_stratified_medium.pkl")
    print("   3. backend/models/model_c_stratified_high.pkl")

# Test 3: Test prediction
print("\n🔮 Test 3: Test Prediction")
print("-" * 50)

if model_c_wrapper.model_loaded:
    try:
        result = model_c_wrapper.predict_price(
            crop_type="พริก",
            province="เชียงใหม่",
            days_ahead=7
        )
        
        if result['success']:
            print("✅ Prediction successful!")
            print(f"   Current price: {result.get('current_price', 'N/A')} baht/kg")
            print(f"   Predictions: {len(result.get('predictions', []))} days")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Trend: {result.get('price_trend', 'N/A')}")
        else:
            print(f"❌ Prediction failed: {result.get('error', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  Skipping prediction test (model not loaded)")

# Summary
print("\n" + "="*80)
print("📊 SUMMARY")
print("="*80)

if model_c_wrapper.model_loaded:
    print("\n✅ SUCCESS: Model C Stratified is ready!")
    print("\n📝 Next Steps:")
    print("   1. ✅ Model C Stratified loaded")
    print("   2. 🔄 Restart backend server")
    print("   3. 🔄 Test API endpoint: /api/v2/model/predict-price-forecast")
    print("   4. 🔄 Check frontend - should show 'Model C Stratified'")
else:
    print("\n❌ FAILED: Model C Stratified not loaded")
    print("\n📝 Action Required:")
    print("   1. Check if model files exist in backend/models/")
    print("   2. Re-train Model C Stratified if needed")
    print("   3. Verify file permissions")

print("\n" + "="*80)
print("✅ Test Complete!")
print("="*80)

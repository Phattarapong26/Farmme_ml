"""
Test Model C Wrapper
====================
ทดสอบการใช้งาน wrapper กับ Model C ใหม่
"""

import sys
sys.path.append('backend')

from model_c_wrapper import model_c_wrapper

print("="*80)
print("🧪 Testing Model C Wrapper")
print("="*80)

# Test 1: Get model info
print("\n" + "="*80)
print("📊 Test 1: Get Model Info")
print("="*80)

info = model_c_wrapper.get_model_info()
print("\nModel Information:")
for key, value in info.items():
    print(f"   {key}: {value}")

# Test 2: Make prediction
print("\n" + "="*80)
print("🔮 Test 2: Make Prediction")
print("="*80)

try:
    result = model_c_wrapper.predict_price(
        crop_type="พริก",
        province="กรุงเทพมหานคร",
        days_ahead=30
    )
    
    if result["success"]:
        print("\n✅ Prediction successful!")
        print(f"   Crop: {result['crop_type']}")
        print(f"   Province: {result['province']}")
        print(f"   Current price: {result['current_price']:.2f} บาท/กก.")
        print(f"   Price trend: {result['price_trend']}")
        print(f"   Trend percentage: {result['trend_percentage']:.1f}%")
        print(f"   Model used: {result['model_used']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        print("\n   Predictions:")
        for pred in result['predictions']:
            print(f"      {pred['days_ahead']} days: {pred['predicted_price']:.2f} บาท (confidence: {pred['confidence']:.2f})")
        
        print("\n   Market Insights:")
        for insight in result['market_insights']:
            print(f"      - {insight}")
    else:
        print("❌ Prediction failed")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ Wrapper Test Complete!")
print("="*80)

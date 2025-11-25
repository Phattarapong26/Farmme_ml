"""
Test API Endpoint Directly
===========================
ทดสอบ API endpoint โดยตรงโดยไม่ต้องรัน server
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("Testing API Endpoint Directly")
print("="*80)

# Test: Call predict_price_forecast directly
print("\n🔮 Test: Call predict_price_forecast endpoint")
print("-" * 50)

try:
    # Import the endpoint function
    from app.routers.model import predict_price_forecast, PriceForecastRequest
    import asyncio
    
    # Create request
    request = PriceForecastRequest(
        province="เชียงใหม่",
        crop_type="พริก",
        crop_category="ผักเครื่องเทศ",
        days_ahead=7
    )
    
    print(f"📊 Request:")
    print(f"   Province: {request.province}")
    print(f"   Crop: {request.crop_type}")
    print(f"   Days ahead: {request.days_ahead}")
    
    # Call endpoint
    print(f"\n🚀 Calling endpoint...")
    result = asyncio.run(predict_price_forecast(request))
    
    print(f"\n✅ Response received!")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Model used: {result.get('model_used', 'unknown')}")
    print(f"   Forecast days: {len(result.get('forecast', []))}")
    print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
    
    # Check metadata
    if 'metadata' in result:
        metadata = result['metadata']
        print(f"\n📊 Metadata:")
        print(f"   Model name: {metadata.get('model_name', 'N/A')}")
        print(f"   Version: {metadata.get('model_version', 'N/A')}")
        print(f"   Algorithm: {metadata.get('algorithm', 'N/A')}")
        print(f"   R²: {metadata.get('r2_score', 'N/A')}")
        print(f"   MAE: {metadata.get('mae', 'N/A')}")
        
        if 'warning' in metadata:
            print(f"   ⚠️  Warning: {metadata['warning']}")
    
    # Show first few forecasts
    if result.get('forecast'):
        print(f"\n📈 First 3 forecasts:")
        for i, forecast in enumerate(result['forecast'][:3]):
            print(f"   Day {i+1}: {forecast['date']} → {forecast['predicted_price']} baht/kg (confidence: {forecast.get('confidence_score', 'N/A')})")
    
    # Check if using Model C Stratified
    print(f"\n" + "="*80)
    if result.get('model_used') == 'model_c_stratified':
        print("✅ SUCCESS: Using Model C Stratified!")
        print("\n🎉 Frontend should now show:")
        print("   - Model C Stratified (AI ขั้นสูง)")
        print("   - R² = 0.7589")
        print("   - MAE = 6.97 baht/kg")
        print("   - Accuracy badges (⭐ แม่นสุด for 7 days)")
    elif result.get('model_used') == 'fallback_trend':
        print("⚠️  WARNING: Using FALLBACK trend-based forecast")
        print("\n❌ Model C Stratified not being used!")
        print("   Possible reasons:")
        print("   1. Model files not loaded properly")
        print("   2. Exception occurred during prediction")
        print("   3. Database connection issue")
        
        if result.get('note'):
            print(f"\n   Note: {result['note']}")
    else:
        print(f"❓ UNKNOWN: model_used = {result.get('model_used', 'unknown')}")
    
    print("="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test Complete!")

"""
Test Chat vs Forecast Consistency
==================================
ทดสอบว่า Chat และ /forecast ใช้ข้อมูลเดียวกัน
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Chat vs Forecast Consistency")
print("="*80)

# Test parameters
crop_type = "พริก"
province = "เชียงใหม่"
days_ahead = 30

# Test 1: Get prediction from Chat (price_prediction_service)
print("\nTest 1: Chat Prediction")
print("-" * 50)

try:
    from price_prediction_service import price_prediction_service
    
    chat_result = price_prediction_service.predict_price(
        crop_type=crop_type,
        province=province,
        days_ahead=days_ahead
    )
    
    if chat_result.get('success'):
        print("SUCCESS: Chat prediction")
        print(f"  Model: {chat_result.get('model_used')}")
        print(f"  Current price: {chat_result.get('current_price')}")
        print(f"  Historical points: {len(chat_result.get('historical_data', []))}")
        print(f"  Forecast points: {len(chat_result.get('daily_forecasts', []))}")
        
        # Check if using fallback
        if 'fallback' in chat_result.get('model_used', '').lower():
            print("  WARNING: Using FALLBACK (not real data!)")
        else:
            print("  OK: Using Model C")
    else:
        print(f"FAILED: {chat_result.get('error')}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    chat_result = None

# Test 2: Get prediction from /forecast endpoint
print("\n\nTest 2: /forecast Endpoint Prediction")
print("-" * 50)

try:
    from app.services.price_forecast_service import PriceForecastService
    from database import SessionLocal
    
    forecast_service = PriceForecastService()
    db = SessionLocal()
    
    try:
        forecast_result = forecast_service.forecast_price(
            db=db,
            province=province,
            crop_type=crop_type,
            days_ahead=days_ahead
        )
        
        if forecast_result.get('success'):
            print("SUCCESS: /forecast prediction")
            metadata = forecast_result.get('metadata', {})
            print(f"  Model: {metadata.get('model_used')}")
            
            summary = forecast_result.get('summary', {})
            print(f"  Current price: {summary.get('current_price')}")
            print(f"  Forecast points: {len(forecast_result.get('daily_forecasts', []))}")
            
            # Check if using fallback
            if 'fallback' in metadata.get('model_used', '').lower():
                print("  WARNING: Using FALLBACK (not real data!)")
            else:
                print("  OK: Using Model C")
        else:
            print(f"FAILED: {forecast_result.get('error')}")
            
    finally:
        db.close()
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    forecast_result = None

# Test 3: Compare results
print("\n\nTest 3: Compare Results")
print("-" * 50)

if chat_result and forecast_result:
    if chat_result.get('success') and forecast_result.get('success'):
        # Compare current prices
        chat_price = chat_result.get('current_price')
        forecast_price = forecast_result.get('summary', {}).get('current_price')
        
        print(f"Current Price:")
        print(f"  Chat: {chat_price}")
        print(f"  /forecast: {forecast_price}")
        
        if chat_price == forecast_price:
            print("  OK: Prices match!")
        else:
            print(f"  WARNING: Prices differ by {abs(chat_price - forecast_price):.2f}")
        
        # Compare models
        chat_model = chat_result.get('model_used', '')
        forecast_model = forecast_result.get('metadata', {}).get('model_used', '')
        
        print(f"\nModel Used:")
        print(f"  Chat: {chat_model}")
        print(f"  /forecast: {forecast_model}")
        
        if 'fallback' in chat_model.lower() and 'fallback' not in forecast_model.lower():
            print("  ERROR: Chat using fallback but /forecast using Model C!")
        elif 'fallback' not in chat_model.lower() and 'fallback' not in forecast_model.lower():
            print("  OK: Both using Model C!")
        
        # Compare historical data
        chat_historical = chat_result.get('historical_data', [])
        
        print(f"\nHistorical Data:")
        print(f"  Chat: {len(chat_historical)} points")
        
        if chat_historical:
            # Check if data looks random (fallback) or real
            prices = [h['price'] for h in chat_historical[:5]]
            print(f"  Sample prices: {prices}")
            
            # Check variance - fallback has high variance due to random
            if len(prices) > 1:
                import statistics
                variance = statistics.variance(prices)
                print(f"  Variance: {variance:.2f}")
                
                if variance > 5:
                    print("  WARNING: High variance - might be random data!")
                else:
                    print("  OK: Low variance - looks like real data")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if chat_result and chat_result.get('success'):
    if 'fallback' in chat_result.get('model_used', '').lower():
        print("\nPROBLEM: Chat is using FALLBACK!")
        print("\nReasons:")
        print("  1. Database connection error")
        print("  2. Model not loaded properly")
        print("  3. Insufficient historical data")
        print("\nSolution:")
        print("  - Fix database connection (DATABASE_URL in config)")
        print("  - Ensure Model C Stratified is loaded")
        print("  - Check if database has data for this crop/province")
    else:
        print("\nSUCCESS: Chat is using Model C!")
        print("  - Historical data from database")
        print("  - Predictions from Model C Stratified")
        print("  - Should be consistent across multiple calls")
else:
    print("\nERROR: Chat prediction failed")

print("\n" + "="*80)
print("Test Complete!")
print("="*80)

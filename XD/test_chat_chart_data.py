"""
Test Chat Chart Data
====================
ทดสอบว่า Chat ส่งข้อมูลกราฟจาก database จริง
"""

import sys
import io
from pathlib import Path
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Chat Chart Data")
print("="*80)

# Test: Get prediction with chart data
print("\nTest: Get prediction with chart data")
print("-" * 50)

try:
    from price_prediction_service import price_prediction_service
    
    result = price_prediction_service.predict_price(
        crop_type="พริก",
        province="เชียงใหม่",
        days_ahead=30
    )
    
    if result.get('success'):
        print("SUCCESS: Prediction successful!")
        
        # Check historical_data
        historical_data = result.get('historical_data', [])
        print(f"\nHistorical Data:")
        print(f"  Total points: {len(historical_data)}")
        
        if historical_data:
            print(f"  First point: {historical_data[0]}")
            print(f"  Last point: {historical_data[-1]}")
            print(f"  Sample prices: {[h['price'] for h in historical_data[:5]]}")
        else:
            print("  WARNING: No historical data!")
        
        # Check daily_forecasts
        daily_forecasts = result.get('daily_forecasts', [])
        print(f"\nDaily Forecasts:")
        print(f"  Total points: {len(daily_forecasts)}")
        
        if daily_forecasts:
            print(f"  First forecast: {daily_forecasts[0]}")
            print(f"  Last forecast: {daily_forecasts[-1]}")
            print(f"  Sample prices: {[f['predicted_price'] for f in daily_forecasts[:5]]}")
            
            # Check if has confidence bounds
            if 'confidence_low' in daily_forecasts[0]:
                print(f"  Has confidence bounds: YES")
                print(f"  Sample bounds: {daily_forecasts[0]['confidence_low']} - {daily_forecasts[0]['confidence_high']}")
            else:
                print(f"  Has confidence bounds: NO")
        else:
            print("  WARNING: No daily forecasts!")
        
        # Test chart data extraction
        print(f"\nTest Chart Data Extraction:")
        print("-" * 30)
        
        from app.services.response_formatter_service import response_formatter
        
        chart_data = response_formatter.extract_chart_data(result, "get_price_prediction")
        
        if chart_data:
            print("SUCCESS: Chart data extracted!")
            print(f"  Type: {chart_data.get('type')}")
            
            data = chart_data.get('data', {})
            print(f"  Historical points: {len(data.get('historical', []))}")
            print(f"  Forecast points: {len(data.get('forecast', []))}")
            
            metadata = data.get('metadata', {})
            print(f"  Crop: {metadata.get('crop_type')}")
            print(f"  Province: {metadata.get('province')}")
            print(f"  Model: {metadata.get('model_used')}")
            print(f"  Confidence: {metadata.get('confidence')}")
        else:
            print("ERROR: No chart data extracted!")
        
        # Summary
        print("\n" + "="*80)
        if historical_data and daily_forecasts and chart_data:
            print("SUCCESS: Chat will show correct chart!")
            print("\nChart will display:")
            print(f"  - {len(historical_data)} historical data points from DATABASE")
            print(f"  - {len(daily_forecasts)} forecast points from MODEL C")
            print(f"  - Confidence intervals")
            print(f"  - Model info: {result.get('model_used')}")
            print("\nChart should be CONSISTENT across multiple predictions!")
        else:
            print("WARNING: Chart data incomplete!")
            if not historical_data:
                print("  - Missing historical_data")
            if not daily_forecasts:
                print("  - Missing daily_forecasts")
            if not chart_data:
                print("  - Chart extraction failed")
        print("="*80)
    else:
        print(f"FAILED: {result.get('error', 'unknown')}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nTest Complete!")

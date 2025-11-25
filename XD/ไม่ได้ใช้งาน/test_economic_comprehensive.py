"""
Test Economic Data in Comprehensive Endpoint
=============================================
ทดสอบว่า economic data ส่งข้อมูลทั้งหมดแล้ว
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Economic Data in Comprehensive Endpoint")
print("="*80)

try:
    from app.routers.provinces import _get_economic_data
    from database import SessionLocal
    
    db = SessionLocal()
    
    try:
        province = "เชียงใหม่"
        
        print(f"\nFetching economic data for: {province}")
        print("-" * 50)
        
        result = _get_economic_data(db, province)
        
        print(f"\nResult keys: {result.keys()}")
        print(f"\nLatest values:")
        print(f"  Fertilizer price: {result.get('fertilizer_price')} baht/kg")
        print(f"  Fuel price: {result.get('fuel_price')} baht/L")
        print(f"  Date: {result.get('date')}")
        
        print(f"\nTimeline data:")
        print(f"  Total data points: {result.get('total_data_points', 0)}")
        
        timeline = result.get('timeline', [])
        if timeline:
            print(f"\n  First 3 data points:")
            for i, point in enumerate(timeline[:3]):
                print(f"    {i+1}. Date: {point['date']}, Fertilizer: {point['fertilizer_price']}, Fuel: {point['fuel_price']}")
            
            if len(timeline) > 6:
                print(f"\n  Last 3 data points:")
                for i, point in enumerate(timeline[-3:]):
                    print(f"    {len(timeline)-2+i}. Date: {point['date']}, Fertilizer: {point['fertilizer_price']}, Fuel: {point['fuel_price']}")
            
            # Calculate statistics
            fertilizer_prices = [p['fertilizer_price'] for p in timeline if p['fertilizer_price'] is not None]
            fuel_prices = [p['fuel_price'] for p in timeline if p['fuel_price'] is not None]
            
            if fertilizer_prices:
                print(f"\n  Fertilizer price range: {min(fertilizer_prices):.2f} - {max(fertilizer_prices):.2f} baht/kg")
            if fuel_prices:
                print(f"  Fuel price range: {min(fuel_prices):.2f} - {max(fuel_prices):.2f} baht/L")
        else:
            print("  No timeline data available")
        
        print("\n" + "="*80)
        if result.get('total_data_points', 0) > 0:
            print("SUCCESS: Economic data includes full timeline!")
            print("\nFrontend will now show:")
            print("  - Latest values in cards")
            print("  - Price range (min-max)")
            print(f"  - Total data points: {result.get('total_data_points')}")
            print("  - Date range")
        else:
            print("WARNING: No timeline data found")
            print("Check if economic_factors table has data")
        print("="*80)
    
    finally:
        db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest Complete!")

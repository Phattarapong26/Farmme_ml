"""
Test Overview Endpoint
======================
ทดสอบ /api/dashboard/overview endpoint
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing /api/dashboard/overview Endpoint")
print("="*80)

try:
    from app.services.dashboard_service import get_dashboard_overview
    from database import SessionLocal
    
    db = SessionLocal()
    
    try:
        province = "เชียงใหม่"
        days_back = 30
        
        print(f"\nFetching dashboard overview for: {province}")
        print(f"Days back parameter: {days_back} (ignored for economic_timeline)")
        print("-" * 50)
        
        result = get_dashboard_overview(db, province, days_back)
        
        if result.get('success'):
            print("\nSUCCESS: Dashboard data fetched!")
            
            # Check economic timeline
            economic_timeline = result.get('economic_timeline', [])
            print(f"\nEconomic Timeline:")
            print(f"  Total data points: {len(economic_timeline)}")
            
            if economic_timeline:
                print(f"\n  First month: {economic_timeline[0]['date']}")
                print(f"    Fuel: {economic_timeline[0]['fuel_price']:.2f} baht/L")
                print(f"    Fertilizer: {economic_timeline[0]['fertilizer_price']:.2f} baht/kg")
                
                print(f"\n  Last month: {economic_timeline[-1]['date']}")
                print(f"    Fuel: {economic_timeline[-1]['fuel_price']:.2f} baht/L")
                print(f"    Fertilizer: {economic_timeline[-1]['fertilizer_price']:.2f} baht/kg")
                
                # Calculate range
                fuel_prices = [item['fuel_price'] for item in economic_timeline]
                fertilizer_prices = [item['fertilizer_price'] for item in economic_timeline]
                
                print(f"\n  Fuel price range: {min(fuel_prices):.2f} - {max(fuel_prices):.2f} baht/L")
                print(f"  Fertilizer price range: {min(fertilizer_prices):.2f} - {max(fertilizer_prices):.2f} baht/kg")
                
                # Check if showing overall time
                if len(economic_timeline) > 12:
                    print(f"\n  OK: Showing OVERALL TIME ({len(economic_timeline)} months)")
                elif len(economic_timeline) > 6:
                    print(f"\n  WARNING: Only {len(economic_timeline)} months (expected more)")
                else:
                    print(f"\n  ERROR: Too few data points ({len(economic_timeline)} months)")
            
            # Check other data
            print(f"\nOther Dashboard Data:")
            print(f"  Price history: {len(result.get('price_history', []))} points")
            print(f"  Weather data: {len(result.get('weather_data', []))} points")
            print(f"  Crop distribution: {len(result.get('crop_distribution', []))} crops")
            print(f"  Profitability: {len(result.get('profitability', []))} crops")
            
        else:
            print("FAILED: Dashboard data fetch failed")
    
    finally:
        db.close()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nChanges made:")
    print("  1. Removed date filter (AND date >= :start_date)")
    print("  2. Now shows ALL available data (overall time)")
    print("  3. Adjusted scale: Fuel ~30-35 baht/L, Fertilizer ~15-20 baht/kg")
    print("\nFrontend will now show:")
    print("  - Complete timeline (all months available)")
    print("  - Realistic price ranges")
    print("  - Better trend visualization")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest Complete!")

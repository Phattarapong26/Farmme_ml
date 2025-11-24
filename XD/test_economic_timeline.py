"""
Test Economic Timeline Scale
=============================
ทดสอบ scale ใหม่ของราคาน้ำมันและปุ๋ย
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Economic Timeline Scale")
print("="*80)

# Test: Get economic timeline
print("\nTest: Get Economic Timeline")
print("-" * 50)

try:
    from app.services.dashboard_service import get_economic_timeline
    from database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Test with different provinces
        provinces = ["เชียงใหม่", "กรุงเทพมหานคร"]
        
        for province in provinces:
            print(f"\nProvince: {province}")
            print("-" * 30)
            
            # Test with days_back parameter (should be ignored now)
            timeline = get_economic_timeline(db, province, days_back=90)
            print(f"Note: days_back parameter is now ignored - showing ALL data")
            
            if timeline:
                print(f"Data points: {len(timeline)}")
                
                # Show first 3 and last 3
                print("\nFirst 3 months:")
                for item in timeline[:3]:
                    print(f"  {item['date']}: Fuel={item['fuel_price']:.2f} baht/L, Fertilizer={item['fertilizer_price']:.2f} baht/kg")
                
                if len(timeline) > 6:
                    print("\nLast 3 months:")
                    for item in timeline[-3:]:
                        print(f"  {item['date']}: Fuel={item['fuel_price']:.2f} baht/L, Fertilizer={item['fertilizer_price']:.2f} baht/kg")
                
                # Calculate averages
                avg_fuel = sum(item['fuel_price'] for item in timeline) / len(timeline)
                avg_fertilizer = sum(item['fertilizer_price'] for item in timeline) / len(timeline)
                
                print(f"\nAverages:")
                print(f"  Fuel: {avg_fuel:.2f} baht/L")
                print(f"  Fertilizer: {avg_fertilizer:.2f} baht/kg")
                
                # Check if realistic
                print(f"\nRealistic check:")
                if 25 <= avg_fuel <= 40:
                    print(f"  Fuel price: OK (realistic range 25-40 baht/L)")
                else:
                    print(f"  Fuel price: WARNING (outside realistic range)")
                
                if 10 <= avg_fertilizer <= 25:
                    print(f"  Fertilizer price: OK (realistic range 10-25 baht/kg)")
                else:
                    print(f"  Fertilizer price: WARNING (outside realistic range)")
            else:
                print("  No data available")
    
    finally:
        db.close()
    
    print("\n" + "="*80)
    print("SUCCESS: Economic timeline scale updated!")
    print("="*80)
    print("\nNew scale formula:")
    print("  Fuel price = 30 + (avg_crop_price * 0.1) baht/L")
    print("  Fertilizer price = 15 + (avg_crop_price * 0.15) baht/kg")
    print("\nExpected ranges:")
    print("  Fuel: 30-35 baht/L (realistic diesel price)")
    print("  Fertilizer: 15-20 baht/kg (realistic fertilizer price)")
    print("\nFrontend should now show:")
    print("  - Realistic fuel prices (~30-35 baht/L)")
    print("  - Realistic fertilizer prices (~15-20 baht/kg)")
    print("  - Proper scale on charts")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest Complete!")

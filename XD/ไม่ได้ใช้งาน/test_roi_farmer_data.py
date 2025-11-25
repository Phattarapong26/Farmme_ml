"""
Test ROI and Farmer Skills Data Format
"""
import sys
sys.path.append('backend')

from database import SessionLocal
from sqlalchemy import text
import json

def test_data_format():
    """Test the exact data format returned"""
    print("\n" + "="*60)
    print("🔍 Testing ROI and Farmer Skills Data Format")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get test province
        result = db.execute(text("SELECT DISTINCT province FROM crop_prices LIMIT 1"))
        province = result.fetchone()[0]
        print(f"\n📍 Testing with province: {province}\n")
        
        from app.services.dashboard_service import (
            get_roi_details,
            get_farmer_skills_data,
            get_dashboard_overview
        )
        
        # Test ROI Details
        print("="*60)
        print("💰 ROI Details")
        print("="*60)
        roi_data = get_roi_details(db, province)
        print(f"Type: {type(roi_data)}")
        print(f"Length: {len(roi_data)}")
        if roi_data:
            print(f"\nFirst item:")
            print(json.dumps(roi_data[0], indent=2, ensure_ascii=False))
            print(f"\nAll items:")
            for item in roi_data:
                print(f"  - {item}")
        else:
            print("⚠️ EMPTY!")
        
        # Test Farmer Skills
        print("\n" + "="*60)
        print("👨‍🌾 Farmer Skills")
        print("="*60)
        farmer_data = get_farmer_skills_data(db, province)
        print(f"Type: {type(farmer_data)}")
        print(f"Length: {len(farmer_data)}")
        if farmer_data:
            print(f"\nFirst item:")
            print(json.dumps(farmer_data[0], indent=2, ensure_ascii=False))
            print(f"\nAll items:")
            for item in farmer_data:
                print(f"  - {item}")
        else:
            print("⚠️ EMPTY!")
        
        # Test Full Dashboard Response
        print("\n" + "="*60)
        print("📊 Full Dashboard Response")
        print("="*60)
        dashboard = get_dashboard_overview(db, province, 30)
        
        print(f"\nROI Details in dashboard:")
        print(f"  Type: {type(dashboard.get('roi_details'))}")
        print(f"  Length: {len(dashboard.get('roi_details', []))}")
        if dashboard.get('roi_details'):
            print(f"  Sample: {dashboard['roi_details'][0]}")
        
        print(f"\nFarmer Skills in dashboard:")
        print(f"  Type: {type(dashboard.get('farmer_skills'))}")
        print(f"  Length: {len(dashboard.get('farmer_skills', []))}")
        if dashboard.get('farmer_skills'):
            print(f"  Sample: {dashboard['farmer_skills'][0]}")
        
        # Check profit_data table directly
        print("\n" + "="*60)
        print("🗄️ Direct Database Query")
        print("="*60)
        
        result = db.execute(text("""
            SELECT crop_type, avg_roi_percent, avg_margin_percent, avg_profit_per_rai
            FROM profit_data
            WHERE province = :province
            ORDER BY avg_roi_percent DESC
            LIMIT 5
        """), {"province": province})
        
        print(f"\nTop 5 ROI from profit_data:")
        for row in result:
            print(f"  {row[0]:20s} ROI: {row[1]:.1f}% Margin: {row[2]:.1f}% Profit/Rai: {row[3]:.0f}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_data_format()

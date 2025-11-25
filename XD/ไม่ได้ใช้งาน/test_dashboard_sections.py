"""
Test Dashboard Sections - Check which sections have data
"""
import sys
sys.path.append('backend')

from database import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_sections():
    """Test all dashboard sections"""
    print("\n" + "="*60)
    print("🔍 Testing Dashboard Sections")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Get test province
        result = db.execute(text("SELECT DISTINCT province FROM crop_prices LIMIT 1"))
        province = result.fetchone()[0]
        print(f"\n📍 Testing with province: {province}\n")
        
        from app.services.dashboard_service import (
            get_province_statistics,
            get_price_history,
            get_weather_data,
            get_crop_distribution,
            get_profitability_data,
            get_farmer_skills_data,
            get_economic_timeline,
            get_soil_analysis,
            get_roi_details,
            get_seasonal_recommendations,
            get_price_volatility,
            get_best_planting_window,
            get_market_demand_trends,
            get_market_potential
        )
        
        # Test each section
        sections = [
            ("Statistics", lambda: get_province_statistics(db, province)),
            ("Price History", lambda: get_price_history(db, province, 30)),
            ("Weather Data", lambda: get_weather_data(db, province, 30)),
            ("Crop Distribution", lambda: get_crop_distribution(db, province)),
            ("Profitability", lambda: get_profitability_data(db, province, 10)),
            ("Farmer Skills", lambda: get_farmer_skills_data(db, province)),
            ("Economic Timeline", lambda: get_economic_timeline(db, province, 90)),
            ("Soil Analysis", lambda: get_soil_analysis(db, province)),
            ("ROI Details", lambda: get_roi_details(db, province)),
            ("Seasonal Recommendations", lambda: get_seasonal_recommendations(db, province)),
            ("Price Volatility", lambda: get_price_volatility(db, province, 30)),
            ("Planting Window", lambda: get_best_planting_window(db, province)),
            ("Market Trends", lambda: get_market_demand_trends(db, province, 30)),
            ("Market Potential", lambda: get_market_potential(db, province)),
        ]
        
        results = {}
        for name, func in sections:
            try:
                data = func()
                
                # Check if data is empty
                if isinstance(data, list):
                    count = len(data)
                    status = "✅" if count > 0 else "⚠️ EMPTY"
                elif isinstance(data, dict):
                    # Check if dict has meaningful data
                    if name == "Statistics":
                        count = f"{data.get('total_crop_types', 0)} crops"
                        status = "✅" if data.get('total_crop_types', 0) > 0 else "⚠️ EMPTY"
                    elif name == "Market Potential":
                        count = f"{data.get('total_population', 0):,} people"
                        status = "✅" if data.get('total_population', 0) > 0 else "⚠️ NO DATA"
                    else:
                        count = f"{len(data)} fields"
                        status = "✅"
                else:
                    count = "unknown"
                    status = "❓"
                
                results[name] = {"status": status, "count": count, "data": data}
                print(f"{status} {name:30s} {count}")
                
            except Exception as e:
                results[name] = {"status": "❌", "error": str(e)}
                print(f"❌ {name:30s} ERROR: {e}")
        
        # Show details for empty sections
        print("\n" + "="*60)
        print("📋 Empty Sections Details")
        print("="*60)
        
        for name, result in results.items():
            if "⚠️" in result.get("status", "") or "❌" in result.get("status", ""):
                print(f"\n{name}:")
                if "error" in result:
                    print(f"  Error: {result['error']}")
                elif "data" in result:
                    print(f"  Data: {result['data']}")
        
        # Check specific tables
        print("\n" + "="*60)
        print("🗄️ Table Data Availability")
        print("="*60)
        
        tables_to_check = [
            ("crop_prices", f"province = '{province}'"),
            ("weather_data", f"province = '{province}'"),
            ("crop_characteristics", "1=1"),
            ("farmer_profiles", f"province = '{province}'"),
            ("population_data", f"province = '{province}'"),
            ("profit_data", f"province = '{province}'"),
        ]
        
        for table, condition in tables_to_check:
            try:
                query = text(f"SELECT COUNT(*) FROM {table} WHERE {condition}")
                count = db.execute(query).scalar()
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {table:25s} {count:,} records")
            except Exception as e:
                print(f"❌ {table:25s} Table not found or error")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_all_sections()

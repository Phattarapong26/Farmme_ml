#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Dashboard Data Queries and Province Filtering
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import SessionLocal
from sqlalchemy import text

def check_dashboard_data(province="เชียงใหม่"):
    """Check all dashboard queries for a specific province"""
    db = SessionLocal()
    
    print("=" * 80)
    print(f"🔍 CHECKING DASHBOARD DATA FOR: {province}")
    print("=" * 80)
    print()
    
    # 1. Check Farmer Skills Data
    print("1️⃣ FARMER SKILLS DATA")
    print("-" * 80)
    query = text("""
        SELECT province, avg_experience_years, avg_land_size_rai, total_farmers
        FROM farmer_profiles
        WHERE province = :province
    """)
    result = db.execute(query, {"province": province})
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"   Province: {row[0]}")
            print(f"   Experience: {row[1]} years")
            print(f"   Land Size: {row[2]} rai")
            print(f"   Total Farmers: {row[3]}")
    else:
        print(f"   ❌ NO DATA for {province}")
        # Check what provinces exist
        all_provinces = db.execute(text("SELECT DISTINCT province FROM farmer_profiles")).fetchall()
        print(f"   Available provinces: {[p[0] for p in all_provinces[:5]]}")
    print()
    
    # 2. Check Economic Timeline
    print("2️⃣ ECONOMIC TIMELINE DATA")
    print("-" * 80)
    query = text("""
        SELECT factor_name, COUNT(*) as count, MIN(date) as min_date, MAX(date) as max_date
        FROM economic_factors
        GROUP BY factor_name
        LIMIT 5
    """)
    result = db.execute(query)
    rows = result.fetchall()
    print(f"   Total factors: {len(rows)}")
    for row in rows:
        print(f"   - {row[0]}: {row[1]} records ({row[2]} to {row[3]})")
    print(f"   ⚠️  Note: Economic data is NOT province-specific!")
    print()
    
    # 3. Check Soil Analysis
    print("3️⃣ SOIL ANALYSIS DATA")
    print("-" * 80)
    query = text("""
        SELECT soil_preference, COUNT(*) as count
        FROM crop_characteristics
        WHERE soil_preference IS NOT NULL
        GROUP BY soil_preference
        ORDER BY count DESC
    """)
    result = db.execute(query)
    rows = result.fetchall()
    print(f"   Total soil types: {len(rows)}")
    for row in rows:
        print(f"   - {row[0]}: {row[1]} crops")
    print(f"   ⚠️  Note: Soil data is NOT province-specific!")
    print()
    
    # 4. Check ROI Details
    print("4️⃣ ROI DETAILS DATA")
    print("-" * 80)
    query = text("""
        SELECT crop_type, avg_roi_percent, avg_margin_percent, avg_profit_per_rai
        FROM profit_data
        WHERE province = :province
        ORDER BY avg_roi_percent DESC
        LIMIT 5
    """)
    result = db.execute(query, {"province": province})
    rows = result.fetchall()
    if rows:
        print(f"   Top 5 ROI crops for {province}:")
        for row in rows:
            print(f"   - {row[0]}: ROI {row[1]:.1f}%, Margin {row[2]:.1f}%, Profit {row[3]:.0f} baht/rai")
    else:
        print(f"   ❌ NO DATA for {province}")
        # Check what provinces exist
        all_provinces = db.execute(text("SELECT DISTINCT province FROM profit_data LIMIT 5")).fetchall()
        print(f"   Available provinces: {[p[0] for p in all_provinces]}")
    print()
    
    # 5. Check Profitability Data
    print("5️⃣ PROFITABILITY DATA (from crop_prices)")
    print("-" * 80)
    query = text("""
        SELECT crop_type, AVG(price_per_kg) as avg_profit
        FROM crop_prices
        WHERE province = :province
        GROUP BY crop_type
        ORDER BY avg_profit DESC
        LIMIT 5
    """)
    result = db.execute(query, {"province": province})
    rows = result.fetchall()
    if rows:
        print(f"   Top 5 profitable crops for {province}:")
        for row in rows:
            print(f"   - {row[0]}: {row[1]:.2f} baht/kg")
    else:
        print(f"   ❌ NO DATA for {province}")
        # Check what provinces exist
        all_provinces = db.execute(text("SELECT DISTINCT province FROM crop_prices LIMIT 5")).fetchall()
        print(f"   Available provinces: {[p[0] for p in all_provinces]}")
    print()
    
    # 6. Check Crop Distribution
    print("6️⃣ CROP DISTRIBUTION DATA")
    print("-" * 80)
    query = text("""
        SELECT crop_type, COUNT(*) as count
        FROM crop_prices
        WHERE province = :province
        GROUP BY crop_type
        ORDER BY count DESC
        LIMIT 5
    """)
    result = db.execute(query, {"province": province})
    rows = result.fetchall()
    if rows:
        print(f"   Top 5 crops by record count for {province}:")
        for row in rows:
            print(f"   - {row[0]}: {row[1]} records")
    else:
        print(f"   ❌ NO DATA for {province}")
    print()
    
    # 7. Compare province names
    print("7️⃣ PROVINCE NAME CONSISTENCY CHECK")
    print("-" * 80)
    tables = [
        ("crop_prices", "province"),
        ("weather_data", "province"),
        ("farmer_profiles", "province"),
        ("profit_data", "province"),
        ("population_data", "province")
    ]
    
    for table, column in tables:
        query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} = :province")
        result = db.execute(query, {"province": province})
        rows = result.fetchall()
        if rows:
            print(f"   ✅ {table}: Found '{rows[0][0]}'")
        else:
            print(f"   ❌ {table}: NOT FOUND")
            # Show similar provinces
            query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} LIKE :pattern LIMIT 3")
            result = db.execute(query, {"pattern": f"%{province[:3]}%"})
            similar = result.fetchall()
            if similar:
                print(f"      Similar: {[s[0] for s in similar]}")
    print()
    
    print("=" * 80)
    print("🔍 SUMMARY")
    print("=" * 80)
    print("Issues found:")
    print("1. Economic Timeline & Soil Analysis are NOT province-specific")
    print("2. Check if province names match exactly across all tables")
    print("3. Some charts may show global data instead of province-specific data")
    
    db.close()

if __name__ == "__main__":
    import sys
    # Default to เชียงใหม่ for testing
    province = "เชียงใหม่"
    if len(sys.argv) > 1:
        # Try to decode argument properly
        try:
            province = sys.argv[1].encode('latin1').decode('utf-8')
        except:
            province = sys.argv[1]
    check_dashboard_data(province)

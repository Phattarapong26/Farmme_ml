"""
Test Supabase Connection and Overview Endpoint
"""
import sys
import os
sys.path.append('backend')

from sqlalchemy import create_engine, text
from database import DATABASE_URL, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connection"""
    print("\n" + "="*60)
    print("🔍 Testing Supabase Database Connection")
    print("="*60)
    
    try:
        # Test connection
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version[:50]}...")
            
        # Test session
        db = SessionLocal()
        try:
            # Check tables
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"\n✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            
            # Check crop_prices data
            result = db.execute(text("SELECT COUNT(*) FROM crop_prices"))
            count = result.fetchone()[0]
            print(f"\n✅ crop_prices table has {count:,} records")
            
            # Check provinces
            result = db.execute(text("SELECT DISTINCT province FROM crop_prices ORDER BY province LIMIT 10"))
            provinces = [row[0] for row in result]
            print(f"\n✅ Found {len(provinces)} provinces (showing first 10):")
            for prov in provinces:
                print(f"   - {prov}")
            
            # Test a specific province
            test_province = provinces[0] if provinces else "เชียงใหม่"
            result = db.execute(text("""
                SELECT crop_type, price_per_kg, date 
                FROM crop_prices 
                WHERE province = :province 
                ORDER BY date DESC 
                LIMIT 5
            """), {"province": test_province})
            
            print(f"\n✅ Sample data from {test_province}:")
            for row in result:
                print(f"   - {row[0]}: {row[1]} บาท/กก. ({row[2]})")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_overview_endpoint():
    """Test overview endpoint logic"""
    print("\n" + "="*60)
    print("🔍 Testing Overview Endpoint Logic")
    print("="*60)
    
    try:
        from app.services.dashboard_service import get_dashboard_overview
        
        db = SessionLocal()
        try:
            # Get first available province
            result = db.execute(text("SELECT DISTINCT province FROM crop_prices LIMIT 1"))
            province = result.fetchone()[0]
            
            print(f"\n📊 Testing with province: {province}")
            
            # Call dashboard service
            data = get_dashboard_overview(db, province, days_back=30)
            
            print(f"\n✅ Dashboard data retrieved successfully")
            print(f"   Statistics: {len(data.get('statistics', {}))} fields")
            print(f"   Price history: {len(data.get('price_history', []))} records")
            print(f"   Weather data: {len(data.get('weather_data', []))} records")
            print(f"   Crop distribution: {len(data.get('crop_distribution', []))} crops")
            print(f"   Profitability: {len(data.get('profitability', []))} crops")
            
            # Show statistics
            stats = data.get('statistics', {})
            print(f"\n📈 Statistics:")
            print(f"   Avg price: {stats.get('avg_price', 0)} บาท/กก.")
            print(f"   Total crop types: {stats.get('total_crop_types', 0)}")
            print(f"   Most profitable: {stats.get('most_profitable_crop', 'N/A')}")
            print(f"   Temperature: {stats.get('current_temp', 0)}°C")
            print(f"   Rainfall: {stats.get('current_rainfall', 0)} mm")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Overview endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Supabase Connection Tests\n")
    
    # Test 1: Database connection
    db_ok = test_database_connection()
    
    # Test 2: Overview endpoint
    if db_ok:
        overview_ok = test_overview_endpoint()
    else:
        print("\n⚠️ Skipping overview test due to database connection failure")
        overview_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Overview Endpoint:   {'✅ PASS' if overview_ok else '❌ FAIL'}")
    print("="*60)
    
    if db_ok and overview_ok:
        print("\n✅ All tests passed! Supabase is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

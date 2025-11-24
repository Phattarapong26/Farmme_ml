"""
Fast Upload Missing Data to Supabase
Upload population_data and profit_data tables
"""
import sys
sys.path.append('backend')

import pandas as pd
from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dataset path
DATASET_PATH = r"C:\Users\LightZ\Desktop\XD\buildingModel.py\Dataset"

def fast_upload_population():
    """Upload population data"""
    print("\n" + "="*60)
    print("📊 Uploading Population Data")
    print("="*60)
    
    try:
        # Read CSV
        df = pd.read_csv(f"{DATASET_PATH}/population.csv")
        print(f"✅ Loaded {len(df):,} records from population.csv")
        print(f"   Columns: {list(df.columns)}")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'population_data'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠️ Creating population_data table...")
                conn.execute(text("""
                    CREATE TABLE population_data (
                        id SERIAL PRIMARY KEY,
                        province VARCHAR(255),
                        year INTEGER,
                        total_population INTEGER,
                        working_age_population INTEGER,
                        agricultural_population INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                print("✅ Table created")
        
        # Rename columns to match database
        column_mapping = {
            'Province': 'province',
            'Year': 'year',
            'Total_Population': 'total_population',
            'Working_Age_Population': 'working_age_population',
            'Agricultural_Population': 'agricultural_population'
        }
        
        # Check which columns exist
        for old_col, new_col in list(column_mapping.items()):
            if old_col not in df.columns:
                # Try lowercase
                if old_col.lower() in df.columns:
                    column_mapping[old_col.lower()] = new_col
                    del column_mapping[old_col]
        
        df = df.rename(columns=column_mapping)
        
        # Select only needed columns
        needed_cols = ['province', 'year', 'total_population', 'working_age_population', 'agricultural_population']
        available_cols = [col for col in needed_cols if col in df.columns]
        df = df[available_cols]
        
        print(f"   Uploading columns: {available_cols}")
        
        # Upload using bulk insert (FAST!)
        df.to_sql('population_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Uploaded {len(df):,} records to population_data")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM population_data"))
            count = result.scalar()
            print(f"✅ Verified: {count:,} total records in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading population data: {e}")
        import traceback
        traceback.print_exc()
        return False


def fast_upload_profit():
    """Upload profit data"""
    print("\n" + "="*60)
    print("💰 Uploading Profit Data")
    print("="*60)
    
    try:
        # Read CSV
        df = pd.read_csv(f"{DATASET_PATH}/profit.csv")
        print(f"✅ Loaded {len(df):,} records from profit.csv")
        print(f"   Columns: {list(df.columns)}")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'profit_data'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠️ Creating profit_data table...")
                conn.execute(text("""
                    CREATE TABLE profit_data (
                        id SERIAL PRIMARY KEY,
                        province VARCHAR(255),
                        crop_type VARCHAR(255),
                        avg_roi_percent FLOAT,
                        avg_margin_percent FLOAT,
                        avg_profit_per_rai FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                print("✅ Table created")
        
        # Rename columns to match database
        column_mapping = {
            'Province': 'province',
            'Crop_Type': 'crop_type',
            'Avg_ROI_Percent': 'avg_roi_percent',
            'Avg_Margin_Percent': 'avg_margin_percent',
            'Avg_Profit_Per_Rai': 'avg_profit_per_rai'
        }
        
        # Check which columns exist
        for old_col, new_col in list(column_mapping.items()):
            if old_col not in df.columns:
                # Try lowercase
                if old_col.lower() in df.columns:
                    column_mapping[old_col.lower()] = new_col
                    del column_mapping[old_col]
        
        df = df.rename(columns=column_mapping)
        
        # Select only needed columns
        needed_cols = ['province', 'crop_type', 'avg_roi_percent', 'avg_margin_percent', 'avg_profit_per_rai']
        available_cols = [col for col in needed_cols if col in df.columns]
        df = df[available_cols]
        
        print(f"   Uploading columns: {available_cols}")
        
        # Upload using bulk insert (FAST!)
        df.to_sql('profit_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Uploaded {len(df):,} records to profit_data")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM profit_data"))
            count = result.scalar()
            print(f"✅ Verified: {count:,} total records in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading profit data: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_all_data():
    """Verify all tables have data"""
    print("\n" + "="*60)
    print("🔍 Verifying All Tables")
    print("="*60)
    
    engine = create_engine(DATABASE_URL)
    
    tables = [
        'crop_prices',
        'weather_data',
        'crop_characteristics',
        'farmer_profiles',
        'population_data',
        'profit_data'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {table:25s} {count:,} records")
            except Exception as e:
                print(f"❌ {table:25s} Error: {e}")


if __name__ == "__main__":
    print("\n🚀 Fast Upload Missing Data to Supabase")
    print("="*60)
    
    import time
    start_time = time.time()
    
    # Upload population data
    pop_ok = fast_upload_population()
    
    # Upload profit data
    profit_ok = fast_upload_profit()
    
    # Verify
    verify_all_data()
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*60)
    print("📋 Upload Summary")
    print("="*60)
    print(f"Population Data: {'✅ SUCCESS' if pop_ok else '❌ FAILED'}")
    print(f"Profit Data:     {'✅ SUCCESS' if profit_ok else '❌ FAILED'}")
    print(f"Total Time:      {elapsed:.2f} seconds")
    print("="*60)
    
    if pop_ok and profit_ok:
        print("\n✅ All data uploaded successfully!")
        print("   Dashboard should now show complete data.")
    else:
        print("\n⚠️ Some uploads failed. Check errors above.")

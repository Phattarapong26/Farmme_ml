"""
Fix Profit Data - Calculate aggregated metrics
"""
import sys
sys.path.append('backend')

import pandas as pd
from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_PATH = r"C:\Users\LightZ\Desktop\XD\buildingModel.py\Dataset"

def fix_profit_data():
    """Calculate aggregated profit metrics"""
    print("\n" + "="*60)
    print("🔧 Fixing Profit Data")
    print("="*60)
    
    try:
        # Read original CSV
        df = pd.read_csv(f"{DATASET_PATH}/profit.csv")
        print(f"✅ Loaded {len(df):,} records")
        print(f"   Columns: {list(df.columns)[:10]}...")
        
        # Calculate aggregated metrics by province and crop_type
        print("\n📊 Calculating aggregated metrics...")
        
        agg_df = df.groupby(['province', 'crop_type']).agg({
            'roi_percent': 'mean',
            'margin_percent': 'mean',
            'profit': 'mean',
            'planting_area_rai': 'mean'
        }).reset_index()
        
        # Calculate profit per rai
        agg_df['avg_profit_per_rai'] = agg_df['profit'] / agg_df['planting_area_rai']
        
        # Rename columns
        agg_df = agg_df.rename(columns={
            'roi_percent': 'avg_roi_percent',
            'margin_percent': 'avg_margin_percent'
        })
        
        # Select final columns
        final_df = agg_df[['province', 'crop_type', 'avg_roi_percent', 'avg_margin_percent', 'avg_profit_per_rai']]
        
        # Remove invalid data
        final_df = final_df[
            (final_df['avg_roi_percent'] > 0) & 
            (final_df['avg_roi_percent'] < 500) &
            (final_df['avg_profit_per_rai'] > 0)
        ]
        
        print(f"✅ Aggregated to {len(final_df):,} records")
        print(f"\nSample data:")
        print(final_df.head())
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Drop and recreate table
        with engine.connect() as conn:
            print("\n🗑️ Dropping old profit_data table...")
            conn.execute(text("DROP TABLE IF EXISTS profit_data"))
            conn.commit()
            
            print("📝 Creating new profit_data table...")
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
        
        # Upload
        print("\n⬆️ Uploading aggregated data...")
        final_df.to_sql('profit_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Uploaded {len(final_df):,} records")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM profit_data"))
            count = result.scalar()
            print(f"✅ Verified: {count:,} records in database")
            
            # Show sample
            result = conn.execute(text("""
                SELECT province, crop_type, avg_roi_percent, avg_margin_percent, avg_profit_per_rai
                FROM profit_data
                ORDER BY avg_roi_percent DESC
                LIMIT 5
            """))
            print("\n📊 Top 5 ROI crops:")
            for row in result:
                print(f"   {row[0]:15s} {row[1]:20s} ROI: {row[2]:.1f}% Margin: {row[3]:.1f}% Profit/Rai: {row[4]:.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_population_data():
    """Add year column to population_data"""
    print("\n" + "="*60)
    print("🔧 Fixing Population Data")
    print("="*60)
    
    try:
        # Read original CSV
        df = pd.read_csv(f"{DATASET_PATH}/population.csv")
        print(f"✅ Loaded {len(df):,} records")
        
        # Extract year from date
        if 'date' in df.columns:
            df['year'] = pd.to_datetime(df['date']).dt.year
        else:
            df['year'] = 2024  # Default year
        
        # Select columns
        final_df = df[['province', 'year', 'total_population', 'working_age_population']].copy()
        
        # Add agricultural_population (estimate as 30% of working age in rural areas)
        final_df['agricultural_population'] = (final_df['working_age_population'] * 0.3).astype(int)
        
        print(f"\nSample data:")
        print(final_df.head())
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Drop and recreate table
        with engine.connect() as conn:
            print("\n🗑️ Dropping old population_data table...")
            conn.execute(text("DROP TABLE IF EXISTS population_data"))
            conn.commit()
            
            print("📝 Creating new population_data table...")
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
        
        # Upload
        print("\n⬆️ Uploading data...")
        final_df.to_sql('population_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        
        print(f"✅ Uploaded {len(final_df):,} records")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM population_data"))
            count = result.scalar()
            print(f"✅ Verified: {count:,} records in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Fixing Data Tables")
    
    import time
    start_time = time.time()
    
    # Fix profit data
    profit_ok = fix_profit_data()
    
    # Fix population data
    pop_ok = fix_population_data()
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*60)
    print("📋 Fix Summary")
    print("="*60)
    print(f"Profit Data:     {'✅ SUCCESS' if profit_ok else '❌ FAILED'}")
    print(f"Population Data: {'✅ SUCCESS' if pop_ok else '❌ FAILED'}")
    print(f"Total Time:      {elapsed:.2f} seconds")
    print("="*60)
    
    if profit_ok and pop_ok:
        print("\n✅ All data fixed successfully!")
    else:
        print("\n⚠️ Some fixes failed.")

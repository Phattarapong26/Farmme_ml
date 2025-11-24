# -*- coding: utf-8 -*-
"""
Import Dataset to PostgreSQL Database
Handles data validation and transformation if needed
"""
import pandas as pd
import numpy as np
from sqlalchemy import text
from database import SessionLocal, engine
from datetime import datetime
import os
import sys

# Dataset paths
DATASET_DIR = "../buildingModel.py/Dataset"

def validate_and_clean_data(df, data_type):
    """
    Validate and clean data before import
    Check for transformed values and convert back if needed
    """
    print(f"  🔍 Validating {data_type} data...")
    
    # Check for NaN/Inf values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        # Replace inf with NaN
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        # Check if values look like log-transformed (very small or negative)
        if col in ['price_per_kg', 'temperature_celsius', 'rainfall_mm']:
            min_val = df[col].min()
            max_val = df[col].max()
            
            # If values are suspiciously small (< 0 for prices), might be log-transformed
            if col == 'price_per_kg' and (min_val < 0 or max_val < 1):
                print(f"  ⚠️  {col} looks log-transformed (range: {min_val:.2f} to {max_val:.2f})")
                print(f"  🔄 Converting back: exp({col})")
                df[col] = np.exp(df[col])
    
    # Fill NaN with appropriate values
    for col in numeric_cols:
        if df[col].isna().any():
            nan_count = df[col].isna().sum()
            print(f"  ⚠️  {col} has {nan_count} NaN values, filling with median")
            df[col] = df[col].fillna(df[col].median())
    
    print(f"  ✅ Validation complete")
    return df

def import_crop_prices():
    """Import crop prices data"""
    print("\n📊 Importing crop prices...")
    try:
        df = pd.read_csv(f"{DATASET_DIR}/price.csv")
        
        # Select relevant columns for crop_prices table
        df_prices = df[['date', 'province', 'crop_type', 'price_per_kg']].copy()
        
        # Validate and clean data
        df_prices = validate_and_clean_data(df_prices, 'crop prices')
        
        # Show sample statistics
        print(f"  📈 Price range: {df_prices['price_per_kg'].min():.2f} - {df_prices['price_per_kg'].max():.2f} บาท/กก.")
        print(f"  📈 Average price: {df_prices['price_per_kg'].mean():.2f} บาท/กก.")
        
        df_prices['date'] = pd.to_datetime(df_prices['date'])
        df_prices['source'] = 'dataset_import'
        df_prices['created_at'] = datetime.utcnow()
        df_prices['updated_at'] = datetime.utcnow()
        
        # Import to database in chunks (for large datasets)
        chunk_size = 10000
        total_rows = len(df_prices)
        
        for i in range(0, total_rows, chunk_size):
            chunk = df_prices.iloc[i:i+chunk_size]
            chunk.to_sql('crop_prices', engine, if_exists='append', index=False)
            print(f"  📦 Imported {min(i+chunk_size, total_rows)}/{total_rows} records...")
        
        print(f"✅ Imported {len(df_prices)} crop price records")
        return True
    except Exception as e:
        print(f"❌ Error importing crop prices: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_weather_data():
    """Import weather data"""
    print("\n🌤️  Importing weather data...")
    try:
        df = pd.read_csv(f"{DATASET_DIR}/weather.csv")
        
        # Select relevant columns first
        df_weather = df[['province', 'date', 'temperature_celsius', 'rainfall_mm']].copy()
        
        # Validate and clean data
        df_weather = validate_and_clean_data(df_weather, 'weather')
        
        # Show sample statistics
        print(f"  🌡️  Temperature range: {df_weather['temperature_celsius'].min():.1f} - {df_weather['temperature_celsius'].max():.1f} °C")
        print(f"  🌧️  Rainfall range: {df_weather['rainfall_mm'].min():.1f} - {df_weather['rainfall_mm'].max():.1f} mm")
        
        # Prepare data for weather_data table
        df_weather['date'] = pd.to_datetime(df_weather['date'])
        df_weather['source'] = 'dataset_import'
        df_weather['created_at'] = datetime.utcnow()
        df_weather['updated_at'] = datetime.utcnow()
        
        # Import to database in chunks
        chunk_size = 10000
        total_rows = len(df_weather)
        
        for i in range(0, total_rows, chunk_size):
            chunk = df_weather.iloc[i:i+chunk_size]
            chunk.to_sql('weather_data', engine, if_exists='append', index=False)
            print(f"  📦 Imported {min(i+chunk_size, total_rows)}/{total_rows} records...")
        
        print(f"✅ Imported {len(df_weather)} weather records")
        return True
    except Exception as e:
        print(f"❌ Error importing weather data: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_crop_cultivation():
    """Import crop cultivation data"""
    print("\n🌾 Importing crop cultivation...")
    try:
        df = pd.read_csv(f"{DATASET_DIR}/cultivation.csv")
        
        # Prepare data for crop_cultivation table
        df_cult = pd.DataFrame({
            'crop_name': df['crop_type'],
            'province': df['province'],
            'planting_date': pd.to_datetime(df['planting_date']),
            'harvest_date': pd.to_datetime(df['harvest_date']),
            'yield_kg': df['actual_yield_kg'],
            'area_rai': df['planting_area_rai'],
            'created_at': datetime.utcnow()
        })
        
        # Import to database
        df_cult.to_sql('crop_cultivation', engine, if_exists='append', index=False)
        
        print(f"✅ Imported {len(df_cult)} cultivation records")
        return True
    except Exception as e:
        print(f"❌ Error importing cultivation data: {e}")
        return False

def import_crop_characteristics():
    """Import crop characteristics data"""
    print("\n🌱 Importing crop characteristics...")
    try:
        df = pd.read_csv(f"{DATASET_DIR}/crop_characteristics.csv")
        
        # Prepare data for crop_characteristics table
        df_char = pd.DataFrame({
            'crop_type': df['crop_type'],
            'growth_days': df['growth_days'],
            'water_requirement': df['water_requirement'],
            'suitable_regions': None,  # Not in source data
            'soil_preference': df['soil_preference'],
            'investment_cost': df['investment_cost'],
            'risk_level': df['risk_level'],
            'seasonal_type': df['seasonal_type'],
            'crop_category': df['crop_category'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        # Remove duplicates (keep first occurrence)
        df_char = df_char.drop_duplicates(subset=['crop_type'], keep='first')
        
        # Import to database
        df_char.to_sql('crop_characteristics', engine, if_exists='append', index=False)
        
        print(f"✅ Imported {len(df_char)} crop characteristic records")
        return True
    except Exception as e:
        print(f"❌ Error importing crop characteristics: {e}")
        return False

def get_database_stats():
    """Get statistics of imported data"""
    print("\n📈 Database Statistics:")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Count records in each table
        tables = [
            ('crop_prices', 'Crop Prices'),
            ('weather_data', 'Weather Data'),
            ('crop_cultivation', 'Crop Cultivation'),
            ('crop_characteristics', 'Crop Characteristics')
        ]
        
        for table_name, display_name in tables:
            query = text(f"SELECT COUNT(*) FROM {table_name}")
            result = db.execute(query).fetchone()
            count = result[0] if result else 0
            print(f"  {display_name:.<40} {count:>10,} records")
        
        # Count unique provinces
        query = text("""
            SELECT COUNT(DISTINCT province) 
            FROM (
                SELECT province FROM crop_prices
                UNION
                SELECT province FROM weather_data
                UNION
                SELECT province FROM crop_cultivation
            ) AS all_provinces
        """)
        result = db.execute(query).fetchone()
        province_count = result[0] if result else 0
        print(f"  {'Unique Provinces':.<40} {province_count:>10}")
        
        # Count unique crops
        query = text("SELECT COUNT(DISTINCT crop_type) FROM crop_characteristics")
        result = db.execute(query).fetchone()
        crop_count = result[0] if result else 0
        print(f"  {'Unique Crops':.<40} {crop_count:>10}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    finally:
        db.close()

def main():
    """Main import function"""
    print("=" * 60)
    print("🚀 Starting Dataset Import to PostgreSQL")
    print("=" * 60)
    
    # Check if dataset directory exists
    if not os.path.exists(DATASET_DIR):
        print(f"❌ Dataset directory not found: {DATASET_DIR}")
        sys.exit(1)
    
    success_count = 0
    total_count = 4
    
    # Import all datasets
    if import_crop_prices():
        success_count += 1
    
    if import_weather_data():
        success_count += 1
    
    if import_crop_cultivation():
        success_count += 1
    
    if import_crop_characteristics():
        success_count += 1
    
    # Show statistics
    get_database_stats()
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ Import Complete: {success_count}/{total_count} datasets imported successfully")
    print(f"{'=' * 60}\n")
    
    if success_count == total_count:
        print("🎉 All datasets imported successfully!")
        print("💡 You can now use the API with real data")
    else:
        print(f"⚠️  {total_count - success_count} dataset(s) failed to import")
        print("💡 Check the error messages above for details")

if __name__ == "__main__":
    main()

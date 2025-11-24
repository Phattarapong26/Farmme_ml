#!/usr/bin/env python3
"""
Script to update PostgreSQL database with CSV data
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import os

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 4955,
    'database': 'Evena',
    'user': 'postgres',
    'password': '592954'
}

def update_crop_prices():
    """Update crop_prices table"""
    print("📊 Updating crop_prices...")
    
    csv_path = '/Users/medlab/Desktop/ฟาร์มมี่Farm/databaseUpdate/crop_prices_77.csv'
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"   Found {len(df)} records")
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Clear existing data
    cur.execute("TRUNCATE TABLE crop_prices RESTART IDENTITY CASCADE;")
    print("   Cleared existing data")
    
    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        records.append((
            row.get('province'),
            row.get('crop_type'),
            float(row.get('price_per_kg', 0)),
            pd.to_datetime(row.get('date')),
            row.get('source', 'import')
        ))
    
    # Batch insert
    insert_query = """
        INSERT INTO crop_prices (province, crop_type, price_per_kg, date, source)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    execute_batch(cur, insert_query, records, page_size=1000)
    conn.commit()
    
    print(f"   ✅ Inserted {len(records)} records")
    
    cur.close()
    conn.close()

def update_weather_data():
    """Update weather_data table"""
    print("🌤️  Updating weather_data...")
    
    csv_path = '/Users/medlab/Desktop/ฟาร์มมี่Farm/databaseUpdate/weather_data_77.csv'
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"   Found {len(df)} records")
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Clear existing data
    cur.execute("TRUNCATE TABLE weather_data RESTART IDENTITY CASCADE;")
    print("   Cleared existing data")
    
    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        records.append((
            row.get('province'),
            pd.to_datetime(row.get('date')),
            float(row.get('temperature_celsius', 0)) if pd.notna(row.get('temperature_celsius')) else None,
            float(row.get('rainfall_mm', 0)) if pd.notna(row.get('rainfall_mm')) else None,
            row.get('source', 'import')
        ))
    
    # Batch insert
    insert_query = """
        INSERT INTO weather_data (province, date, temperature_celsius, rainfall_mm, source)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    execute_batch(cur, insert_query, records, page_size=1000)
    conn.commit()
    
    print(f"   ✅ Inserted {len(records)} records")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 Starting database update...\n")
    
    try:
        update_crop_prices()
        print()
        update_weather_data()
        print("\n✅ Database update completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

# -*- coding: utf-8 -*-
"""
Add indexes for dashboard queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def add_indexes():
    """Add indexes to improve dashboard query performance"""
    
    indexes = [
        # Index for crop_prices queries
        "CREATE INDEX IF NOT EXISTS idx_crop_prices_province_date ON crop_prices(province, date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_crop_prices_province ON crop_prices(province);",
        
        # Index for weather_data queries
        "CREATE INDEX IF NOT EXISTS idx_weather_data_province_date ON weather_data(province, date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_weather_data_province ON weather_data(province);",
    ]
    
    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                print(f"Creating index: {idx_sql}")
                conn.execute(text(idx_sql))
                conn.commit()
                print("✅ Success")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n✅ All indexes created successfully!")

if __name__ == "__main__":
    add_indexes()

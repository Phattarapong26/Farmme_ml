#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add database indexes for province columns to improve query performance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_province_indexes():
    """Add indexes for province columns in multiple tables"""
    try:
        with engine.connect() as conn:
            logger.info("🔧 Adding database indexes for province columns...")
            
            # Check and add index for crop_prices.province
            logger.info("📊 Checking crop_prices table...")
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'crop_prices' AND indexname = 'idx_crop_prices_province'
            """))
            
            if result.fetchone() is None:
                logger.info("  Adding index idx_crop_prices_province...")
                conn.execute(text("""
                    CREATE INDEX idx_crop_prices_province ON crop_prices(province)
                """))
                conn.commit()
                logger.info("  ✅ Index added successfully")
            else:
                logger.info("  ✅ Index already exists")
            
            # Check and add index for weather_data.province
            logger.info("🌤️  Checking weather_data table...")
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'weather_data' AND indexname = 'idx_weather_data_province'
            """))
            
            if result.fetchone() is None:
                logger.info("  Adding index idx_weather_data_province...")
                conn.execute(text("""
                    CREATE INDEX idx_weather_data_province ON weather_data(province)
                """))
                conn.commit()
                logger.info("  ✅ Index added successfully")
            else:
                logger.info("  ✅ Index already exists")
            
            # Check and add index for users.province
            logger.info("👤 Checking users table...")
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'users' AND indexname = 'idx_users_province'
            """))
            
            if result.fetchone() is None:
                logger.info("  Adding index idx_users_province...")
                conn.execute(text("""
                    CREATE INDEX idx_users_province ON users(province)
                """))
                conn.commit()
                logger.info("  ✅ Index added successfully")
            else:
                logger.info("  ✅ Index already exists")
            
            # Check and add index for crop_cultivation.province (if table exists)
            logger.info("🌱 Checking crop_cultivation table...")
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'crop_cultivation'
                )
            """))
            
            if result.fetchone()[0]:
                result = conn.execute(text("""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'crop_cultivation' AND indexname = 'idx_crop_cultivation_province'
                """))
                
                if result.fetchone() is None:
                    logger.info("  Adding index idx_crop_cultivation_province...")
                    conn.execute(text("""
                        CREATE INDEX idx_crop_cultivation_province ON crop_cultivation(province)
                    """))
                    conn.commit()
                    logger.info("  ✅ Index added successfully")
                else:
                    logger.info("  ✅ Index already exists")
            else:
                logger.info("  ⚠️  Table does not exist, skipping")
            
            logger.info("\n✅ All province indexes added successfully!")
            
            # Test query performance
            logger.info("\n🧪 Testing query performance...")
            result = conn.execute(text("""
                EXPLAIN ANALYZE
                SELECT DISTINCT province 
                FROM (
                    SELECT province FROM crop_prices
                    UNION
                    SELECT province FROM weather_data
                ) AS all_provinces
                ORDER BY province
                LIMIT 10
            """))
            
            logger.info("Query plan:")
            for row in result:
                logger.info(f"  {row[0]}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding indexes: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting database index creation...\n")
    
    if add_province_indexes():
        logger.info("\n✅ Database indexes created successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Failed to create database indexes")
        sys.exit(1)

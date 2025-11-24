#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix database schema - Add missing password column
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_users_table():
    """Add password column to users table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if password column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='password'
            """))
            
            if result.fetchone() is None:
                logger.info("❌ Password column not found. Adding it...")
                
                # Add password column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password VARCHAR(255)
                """))
                conn.commit()
                
                logger.info("✅ Password column added successfully!")
            else:
                logger.info("✅ Password column already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing users table: {e}")
        return False

def check_all_columns():
    """Check all columns in users table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='users'
                ORDER BY ordinal_position
            """))
            
            logger.info("\n📊 Current users table schema:")
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking columns: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Starting database schema fix...")
    logger.info("-" * 50)
    
    # Check current schema
    logger.info("\n1️⃣ Checking current schema...")
    check_all_columns()
    
    # Fix users table
    logger.info("\n2️⃣ Fixing users table...")
    if fix_users_table():
        logger.info("\n3️⃣ Verifying changes...")
        check_all_columns()
        logger.info("\n✅ Database schema fixed successfully!")
    else:
        logger.error("\n❌ Failed to fix database schema")
        sys.exit(1)

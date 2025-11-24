#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix chat_sessions table schema - Add missing user_id column
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_chat_sessions_table():
    """Add user_id column to chat_sessions table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if user_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='chat_sessions' AND column_name='user_id'
            """))
            
            if result.fetchone() is None:
                logger.info("❌ user_id column not found. Adding it...")
                
                # Add user_id column
                conn.execute(text("""
                    ALTER TABLE chat_sessions 
                    ADD COLUMN user_id INTEGER
                """))
                
                # Add index for better performance
                conn.execute(text("""
                    CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id)
                """))
                
                conn.commit()
                
                logger.info("✅ user_id column and index added successfully!")
            else:
                logger.info("✅ user_id column already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing chat_sessions table: {e}")
        return False

def check_all_columns():
    """Check all columns in chat_sessions table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name='chat_sessions'
                ORDER BY ordinal_position
            """))
            
            logger.info("\n📊 Current chat_sessions table schema:")
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking columns: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Starting chat_sessions schema fix...")
    logger.info("-" * 50)
    
    # Check current schema
    logger.info("\n1️⃣ Checking current schema...")
    check_all_columns()
    
    # Fix chat_sessions table
    logger.info("\n2️⃣ Fixing chat_sessions table...")
    if fix_chat_sessions_table():
        logger.info("\n3️⃣ Verifying changes...")
        check_all_columns()
        logger.info("\n✅ chat_sessions schema fixed successfully!")
    else:
        logger.error("\n❌ Failed to fix chat_sessions schema")
        sys.exit(1)

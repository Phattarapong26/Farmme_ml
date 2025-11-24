# -*- coding: utf-8 -*-
"""
Create Tables in Supabase
Uses SQLAlchemy models to create all tables
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create all tables in Supabase"""
    logger.info("=" * 60)
    logger.info("🏗️  Creating Tables in Supabase")
    logger.info("=" * 60)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ All tables created successfully!")
        logger.info("\n📋 Tables created:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  ✅ {table.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

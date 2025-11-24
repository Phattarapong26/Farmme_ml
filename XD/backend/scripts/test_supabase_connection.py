# -*- coding: utf-8 -*-
"""
Test Supabase Connection
Verifies database connectivity and SSL/TLS connection
"""

import os
import sys
import time
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test Supabase database connection"""
    logger.info("=" * 60)
    logger.info("🔌 Testing Supabase Connection")
    logger.info("=" * 60)
    
    try:
        # Import config to get DATABASE_URL
        from config import DATABASE_URL
        
        # Check if using Supabase
        if "supabase" not in DATABASE_URL:
            logger.warning("⚠️  DATABASE_URL does not contain 'supabase'")
            logger.warning("   Current URL might be local PostgreSQL")
            logger.info(f"\n📍 Current DATABASE_URL: {DATABASE_URL[:50]}...")
        else:
            logger.info("✅ Using Supabase connection string")
        
        # Create test engine
        logger.info("\n🔄 Creating database engine...")
        start_time = time.time()
        
        engine = create_engine(
            DATABASE_URL,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 30,
                "application_name": "farmme_connection_test"
            }
        )
        
        # Test connection
        logger.info("🔄 Testing connection...")
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            connection_time = time.time() - start_time
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Connection Successful!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Connection time: {connection_time:.2f} seconds")
            logger.info(f"🗄️  PostgreSQL version: {version[:50]}...")
            
            # Test SSL/TLS
            result = conn.execute(text("SHOW ssl"))
            ssl_status = result.scalar()
            logger.info(f"🔒 SSL/TLS: {ssl_status}")
            
            # Get current database
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            logger.info(f"📊 Database: {db_name}")
            
            # Get current user
            result = conn.execute(text("SELECT current_user"))
            user = result.scalar()
            logger.info(f"👤 User: {user}")
            
            # Test write permission
            logger.info("\n🔄 Testing write permissions...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS _connection_test (
                        id SERIAL PRIMARY KEY,
                        test_value TEXT
                    )
                """))
                conn.execute(text("INSERT INTO _connection_test (test_value) VALUES ('test')"))
                conn.execute(text("DROP TABLE _connection_test"))
                conn.commit()
                logger.info("✅ Write permissions: OK")
            except Exception as e:
                logger.warning(f"⚠️  Write test failed: {e}")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ All Connection Tests Passed")
            logger.info("=" * 60)
            
            return True
            
    except OperationalError as e:
        logger.error("\n" + "=" * 60)
        logger.error("❌ Connection Failed")
        logger.error("=" * 60)
        logger.error(f"\nError: {e}")
        logger.error("\n💡 Troubleshooting:")
        logger.error("1. Check DATABASE_URL in .env file")
        logger.error("2. Verify Supabase password is correct")
        logger.error("3. Check internet connection")
        logger.error("4. Verify Supabase project is active")
        logger.error("5. Check firewall settings")
        return False
        
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_latency():
    """Test connection latency"""
    logger.info("\n" + "=" * 60)
    logger.info("⏱️  Testing Connection Latency")
    logger.info("=" * 60)
    
    try:
        from config import DATABASE_URL
        engine = create_engine(DATABASE_URL, pool_size=1)
        
        latencies = []
        for i in range(5):
            start = time.time()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000  # Convert to ms
            latencies.append(latency)
            logger.info(f"  Test {i+1}: {latency:.2f} ms")
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        logger.info(f"\n📊 Latency Statistics:")
        logger.info(f"  Average: {avg_latency:.2f} ms")
        logger.info(f"  Min: {min_latency:.2f} ms")
        logger.info(f"  Max: {max_latency:.2f} ms")
        
        if avg_latency < 100:
            logger.info("✅ Excellent latency")
        elif avg_latency < 300:
            logger.info("✅ Good latency")
        elif avg_latency < 500:
            logger.info("⚠️  Moderate latency")
        else:
            logger.info("⚠️  High latency - consider optimization")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Latency test failed: {e}")
        return False

def main():
    """Main function"""
    success = test_connection()
    
    if success:
        test_latency()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Connection Test Complete")
        logger.info("=" * 60)
        logger.info("\n📋 Next Steps:")
        logger.info("1. Create tables: python backend/scripts/import_to_supabase.py")
        logger.info("2. Or use existing import script if tables exist")
        logger.info("3. Verify migration: python backend/scripts/verify_migration.py\n")
    else:
        logger.info("\n" + "=" * 60)
        logger.info("❌ Connection Test Failed")
        logger.info("=" * 60)
        logger.info("\n💡 Fix the connection issues before proceeding\n")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

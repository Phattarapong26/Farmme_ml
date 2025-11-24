# -*- coding: utf-8 -*-
"""
Import Database to Supabase
Imports SQL dump file into Supabase PostgreSQL database
"""

import os
import sys
import time
import re
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_supabase():
    """Establish connection to Supabase using DATABASE_URL"""
    logger.info("🔌 Connecting to Supabase...")
    
    try:
        from config import DATABASE_URL
        
        if "supabase" not in DATABASE_URL:
            logger.warning("⚠️  DATABASE_URL does not contain 'supabase'")
            logger.warning("   Make sure you've updated .env with Supabase credentials")
        
        # Parse connection string
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        logger.info("✅ Connected to Supabase")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.error("\n💡 Troubleshooting:")
        logger.error("1. Run: python backend/scripts/test_supabase_connection.py")
        logger.error("2. Verify DATABASE_URL in .env")
        logger.error("3. Check Supabase password")
        raise

def parse_sql_file(sql_file):
    """Parse SQL dump file and separate CREATE and INSERT statements"""
    logger.info(f"📖 Parsing SQL file: {sql_file.name}")
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into statements
        create_statements = []
        insert_statements = []
        
        # Extract CREATE TABLE statements
        create_pattern = r'CREATE TABLE.*?;'
        creates = re.findall(create_pattern, content, re.DOTALL | re.IGNORECASE)
        create_statements.extend(creates)
        
        # Extract CREATE INDEX statements
        index_pattern = r'CREATE INDEX.*?;'
        indexes = re.findall(index_pattern, content, re.DOTALL | re.IGNORECASE)
        create_statements.extend(indexes)
        
        # Extract INSERT statements
        insert_pattern = r'INSERT INTO.*?;'
        inserts = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
        insert_statements.extend(inserts)
        
        logger.info(f"  📊 Found {len(creates)} CREATE TABLE statements")
        logger.info(f"  📊 Found {len(indexes)} CREATE INDEX statements")
        logger.info(f"  📊 Found {len(inserts)} INSERT statements")
        
        return create_statements, insert_statements
        
    except Exception as e:
        logger.error(f"❌ Failed to parse SQL file: {e}")
        raise

def create_tables(conn, create_statements):
    """Execute CREATE TABLE statements"""
    logger.info("\n🏗️  Creating tables in Supabase...")
    
    cursor = conn.cursor()
    success_count = 0
    error_count = 0
    
    for statement in create_statements:
        try:
            # Extract table name for logging
            table_match = re.search(r'CREATE TABLE\s+(\w+)', statement, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else "unknown"
            
            cursor.execute(statement)
            logger.info(f"  ✅ Created: {table_name}")
            success_count += 1
            
        except psycopg2.errors.DuplicateTable:
            logger.info(f"  ⏭️  Table {table_name} already exists (skipping)")
            success_count += 1
        except Exception as e:
            logger.error(f"  ❌ Failed to create {table_name}: {e}")
            error_count += 1
    
    cursor.close()
    
    logger.info(f"\n📊 Table creation: {success_count} succeeded, {error_count} failed")
    return success_count, error_count

def import_data_batch(conn, insert_statements, batch_size=100):
    """Import data in batches with error handling"""
    logger.info(f"\n📦 Importing data (batch size: {batch_size})...")
    
    cursor = conn.cursor()
    total_inserts = len(insert_statements)
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    for i, statement in enumerate(insert_statements, 1):
        try:
            # Extract table name for progress
            table_match = re.search(r'INSERT INTO\s+(\w+)', statement, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else "unknown"
            
            cursor.execute(statement)
            success_count += 1
            
            # Progress update every batch_size
            if i % batch_size == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                eta = (total_inserts - i) / rate if rate > 0 else 0
                
                logger.info(f"  📊 Progress: {i}/{total_inserts} ({i*100//total_inserts}%) "
                          f"| Rate: {rate:.1f} stmt/s | ETA: {eta:.0f}s")
            
        except psycopg2.errors.UniqueViolation:
            # Duplicate key - skip
            skipped_count += 1
        except Exception as e:
            logger.error(f"  ❌ Error in statement {i}: {str(e)[:100]}")
            error_count += 1
            
            # Stop if too many errors
            if error_count > 100:
                logger.error("❌ Too many errors, stopping import")
                break
    
    cursor.close()
    
    elapsed = time.time() - start_time
    logger.info(f"\n📊 Import complete in {elapsed:.1f}s")
    logger.info(f"  ✅ Success: {success_count:,}")
    logger.info(f"  ⏭️  Skipped (duplicates): {skipped_count:,}")
    logger.info(f"  ❌ Errors: {error_count:,}")
    
    return success_count, skipped_count, error_count

def retry_with_backoff(func, max_retries=3, *args, **kwargs):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"⚠️  Attempt {attempt + 1} failed: {e}")
                logger.info(f"🔄 Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

def find_latest_export():
    """Find the most recent export file"""
    export_dir = Path(__file__).parent / "exports"
    
    if not export_dir.exists():
        return None
    
    export_files = list(export_dir.glob("farmme_export_*.sql"))
    
    if not export_files:
        return None
    
    # Sort by modification time, newest first
    export_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return export_files[0]

def main():
    """Main import function"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Supabase Import")
    logger.info("=" * 60)
    
    # Find export file
    export_file = find_latest_export()
    
    if not export_file:
        logger.error("❌ No export file found")
        logger.error("💡 Run: python backend/scripts/export_database.py")
        return False
    
    logger.info(f"📁 Using export file: {export_file.name}")
    logger.info(f"📅 Created: {time.ctime(export_file.stat().st_mtime)}")
    
    try:
        # Connect to Supabase
        conn = retry_with_backoff(connect_to_supabase)
        
        # Parse SQL file
        create_statements, insert_statements = parse_sql_file(export_file)
        
        # Create tables
        table_success, table_errors = create_tables(conn, create_statements)
        
        if table_errors > 0:
            logger.warning(f"⚠️  {table_errors} table creation errors")
            response = input("\nContinue with data import? (y/n): ")
            if response.lower() != 'y':
                logger.info("Import cancelled")
                return False
        
        # Import data
        if insert_statements:
            success, skipped, errors = import_data_batch(conn, insert_statements)
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("✅ Import Complete")
            logger.info("=" * 60)
            logger.info(f"📊 Tables: {table_success} created")
            logger.info(f"📊 Records: {success:,} imported, {skipped:,} skipped")
            
            if errors > 0:
                logger.warning(f"⚠️  {errors} errors occurred")
            
            logger.info("\n📋 Next Steps:")
            logger.info("1. Verify migration: python backend/scripts/verify_migration.py")
            logger.info("2. Test application: python backend/run.py")
        else:
            logger.warning("⚠️  No data to import")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

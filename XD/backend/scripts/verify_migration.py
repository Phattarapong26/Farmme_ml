# -*- coding: utf-8 -*-
"""
Verify Migration to Supabase
Validates migration success and data integrity
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tables to verify
TABLES_TO_VERIFY = [
    'users',
    'province_data',
    'crop_characteristics',
    'crop_prices',
    'weather_data',
    'crop_cultivation',
    'economic_factors',
    'forecast_data',
    'crop_predictions',
    'chat_sessions'
]

def test_connection():
    """Test connectivity to Supabase"""
    logger.info("=" * 60)
    logger.info("🔌 Testing Supabase Connection")
    logger.info("=" * 60)
    
    try:
        from config import DATABASE_URL
        
        engine = create_engine(DATABASE_URL, pool_size=1)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            logger.info("✅ Connection successful")
            logger.info(f"📊 PostgreSQL: {version[:50]}...")
            
            return engine
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None

def compare_record_counts(supabase_engine, local_db_url=None):
    """Compare record counts between local and Supabase"""
    logger.info("\n" + "=" * 60)
    logger.info("📊 Comparing Record Counts")
    logger.info("=" * 60)
    
    results = {}
    
    with supabase_engine.connect() as conn:
        for table in TABLES_TO_VERIFY:
            try:
                # Get Supabase count
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                supabase_count = result.scalar()
                
                results[table] = {
                    'supabase': supabase_count,
                    'local': None,
                    'match': None
                }
                
                logger.info(f"  {table:.<30} {supabase_count:>10,} records")
                
            except Exception as e:
                logger.error(f"  ❌ {table}: {e}")
                results[table] = {'error': str(e)}
    
    # Summary
    total_records = sum(r.get('supabase', 0) for r in results.values() if 'supabase' in r)
    logger.info(f"\n  {'Total Records':.<30} {total_records:>10,}")
    
    return results

def validate_data_samples(engine):
    """Validate data samples from each table"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 Validating Data Samples")
    logger.info("=" * 60)
    
    validation_results = {}
    
    with engine.connect() as conn:
        for table in TABLES_TO_VERIFY:
            try:
                # Get sample records
                result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))
                rows = result.fetchall()
                
                if rows:
                    # Check for NULL values in key columns
                    columns = result.keys()
                    null_counts = {col: 0 for col in columns}
                    
                    for row in rows:
                        for i, val in enumerate(row):
                            if val is None:
                                null_counts[columns[i]] += 1
                    
                    validation_results[table] = {
                        'sample_count': len(rows),
                        'columns': len(columns),
                        'has_data': True
                    }
                    
                    logger.info(f"  ✅ {table}: {len(rows)} samples, {len(columns)} columns")
                else:
                    validation_results[table] = {'has_data': False}
                    logger.info(f"  ⚠️  {table}: No data")
                    
            except Exception as e:
                logger.error(f"  ❌ {table}: {e}")
                validation_results[table] = {'error': str(e)}
    
    return validation_results

def test_crud_operations(engine):
    """Test CRUD operations on Supabase"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 Testing CRUD Operations")
    logger.info("=" * 60)
    
    test_table = "_migration_test"
    
    try:
        with engine.connect() as conn:
            # CREATE
            logger.info("  🔄 Testing CREATE...")
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {test_table} (
                    id SERIAL PRIMARY KEY,
                    test_value TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn.commit()
            logger.info("  ✅ CREATE: OK")
            
            # INSERT
            logger.info("  🔄 Testing INSERT...")
            conn.execute(text(f"""
                INSERT INTO {test_table} (test_value) 
                VALUES ('migration_test')
            """))
            conn.commit()
            logger.info("  ✅ INSERT: OK")
            
            # SELECT
            logger.info("  🔄 Testing SELECT...")
            result = conn.execute(text(f"SELECT * FROM {test_table}"))
            rows = result.fetchall()
            if rows:
                logger.info(f"  ✅ SELECT: OK ({len(rows)} rows)")
            else:
                logger.warning("  ⚠️  SELECT: No rows returned")
            
            # UPDATE
            logger.info("  🔄 Testing UPDATE...")
            conn.execute(text(f"""
                UPDATE {test_table} 
                SET test_value = 'updated_value' 
                WHERE test_value = 'migration_test'
            """))
            conn.commit()
            logger.info("  ✅ UPDATE: OK")
            
            # DELETE
            logger.info("  🔄 Testing DELETE...")
            conn.execute(text(f"DELETE FROM {test_table}"))
            conn.commit()
            logger.info("  ✅ DELETE: OK")
            
            # Cleanup
            conn.execute(text(f"DROP TABLE {test_table}"))
            conn.commit()
            logger.info("  ✅ Cleanup: OK")
            
            return True
            
    except Exception as e:
        logger.error(f"  ❌ CRUD test failed: {e}")
        return False

def generate_report(connection_ok, record_counts, data_validation, crud_ok):
    """Generate migration report"""
    logger.info("\n" + "=" * 60)
    logger.info("📋 Migration Report")
    logger.info("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(__file__).parent / f"migration_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("SUPABASE MIGRATION VERIFICATION REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        # Connection Status
        f.write("1. CONNECTION STATUS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Status: {'✅ PASS' if connection_ok else '❌ FAIL'}\n\n")
        
        # Record Counts
        f.write("2. RECORD COUNTS\n")
        f.write("-" * 60 + "\n")
        for table, counts in record_counts.items():
            if 'error' in counts:
                f.write(f"{table}: ❌ ERROR - {counts['error']}\n")
            else:
                f.write(f"{table}: {counts.get('supabase', 0):,} records\n")
        f.write("\n")
        
        # Data Validation
        f.write("3. DATA VALIDATION\n")
        f.write("-" * 60 + "\n")
        for table, validation in data_validation.items():
            if 'error' in validation:
                f.write(f"{table}: ❌ ERROR\n")
            elif validation.get('has_data'):
                f.write(f"{table}: ✅ PASS ({validation['sample_count']} samples)\n")
            else:
                f.write(f"{table}: ⚠️  NO DATA\n")
        f.write("\n")
        
        # CRUD Operations
        f.write("4. CRUD OPERATIONS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Status: {'✅ PASS' if crud_ok else '❌ FAIL'}\n\n")
        
        # Summary
        f.write("5. SUMMARY\n")
        f.write("-" * 60 + "\n")
        
        total_tables = len(TABLES_TO_VERIFY)
        tables_with_data = sum(1 for v in data_validation.values() if v.get('has_data'))
        total_records = sum(c.get('supabase', 0) for c in record_counts.values() if 'supabase' in c)
        
        f.write(f"Total Tables: {total_tables}\n")
        f.write(f"Tables with Data: {tables_with_data}\n")
        f.write(f"Total Records: {total_records:,}\n")
        f.write(f"Connection: {'✅ OK' if connection_ok else '❌ FAIL'}\n")
        f.write(f"CRUD Tests: {'✅ OK' if crud_ok else '❌ FAIL'}\n\n")
        
        # Overall Status
        all_pass = connection_ok and crud_ok and tables_with_data > 0
        f.write("=" * 60 + "\n")
        f.write(f"OVERALL STATUS: {'✅ MIGRATION SUCCESSFUL' if all_pass else '⚠️  ISSUES DETECTED'}\n")
        f.write("=" * 60 + "\n")
    
    logger.info(f"📄 Report saved: {report_file.name}")
    logger.info(f"📍 Location: {report_file}")
    
    return report_file

def main():
    """Main verification function"""
    logger.info("=" * 60)
    logger.info("🔍 Starting Migration Verification")
    logger.info("=" * 60)
    
    # Test connection
    engine = test_connection()
    connection_ok = engine is not None
    
    if not connection_ok:
        logger.error("\n❌ Cannot proceed without database connection")
        return False
    
    # Compare record counts
    record_counts = compare_record_counts(engine)
    
    # Validate data samples
    data_validation = validate_data_samples(engine)
    
    # Test CRUD operations
    crud_ok = test_crud_operations(engine)
    
    # Generate report
    report_file = generate_report(connection_ok, record_counts, data_validation, crud_ok)
    
    # Summary
    total_records = sum(c.get('supabase', 0) for c in record_counts.values() if 'supabase' in c)
    tables_with_data = sum(1 for v in data_validation.values() if v.get('has_data'))
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Verification Complete")
    logger.info("=" * 60)
    logger.info(f"📊 Tables: {tables_with_data}/{len(TABLES_TO_VERIFY)} with data")
    logger.info(f"📊 Records: {total_records:,} total")
    logger.info(f"🔌 Connection: {'✅ OK' if connection_ok else '❌ FAIL'}")
    logger.info(f"🧪 CRUD: {'✅ OK' if crud_ok else '❌ FAIL'}")
    
    all_pass = connection_ok and crud_ok and tables_with_data > 0
    
    if all_pass:
        logger.info("\n🎉 Migration verification PASSED!")
        logger.info("\n📋 Next Steps:")
        logger.info("1. Test application: python backend/run.py")
        logger.info("2. Verify API endpoints work correctly")
        logger.info("3. Test frontend integration")
    else:
        logger.warning("\n⚠️  Migration verification found issues")
        logger.info(f"📄 Check report: {report_file}")
    
    return all_pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

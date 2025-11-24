# -*- coding: utf-8 -*-
"""
Export Database Script
Exports local PostgreSQL database to SQL dump file for Supabase migration
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from database import engine, SessionLocal, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tables to export in order (respecting foreign key dependencies)
TABLES_TO_EXPORT = [
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

def get_export_filename():
    """Generate timestamped export filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = Path(__file__).parent / "exports"
    export_dir.mkdir(exist_ok=True)
    return export_dir / f"farmme_export_{timestamp}.sql"

def escape_sql_value(value):
    """Escape SQL values for INSERT statements"""
    if value is None:
        return 'NULL'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    else:
        # Escape single quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

def export_schema(db, output_file):
    """Export table schemas (CREATE TABLE statements)"""
    logger.info("📋 Exporting table schemas...")
    
    inspector = inspect(engine)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- FarmMe Database Export\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write("-- Source: Local PostgreSQL\n")
        f.write("-- Target: Supabase\n\n")
        f.write("-- Disable triggers during import\n")
        f.write("SET session_replication_role = 'replica';\n\n")
        
        for table_name in TABLES_TO_EXPORT:
            if table_name not in inspector.get_table_names():
                logger.warning(f"⚠️  Table {table_name} not found, skipping...")
                continue
            
            logger.info(f"  📝 Exporting schema for {table_name}")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            indexes = inspector.get_indexes(table_name)
            
            # Write CREATE TABLE statement
            f.write(f"-- Table: {table_name}\n")
            f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n")
            f.write(f"CREATE TABLE {table_name} (\n")
            
            col_definitions = []
            for col in columns:
                col_def = f"  {col['name']} {col['type']}"
                if not col['nullable']:
                    col_def += " NOT NULL"
                if col.get('default'):
                    col_def += f" DEFAULT {col['default']}"
                col_definitions.append(col_def)
            
            # Add primary key
            if pk_constraint and pk_constraint['constrained_columns']:
                pk_cols = ', '.join(pk_constraint['constrained_columns'])
                col_definitions.append(f"  PRIMARY KEY ({pk_cols})")
            
            f.write(',\n'.join(col_definitions))
            f.write("\n);\n\n")
            
            # Add indexes
            for idx in indexes:
                if not idx['unique']:  # Skip unique indexes (handled by constraints)
                    idx_cols = ', '.join(idx['column_names'])
                    f.write(f"CREATE INDEX IF NOT EXISTS {idx['name']} ON {table_name} ({idx_cols});\n")
            
            f.write("\n")
    
    logger.info("✅ Schema export complete")

def export_data(db, output_file):
    """Export all table data as INSERT statements"""
    logger.info("📊 Exporting table data...")
    
    total_records = 0
    
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n-- Data Export\n\n")
        
        for table_name in TABLES_TO_EXPORT:
            try:
                # Check if table exists
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                
                if count == 0:
                    logger.info(f"  ⏭️  {table_name}: 0 records (skipping)")
                    continue
                
                logger.info(f"  📦 Exporting {table_name}: {count:,} records")
                
                # Get column names
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                col_names = ', '.join(columns)
                
                # Fetch all data
                query = text(f"SELECT * FROM {table_name}")
                rows = db.execute(query).fetchall()
                
                # Write INSERT statements in batches
                f.write(f"-- Data for {table_name}\n")
                batch_size = 100
                
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    
                    f.write(f"INSERT INTO {table_name} ({col_names}) VALUES\n")
                    
                    values_list = []
                    for row in batch:
                        values = ', '.join([escape_sql_value(val) for val in row])
                        values_list.append(f"  ({values})")
                    
                    f.write(',\n'.join(values_list))
                    f.write("\nON CONFLICT DO NOTHING;\n\n")
                
                total_records += count
                
            except Exception as e:
                logger.error(f"❌ Error exporting {table_name}: {e}")
                continue
        
        f.write("\n-- Re-enable triggers\n")
        f.write("SET session_replication_role = 'origin';\n\n")
        f.write(f"-- Export complete: {total_records:,} total records\n")
    
    logger.info(f"✅ Data export complete: {total_records:,} total records")
    return total_records

def validate_export(output_file, expected_records):
    """Validate export file integrity"""
    logger.info("🔍 Validating export file...")
    
    try:
        # Check file exists and has content
        if not os.path.exists(output_file):
            logger.error("❌ Export file not found")
            return False
        
        file_size = os.path.getsize(output_file)
        if file_size == 0:
            logger.error("❌ Export file is empty")
            return False
        
        logger.info(f"  📄 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        # Count INSERT statements
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            insert_count = content.count('INSERT INTO')
            create_count = content.count('CREATE TABLE')
        
        logger.info(f"  📊 CREATE TABLE statements: {create_count}")
        logger.info(f"  📊 INSERT statements: {insert_count}")
        
        if create_count == 0:
            logger.error("❌ No CREATE TABLE statements found")
            return False
        
        if insert_count == 0 and expected_records > 0:
            logger.error("❌ No INSERT statements found but records expected")
            return False
        
        logger.info("✅ Export file validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False

def main():
    """Main export function"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Database Export")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Generate export filename
        output_file = get_export_filename()
        logger.info(f"📁 Export file: {output_file}")
        
        # Export schema
        export_schema(db, output_file)
        
        # Export data
        total_records = export_data(db, output_file)
        
        # Validate export
        if validate_export(output_file, total_records):
            logger.info("=" * 60)
            logger.info("✅ Export Complete!")
            logger.info(f"📁 File: {output_file}")
            logger.info(f"📊 Records: {total_records:,}")
            logger.info("=" * 60)
            return True
        else:
            logger.error("=" * 60)
            logger.error("❌ Export validation failed")
            logger.error("=" * 60)
            return False
            
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

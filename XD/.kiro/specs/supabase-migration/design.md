# Design Document: Supabase Database Migration

## Overview

This design outlines the migration strategy for moving the FarmMe application database from local PostgreSQL to Supabase cloud database. The migration will be performed in phases to minimize risk and ensure data integrity. The solution includes scripts for data export, configuration updates, data import, and verification.

## Architecture

### Current Architecture
```
FarmMe Backend (FastAPI)
    ↓
SQLAlchemy ORM
    ↓
Local PostgreSQL (localhost:5432)
    ↓
Database: Evena
```

### Target Architecture
```
FarmMe Backend (FastAPI)
    ↓
SQLAlchemy ORM
    ↓
Supabase PostgreSQL (inhanxxglxnjbugppulg.supabase.co)
    ↓
Cloud Database with API Layer
```

### Migration Flow
```
1. Export Phase
   Local PostgreSQL → SQL Dump File

2. Configuration Phase
   Update .env files → New DATABASE_URL

3. Import Phase
   SQL Dump File → Supabase Database

4. Verification Phase
   Test Connectivity → Validate Data → Generate Report
```

## Components and Interfaces

### 1. Export Script (`export_database.py`)

**Purpose**: Export all data from local PostgreSQL to SQL dump file

**Key Functions**:
- `export_schema()`: Export table schemas (CREATE TABLE statements)
- `export_data()`: Export all table data as INSERT statements
- `validate_export()`: Verify export file integrity

**Output**: `farmme_export_YYYYMMDD_HHMMSS.sql`

**Tables to Export**:
- users
- crop_predictions
- chat_sessions
- forecast_data
- province_data
- crop_prices
- crop_characteristics
- weather_data
- economic_factors
- crop_cultivation

### 2. Configuration Manager (`update_config.py`)

**Purpose**: Update environment variables to use Supabase connection

**Key Functions**:
- `get_supabase_connection_string()`: Build connection string from Supabase credentials
- `update_env_file()`: Update backend/.env with new DATABASE_URL
- `backup_env_file()`: Create backup of original .env file
- `validate_connection()`: Test connection to Supabase

**Supabase Connection String Format**:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Given Credentials**:
- URL: `https://inhanxxglxnjbugppulg.supabase.co`
- Anon Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Project Ref: `inhanxxglxnjbugppulg`

### 3. Import Script (`import_to_supabase.py`)

**Purpose**: Import SQL dump into Supabase database

**Key Functions**:
- `connect_to_supabase()`: Establish connection using psycopg2
- `create_tables()`: Execute CREATE TABLE statements
- `import_data()`: Execute INSERT statements in batches
- `handle_conflicts()`: Resolve duplicate key conflicts
- `log_progress()`: Track import progress

**Import Strategy**:
- Use transactions for data integrity
- Batch inserts (1000 records per batch)
- Skip duplicate records (ON CONFLICT DO NOTHING)
- Log errors without stopping entire import

### 4. Verification Script (`verify_migration.py`)

**Purpose**: Validate migration success and data integrity

**Key Functions**:
- `test_connection()`: Verify Supabase connectivity
- `compare_record_counts()`: Compare table row counts
- `validate_data_samples()`: Compare sample data between databases
- `test_crud_operations()`: Test Create, Read, Update, Delete
- `generate_report()`: Create migration report

**Validation Checks**:
- Connection status
- Table existence
- Record count matching (±5% tolerance)
- Data type consistency
- Sample data comparison (10 random records per table)
- CRUD operation success

### 5. Database Module Updates (`database.py`)

**Changes Required**:
- No code changes needed (SQLAlchemy handles connection string)
- Connection pooling settings may need adjustment for cloud database
- Add connection retry logic for network issues

**Recommended Pool Settings for Supabase**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Reduced from 20 for cloud
    max_overflow=20,       # Reduced from 30
    pool_pre_ping=True,    # Keep for connection health checks
    pool_recycle=3600,     # Keep for long-running connections
    connect_args={
        "connect_timeout": 30,  # Increased for cloud latency
        "application_name": "farmme_api"
    }
)
```

## Data Models

### No Schema Changes Required

All existing SQLAlchemy models remain unchanged:
- User
- CropPrediction
- ChatSession
- ForecastData
- ProvinceData
- CropPrice
- CropCharacteristics
- WeatherData
- EconomicFactors
- CropCultivation

### Data Volume Estimates

Based on existing import script:
- crop_prices: ~50,000-100,000 records
- weather_data: ~50,000-100,000 records
- crop_cultivation: ~10,000-20,000 records
- crop_characteristics: ~50-100 records
- Other tables: Minimal data (user-generated)

**Total Estimated Size**: 100,000-200,000 records

## Error Handling

### Export Phase Errors

1. **Connection Failure**
   - Error: Cannot connect to local PostgreSQL
   - Solution: Verify PostgreSQL is running, check credentials
   - Fallback: Manual pg_dump command

2. **Disk Space**
   - Error: Insufficient disk space for export file
   - Solution: Check available space, clean up old files
   - Fallback: Export tables individually

3. **Data Corruption**
   - Error: Invalid data types or encoding issues
   - Solution: Clean data before export, handle special characters
   - Fallback: Export as CSV and convert to SQL

### Import Phase Errors

1. **Connection Timeout**
   - Error: Cannot connect to Supabase
   - Solution: Check internet connection, verify credentials
   - Retry: 3 attempts with exponential backoff

2. **Duplicate Keys**
   - Error: Primary key constraint violation
   - Solution: Use ON CONFLICT DO NOTHING
   - Log: Record skipped entries

3. **Data Type Mismatch**
   - Error: Column type incompatibility
   - Solution: Cast data types in SQL statements
   - Fallback: Manual data transformation

4. **Transaction Rollback**
   - Error: Import fails mid-transaction
   - Solution: Use smaller batch sizes
   - Recovery: Resume from last successful batch

### Verification Phase Errors

1. **Record Count Mismatch**
   - Error: Different number of records
   - Solution: Investigate missing/duplicate records
   - Action: Re-import affected tables

2. **Data Inconsistency**
   - Error: Sample data doesn't match
   - Solution: Check data transformation issues
   - Action: Manual data comparison and correction

## Testing Strategy

### Pre-Migration Testing

1. **Backup Verification**
   - Create full backup of local database
   - Test backup restoration
   - Verify backup file integrity

2. **Connection Testing**
   - Test Supabase connection from backend
   - Verify credentials and permissions
   - Check network latency

### Migration Testing

1. **Dry Run**
   - Export data to file
   - Validate export file
   - Test import on empty Supabase database
   - Verify without affecting production

2. **Incremental Testing**
   - Import one table at a time
   - Verify each table before proceeding
   - Test application functionality after each table

### Post-Migration Testing

1. **Functional Testing**
   - Test all API endpoints
   - Verify data retrieval
   - Test data creation/updates
   - Check query performance

2. **Integration Testing**
   - Test frontend-backend integration
   - Verify ML model predictions
   - Test chat functionality
   - Validate forecast generation

3. **Performance Testing**
   - Measure query response times
   - Compare with local database performance
   - Identify slow queries
   - Optimize if needed

### Rollback Strategy

If migration fails:
1. Restore DATABASE_URL to local PostgreSQL
2. Restart backend application
3. Verify local database is intact
4. Investigate and fix issues
5. Retry migration

## Security Considerations

### Credential Management

1. **Environment Variables**
   - Store Supabase credentials in .env file
   - Never commit credentials to git
   - Use different credentials for development/production

2. **Connection Security**
   - Use SSL/TLS for database connections
   - Verify Supabase certificate
   - Use connection pooling to limit connections

### Access Control

1. **Database Permissions**
   - Use least privilege principle
   - Create separate user for application
   - Limit permissions to required tables only

2. **API Security**
   - Keep Supabase anon key secure
   - Use Row Level Security (RLS) if needed
   - Monitor database access logs

## Performance Optimization

### Connection Pooling

- Reduce pool size for cloud database (10 vs 20)
- Increase connection timeout (30s vs 10s)
- Enable pool pre-ping for connection health

### Query Optimization

- Maintain existing indexes
- Add indexes for frequently queried columns
- Use EXPLAIN ANALYZE for slow queries

### Caching Strategy

- Keep Redis caching for frequently accessed data
- Cache database query results
- Reduce database round trips

## Deployment Plan

### Phase 1: Preparation (Day 1)
1. Backup local database
2. Test Supabase connection
3. Run export script
4. Validate export file

### Phase 2: Configuration (Day 1)
1. Update .env files
2. Test connection with new credentials
3. Verify application startup

### Phase 3: Migration (Day 2)
1. Create tables in Supabase
2. Import data in batches
3. Monitor import progress
4. Handle errors

### Phase 4: Verification (Day 2)
1. Run verification script
2. Test all API endpoints
3. Validate data integrity
4. Performance testing

### Phase 5: Cutover (Day 3)
1. Update production .env
2. Restart backend services
3. Monitor application logs
4. User acceptance testing

## Monitoring and Maintenance

### Post-Migration Monitoring

1. **Database Metrics**
   - Connection count
   - Query performance
   - Error rates
   - Storage usage

2. **Application Metrics**
   - API response times
   - Error logs
   - User activity
   - ML model performance

### Maintenance Tasks

1. **Regular Backups**
   - Daily automated backups via Supabase
   - Weekly manual backup verification
   - Monthly backup restoration tests

2. **Performance Tuning**
   - Monitor slow queries
   - Optimize indexes
   - Review connection pool settings
   - Update statistics

## Documentation Updates

### Files to Update

1. **README.md**
   - Add Supabase setup instructions
   - Update database configuration section
   - Add troubleshooting guide

2. **backend/.env.example**
   - Add Supabase connection string template
   - Document required environment variables

3. **API_DOCUMENTATION.md**
   - Update database architecture diagram
   - Add Supabase-specific notes

## Success Criteria

Migration is considered successful when:

1. ✅ All tables exist in Supabase
2. ✅ Record counts match (±5% tolerance)
3. ✅ Sample data validation passes
4. ✅ All API endpoints work correctly
5. ✅ CRUD operations succeed
6. ✅ Application performance is acceptable
7. ✅ No data loss or corruption
8. ✅ Team members can access shared database

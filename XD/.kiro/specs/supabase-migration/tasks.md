# Implementation Plan: Supabase Database Migration

- [x] 1. Create database export script


  - Create `backend/scripts/export_database.py` to export local PostgreSQL data
  - Implement function to export table schemas (CREATE TABLE statements)
  - Implement function to export all table data as INSERT statements with proper escaping
  - Add validation to check export file integrity and completeness
  - Generate timestamped export file: `farmme_export_YYYYMMDD_HHMMSS.sql`
  - Include all 10 tables: users, crop_predictions, chat_sessions, forecast_data, province_data, crop_prices, crop_characteristics, weather_data, economic_factors, crop_cultivation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_





- [ ] 2. Get Supabase database connection details
  - [ ] 2.1 Access Supabase dashboard to get database credentials
    - Navigate to Supabase project settings
    - Find database connection string in Settings → Database


    - Copy the connection pooler string (port 6543 for connection pooling)
    - Note: Direct connection uses port 5432, pooler uses port 6543




    - _Requirements: 1.4, 3.1_
  
  - [ ] 2.2 Create backup of current .env file
    - Copy `backend/.env` to `backend/.env.backup`


    - Add timestamp to backup filename
    - _Requirements: 3.2_

- [ ] 3. Update configuration files for Supabase
  - [x] 3.1 Update backend/.env with Supabase connection string


    - Replace DATABASE_URL with Supabase PostgreSQL connection string
    - Format: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`
    - Keep local PostgreSQL URL as comment for rollback
    - _Requirements: 3.1, 3.2, 3.4_




  
  - [ ] 3.2 Update database.py connection pool settings
    - Adjust pool_size from 20 to 10 for cloud database

    - Adjust max_overflow from 30 to 20
    - Increase connect_timeout from 10 to 30 seconds for cloud latency
    - Keep pool_pre_ping=True for connection health checks
    - _Requirements: 1.1, 3.3_
  

  - [ ] 3.3 Test Supabase connection
    - Create `backend/scripts/test_supabase_connection.py`
    - Test database connectivity with new credentials
    - Verify SSL/TLS connection
    - Log connection status and latency
    - _Requirements: 3.3, 3.4, 3.5_


- [ ] 4. Create import script for Supabase
  - [ ] 4.1 Create `backend/scripts/import_to_supabase.py`
    - Implement connection to Supabase using psycopg2
    - Parse SQL dump file and separate CREATE and INSERT statements




    - _Requirements: 4.1, 4.2_
  

  - [ ] 4.2 Implement table creation in Supabase
    - Execute CREATE TABLE statements from export file
    - Handle "table already exists" errors gracefully
    - Create tables in correct order to respect foreign key dependencies
    - _Requirements: 4.2_

  
  - [ ] 4.3 Implement data import with batch processing
    - Import data in batches of 1000 records
    - Use transactions for data integrity
    - Implement ON CONFLICT DO NOTHING for duplicate handling
    - Log progress after each batch

    - _Requirements: 4.1, 4.3_
  
  - [ ] 4.4 Add error handling and recovery
    - Catch and log import errors without stopping entire process
    - Implement retry logic for transient failures (3 attempts with exponential backoff)
    - Continue with next table if one fails
    - Generate error report at the end

    - _Requirements: 4.5_

- [ ] 5. Create verification script
  - [ ] 5.1 Create `backend/scripts/verify_migration.py`
    - Test connectivity to both local and Supabase databases


    - _Requirements: 5.1, 5.2_
  
  - [ ] 5.2 Implement record count comparison
    - Query each table in both databases
    - Compare record counts with ±5% tolerance
    - Report tables with mismatched counts




    - _Requirements: 4.4, 5.2_
  
  - [ ] 5.3 Implement data sample validation
    - Select 10 random records from each table
    - Compare data values between local and Supabase


    - Check for data type consistency
    - Report any discrepancies
    - _Requirements: 5.4_
  


  - [ ] 5.4 Implement CRUD operation tests
    - Test INSERT operation (create test record)
    - Test SELECT operation (read test record)





    - Test UPDATE operation (modify test record)
    - Test DELETE operation (remove test record)
    - Clean up test data after verification
    - _Requirements: 5.3_



  
  - [ ] 5.5 Generate migration report
    - Create detailed report with all verification results


    - Include success/failure status for each table
    - List any errors or warnings
    - Save report as `migration_report_YYYYMMDD_HHMMSS.txt`
    - _Requirements: 5.5_



- [ ] 6. Create migration orchestration script
  - Create `backend/scripts/migrate_to_supabase.py` as main entry point
  - Orchestrate all migration steps in sequence: backup → export → import → verify
  - Provide clear progress updates and status messages
  - Handle errors and provide rollback instructions if migration fails
  - Generate final summary report
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_





- [ ] 7. Update documentation
  - [ ] 7.1 Create migration guide
    - Create `backend/SUPABASE_MIGRATION_GUIDE.md`
    - Document step-by-step migration process
    - Include troubleshooting section
    - Add rollback instructions
    - _Requirements: 3.5_
  
  - [ ] 7.2 Update backend README
    - Add Supabase setup instructions
    - Update database configuration section
    - Document environment variables
    - _Requirements: 3.1, 3.4_
  
  - [ ] 7.3 Create .env.example with Supabase template
    - Add Supabase connection string template
    - Document all required environment variables
    - Include comments explaining each variable
    - _Requirements: 3.1_

- [ ] 8. Perform migration execution
  - [ ] 8.1 Run pre-migration backup
    - Backup local PostgreSQL database using pg_dump
    - Verify backup file integrity
    - Test backup restoration
    - _Requirements: 1.3_
  
  - [ ] 8.2 Execute export script
    - Run `export_database.py` to create SQL dump
    - Validate export file completeness
    - Check file size and record counts
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 8.3 Execute import script
    - Run `import_to_supabase.py` to import data
    - Monitor import progress
    - Handle any errors that occur
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [ ] 8.4 Execute verification script
    - Run `verify_migration.py` to validate migration
    - Review migration report
    - Address any issues found
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 8.5 Update production configuration
    - Update backend/.env with Supabase credentials
    - Restart backend application
    - Verify application starts successfully
    - _Requirements: 1.1, 3.1, 3.3_
  
  - [ ] 8.6 Perform post-migration testing
    - Test all API endpoints
    - Verify data retrieval works correctly
    - Test data creation and updates
    - Check ML model predictions
    - Validate frontend-backend integration
    - _Requirements: 1.1, 1.2, 5.3_

# Supabase Migration Guide

## Overview

This guide walks you through migrating the FarmMe database from local PostgreSQL to Supabase cloud database. This enables all team members to access the same data regardless of their machine.

## Prerequisites

- Local PostgreSQL database with existing data
- Supabase account and project
- Python 3.8+ with required dependencies
- Internet connection

## Supabase Project Details

- **Project URL**: https://inhanxxglxnjbugppulg.supabase.co
- **Project Reference**: inhanxxglxnjbugppulg
- **Region**: ap-southeast-1 (Singapore)

## Quick Start (Automated Migration)

The easiest way to migrate is using the orchestration script:

```bash
cd backend
python scripts/migrate_to_supabase.py
```

This script will guide you through all steps automatically.

## Manual Migration Steps

If you prefer to run each step manually:

### Step 1: Get Supabase Database Password

1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/inhanxxglxnjbugppulg)
2. Click **Settings** (gear icon) → **Database**
3. Scroll to **Connection string** section
4. Click **Connection pooling** tab
5. Copy the password from the connection string

### Step 2: Backup Current Configuration

```bash
python scripts/backup_env.py
```

This creates:
- `.env.backup_YYYYMMDD_HHMMSS` - Timestamped backup
- `.env.local` - Quick rollback copy

### Step 3: Export Local Database

```bash
python scripts/export_database.py
```

This creates a SQL dump file in `scripts/exports/farmme_export_YYYYMMDD_HHMMSS.sql`

**What it exports:**
- All table schemas (CREATE TABLE statements)
- All data (INSERT statements)
- Indexes and constraints

### Step 4: Update Configuration

```bash
python scripts/update_config.py
```

You'll be prompted to:
1. Enter your Supabase database password
2. Choose connection type (pooler recommended)

This updates `backend/.env` with the Supabase connection string.

### Step 5: Test Connection

```bash
python scripts/test_supabase_connection.py
```

Verifies:
- Database connectivity
- SSL/TLS connection
- Write permissions
- Connection latency

### Step 6: Import Data to Supabase

```bash
python scripts/import_to_supabase.py
```

This will:
- Create all tables in Supabase
- Import data in batches
- Handle duplicate records
- Log progress and errors

**Note**: This may take several minutes depending on data size.

### Step 7: Verify Migration

```bash
python scripts/verify_migration.py
```

Checks:
- Connection status
- Record counts per table
- Data sample validation
- CRUD operations
- Generates detailed report

## Connection String Format

### Connection Pooler (Recommended)
```
postgresql://postgres.inhanxxglxnjbugppulg:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### Direct Connection
```
postgresql://postgres.inhanxxglxnjbugppulg:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

**Why use Connection Pooler?**
- Better for serverless/API applications
- Handles connection pooling automatically
- Reduces connection overhead
- Recommended for FastAPI applications

## Configuration Changes

### backend/.env

Before:
```env
DATABASE_URL=postgresql://postgres:123@localhost:5432/Evena
```

After:
```env
# Supabase PostgreSQL (Cloud Database)
DATABASE_URL=postgresql://postgres.inhanxxglxnjbugppulg:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Local PostgreSQL (backup)
# DATABASE_URL=postgresql://postgres:123@localhost:5432/Evena
```

### backend/database.py

Connection pool settings optimized for cloud:
- `pool_size`: 20 → 10
- `max_overflow`: 30 → 20
- `connect_timeout`: 10s → 30s

## Team Setup

Once migration is complete, team members should:

1. **Get Supabase credentials** from team lead
2. **Update their .env file**:
   ```bash
   cd backend
   # Backup current .env
   copy .env .env.local
   
   # Update DATABASE_URL
   # Edit .env and replace DATABASE_URL with Supabase connection string
   ```

3. **Test connection**:
   ```bash
   python scripts/test_supabase_connection.py
   ```

4. **Start application**:
   ```bash
   python run.py
   ```

## Troubleshooting

### Connection Failed

**Error**: `OperationalError: could not connect to server`

**Solutions**:
1. Check internet connection
2. Verify password is correct
3. Check firewall settings
4. Verify Supabase project is active

### Import Errors

**Error**: `UniqueViolation: duplicate key value`

**Solution**: This is normal - the script uses `ON CONFLICT DO NOTHING` to skip duplicates.

**Error**: `relation "table_name" does not exist`

**Solution**: Run the import script again - it will create missing tables.

### Slow Performance

**Issue**: Queries are slower than local database

**Solutions**:
1. Check connection latency: `python scripts/test_supabase_connection.py`
2. Use connection pooler (port 6543) instead of direct connection
3. Add indexes for frequently queried columns
4. Enable Redis caching (already configured)

### Data Mismatch

**Issue**: Record counts don't match

**Solutions**:
1. Check verification report in `scripts/migration_report_*.txt`
2. Re-run export and import for specific tables
3. Compare data samples manually

## Rollback Procedure

If you need to rollback to local PostgreSQL:

1. **Restore .env file**:
   ```bash
   cd backend
   copy .env.backup_YYYYMMDD_HHMMSS .env
   # Or
   copy .env.local .env
   ```

2. **Restart application**:
   ```bash
   python run.py
   ```

3. **Verify local database**:
   - Check application logs
   - Test API endpoints
   - Verify data access

## Security Best Practices

1. **Never commit credentials**:
   - `.env` is in `.gitignore`
   - Never share passwords in chat/email
   - Use secure channels for credential sharing

2. **Use environment variables**:
   - Store all secrets in `.env`
   - Never hardcode credentials
   - Use different credentials for dev/prod

3. **Monitor access**:
   - Check Supabase dashboard for activity
   - Review connection logs
   - Set up alerts for unusual activity

4. **Rotate passwords**:
   - Change database password periodically
   - Update all team members' .env files
   - Test connections after rotation

## Performance Optimization

### Connection Pooling

Already configured in `database.py`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pre-ping enabled for health checks
- Connection recycling every hour

### Caching

Redis caching is already configured:
- Predictions cached for 1 hour
- Recommendations cached for 30 minutes
- Reduces database load

### Query Optimization

1. **Use indexes** for frequently queried columns
2. **Limit result sets** with pagination
3. **Use EXPLAIN ANALYZE** for slow queries
4. **Batch operations** when possible

## Monitoring

### Supabase Dashboard

Monitor in real-time:
- Database size and growth
- Active connections
- Query performance
- Error rates

Access: https://supabase.com/dashboard/project/inhanxxglxnjbugppulg

### Application Logs

Check backend logs for:
- Connection errors
- Slow queries
- Database timeouts
- Pool exhaustion

## Support

### Common Issues

1. **Connection timeout**: Increase `connect_timeout` in `database.py`
2. **Pool exhausted**: Increase `pool_size` or `max_overflow`
3. **Slow queries**: Add indexes or optimize queries
4. **Data sync issues**: Re-run verification script

### Getting Help

1. Check this guide first
2. Review error messages and logs
3. Run verification script for diagnostics
4. Check Supabase documentation: https://supabase.com/docs
5. Contact team lead for credentials/access issues

## Maintenance

### Regular Tasks

1. **Weekly**: Check database size and growth
2. **Monthly**: Review slow queries and optimize
3. **Quarterly**: Rotate database password
4. **As needed**: Update connection pool settings

### Backup Strategy

Supabase provides:
- **Automatic daily backups** (retained for 7 days)
- **Point-in-time recovery** (for paid plans)
- **Manual backups** via dashboard

To create manual backup:
1. Go to Supabase Dashboard → Database → Backups
2. Click "Create backup"
3. Download backup file

## Next Steps

After successful migration:

1. ✅ Test all API endpoints
2. ✅ Verify frontend integration
3. ✅ Test ML model predictions
4. ✅ Check chat functionality
5. ✅ Validate forecast generation
6. ✅ Share credentials with team
7. ✅ Update deployment configuration
8. ✅ Monitor performance for 24-48 hours

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/14/core/engines.html)
- [FastAPI Database Integration](https://fastapi.tiangolo.com/tutorial/sql-databases/)

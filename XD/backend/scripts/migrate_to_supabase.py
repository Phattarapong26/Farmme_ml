# -*- coding: utf-8 -*-
"""
Migrate to Supabase - Main Orchestration Script
Coordinates all migration steps: backup → export → config → import → verify
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """Run a Python script and return success status"""
    logger.info("\n" + "=" * 60)
    logger.info(f"🔄 {description}")
    logger.info("=" * 60)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        logger.error(f"❌ Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} - SUCCESS")
            return True
        else:
            logger.error(f"❌ {description} - FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running {script_name}: {e}")
        return False

def confirm_step(message):
    """Ask user to confirm before proceeding"""
    response = input(f"\n{message} (y/n): ").strip().lower()
    return response == 'y'

def main():
    """Main orchestration function"""
    logger.info("=" * 60)
    logger.info("🚀 SUPABASE MIGRATION ORCHESTRATOR")
    logger.info("=" * 60)
    logger.info("\nThis script will guide you through the complete migration process:")
    logger.info("1. Backup current .env file")
    logger.info("2. Export local database")
    logger.info("3. Update configuration for Supabase")
    logger.info("4. Import data to Supabase")
    logger.info("5. Verify migration")
    
    if not confirm_step("\n⚠️  Ready to start migration?"):
        logger.info("Migration cancelled")
        return False
    
    # Step 1: Backup .env
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Backup Configuration")
    logger.info("=" * 60)
    
    if not run_script("backup_env.py", "Backing up .env file"):
        if not confirm_step("⚠️  Backup failed. Continue anyway?"):
            return False
    
    # Step 2: Export database
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Export Local Database")
    logger.info("=" * 60)
    
    if not run_script("export_database.py", "Exporting local database"):
        logger.error("❌ Export failed. Cannot proceed without data export.")
        return False
    
    # Step 3: Get Supabase credentials
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Supabase Credentials")
    logger.info("=" * 60)
    
    run_script("get_supabase_credentials.py", "Getting Supabase connection info")
    
    logger.info("\n📋 Before proceeding:")
    logger.info("1. Get your Supabase database password from the dashboard")
    logger.info("2. Have it ready for the next step")
    
    if not confirm_step("\n✅ Do you have your Supabase password ready?"):
        logger.info("\n💡 Get your password:")
        logger.info("   https://supabase.com/dashboard/project/inhanxxglxnjbugppulg")
        logger.info("   Settings → Database → Connection string")
        logger.info("\nRun this script again when ready.")
        return False
    
    # Step 4: Update configuration
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Update Configuration")
    logger.info("=" * 60)
    
    if not run_script("update_config.py", "Updating .env with Supabase credentials"):
        logger.error("❌ Configuration update failed")
        if not confirm_step("⚠️  Continue anyway?"):
            return False
    
    # Step 5: Test connection
    logger.info("\n" + "=" * 60)
    logger.info("STEP 5: Test Supabase Connection")
    logger.info("=" * 60)
    
    if not run_script("test_supabase_connection.py", "Testing Supabase connection"):
        logger.error("❌ Connection test failed")
        logger.error("\n💡 Troubleshooting:")
        logger.error("1. Check DATABASE_URL in .env")
        logger.error("2. Verify password is correct")
        logger.error("3. Check internet connection")
        
        if not confirm_step("\n⚠️  Connection failed. Continue with import anyway?"):
            logger.info("\n💡 To rollback:")
            logger.info("   Restore .env from .env.backup_* file")
            return False
    
    # Step 6: Import data
    logger.info("\n" + "=" * 60)
    logger.info("STEP 6: Import Data to Supabase")
    logger.info("=" * 60)
    
    logger.info("\n⚠️  This will import all data to Supabase.")
    logger.info("   This may take several minutes depending on data size.")
    
    if not confirm_step("\n✅ Proceed with data import?"):
        logger.info("Import cancelled")
        return False
    
    if not run_script("import_to_supabase.py", "Importing data to Supabase"):
        logger.error("❌ Import failed")
        
        if not confirm_step("\n⚠️  Import had errors. Continue with verification?"):
            return False
    
    # Step 7: Verify migration
    logger.info("\n" + "=" * 60)
    logger.info("STEP 7: Verify Migration")
    logger.info("=" * 60)
    
    verification_success = run_script("verify_migration.py", "Verifying migration")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("🎉 MIGRATION COMPLETE")
    logger.info("=" * 60)
    
    if verification_success:
        logger.info("\n✅ Migration successful!")
        logger.info("\n📋 Next Steps:")
        logger.info("1. Test your application: python backend/run.py")
        logger.info("2. Verify API endpoints work correctly")
        logger.info("3. Test frontend integration")
        logger.info("4. Share Supabase credentials with team members")
        logger.info("\n💡 All team members should update their .env with:")
        logger.info("   DATABASE_URL=<supabase-connection-string>")
    else:
        logger.warning("\n⚠️  Migration completed with issues")
        logger.info("\n📋 Review:")
        logger.info("1. Check migration report in backend/scripts/")
        logger.info("2. Review error messages above")
        logger.info("3. Fix issues and re-run verification")
        logger.info("\n💡 To rollback:")
        logger.info("   1. Restore .env from .env.backup_* file")
        logger.info("   2. Restart application")
    
    logger.info("\n" + "=" * 60)
    
    return verification_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Migration interrupted by user")
        logger.info("💡 To rollback: Restore .env from .env.backup_* file")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

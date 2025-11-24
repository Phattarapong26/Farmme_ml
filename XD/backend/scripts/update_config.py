# -*- coding: utf-8 -*-
"""
Update Configuration for Supabase
Updates .env file with Supabase connection string
"""

import os
import re
from pathlib import Path
import logging
import getpass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase project details
PROJECT_REF = "inhanxxglxnjbugppulg"
SUPABASE_URL = "https://inhanxxglxnjbugppulg.supabase.co"

def get_supabase_connection_string(password, use_pooler=True):
    """Build Supabase connection string"""
    if use_pooler:
        # Connection pooler (recommended)
        return f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
    else:
        # Direct connection
        return f"postgresql://postgres.{PROJECT_REF}:{password}@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def update_env_file(connection_string):
    """Update .env file with new DATABASE_URL"""
    logger.info("=" * 60)
    logger.info("⚙️  Updating .env Configuration")
    logger.info("=" * 60)
    
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        logger.error(f"❌ .env file not found at: {env_file}")
        return False
    
    try:
        # Read current .env
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original DATABASE_URL as comment
        original_db_url = None
        db_url_pattern = r'^DATABASE_URL=(.+)$'
        match = re.search(db_url_pattern, content, re.MULTILINE)
        
        if match:
            original_db_url = match.group(1)
            logger.info(f"📝 Found existing DATABASE_URL")
        
        # Comment out old DATABASE_URL lines
        content = re.sub(
            r'^(DATABASE_URL=.+)$',
            r'# \1  # Local PostgreSQL (backup)',
            content,
            flags=re.MULTILINE
        )
        
        # Add new Supabase DATABASE_URL
        new_config = f"\n# Supabase PostgreSQL (Cloud Database)\nDATABASE_URL={connection_string}\n"
        
        # Find the database configuration section
        if "# Database Configuration" in content:
            content = re.sub(
                r'(# Database Configuration\n)',
                r'\1' + new_config,
                content
            )
        else:
            # Add at the end
            content += new_config
        
        # Write updated .env
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ .env file updated successfully")
        logger.info(f"📍 File: {env_file}")
        logger.info(f"🔗 New DATABASE_URL: postgresql://postgres.{PROJECT_REF}:***@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres")
        
        if original_db_url:
            logger.info(f"💾 Original DATABASE_URL backed up as comment")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update .env: {e}")
        return False

def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("🔧 Supabase Configuration Update")
    logger.info("=" * 60)
    
    logger.info(f"\n📍 Project: {PROJECT_REF}")
    logger.info(f"🌐 URL: {SUPABASE_URL}")
    
    # Get password from user
    logger.info("\n" + "=" * 60)
    logger.info("🔑 Database Password Required")
    logger.info("=" * 60)
    logger.info("\nTo get your password:")
    logger.info("1. Go to: https://supabase.com/dashboard/project/" + PROJECT_REF)
    logger.info("2. Settings → Database → Connection string")
    logger.info("3. Copy the password from the connection string\n")
    
    password = getpass.getpass("Enter Supabase database password: ")
    
    if not password:
        logger.error("❌ Password is required")
        return False
    
    # Ask about connection type
    logger.info("\n" + "=" * 60)
    logger.info("🔌 Connection Type")
    logger.info("=" * 60)
    logger.info("1. Connection Pooler (Port 6543) - RECOMMENDED")
    logger.info("   • Better for serverless/API applications")
    logger.info("   • Handles connection pooling automatically")
    logger.info("2. Direct Connection (Port 5432)")
    logger.info("   • Direct database connection")
    
    choice = input("\nSelect connection type (1 or 2) [1]: ").strip() or "1"
    use_pooler = choice == "1"
    
    # Build connection string
    connection_string = get_supabase_connection_string(password, use_pooler)
    
    # Update .env file
    success = update_env_file(connection_string)
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ Configuration Update Complete")
        logger.info("=" * 60)
        logger.info("\n📋 Next Steps:")
        logger.info("1. Test connection: python backend/scripts/test_supabase_connection.py")
        logger.info("2. Import data: python backend/scripts/import_to_supabase.py")
        logger.info("\n💡 To rollback:")
        logger.info("   • Restore from .env.backup_* file")
        logger.info("   • Or uncomment the local PostgreSQL DATABASE_URL\n")
    else:
        logger.info("\n" + "=" * 60)
        logger.info("❌ Configuration Update Failed")
        logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

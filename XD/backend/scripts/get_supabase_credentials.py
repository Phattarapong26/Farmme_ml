# -*- coding: utf-8 -*-
"""
Get Supabase Database Credentials
Extracts database connection details from Supabase project
"""

import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase credentials provided
SUPABASE_URL = "https://inhanxxglxnjbugppulg.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImluaGFueHhnbHhuamJ1Z3BwdWxnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM3MTY3MjEsImV4cCI6MjA3OTI5MjcyMX0.oeyGs84toL4LaIz-fCqQbyuW0NUBPE560Hvn5pr3l1Y"

def extract_project_ref(url):
    """Extract project reference from Supabase URL"""
    # Format: https://[project-ref].supabase.co
    match = re.match(r'https://([^.]+)\.supabase\.co', url)
    if match:
        return match.group(1)
    return None

def get_connection_strings(project_ref):
    """Generate Supabase PostgreSQL connection strings"""
    
    logger.info("=" * 70)
    logger.info("🔑 Supabase Database Connection Details")
    logger.info("=" * 70)
    
    logger.info(f"\n📍 Project Reference: {project_ref}")
    logger.info(f"🌐 Supabase URL: {SUPABASE_URL}")
    
    logger.info("\n" + "=" * 70)
    logger.info("📋 IMPORTANT: You need to get the database password")
    logger.info("=" * 70)
    logger.info("\nTo get your database password:")
    logger.info("1. Go to: https://supabase.com/dashboard/project/" + project_ref)
    logger.info("2. Click on 'Settings' (gear icon) in the left sidebar")
    logger.info("3. Click on 'Database' under Project Settings")
    logger.info("4. Scroll down to 'Connection string'")
    logger.info("5. Click 'Connection pooling' tab")
    logger.info("6. Copy the password from the connection string")
    
    logger.info("\n" + "=" * 70)
    logger.info("🔌 Connection String Formats")
    logger.info("=" * 70)
    
    # Connection pooler (recommended for serverless/API)
    pooler_template = f"postgresql://postgres.{project_ref}:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
    logger.info("\n📌 Connection Pooler (Port 6543) - RECOMMENDED:")
    logger.info(f"   {pooler_template}")
    
    # Direct connection
    direct_template = f"postgresql://postgres.{project_ref}:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    logger.info("\n📌 Direct Connection (Port 5432):")
    logger.info(f"   {direct_template}")
    
    logger.info("\n" + "=" * 70)
    logger.info("⚙️  Configuration Steps")
    logger.info("=" * 70)
    logger.info("\n1. Get your password from Supabase dashboard")
    logger.info("2. Replace [YOUR-PASSWORD] in the connection string above")
    logger.info("3. Update backend/.env file with:")
    logger.info(f"   DATABASE_URL={pooler_template}")
    logger.info("\n4. Keep your local PostgreSQL URL as backup:")
    logger.info("   # DATABASE_URL=postgresql://postgres:123@localhost:5432/Evena")
    
    logger.info("\n" + "=" * 70)
    logger.info("🔒 Security Notes")
    logger.info("=" * 70)
    logger.info("• Never commit .env file to git")
    logger.info("• Use connection pooler (port 6543) for better performance")
    logger.info("• The anon key is for client-side API access, not database")
    logger.info("• Database password is different from anon key")
    
    logger.info("\n" + "=" * 70)
    
    return {
        'project_ref': project_ref,
        'pooler_template': pooler_template,
        'direct_template': direct_template,
        'supabase_url': SUPABASE_URL,
        'anon_key': SUPABASE_ANON_KEY
    }

def main():
    """Main function"""
    project_ref = extract_project_ref(SUPABASE_URL)
    
    if not project_ref:
        logger.error("❌ Could not extract project reference from URL")
        return None
    
    credentials = get_connection_strings(project_ref)
    
    logger.info("\n✅ Next Steps:")
    logger.info("1. Get your database password from Supabase dashboard")
    logger.info("2. Run: python backend/scripts/update_config.py")
    logger.info("3. Enter your password when prompted")
    logger.info("4. The script will update your .env file automatically\n")
    
    return credentials

if __name__ == "__main__":
    main()

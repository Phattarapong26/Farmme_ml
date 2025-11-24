# -*- coding: utf-8 -*-
"""
Backup .env file before migration
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_env_file():
    """Create timestamped backup of .env file"""
    logger.info("=" * 60)
    logger.info("💾 Creating .env Backup")
    logger.info("=" * 60)
    
    # Get paths
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        logger.error(f"❌ .env file not found at: {env_file}")
        return False
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backend_dir / f".env.backup_{timestamp}"
    
    try:
        # Copy file
        shutil.copy2(env_file, backup_file)
        
        # Verify backup
        if backup_file.exists():
            original_size = os.path.getsize(env_file)
            backup_size = os.path.getsize(backup_file)
            
            if original_size == backup_size:
                logger.info(f"✅ Backup created: {backup_file.name}")
                logger.info(f"📄 File size: {backup_size} bytes")
                logger.info(f"📍 Location: {backup_file}")
                
                # Also create a .env.local backup (for easy rollback)
                local_backup = backend_dir / ".env.local"
                shutil.copy2(env_file, local_backup)
                logger.info(f"✅ Local backup: {local_backup.name}")
                
                logger.info("\n💡 To restore backup:")
                logger.info(f"   copy {backup_file.name} .env")
                
                return True
            else:
                logger.error("❌ Backup file size mismatch")
                return False
        else:
            logger.error("❌ Backup file not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False

def main():
    """Main function"""
    success = backup_env_file()
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ Backup Complete")
        logger.info("=" * 60)
    else:
        logger.info("\n" + "=" * 60)
        logger.info("❌ Backup Failed")
        logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

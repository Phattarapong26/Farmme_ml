"""
Dataset Cleanup Script
ทำความสะอาด dataset ที่ไม่ได้ใช้ตามคำแนะนำ

Usage:
    python cleanup_datasets.py --dry-run     # ดูว่าจะลบอะไรบ้าง (ไม่ลบจริง)
    python cleanup_datasets.py --execute     # ลบจริง (ย้ายไปที่ backup)
    python cleanup_datasets.py --restore     # กู้คืนไฟล์จาก backup
"""

import shutil
from pathlib import Path
from datetime import datetime
import json

DATASET_DIR = Path("buildingModel.py/Dataset")
BACKUP_DIR = DATASET_DIR / "backup_unused"

# Files to delete (HIGH PRIORITY)
HIGH_PRIORITY_DELETE = [
    "FARMME_GPU_DATASET.csv",  # 1.1 GB
    "population.csv",           # 10.71 MB
    "profit.csv"                # 1.33 MB
]

# Files to consider (MEDIUM/LOW PRIORITY)
MEDIUM_PRIORITY_DELETE = [
    "compatibility.csv",        # 0.31 MB
    "economic.csv"              # 0.11 MB
]

def format_size(size_bytes):
    """Format file size"""
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} bytes"

def dry_run():
    """แสดงว่าจะลบอะไรบ้าง (ไม่ลบจริง)"""
    print("\n" + "="*80)
    print("DRY RUN - CLEANUP PREVIEW".center(80))
    print("="*80)
    
    total_size = 0
    
    print("\n🔴 HIGH PRIORITY FILES (will be moved to backup):")
    for filename in HIGH_PRIORITY_DELETE:
        filepath = DATASET_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size
            total_size += size
            print(f"\n   ❌ {filename}")
            print(f"      Size: {format_size(size)}")
            print(f"      Path: {filepath}")
            print(f"      → Will move to: {BACKUP_DIR / filename}")
        else:
            print(f"\n   ⚠️  {filename} - NOT FOUND")
    
    print("\n\n🟡 MEDIUM PRIORITY FILES (optional, not included in this cleanup):")
    for filename in MEDIUM_PRIORITY_DELETE:
        filepath = DATASET_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"\n   ⚠️  {filename}")
            print(f"      Size: {format_size(size)}")
            print(f"      Note: Keep for now, can delete manually if needed")
    
    print("\n" + "="*80)
    print(f"TOTAL SPACE TO BE FREED: {format_size(total_size)}".center(80))
    print("="*80)
    print("\n⚠️  This is a DRY RUN. No files were actually moved.")
    print("   Run with --execute to perform actual cleanup.")

def execute_cleanup():
    """ทำความสะอาดจริง (ย้ายไปที่ backup)"""
    print("\n" + "="*80)
    print("EXECUTING CLEANUP".center(80))
    print("="*80)
    
    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    print(f"\n📁 Backup directory: {BACKUP_DIR}")
    
    # Create cleanup log
    cleanup_log = {
        "timestamp": datetime.now().isoformat(),
        "action": "cleanup",
        "files_moved": []
    }
    
    total_size = 0
    moved_count = 0
    
    print("\n🔴 Moving HIGH PRIORITY files to backup...")
    
    for filename in HIGH_PRIORITY_DELETE:
        filepath = DATASET_DIR / filename
        
        if not filepath.exists():
            print(f"\n   ⚠️  {filename} - NOT FOUND, skipping")
            continue
        
        size = filepath.stat().st_size
        backup_path = BACKUP_DIR / filename
        
        print(f"\n   📦 Moving: {filename}")
        print(f"      Size: {format_size(size)}")
        
        try:
            # Move file to backup
            shutil.move(str(filepath), str(backup_path))
            print(f"      ✅ Moved to: {backup_path}")
            
            # Log
            cleanup_log["files_moved"].append({
                "filename": filename,
                "size_bytes": size,
                "original_path": str(filepath),
                "backup_path": str(backup_path)
            })
            
            total_size += size
            moved_count += 1
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Save cleanup log
    log_file = BACKUP_DIR / "cleanup_log.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(cleanup_log, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("CLEANUP COMPLETE".center(80))
    print("="*80)
    print(f"\n✅ Files moved: {moved_count}")
    print(f"✅ Space freed: {format_size(total_size)}")
    print(f"✅ Backup location: {BACKUP_DIR}")
    print(f"✅ Cleanup log: {log_file}")
    print("\n💡 To restore files, run: python cleanup_datasets.py --restore")

def restore_files():
    """กู้คืนไฟล์จาก backup"""
    print("\n" + "="*80)
    print("RESTORING FILES FROM BACKUP".center(80))
    print("="*80)
    
    if not BACKUP_DIR.exists():
        print("\n❌ Backup directory not found!")
        return
    
    # Read cleanup log
    log_file = BACKUP_DIR / "cleanup_log.json"
    if not log_file.exists():
        print("\n❌ Cleanup log not found!")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        cleanup_log = json.load(f)
    
    print(f"\n📄 Found cleanup log from: {cleanup_log['timestamp']}")
    print(f"   Files to restore: {len(cleanup_log['files_moved'])}")
    
    restored_count = 0
    
    for file_info in cleanup_log['files_moved']:
        filename = file_info['filename']
        backup_path = Path(file_info['backup_path'])
        original_path = Path(file_info['original_path'])
        
        if not backup_path.exists():
            print(f"\n   ⚠️  {filename} - backup not found, skipping")
            continue
        
        print(f"\n   📦 Restoring: {filename}")
        print(f"      From: {backup_path}")
        print(f"      To: {original_path}")
        
        try:
            shutil.move(str(backup_path), str(original_path))
            print(f"      ✅ Restored")
            restored_count += 1
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("RESTORE COMPLETE".center(80))
    print("="*80)
    print(f"\n✅ Files restored: {restored_count}")

def show_status():
    """แสดงสถานะปัจจุบัน"""
    print("\n" + "="*80)
    print("DATASET STATUS".center(80))
    print("="*80)
    
    print("\n📊 Current Dataset Files:")
    
    total_size = 0
    file_count = 0
    
    for filepath in sorted(DATASET_DIR.glob("*.csv")):
        size = filepath.stat().st_size
        total_size += size
        file_count += 1
        
        status = "✅" if filepath.name not in HIGH_PRIORITY_DELETE else "❌"
        print(f"   {status} {filepath.name:40s} {format_size(size):>15s}")
    
    print(f"\n   Total: {file_count} files, {format_size(total_size)}")
    
    # Check backup
    if BACKUP_DIR.exists():
        print(f"\n📦 Backup Directory: {BACKUP_DIR}")
        backup_files = list(BACKUP_DIR.glob("*.csv"))
        if backup_files:
            backup_size = sum(f.stat().st_size for f in backup_files)
            print(f"   Files in backup: {len(backup_files)}")
            print(f"   Backup size: {format_size(backup_size)}")
        else:
            print(f"   No files in backup")
    else:
        print(f"\n📦 No backup directory found")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dataset Cleanup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_datasets.py --dry-run     # Preview what will be deleted
  python cleanup_datasets.py --execute     # Perform actual cleanup
  python cleanup_datasets.py --restore     # Restore files from backup
  python cleanup_datasets.py --status      # Show current status
        """
    )
    
    parser.add_argument("--dry-run", action="store_true", help="Preview cleanup (no actual changes)")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (move files to backup)")
    parser.add_argument("--restore", action="store_true", help="Restore files from backup")
    parser.add_argument("--status", action="store_true", help="Show current dataset status")
    
    args = parser.parse_args()
    
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found: {DATASET_DIR}")
        return
    
    if args.execute:
        # Confirm before executing
        print("\n⚠️  WARNING: This will move files to backup directory.")
        print("   Files can be restored later using --restore option.")
        response = input("\n   Continue? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            execute_cleanup()
        else:
            print("\n   Cleanup cancelled.")
    elif args.restore:
        restore_files()
    elif args.status:
        show_status()
    else:
        # Default: dry run
        dry_run()

if __name__ == "__main__":
    main()

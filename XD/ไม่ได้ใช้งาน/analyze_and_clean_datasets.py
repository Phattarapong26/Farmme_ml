"""
Dataset Analysis and Cleanup Tool
วิเคราะห์และทำความสะอาด dataset ที่ไม่ได้ใช้ใน Model A, B, C, D

Usage:
    python analyze_and_clean_datasets.py --analyze  # วิเคราะห์เท่านั้น
    python analyze_and_clean_datasets.py --clean    # ทำความสะอาดจริง
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import json

# Dataset directory
DATASET_DIR = Path("buildingModel.py/Dataset")

# Dataset usage mapping based on model analysis
DATASET_USAGE = {
    # ใช้งานจริง
    "cultivation.csv": ["Model A", "Model B"],
    "crop_characteristics.csv": ["Model A"],
    "farmer_profiles.csv": ["Model A"],
    "weather.csv": ["Model A", "Model B"],
    "price.csv": ["Model C"],
    
    # ไม่ได้ใช้
    "compatibility.csv": [],
    "economic.csv": [],
    "population.csv": [],
    "profit.csv": [],
    "FARMME_GPU_DATASET.csv": []
}

def analyze_datasets():
    """วิเคราะห์ dataset ทั้งหมด"""
    print("\n" + "="*80)
    print("DATASET ANALYSIS REPORT".center(80))
    print("="*80)
    
    total_size = 0
    unused_size = 0
    
    results = {
        "analysis_date": datetime.now().isoformat(),
        "datasets": {}
    }
    
    for dataset_file in sorted(DATASET_DIR.glob("*.csv")):
        file_name = dataset_file.name
        file_size = dataset_file.stat().st_size
        total_size += file_size
        
        # Read dataset info
        try:
            df = pd.read_csv(dataset_file, nrows=5)
            row_count_sample = len(df)
            col_count = len(df.columns)
            
            # Get full row count
            df_full = pd.read_csv(dataset_file)
            row_count = len(df_full)
            
        except Exception as e:
            print(f"⚠️  Error reading {file_name}: {e}")
            continue
        
        # Check usage
        used_by = DATASET_USAGE.get(file_name, [])
        is_used = len(used_by) > 0
        
        if not is_used:
            unused_size += file_size
        
        # Store results
        results["datasets"][file_name] = {
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "rows": row_count,
            "columns": col_count,
            "column_names": df.columns.tolist(),
            "used_by": used_by,
            "is_used": is_used
        }
        
        # Print info
        status = "✅ USED" if is_used else "❌ UNUSED"
        print(f"\n{status}: {file_name}")
        print(f"  Size: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
        print(f"  Rows: {row_count:,}")
        print(f"  Columns: {col_count}")
        print(f"  Column names: {', '.join(df.columns.tolist()[:5])}{'...' if col_count > 5 else ''}")
        
        if is_used:
            print(f"  Used by: {', '.join(used_by)}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY".center(80))
    print("="*80)
    print(f"\nTotal datasets: {len(results['datasets'])}")
    print(f"Used datasets: {sum(1 for d in results['datasets'].values() if d['is_used'])}")
    print(f"Unused datasets: {sum(1 for d in results['datasets'].values() if not d['is_used'])}")
    print(f"\nTotal size: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")
    print(f"Unused size: {unused_size:,} bytes ({unused_size/(1024*1024):.2f} MB)")
    print(f"Potential savings: {(unused_size/total_size)*100:.1f}%")
    
    # Save report
    report_file = "dataset_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    return results

def clean_datasets(dry_run=True):
    """ทำความสะอาด dataset ที่ไม่ได้ใช้"""
    print("\n" + "="*80)
    if dry_run:
        print("DATASET CLEANUP (DRY RUN)".center(80))
    else:
        print("DATASET CLEANUP (ACTUAL)".center(80))
    print("="*80)
    
    # Create backup directory
    backup_dir = DATASET_DIR / "backup_unused"
    if not dry_run:
        backup_dir.mkdir(exist_ok=True)
        print(f"\n📁 Backup directory: {backup_dir}")
    
    deleted_count = 0
    deleted_size = 0
    
    for dataset_file in sorted(DATASET_DIR.glob("*.csv")):
        file_name = dataset_file.name
        used_by = DATASET_USAGE.get(file_name, [])
        
        if len(used_by) == 0:  # Unused
            file_size = dataset_file.stat().st_size
            
            print(f"\n❌ Removing: {file_name}")
            print(f"   Size: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
            
            if not dry_run:
                # Move to backup instead of delete
                backup_path = backup_dir / file_name
                dataset_file.rename(backup_path)
                print(f"   ✅ Moved to: {backup_path}")
            else:
                print(f"   [DRY RUN] Would move to: {backup_dir / file_name}")
            
            deleted_count += 1
            deleted_size += file_size
    
    # Summary
    print("\n" + "="*80)
    print("CLEANUP SUMMARY".center(80))
    print("="*80)
    print(f"\nFiles {'moved' if not dry_run else 'to be moved'}: {deleted_count}")
    print(f"Space {'freed' if not dry_run else 'to be freed'}: {deleted_size:,} bytes ({deleted_size/(1024*1024):.2f} MB)")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were actually moved.")
        print("   Run with --clean to perform actual cleanup.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dataset Analysis and Cleanup Tool")
    parser.add_argument("--analyze", action="store_true", help="Analyze datasets only")
    parser.add_argument("--clean", action="store_true", help="Clean unused datasets (moves to backup)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run cleanup (no actual changes)")
    
    args = parser.parse_args()
    
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found: {DATASET_DIR}")
        sys.exit(1)
    
    if args.analyze or (not args.clean and not args.dry_run):
        # Default: analyze
        analyze_datasets()
    
    if args.clean:
        clean_datasets(dry_run=False)
    elif args.dry_run:
        clean_datasets(dry_run=True)

if __name__ == "__main__":
    main()

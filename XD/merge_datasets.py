"""
Merge Multiple Datasets into One
รวม dataset หลายๆ ตัวเป็นไฟล์เดียว เพื่อลดจำนวนไฟล์และง่ายต่อการจัดการ

Features:
- รวม cultivation, weather, crop_characteristics, farmer_profiles
- เก็บเฉพาะ columns ที่จำเป็น
- ลด redundancy
- สร้าง master dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

DATASET_DIR = Path("buildingModel.py/Dataset")

def merge_for_model_ab():
    """
    รวม dataset สำหรับ Model A และ B
    - cultivation.csv
    - crop_characteristics.csv
    - farmer_profiles.csv
    - weather.csv
    """
    print("\n" + "="*80)
    print("MERGING DATASETS FOR MODEL A & B".center(80))
    print("="*80)
    
    # 1. Load cultivation (base dataset)
    print("\n📥 Loading cultivation.csv...")
    cultivation = pd.read_csv(
        DATASET_DIR / "cultivation.csv",
        parse_dates=['planting_date', 'harvest_date']
    )
    print(f"   Rows: {len(cultivation):,}")
    
    # 2. Load crop characteristics
    print("\n📥 Loading crop_characteristics.csv...")
    crops = pd.read_csv(DATASET_DIR / "crop_characteristics.csv")
    print(f"   Rows: {len(crops):,}")
    
    # 3. Load farmer profiles
    print("\n📥 Loading farmer_profiles.csv...")
    farmers = pd.read_csv(DATASET_DIR / "farmer_profiles.csv")
    print(f"   Rows: {len(farmers):,}")
    
    # 4. Load weather
    print("\n📥 Loading weather.csv...")
    weather = pd.read_csv(
        DATASET_DIR / "weather.csv",
        parse_dates=['date']
    )
    print(f"   Rows: {len(weather):,}")
    
    # Merge cultivation with crops
    print("\n🔗 Merging cultivation + crop_characteristics...")
    merged = cultivation.merge(
        crops,
        on='crop_type',
        how='left',
        suffixes=('', '_crop')
    )
    print(f"   Rows after merge: {len(merged):,}")
    
    # Merge with farmers (by province)
    print("\n🔗 Merging + farmer_profiles...")
    merged = merged.merge(
        farmers[['province', 'farmer_type', 'land_size_rai', 'available_capital_baht', 
                 'risk_tolerance', 'farming_experience_years']],
        on='province',
        how='left',
        suffixes=('', '_farmer')
    )
    print(f"   Rows after merge: {len(merged):,}")
    
    # Merge with weather (by province and date)
    print("\n🔗 Merging + weather...")
    # Create date column for matching
    merged['date'] = merged['planting_date']
    
    merged = merged.merge(
        weather,
        on=['province', 'date'],
        how='left',
        suffixes=('', '_weather')
    )
    print(f"   Rows after merge: {len(merged):,}")
    
    # Drop redundant columns
    print("\n🧹 Cleaning up columns...")
    
    # Remove duplicate columns
    cols_to_drop = [col for col in merged.columns if col.endswith('_crop') or col.endswith('_farmer') or col.endswith('_weather')]
    merged = merged.drop(columns=cols_to_drop, errors='ignore')
    
    # Remove date column (we have planting_date)
    if 'date' in merged.columns:
        merged = merged.drop(columns=['date'])
    
    print(f"   Final columns: {len(merged.columns)}")
    print(f"   Final rows: {len(merged):,}")
    
    # Save merged dataset
    output_file = DATASET_DIR / "merged_model_ab.csv"
    merged.to_csv(output_file, index=False)
    
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"\n✅ Saved: {output_file}")
    print(f"   Size: {file_size:.2f} MB")
    
    return merged

def create_minimal_datasets():
    """
    สร้าง dataset ที่เล็กลงโดยเก็บเฉพาะ columns ที่จำเป็น
    """
    print("\n" + "="*80)
    print("CREATING MINIMAL DATASETS".center(80))
    print("="*80)
    
    # 1. Minimal cultivation (เฉพาะ pre-planting features)
    print("\n📥 Creating minimal_cultivation.csv...")
    cultivation = pd.read_csv(
        DATASET_DIR / "cultivation.csv",
        parse_dates=['planting_date', 'harvest_date']
    )
    
    # Keep only pre-planting features (no data leakage)
    minimal_cultivation = cultivation[[
        'province', 'crop_type', 'crop_id',
        'planting_date', 'harvest_date',
        'planting_area_rai', 'expected_yield_kg',
        'investment_cost', 'farm_skill', 'tech_adoption'
    ]].copy()
    
    output_file = DATASET_DIR / "minimal_cultivation.csv"
    minimal_cultivation.to_csv(output_file, index=False)
    
    original_size = (DATASET_DIR / "cultivation.csv").stat().st_size / (1024 * 1024)
    new_size = output_file.stat().st_size / (1024 * 1024)
    
    print(f"   Original: {original_size:.2f} MB")
    print(f"   Minimal: {new_size:.2f} MB")
    print(f"   Saved: {original_size - new_size:.2f} MB ({((original_size - new_size) / original_size * 100):.1f}%)")
    
    # 2. Minimal weather (aggregate by month)
    print("\n📥 Creating minimal_weather.csv...")
    weather = pd.read_csv(
        DATASET_DIR / "weather.csv",
        parse_dates=['date']
    )
    
    # Aggregate by province and month
    weather['year_month'] = weather['date'].dt.to_period('M')
    
    minimal_weather = weather.groupby(['province', 'year_month']).agg({
        'temperature_celsius': 'mean',
        'rainfall_mm': 'sum',
        'humidity_percent': 'mean',
        'drought_index': 'mean'
    }).reset_index()
    
    minimal_weather['year_month'] = minimal_weather['year_month'].astype(str)
    
    output_file = DATASET_DIR / "minimal_weather.csv"
    minimal_weather.to_csv(output_file, index=False)
    
    original_size = (DATASET_DIR / "weather.csv").stat().st_size / (1024 * 1024)
    new_size = output_file.stat().st_size / (1024 * 1024)
    
    print(f"   Original: {original_size:.2f} MB ({len(weather):,} rows)")
    print(f"   Minimal: {new_size:.2f} MB ({len(minimal_weather):,} rows)")
    print(f"   Saved: {original_size - new_size:.2f} MB ({((original_size - new_size) / original_size * 100):.1f}%)")
    
    # 3. Minimal price (sample or aggregate)
    print("\n📥 Creating minimal_price.csv...")
    price = pd.read_csv(
        DATASET_DIR / "price.csv",
        parse_dates=['date']
    )
    
    # Keep only essential columns
    minimal_price = price[[
        'date', 'province', 'crop_type',
        'price_per_kg', 'market_type'
    ]].copy()
    
    # Aggregate by day (remove market_id level)
    minimal_price = minimal_price.groupby(
        ['date', 'province', 'crop_type', 'market_type']
    ).agg({
        'price_per_kg': 'mean'
    }).reset_index()
    
    output_file = DATASET_DIR / "minimal_price.csv"
    minimal_price.to_csv(output_file, index=False)
    
    original_size = (DATASET_DIR / "price.csv").stat().st_size / (1024 * 1024)
    new_size = output_file.stat().st_size / (1024 * 1024)
    
    print(f"   Original: {original_size:.2f} MB ({len(price):,} rows)")
    print(f"   Minimal: {new_size:.2f} MB ({len(minimal_price):,} rows)")
    print(f"   Saved: {original_size - new_size:.2f} MB ({((original_size - new_size) / original_size * 100):.1f}%)")

def create_master_dataset():
    """
    สร้าง master dataset ที่รวมทุกอย่างเข้าด้วยกัน
    """
    print("\n" + "="*80)
    print("CREATING MASTER DATASET".center(80))
    print("="*80)
    
    print("\n⚠️  Warning: This will create a large file!")
    print("   Recommended: Use merged_model_ab.csv instead for Model A & B")
    print("   Or use minimal_*.csv for smaller files")
    
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n   Cancelled.")
        return
    
    # Load all datasets
    print("\n📥 Loading all datasets...")
    
    cultivation = pd.read_csv(DATASET_DIR / "cultivation.csv", parse_dates=['planting_date', 'harvest_date'])
    crops = pd.read_csv(DATASET_DIR / "crop_characteristics.csv")
    farmers = pd.read_csv(DATASET_DIR / "farmer_profiles.csv")
    weather = pd.read_csv(DATASET_DIR / "weather.csv", parse_dates=['date'])
    price = pd.read_csv(DATASET_DIR / "price.csv", parse_dates=['date'])
    
    print(f"   cultivation: {len(cultivation):,} rows")
    print(f"   crops: {len(crops):,} rows")
    print(f"   farmers: {len(farmers):,} rows")
    print(f"   weather: {len(weather):,} rows")
    print(f"   price: {len(price):,} rows")
    
    # Merge step by step
    print("\n🔗 Merging datasets...")
    
    master = cultivation.merge(crops, on='crop_type', how='left', suffixes=('', '_crop'))
    print(f"   + crops: {len(master):,} rows")
    
    master = master.merge(
        farmers[['province', 'farmer_type', 'land_size_rai', 'available_capital_baht']],
        on='province', how='left', suffixes=('', '_farmer')
    )
    print(f"   + farmers: {len(master):,} rows")
    
    # Merge weather by province and planting_date
    master['date'] = master['planting_date']
    master = master.merge(weather, on=['province', 'date'], how='left', suffixes=('', '_weather'))
    print(f"   + weather: {len(master):,} rows")
    
    # Merge price by province, crop_type, and planting_date
    price_agg = price.groupby(['date', 'province', 'crop_type']).agg({
        'price_per_kg': 'mean'
    }).reset_index()
    
    master = master.merge(
        price_agg,
        left_on=['date', 'province', 'crop_type'],
        right_on=['date', 'province', 'crop_type'],
        how='left',
        suffixes=('', '_price')
    )
    print(f"   + price: {len(master):,} rows")
    
    # Clean up
    master = master.drop(columns=['date'], errors='ignore')
    
    # Save
    output_file = DATASET_DIR / "master_dataset.csv"
    master.to_csv(output_file, index=False)
    
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"\n✅ Saved: {output_file}")
    print(f"   Size: {file_size:.2f} MB")
    print(f"   Rows: {len(master):,}")
    print(f"   Columns: {len(master.columns)}")

def show_merge_summary():
    """แสดงสรุปการรวม dataset"""
    print("\n" + "="*80)
    print("MERGE SUMMARY".center(80))
    print("="*80)
    
    merged_files = [
        "merged_model_ab.csv",
        "minimal_cultivation.csv",
        "minimal_weather.csv",
        "minimal_price.csv",
        "master_dataset.csv"
    ]
    
    print("\n📊 Merged Files:")
    
    total_size = 0
    for filename in merged_files:
        filepath = DATASET_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size / (1024 * 1024)
            total_size += size
            
            # Count rows
            df = pd.read_csv(filepath, nrows=1)
            row_count = len(pd.read_csv(filepath))
            
            print(f"\n   ✅ {filename}")
            print(f"      Size: {size:.2f} MB")
            print(f"      Rows: {row_count:,}")
            print(f"      Columns: {len(df.columns)}")
        else:
            print(f"\n   ❌ {filename} - NOT FOUND")
    
    print(f"\n   Total merged size: {total_size:.2f} MB")
    
    # Compare with original
    print("\n📊 Original Files (used):")
    original_files = [
        "cultivation.csv",
        "crop_characteristics.csv",
        "farmer_profiles.csv",
        "weather.csv",
        "price.csv"
    ]
    
    original_size = 0
    for filename in original_files:
        filepath = DATASET_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size / (1024 * 1024)
            original_size += size
            print(f"   {filename}: {size:.2f} MB")
    
    print(f"\n   Total original size: {original_size:.2f} MB")
    
    if total_size > 0:
        print(f"\n💡 Space comparison:")
        print(f"   Original: {original_size:.2f} MB")
        print(f"   Merged: {total_size:.2f} MB")
        if total_size < original_size:
            print(f"   Saved: {original_size - total_size:.2f} MB ({((original_size - total_size) / original_size * 100):.1f}%)")
        else:
            print(f"   Increased: {total_size - original_size:.2f} MB")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Merge Multiple Datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python merge_datasets.py --model-ab      # Merge for Model A & B
  python merge_datasets.py --minimal       # Create minimal datasets
  python merge_datasets.py --master        # Create master dataset (large!)
  python merge_datasets.py --summary       # Show merge summary
  python merge_datasets.py --all           # Do all merges
        """
    )
    
    parser.add_argument("--model-ab", action="store_true", help="Merge datasets for Model A & B")
    parser.add_argument("--minimal", action="store_true", help="Create minimal datasets")
    parser.add_argument("--master", action="store_true", help="Create master dataset")
    parser.add_argument("--summary", action="store_true", help="Show merge summary")
    parser.add_argument("--all", action="store_true", help="Do all merges")
    
    args = parser.parse_args()
    
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found: {DATASET_DIR}")
        return
    
    if args.all:
        merge_for_model_ab()
        create_minimal_datasets()
        show_merge_summary()
    else:
        if args.model_ab:
            merge_for_model_ab()
        if args.minimal:
            create_minimal_datasets()
        if args.master:
            create_master_dataset()
        if args.summary:
            show_merge_summary()
        
        if not any([args.model_ab, args.minimal, args.master, args.summary]):
            print("Please specify an option. Use --help for more information.")
            print("\nQuick start:")
            print("  python merge_datasets.py --model-ab    # Recommended for Model A & B")
            print("  python merge_datasets.py --minimal     # Create smaller files")

if __name__ == "__main__":
    main()

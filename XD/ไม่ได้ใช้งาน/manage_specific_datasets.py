"""
Manage Specific Datasets
จัดการ dataset แต่ละตารางที่ไม่ได้ใช้ใน Model A, B, C, D

Features:
- ดูข้อมูลตัวอย่างของแต่ละ dataset
- ตรวจสอบความซ้ำซ้อน
- ลบ columns ที่ไม่จำเป็น
- บีบอัดข้อมูล
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

DATASET_DIR = Path("buildingModel.py/Dataset")

def inspect_dataset(filename):
    """ตรวจสอบ dataset แบบละเอียด"""
    filepath = DATASET_DIR / filename
    
    if not filepath.exists():
        print(f"❌ File not found: {filename}")
        return
    
    print(f"\n{'='*80}")
    print(f"INSPECTING: {filename}".center(80))
    print(f"{'='*80}\n")
    
    df = pd.read_csv(filepath)
    
    # Basic info
    print(f"📊 Basic Information:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Memory: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
    
    # Column info
    print(f"\n📋 Columns:")
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        print(f"   {col:30s} | {str(dtype):10s} | Nulls: {null_count:6,} ({null_pct:5.1f}%) | Unique: {unique_count:,}")
    
    # Sample data
    print(f"\n📄 Sample Data (first 3 rows):")
    print(df.head(3).to_string())
    
    # Duplicates
    dup_count = df.duplicated().sum()
    print(f"\n🔍 Duplicates: {dup_count:,} rows ({(dup_count/len(df))*100:.1f}%)")
    
    return df

def analyze_compatibility():
    """วิเคราะห์ compatibility.csv"""
    print("\n" + "="*80)
    print("ANALYZING: compatibility.csv")
    print("="*80)
    
    df = inspect_dataset("compatibility.csv")
    
    if df is None:
        return
    
    print(f"\n💡 Analysis:")
    print(f"   - ข้อมูลความเข้ากันได้ระหว่างจังหวัดกับพืช")
    print(f"   - มี {df['province'].nunique()} จังหวัด")
    print(f"   - มี {df['crop_type'].nunique()} ชนิดพืช")
    print(f"   - Compatibility score range: {df['compatibility_score'].min():.3f} - {df['compatibility_score'].max():.3f}")
    
    print(f"\n🤔 Usage Assessment:")
    print(f"   - ไม่ได้ใช้ใน Model A, B, C, D")
    print(f"   - ข้อมูลนี้อาจซ้ำซ้อนกับ crop_characteristics.csv")
    print(f"   - แนะนำ: ลบออก หรือ merge เข้ากับ crop_characteristics")

def analyze_economic():
    """วิเคราะห์ economic.csv"""
    print("\n" + "="*80)
    print("ANALYZING: economic.csv")
    print("="*80)
    
    df = inspect_dataset("economic.csv")
    
    if df is None:
        return
    
    print(f"\n💡 Analysis:")
    print(f"   - ข้อมูลเศรษฐกิจมหภาค (fuel, fertilizer, GDP, inflation)")
    print(f"   - ช่วงเวลา: {df['date'].min()} ถึง {df['date'].max()}")
    print(f"   - {len(df)} วัน")
    
    print(f"\n🤔 Usage Assessment:")
    print(f"   - ไม่ได้ใช้ใน Model A, B, C, D")
    print(f"   - อาจมีประโยชน์สำหรับ Model C (Price Forecast) ในอนาคต")
    print(f"   - แนะนำ: เก็บไว้ถ้าจะพัฒนา Model C ต่อ, ไม่งั้นลบออก")

def analyze_population():
    """วิเคราะห์ population.csv"""
    print("\n" + "="*80)
    print("ANALYZING: population.csv")
    print("="*80)
    
    df = inspect_dataset("population.csv")
    
    if df is None:
        return
    
    print(f"\n💡 Analysis:")
    print(f"   - ข้อมูลประชากรแต่ละจังหวัด")
    print(f"   - มี {df['province'].nunique()} จังหวัด")
    print(f"   - ช่วงเวลา: {df['date'].min()} ถึง {df['date'].max()}")
    
    print(f"\n🤔 Usage Assessment:")
    print(f"   - ไม่ได้ใช้ใน Model A, B, C, D")
    print(f"   - ข้อมูลนี้ไม่เกี่ยวข้องโดยตรงกับการทำนายพืช")
    print(f"   - แนะนำ: ลบออก")

def analyze_profit():
    """วิเคราะห์ profit.csv"""
    print("\n" + "="*80)
    print("ANALYZING: profit.csv")
    print("="*80)
    
    df = inspect_dataset("profit.csv")
    
    if df is None:
        return
    
    print(f"\n💡 Analysis:")
    print(f"   - ข้อมูลกำไรจากการปลูก")
    print(f"   - มี {len(df)} records")
    print(f"   - Average profit: {df['profit'].mean():,.2f} baht")
    print(f"   - Average ROI: {df['roi_percent'].mean():.2f}%")
    
    print(f"\n🤔 Usage Assessment:")
    print(f"   - ไม่ได้ใช้ใน Model A, B, C, D")
    print(f"   - ข้อมูลนี้มี POST-HARVEST information (data leakage risk)")
    print(f"   - ข้อมูลบางส่วนซ้ำกับ cultivation.csv")
    print(f"   - แนะนำ: ลบออก (มีความเสี่ยง data leakage)")

def analyze_farmme_gpu():
    """วิเคราะห์ FARMME_GPU_DATASET.csv"""
    print("\n" + "="*80)
    print("ANALYZING: FARMME_GPU_DATASET.csv")
    print("="*80)
    
    filepath = DATASET_DIR / "FARMME_GPU_DATASET.csv"
    
    if not filepath.exists():
        print(f"❌ File not found")
        return
    
    # Read only first few rows (file is huge)
    df_sample = pd.read_csv(filepath, nrows=1000)
    
    print(f"📊 Basic Information (from sample):")
    print(f"   File size: {filepath.stat().st_size / (1024*1024*1024):.2f} GB")
    print(f"   Columns: {len(df_sample.columns)}")
    print(f"   Sample rows: {len(df_sample)}")
    
    print(f"\n📋 Columns:")
    for col in df_sample.columns[:20]:  # Show first 20 columns
        print(f"   - {col}")
    if len(df_sample.columns) > 20:
        print(f"   ... and {len(df_sample.columns) - 20} more columns")
    
    print(f"\n🤔 Usage Assessment:")
    print(f"   - ไม่ได้ใช้ใน Model A, B, C, D")
    print(f"   - ไฟล์ใหญ่มาก (1.1 GB)")
    print(f"   - อาจเป็น raw dataset ที่ยังไม่ได้ประมวลผล")
    print(f"   - แนะนำ: ลบออก (ประหยัดพื้นที่ได้มาก)")

def generate_cleanup_recommendations():
    """สร้างคำแนะนำการทำความสะอาด"""
    print("\n" + "="*80)
    print("CLEANUP RECOMMENDATIONS".center(80))
    print("="*80)
    
    recommendations = {
        "immediate_delete": [
            {
                "file": "FARMME_GPU_DATASET.csv",
                "reason": "ไฟล์ใหญ่มาก (1.1 GB), ไม่ได้ใช้, ประหยัดพื้นที่ได้มาก",
                "size_mb": 1125.87,
                "priority": "HIGH"
            },
            {
                "file": "population.csv",
                "reason": "ไม่เกี่ยวข้องกับ models, ไม่มีประโยชน์",
                "size_mb": 10.71,
                "priority": "HIGH"
            },
            {
                "file": "profit.csv",
                "reason": "มีความเสี่ยง data leakage, ข้อมูลซ้ำกับ cultivation.csv",
                "size_mb": 1.33,
                "priority": "HIGH"
            }
        ],
        "consider_delete": [
            {
                "file": "compatibility.csv",
                "reason": "ซ้ำซ้อนกับ crop_characteristics.csv",
                "size_mb": 0.31,
                "priority": "MEDIUM"
            },
            {
                "file": "economic.csv",
                "reason": "ไม่ได้ใช้ตอนนี้, แต่อาจมีประโยชน์ในอนาคต",
                "size_mb": 0.11,
                "priority": "LOW"
            }
        ]
    }
    
    print("\n🔴 HIGH PRIORITY - ลบทันที:")
    total_savings = 0
    for item in recommendations["immediate_delete"]:
        print(f"\n   ❌ {item['file']}")
        print(f"      Size: {item['size_mb']:.2f} MB")
        print(f"      Reason: {item['reason']}")
        total_savings += item['size_mb']
    
    print(f"\n   💾 Total savings: {total_savings:.2f} MB")
    
    print("\n\n🟡 MEDIUM/LOW PRIORITY - พิจารณาลบ:")
    for item in recommendations["consider_delete"]:
        print(f"\n   ⚠️  {item['file']}")
        print(f"      Size: {item['size_mb']:.2f} MB")
        print(f"      Reason: {item['reason']}")
        print(f"      Priority: {item['priority']}")
    
    # Save recommendations
    with open("cleanup_recommendations.json", 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n📄 Recommendations saved to: cleanup_recommendations.json")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Specific Datasets")
    parser.add_argument("--all", action="store_true", help="Analyze all unused datasets")
    parser.add_argument("--compatibility", action="store_true", help="Analyze compatibility.csv")
    parser.add_argument("--economic", action="store_true", help="Analyze economic.csv")
    parser.add_argument("--population", action="store_true", help="Analyze population.csv")
    parser.add_argument("--profit", action="store_true", help="Analyze profit.csv")
    parser.add_argument("--farmme", action="store_true", help="Analyze FARMME_GPU_DATASET.csv")
    parser.add_argument("--recommend", action="store_true", help="Generate cleanup recommendations")
    
    args = parser.parse_args()
    
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found: {DATASET_DIR}")
        return
    
    if args.all:
        analyze_compatibility()
        analyze_economic()
        analyze_population()
        analyze_profit()
        analyze_farmme_gpu()
        generate_cleanup_recommendations()
    else:
        if args.compatibility:
            analyze_compatibility()
        if args.economic:
            analyze_economic()
        if args.population:
            analyze_population()
        if args.profit:
            analyze_profit()
        if args.farmme:
            analyze_farmme_gpu()
        if args.recommend:
            generate_cleanup_recommendations()
        
        if not any([args.compatibility, args.economic, args.population, 
                   args.profit, args.farmme, args.recommend]):
            print("Please specify an option. Use --help for more information.")
            print("\nQuick start: python manage_specific_datasets.py --all")

if __name__ == "__main__":
    main()

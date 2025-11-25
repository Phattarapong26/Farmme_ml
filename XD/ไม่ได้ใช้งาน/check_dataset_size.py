# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

dataset_dir = Path("buildingModel.py/Dataset")

files = [
    'cultivation.csv',
    'weather.csv', 
    'price.csv',
    'economic.csv',
    'crop_characteristics.csv'
]

print("=" * 60)
print("DATASET SIZE ANALYSIS")
print("=" * 60)
print()

total_rows = 0

for file in files:
    filepath = dataset_dir / file
    if filepath.exists():
        df = pd.read_csv(filepath, encoding='utf-8')
        rows = len(df)
        cols = len(df.columns)
        total_rows += rows
        
        print(f"{file:30s}: {rows:>10,} rows x {cols:>3} cols")
        
        # Show date range if date column exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            date_range = f"({df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')})"
            print(f"{'':30s}  {date_range}")
        
        # Show unique values for key columns
        if file == 'cultivation.csv':
            print(f"{'':30s}  Unique crops: {df['crop_type'].nunique()}")
            print(f"{'':30s}  Unique provinces: {df['province'].nunique()}")
        
        print()

print("=" * 60)
print(f"TOTAL ROWS ACROSS ALL FILES: {total_rows:,}")
print("=" * 60)

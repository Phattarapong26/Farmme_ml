#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import All Datasets to Supabase
นำเข้าข้อมูลทั้งหมดจาก Dataset folder เข้า Supabase
"""

import sys
import os
sys.path.insert(0, 'backend')

import pandas as pd
from datetime import datetime
from database import SessionLocal, CropPrice, CropCharacteristics, WeatherData, CropCultivation, EconomicFactors
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dataset paths
DATASET_DIR = "Farmme_SmartEconomic/buildingModel.py/Dataset"

def import_crop_characteristics():
    """นำเข้าข้อมูล crop_characteristics.csv"""
    logger.info("=" * 60)
    logger.info("📊 Importing Crop Characteristics...")
    
    try:
        df = pd.read_csv(f"{DATASET_DIR}/crop_characteristics.csv")
        logger.info(f"✅ Found {len(df)} crop characteristics")
        
        db = SessionLocal()
        imported = 0
        updated = 0
        
        for _, row in df.iterrows():
            # Check if exists
            existing = db.query(CropCharacteristics).filter(
                CropCharacteristics.crop_type == row['crop_type']
            ).first()
            
            if existing:
                # Update
                existing.crop_category = row.get('crop_category')
                existing.growth_days = int(row['growth_days']) if pd.notna(row['growth_days']) else None
                existing.water_requirement = row.get('water_requirement')
                existing.soil_preference = row.get('soil_preference')
                existing.investment_cost = float(row['investment_cost']) if pd.notna(row['investment_cost']) else None
                existing.risk_level = row.get('risk_level')
                existing.seasonal_type = row.get('seasonal_type')
                existing.updated_at = datetime.now()
                updated += 1
            else:
                # Insert
                crop = CropCharacteristics(
                    crop_type=row['crop_type'],
                    crop_category=row.get('crop_category'),
                    growth_days=int(row['growth_days']) if pd.notna(row['growth_days']) else None,
                    water_requirement=row.get('water_requirement'),
                    soil_preference=row.get('soil_preference'),
                    investment_cost=float(row['investment_cost']) if pd.notna(row['investment_cost']) else None,
                    risk_level=row.get('risk_level'),
                    seasonal_type=row.get('seasonal_type'),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(crop)
                imported += 1
        
        db.commit()
        logger.info(f"✅ Imported {imported} new crops, Updated {updated} crops")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing crop characteristics: {e}")
        return False

def import_weather_data():
    """นำเข้าข้อมูล weather.csv"""
    logger.info("=" * 60)
    logger.info("🌤️ Importing Weather Data...")
    
    try:
        df = pd.read_csv(f"{DATASET_DIR}/weather.csv")
        logger.info(f"✅ Found {len(df)} weather records")
        
        db = SessionLocal()
        imported = 0
        skipped = 0
        batch_size = 1000
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    weather_date = pd.to_datetime(row['date']).date()
                    province = row['province']
                    
                    # Check if exists
                    existing = db.query(WeatherData).filter(
                        WeatherData.province == province,
                        WeatherData.date == weather_date
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Insert
                    weather = WeatherData(
                        province=province,
                        date=weather_date,
                        temperature_celsius=float(row['temperature_celsius']) if pd.notna(row['temperature_celsius']) else None,
                        rainfall_mm=float(row['rainfall_mm']) if pd.notna(row['rainfall_mm']) else None,
                        source='dataset',
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.add(weather)
                    imported += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Skipping row: {e}")
                    continue
            
            # Commit batch
            db.commit()
            logger.info(f"📦 Batch {i//batch_size + 1}: Imported {imported}, Skipped {skipped}")
        
        logger.info(f"✅ Total: Imported {imported} new records, Skipped {skipped} duplicates")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing weather data: {e}")
        return False

def import_price_data():
    """นำเข้าข้อมูล price.csv (ไฟล์ใหญ่)"""
    logger.info("=" * 60)
    logger.info("💰 Importing Price Data (Large File)...")
    
    try:
        # Read in chunks
        chunk_size = 10000
        imported = 0
        skipped = 0
        chunk_num = 0
        
        db = SessionLocal()
        
        for chunk in pd.read_csv(f"{DATASET_DIR}/price.csv", chunksize=chunk_size):
            chunk_num += 1
            logger.info(f"📦 Processing chunk {chunk_num} ({len(chunk)} rows)...")
            
            for _, row in chunk.iterrows():
                try:
                    price_date = pd.to_datetime(row['date']).date()
                    crop_type = row['crop_type']
                    province = row['province']
                    
                    # Check if exists
                    existing = db.query(CropPrice).filter(
                        CropPrice.crop_type == crop_type,
                        CropPrice.province == province,
                        CropPrice.date == price_date
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Insert
                    price = CropPrice(
                        crop_type=crop_type,
                        province=province,
                        price_per_kg=float(row['price_per_kg']) if pd.notna(row['price_per_kg']) else None,
                        date=price_date,
                        source='dataset',
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.add(price)
                    imported += 1
                    
                    # Commit every 1000 records
                    if imported % 1000 == 0:
                        db.commit()
                        logger.info(f"   💾 Committed {imported} records...")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Skipping row: {e}")
                    continue
            
            # Commit chunk
            db.commit()
            logger.info(f"✅ Chunk {chunk_num}: Imported {imported}, Skipped {skipped}")
        
        logger.info(f"✅ Total: Imported {imported} new records, Skipped {skipped} duplicates")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing price data: {e}")
        return False

def import_cultivation_data():
    """นำเข้าข้อมูล cultivation.csv"""
    logger.info("=" * 60)
    logger.info("🌾 Importing Cultivation Data...")
    
    try:
        df = pd.read_csv(f"{DATASET_DIR}/cultivation.csv")
        logger.info(f"✅ Found {len(df)} cultivation records")
        
        db = SessionLocal()
        imported = 0
        batch_size = 1000
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    cultivation = CropCultivation(
                        crop_name=row['crop_type'],
                        province=row['province'],
                        planting_date=pd.to_datetime(row['planting_date']).date() if pd.notna(row['planting_date']) else None,
                        harvest_date=pd.to_datetime(row['harvest_date']).date() if pd.notna(row['harvest_date']) else None,
                        yield_kg=float(row['actual_yield_kg']) if pd.notna(row['actual_yield_kg']) else None,
                        area_rai=float(row['planting_area_rai']) if pd.notna(row['planting_area_rai']) else None,
                        created_at=datetime.now()
                    )
                    db.add(cultivation)
                    imported += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Skipping row: {e}")
                    continue
            
            # Commit batch
            db.commit()
            logger.info(f"📦 Batch {i//batch_size + 1}: Imported {imported}")
        
        logger.info(f"✅ Total: Imported {imported} records")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing cultivation data: {e}")
        return False

def import_economic_data():
    """นำเข้าข้อมูล economic.csv"""
    logger.info("=" * 60)
    logger.info("📈 Importing Economic Data...")
    
    try:
        df = pd.read_csv(f"{DATASET_DIR}/economic.csv")
        logger.info(f"✅ Found {len(df)} economic records")
        
        db = SessionLocal()
        imported = 0
        
        # Import multiple factors per date
        factors_to_import = [
            ('fuel_price', 'fuel_price'),
            ('fertilizer_price', 'fertilizer_price'),
            ('export_volume', 'export_volume'),
            ('inflation_rate', 'inflation_rate'),
            ('gdp_growth', 'gdp_growth'),
            ('unemployment_rate', 'unemployment_rate'),
        ]
        
        for _, row in df.iterrows():
            try:
                econ_date = pd.to_datetime(row['date']).date()
                
                for factor_name, column_name in factors_to_import:
                    if pd.notna(row[column_name]):
                        # Check if exists
                        existing = db.query(EconomicFactors).filter(
                            EconomicFactors.factor_name == factor_name,
                            EconomicFactors.date == econ_date
                        ).first()
                        
                        if not existing:
                            factor = EconomicFactors(
                                factor_name=factor_name,
                                value=float(row[column_name]),
                                date=econ_date,
                                created_at=datetime.now()
                            )
                            db.add(factor)
                            imported += 1
                
                # Commit every 100 dates
                if imported % 600 == 0:
                    db.commit()
                    logger.info(f"   💾 Committed {imported} records...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Skipping row: {e}")
                continue
        
        db.commit()
        logger.info(f"✅ Total: Imported {imported} records")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing economic data: {e}")
        return False

def main():
    """Main import function"""
    logger.info("🚀 Starting Dataset Import to Supabase")
    logger.info("=" * 60)
    
    results = {}
    
    # 1. Import Crop Characteristics (small, fast)
    results['crop_characteristics'] = import_crop_characteristics()
    
    # 2. Import Weather Data (medium size)
    results['weather'] = import_weather_data()
    
    # 3. Import Price Data (LARGE - will take time)
    logger.info("\n⚠️ WARNING: Price data is LARGE. This will take several minutes...")
    results['price'] = import_price_data()
    
    # 4. Import Cultivation Data (medium size)
    results['cultivation'] = import_cultivation_data()
    
    # 5. Import Economic Data (small)
    results['economic'] = import_economic_data()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 IMPORT SUMMARY")
    logger.info("=" * 60)
    for table, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{table:25s}: {status}")
    
    logger.info("=" * 60)
    logger.info("🎉 Import process completed!")

if __name__ == "__main__":
    main()

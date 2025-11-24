#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import Dashboard Data from CSV files to PostgreSQL Database
Imports all datasets needed for comprehensive dashboard charts
"""

import sys
import os
import pandas as pd
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from database import (
    CropPrice, WeatherData, CropCharacteristics, 
    CropCultivation, EconomicFactors
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dataset paths
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'buildingModel.py', 'Dataset')

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

def import_price_data():
    """Import price data from price.csv"""
    try:
        logger.info("📊 Importing price data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'price.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                price = CropPrice(
                    crop_type=str(row.get('crop_type', row.get('Crop_Type', ''))),
                    province=str(row.get('province', row.get('Province', ''))),
                    price_per_kg=float(row.get('price_per_kg', row.get('Price_Per_Kg', 0))),
                    date=pd.to_datetime(row.get('date', row.get('Date', datetime.now()))),
                    source=str(row.get('source', 'CSV Import')),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(price)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} price records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} price records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing price data: {e}")
        return 0

def import_weather_data():
    """Import weather data from weather.csv"""
    try:
        logger.info("🌤️ Importing weather data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'weather.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                weather = WeatherData(
                    province=str(row.get('province', row.get('Province', ''))),
                    date=pd.to_datetime(row.get('date', row.get('Date', datetime.now()))),
                    temperature_celsius=float(row.get('temperature', row.get('Temperature', 0))),
                    rainfall_mm=float(row.get('rainfall', row.get('Rainfall', 0))),
                    source=str(row.get('source', 'CSV Import')),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(weather)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} weather records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} weather records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing weather data: {e}")
        return 0

def import_crop_characteristics():
    """Import crop characteristics from crop_characteristics.csv"""
    try:
        logger.info("🌱 Importing crop characteristics...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'crop_characteristics.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                crop_char = CropCharacteristics(
                    crop_type=str(row.get('crop_type', row.get('Crop_Type', ''))),
                    growth_days=int(row.get('growth_days', row.get('Growth_Days', 0))) if pd.notna(row.get('growth_days', row.get('Growth_Days'))) else None,
                    water_requirement=str(row.get('water_requirement', row.get('Water_Requirement', ''))) if pd.notna(row.get('water_requirement')) else None,
                    suitable_regions=str(row.get('suitable_regions', row.get('Suitable_Regions', ''))) if pd.notna(row.get('suitable_regions')) else None,
                    soil_preference=str(row.get('soil_preference', row.get('Soil_Preference', ''))) if pd.notna(row.get('soil_preference')) else None,
                    investment_cost=float(row.get('investment_cost', row.get('Investment_Cost', 0))) if pd.notna(row.get('investment_cost')) else None,
                    risk_level=str(row.get('risk_level', row.get('Risk_Level', ''))) if pd.notna(row.get('risk_level')) else None,
                    seasonal_type=str(row.get('seasonal_type', row.get('Seasonal_Type', ''))) if pd.notna(row.get('seasonal_type')) else None,
                    crop_category=str(row.get('crop_category', row.get('Crop_Category', 'อื่นๆ'))),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(crop_char)
                count += 1
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} crop characteristic records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing crop characteristics: {e}")
        return 0

def import_cultivation_data():
    """Import cultivation data from cultivation.csv"""
    try:
        logger.info("🚜 Importing cultivation data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'cultivation.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                cultivation = CropCultivation(
                    crop_name=str(row.get('crop_name', row.get('Crop_Name', ''))),
                    province=str(row.get('province', row.get('Province', ''))),
                    planting_date=pd.to_datetime(row.get('planting_date', row.get('Planting_Date'))) if pd.notna(row.get('planting_date')) else None,
                    harvest_date=pd.to_datetime(row.get('harvest_date', row.get('Harvest_Date'))) if pd.notna(row.get('harvest_date')) else None,
                    yield_kg=float(row.get('yield_kg', row.get('Yield_Kg', 0))) if pd.notna(row.get('yield_kg')) else None,
                    area_rai=float(row.get('area_rai', row.get('Area_Rai', 0))) if pd.notna(row.get('area_rai')) else None,
                    created_at=datetime.now()
                )
                db.add(cultivation)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} cultivation records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} cultivation records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing cultivation data: {e}")
        return 0

def import_economic_data():
    """Import economic data from economic.csv"""
    try:
        logger.info("💰 Importing economic data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'economic.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                economic = EconomicFactors(
                    factor_name=str(row.get('factor_name', row.get('Factor_Name', ''))),
                    value=float(row.get('value', row.get('Value', 0))),
                    date=pd.to_datetime(row.get('date', row.get('Date', datetime.now()))),
                    created_at=datetime.now()
                )
                db.add(economic)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} economic records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} economic records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing economic data: {e}")
        return 0

def main():
    """Main import function"""
    print("=" * 60)
    print("🚀 Dashboard Data Import Script")
    print("=" * 60)
    print()
    
    # Create tables
    create_tables()
    print()
    
    # Import all datasets
    total_records = 0
    
    total_records += import_price_data()
    print()
    
    total_records += import_weather_data()
    print()
    
    total_records += import_crop_characteristics()
    print()
    
    total_records += import_cultivation_data()
    print()
    
    total_records += import_economic_data()
    print()
    
    print("=" * 60)
    print(f"✅ Import Complete!")
    print(f"📊 Total records imported: {total_records}")
    print("=" * 60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import Additional Dashboard Data
Imports: Farmer Profiles, Population, Profit, Compatibility data
"""

import sys
import os
import pandas as pd
from datetime import datetime
import logging
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dataset paths
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'buildingModel.py', 'Dataset')

# Define additional models
class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    province = Column(String, index=True)
    total_farmers = Column(Integer)
    avg_age = Column(Float)
    avg_experience_years = Column(Float)
    avg_land_size_rai = Column(Float)
    education_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class PopulationData(Base):
    __tablename__ = "population_data"
    
    id = Column(Integer, primary_key=True, index=True)
    province = Column(String, index=True)
    total_population = Column(Integer)
    working_age_population = Column(Integer)
    agricultural_population = Column(Integer)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProfitData(Base):
    __tablename__ = "profit_data"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True)
    province = Column(String, index=True)
    avg_profit_per_rai = Column(Float)
    avg_roi_percent = Column(Float)
    avg_margin_percent = Column(Float)
    investment_cost = Column(Float)
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class CompatibilityScore(Base):
    __tablename__ = "compatibility_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True)
    province = Column(String, index=True)
    soil_compatibility = Column(Float)
    climate_compatibility = Column(Float)
    water_compatibility = Column(Float)
    overall_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_additional_tables():
    """Create additional database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Additional tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

def import_farmer_profiles():
    """Import farmer profile data"""
    try:
        logger.info("👨‍🌾 Importing farmer profiles...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'farmer_profiles.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                profile = FarmerProfile(
                    province=str(row.get('province', row.get('Province', ''))),
                    total_farmers=int(row.get('total_farmers', row.get('Total_Farmers', 0))) if pd.notna(row.get('total_farmers')) else 0,
                    avg_age=float(row.get('avg_age', row.get('Avg_Age', 0))) if pd.notna(row.get('avg_age')) else None,
                    avg_experience_years=float(row.get('avg_experience', row.get('Avg_Experience', 0))) if pd.notna(row.get('avg_experience')) else None,
                    avg_land_size_rai=float(row.get('avg_land_size', row.get('Avg_Land_Size', 0))) if pd.notna(row.get('avg_land_size')) else None,
                    education_level=str(row.get('education_level', row.get('Education_Level', ''))) if pd.notna(row.get('education_level')) else None,
                    created_at=datetime.now()
                )
                db.add(profile)
                count += 1
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} farmer profile records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing farmer profiles: {e}")
        return 0

def import_population_data():
    """Import population data"""
    try:
        logger.info("👥 Importing population data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'population.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                population = PopulationData(
                    province=str(row.get('province', row.get('Province', ''))),
                    total_population=int(row.get('total_population', row.get('Total_Population', 0))) if pd.notna(row.get('total_population')) else 0,
                    working_age_population=int(row.get('working_age', row.get('Working_Age', 0))) if pd.notna(row.get('working_age')) else 0,
                    agricultural_population=int(row.get('agricultural_pop', row.get('Agricultural_Population', 0))) if pd.notna(row.get('agricultural_pop')) else 0,
                    year=int(row.get('year', row.get('Year', 2024))) if pd.notna(row.get('year')) else 2024,
                    created_at=datetime.now()
                )
                db.add(population)
                count += 1
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} population records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing population data: {e}")
        return 0

def import_profit_data():
    """Import profit data"""
    try:
        logger.info("💵 Importing profit data...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'profit.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                profit = ProfitData(
                    crop_type=str(row.get('crop_type', row.get('Crop_Type', ''))),
                    province=str(row.get('province', row.get('Province', ''))),
                    avg_profit_per_rai=float(row.get('profit_per_rai', row.get('Profit_Per_Rai', 0))) if pd.notna(row.get('profit_per_rai')) else 0,
                    avg_roi_percent=float(row.get('roi_percent', row.get('ROI_Percent', 0))) if pd.notna(row.get('roi_percent')) else 0,
                    avg_margin_percent=float(row.get('margin_percent', row.get('Margin_Percent', 0))) if pd.notna(row.get('margin_percent')) else 0,
                    investment_cost=float(row.get('investment', row.get('Investment', 0))) if pd.notna(row.get('investment')) else 0,
                    revenue=float(row.get('revenue', row.get('Revenue', 0))) if pd.notna(row.get('revenue')) else 0,
                    created_at=datetime.now()
                )
                db.add(profit)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} profit records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} profit records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing profit data: {e}")
        return 0

def import_compatibility_data():
    """Import compatibility score data"""
    try:
        logger.info("🎯 Importing compatibility scores...")
        df = pd.read_csv(os.path.join(DATASET_DIR, 'compatibility.csv'))
        
        db = SessionLocal()
        count = 0
        
        for _, row in df.iterrows():
            try:
                compatibility = CompatibilityScore(
                    crop_type=str(row.get('crop_type', row.get('Crop_Type', ''))),
                    province=str(row.get('province', row.get('Province', ''))),
                    soil_compatibility=float(row.get('soil_score', row.get('Soil_Score', 0))) if pd.notna(row.get('soil_score')) else 0,
                    climate_compatibility=float(row.get('climate_score', row.get('Climate_Score', 0))) if pd.notna(row.get('climate_score')) else 0,
                    water_compatibility=float(row.get('water_score', row.get('Water_Score', 0))) if pd.notna(row.get('water_score')) else 0,
                    overall_score=float(row.get('overall_score', row.get('Overall_Score', 0))) if pd.notna(row.get('overall_score')) else 0,
                    created_at=datetime.now()
                )
                db.add(compatibility)
                count += 1
                
                if count % 1000 == 0:
                    db.commit()
                    logger.info(f"   Imported {count} compatibility records...")
            except Exception as e:
                logger.warning(f"   Skipping row: {e}")
                continue
        
        db.commit()
        db.close()
        logger.info(f"✅ Imported {count} compatibility records")
        return count
    except Exception as e:
        logger.error(f"❌ Error importing compatibility data: {e}")
        return 0

def main():
    """Main import function"""
    print("=" * 60)
    print("🚀 Additional Dashboard Data Import Script")
    print("=" * 60)
    print()
    
    # Create tables
    create_additional_tables()
    print()
    
    # Import all datasets
    total_records = 0
    
    total_records += import_farmer_profiles()
    print()
    
    total_records += import_population_data()
    print()
    
    total_records += import_profit_data()
    print()
    
    total_records += import_compatibility_data()
    print()
    
    print("=" * 60)
    print(f"✅ Additional Data Import Complete!")
    print(f"📊 Total records imported: {total_records}")
    print("=" * 60)

if __name__ == "__main__":
    main()

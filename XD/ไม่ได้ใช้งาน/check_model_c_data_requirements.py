#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ตรวจสอบว่า Dataset เพียงพอสำหรับ Model C หรือไม่
"""

import sys
sys.path.insert(0, 'backend')

from database import SessionLocal, CropPrice, WeatherData, CropCharacteristics
from sqlalchemy import func, distinct, desc
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_crop_price_data():
    """ตรวจสอบข้อมูล CropPrice"""
    logger.info("=" * 60)
    logger.info("💰 Checking CropPrice Data for Model C")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    # 1. Total records
    total = db.query(CropPrice).count()
    logger.info(f"📊 Total price records: {total:,}")
    
    # 2. Date range
    oldest = db.query(func.min(CropPrice.date)).scalar()
    newest = db.query(func.max(CropPrice.date)).scalar()
    logger.info(f"📅 Date range: {oldest} to {newest}")
    
    if oldest and newest:
        days_span = (newest - oldest).days
        logger.info(f"📆 Data span: {days_span} days")
    
    # 3. Unique crops
    crops = db.query(distinct(CropPrice.crop_type)).count()
    logger.info(f"🌾 Unique crops: {crops}")
    
    # 4. Unique provinces
    provinces = db.query(distinct(CropPrice.province)).count()
    logger.info(f"📍 Unique provinces: {provinces}")
    
    # 5. Check Model C requirements (90 days of data)
    logger.info("\n" + "=" * 60)
    logger.info("🔍 Model C Requirements Check (Need 90 days)")
    logger.info("=" * 60)
    
    # Get sample crops
    sample_crops = db.query(distinct(CropPrice.crop_type)).limit(10).all()
    sample_provinces = db.query(distinct(CropPrice.province)).limit(5).all()
    
    sufficient_count = 0
    insufficient_count = 0
    
    for crop in sample_crops[:5]:  # Check first 5 crops
        crop_type = crop[0]
        for province in sample_provinces[:3]:  # Check first 3 provinces
            province_name = province[0]
            
            # Count records for this crop+province
            count = db.query(CropPrice).filter(
                CropPrice.crop_type == crop_type,
                CropPrice.province == province_name
            ).count()
            
            # Get latest date
            latest = db.query(func.max(CropPrice.date)).filter(
                CropPrice.crop_type == crop_type,
                CropPrice.province == province_name
            ).scalar()
            
            status = "✅" if count >= 90 else "⚠️"
            if count >= 90:
                sufficient_count += 1
            else:
                insufficient_count += 1
            
            logger.info(f"{status} {crop_type:20s} | {province_name:20s} | {count:4d} records | Latest: {latest}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Sufficient data (≥90 days): {sufficient_count}")
    logger.info(f"⚠️  Insufficient data (<90 days): {insufficient_count}")
    
    db.close()
    return sufficient_count > 0

def check_weather_data():
    """ตรวจสอบข้อมูล WeatherData"""
    logger.info("\n" + "=" * 60)
    logger.info("🌤️ Checking WeatherData")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    # 1. Total records
    total = db.query(WeatherData).count()
    logger.info(f"📊 Total weather records: {total:,}")
    
    # 2. Date range
    oldest = db.query(func.min(WeatherData.date)).scalar()
    newest = db.query(func.max(WeatherData.date)).scalar()
    logger.info(f"📅 Date range: {oldest} to {newest}")
    
    # 3. Unique provinces
    provinces = db.query(distinct(WeatherData.province)).count()
    logger.info(f"📍 Unique provinces: {provinces}")
    
    db.close()
    return total > 0

def check_crop_characteristics():
    """ตรวจสอบข้อมูล CropCharacteristics"""
    logger.info("\n" + "=" * 60)
    logger.info("🌾 Checking CropCharacteristics")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    # 1. Total crops
    total = db.query(CropCharacteristics).count()
    logger.info(f"📊 Total crops: {total}")
    
    # 2. Sample crops
    crops = db.query(CropCharacteristics).limit(10).all()
    logger.info("\n📋 Sample crops:")
    for crop in crops:
        logger.info(f"   - {crop.crop_type:20s} | {crop.crop_category:10s} | {crop.growth_days} days")
    
    db.close()
    return total > 0

def check_model_c_compatibility():
    """ตรวจสอบความพร้อมสำหรับ Model C"""
    logger.info("\n" + "=" * 60)
    logger.info("🎯 Model C Compatibility Check")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    # Test with actual Model C crops
    test_cases = [
        ("พริก", "เชียงใหม่"),
        ("มะเขือเทศ", "เชียงใหม่"),
        ("ข้าว", "สุพรรณบุรี"),
        ("กะหล่ำปลี", "เชียงใหม่"),
        ("ผักบุ้ง", "กรุงเทพมหานคร"),
    ]
    
    ready_count = 0
    
    for crop_type, province in test_cases:
        # Get latest 90 records
        prices = db.query(CropPrice.price_per_kg).filter(
            CropPrice.crop_type == crop_type,
            CropPrice.province == province
        ).order_by(desc(CropPrice.date)).limit(90).all()
        
        count = len(prices)
        
        if count >= 90:
            latest_price = prices[0][0] if prices else None
            status = "✅ READY"
            ready_count += 1
        elif count >= 30:
            latest_price = prices[0][0] if prices else None
            status = "⚠️  PARTIAL"
        else:
            latest_price = None
            status = "❌ NOT READY"
        
        logger.info(f"{status} | {crop_type:15s} | {province:20s} | {count:3d}/90 records | Price: {latest_price}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Ready for Model C: {ready_count}/{len(test_cases)}")
    logger.info("=" * 60)
    
    db.close()
    return ready_count >= 3  # At least 3 test cases should be ready

def main():
    """Main check function"""
    logger.info("🚀 Checking Dataset Requirements for Model C")
    logger.info("=" * 60)
    
    results = {}
    
    # 1. Check CropPrice (most important)
    results['crop_price'] = check_crop_price_data()
    
    # 2. Check WeatherData (optional for Model C)
    results['weather'] = check_weather_data()
    
    # 3. Check CropCharacteristics (optional)
    results['crop_characteristics'] = check_crop_characteristics()
    
    # 4. Check Model C compatibility
    results['model_c_ready'] = check_model_c_compatibility()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 FINAL SUMMARY")
    logger.info("=" * 60)
    
    if results['crop_price'] and results['model_c_ready']:
        logger.info("✅ Dataset is SUFFICIENT for Model C!")
        logger.info("   - CropPrice data: ✅")
        logger.info("   - Model C compatibility: ✅")
    elif results['crop_price']:
        logger.info("⚠️  Dataset is PARTIALLY SUFFICIENT")
        logger.info("   - CropPrice data exists but may need more records")
    else:
        logger.info("❌ Dataset is INSUFFICIENT for Model C")
        logger.info("   - Need to import more CropPrice data")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

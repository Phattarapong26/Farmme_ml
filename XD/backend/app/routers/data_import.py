# -*- coding: utf-8 -*-
"""
Data Import API Router
Endpoints for adding new data to the system
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import logging
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, CropPrice, WeatherData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data", tags=["data-import"])


class NewPriceData(BaseModel):
    """New crop price data"""
    crop_type: str = Field(..., description="Crop type (Thai name)")
    province: str = Field(..., description="Province name (Thai)")
    price_per_kg: float = Field(..., gt=0, description="Price per kg in THB")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    source: Optional[str] = Field("api_import", description="Data source")


class NewWeatherData(BaseModel):
    """New weather data"""
    province: str = Field(..., description="Province name (Thai)")
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    rainfall_mm: float = Field(..., ge=0, description="Rainfall in mm")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    source: Optional[str] = Field("api_import", description="Data source")


class BulkPriceData(BaseModel):
    """Bulk crop price data"""
    prices: List[NewPriceData]


class BulkWeatherData(BaseModel):
    """Bulk weather data"""
    weather: List[NewWeatherData]


@router.post("/price")
async def add_price_data(data: NewPriceData, db: Session = Depends(get_db)):
    """
    Add new crop price data to the database
    
    This endpoint allows adding new price data which will be used by Model C for predictions.
    """
    try:
        logger.info(f"📊 Adding new price data: {data.crop_type} in {data.province} = {data.price_per_kg} บาท/กก.")
        
        # Parse date
        price_date = datetime.strptime(data.date, "%Y-%m-%d").date()
        
        # Check if data already exists
        existing = db.query(CropPrice).filter(
            CropPrice.crop_type == data.crop_type,
            CropPrice.province == data.province,
            CropPrice.date == price_date
        ).first()
        
        if existing:
            # Update existing record
            existing.price_per_kg = data.price_per_kg
            existing.source = data.source
            existing.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"✅ Updated existing price record (ID: {existing.id})")
            return {
                "success": True,
                "action": "updated",
                "message": f"Updated price for {data.crop_type} in {data.province}",
                "data": {
                    "id": existing.id,
                    "crop_type": data.crop_type,
                    "province": data.province,
                    "price_per_kg": data.price_per_kg,
                    "date": data.date
                }
            }
        else:
            # Create new record
            new_price = CropPrice(
                crop_type=data.crop_type,
                province=data.province,
                price_per_kg=data.price_per_kg,
                date=price_date,
                source=data.source,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_price)
            db.commit()
            db.refresh(new_price)
            
            logger.info(f"✅ Created new price record (ID: {new_price.id})")
            return {
                "success": True,
                "action": "created",
                "message": f"Added new price for {data.crop_type} in {data.province}",
                "data": {
                    "id": new_price.id,
                    "crop_type": data.crop_type,
                    "province": data.province,
                    "price_per_kg": data.price_per_kg,
                    "date": data.date
                }
            }
            
    except ValueError as e:
        logger.error(f"❌ Invalid date format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error adding price data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather")
async def add_weather_data(data: NewWeatherData, db: Session = Depends(get_db)):
    """
    Add new weather data to the database
    
    This endpoint allows adding new weather data which will be used by models for predictions.
    """
    try:
        logger.info(f"🌤️  Adding new weather data: {data.province} - {data.temperature_celsius}°C, {data.rainfall_mm}mm")
        
        # Parse date
        weather_date = datetime.strptime(data.date, "%Y-%m-%d").date()
        
        # Check if data already exists
        existing = db.query(WeatherData).filter(
            WeatherData.province == data.province,
            WeatherData.date == weather_date
        ).first()
        
        if existing:
            # Update existing record
            existing.temperature_celsius = data.temperature_celsius
            existing.rainfall_mm = data.rainfall_mm
            existing.source = data.source
            existing.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"✅ Updated existing weather record (ID: {existing.id})")
            return {
                "success": True,
                "action": "updated",
                "message": f"Updated weather for {data.province}",
                "data": {
                    "id": existing.id,
                    "province": data.province,
                    "temperature_celsius": data.temperature_celsius,
                    "rainfall_mm": data.rainfall_mm,
                    "date": data.date
                }
            }
        else:
            # Create new record
            new_weather = WeatherData(
                province=data.province,
                temperature_celsius=data.temperature_celsius,
                rainfall_mm=data.rainfall_mm,
                date=weather_date,
                source=data.source,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_weather)
            db.commit()
            db.refresh(new_weather)
            
            logger.info(f"✅ Created new weather record (ID: {new_weather.id})")
            return {
                "success": True,
                "action": "created",
                "message": f"Added new weather for {data.province}",
                "data": {
                    "id": new_weather.id,
                    "province": data.province,
                    "temperature_celsius": data.temperature_celsius,
                    "rainfall_mm": data.rainfall_mm,
                    "date": data.date
                }
            }
            
    except ValueError as e:
        logger.error(f"❌ Invalid date format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error adding weather data: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price/bulk")
async def add_bulk_price_data(data: BulkPriceData, db: Session = Depends(get_db)):
    """
    Add multiple crop price records at once
    """
    try:
        logger.info(f"📊 Adding {len(data.prices)} price records in bulk")
        
        created = 0
        updated = 0
        errors = []
        
        for price_data in data.prices:
            try:
                price_date = datetime.strptime(price_data.date, "%Y-%m-%d").date()
                
                existing = db.query(CropPrice).filter(
                    CropPrice.crop_type == price_data.crop_type,
                    CropPrice.province == price_data.province,
                    CropPrice.date == price_date
                ).first()
                
                if existing:
                    existing.price_per_kg = price_data.price_per_kg
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    new_price = CropPrice(
                        crop_type=price_data.crop_type,
                        province=price_data.province,
                        price_per_kg=price_data.price_per_kg,
                        date=price_date,
                        source=price_data.source,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(new_price)
                    created += 1
                    
            except Exception as e:
                errors.append(f"{price_data.crop_type} - {price_data.province}: {str(e)}")
        
        db.commit()
        
        logger.info(f"✅ Bulk import complete: {created} created, {updated} updated, {len(errors)} errors")
        
        return {
            "success": True,
            "created": created,
            "updated": updated,
            "errors": errors,
            "total_processed": len(data.prices)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in bulk import: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-prices")
async def get_recent_prices(
    crop_type: Optional[str] = None,
    province: Optional[str] = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get recent price data to verify imports
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        query = db.query(CropPrice).filter(CropPrice.date >= cutoff_date)
        
        if crop_type:
            query = query.filter(CropPrice.crop_type == crop_type)
        if province:
            query = query.filter(CropPrice.province == province)
        
        prices = query.order_by(CropPrice.date.desc()).limit(100).all()
        
        return {
            "success": True,
            "count": len(prices),
            "prices": [
                {
                    "id": p.id,
                    "crop_type": p.crop_type,
                    "province": p.province,
                    "price_per_kg": float(p.price_per_kg),
                    "date": p.date.isoformat(),
                    "source": p.source
                }
                for p in prices
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching recent prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

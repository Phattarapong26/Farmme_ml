# -*- coding: utf-8 -*-
"""
Forecast endpoints - API v2
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import get_db, CropPrice, ProvinceData, CropCharacteristics, WeatherData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/forecast", tags=["forecast"])

# Pydantic models for request/response
class PriceForecastRequest(BaseModel):
    province: str
    crop_type: str
    crop_category: Optional[str] = None
    days_ahead: int = 30

class PriceHistoryResponse(BaseModel):
    success: bool
    history: List[dict]
    statistics: dict
    total_records: int

@router.get("/provinces")
def get_forecast_provinces(db: Session = Depends(get_db)):
    """
    🚀 PRODUCTION: Get provinces list for frontend
    Returns provinces from database
    """
    try:
        from sqlalchemy import text
        
        # Get provinces from database
        query = text("""
            SELECT DISTINCT province 
            FROM (
                SELECT province FROM crop_prices
                UNION
                SELECT province FROM weather_data
                UNION
                SELECT province FROM crop_cultivation
            ) AS all_provinces
            ORDER BY province
        """)
        
        result = db.execute(query).fetchall()
        provinces = [row[0] for row in result]
        
        return {
            "success": True,
            "provinces": provinces,
            "total": len(provinces),
            "source": "database"
        }
        
    except Exception as e:
        logger.error(f"Error fetching provinces: {e}")
        return {
            "success": True,
            "provinces": [],
            "total": 0,
            "source": "error"
        }

@router.get("/crops")
def get_crops(province: str = None, db: Session = Depends(get_db)):
    """
    🚀 PRODUCTION: Get available crops (optionally filtered by province)
    If province is provided, returns only crops that have price data in that province
    Returns format expected by frontend: crops array with crop_type and crop_category
    """
    try:
        # If province is provided, get crops from crop_prices table for that province
        if province:
            # Query distinct crop types for the province
            crops_query = db.query(
                CropPrice.crop_type
            ).filter(
                CropPrice.province == province
            ).distinct().all()
            
            # Get crop characteristics from database
            crop_types = [crop[0] for crop in crops_query]
            
            crops = []
            for crop_type in crop_types:
                # Try to get crop info from crop_characteristics table
                crop_info = db.query(CropCharacteristics).filter(
                    CropCharacteristics.crop_type == crop_type
                ).first()
                
                if crop_info:
                    crops.append({
                        "crop_type": crop_type,
                        "crop_category": crop_info.crop_category or crop_type,
                        "growth_days": crop_info.growth_days or 90
                    })
                else:
                    # Fallback if no crop info found
                    crops.append({
                        "crop_type": crop_type,
                        "crop_category": crop_type,
                        "growth_days": 90
                    })
            
            # Sort by crop_type
            crops.sort(key=lambda x: x["crop_type"])
            
            return {
                "success": True,
                "crops": crops,
                "total": len(crops),
                "province": province,
                "source": "database"
            }
        
        # If no province, return all crops from planting model
        from planting_model_service import planting_model_service
        
        # Get crops from the ML model dataset
        crops_data = planting_model_service.get_available_crops()
        
        # Transform to format expected by frontend
        crops = []
        for crop in crops_data:
            crops.append({
                "crop_type": crop["crop_type"],
                "crop_category": crop.get("category", "ผักอื่นๆ"),
                "growth_days": crop["growth_days"]
            })
        
        return {
            "success": True,
            "crops": crops,
            "total": len(crops),
            "province": province,
            "source": "ml_model_dataset"
        }
        
    except Exception as e:
        logger.error(f"Error fetching crops: {e}")
        # Return empty list on error
        return {
            "success": True,
            "crops": [],
            "total": 0,
            "province": province,
            "source": "error"
        }

@router.get("/price-history")
def get_price_history(
    province: str,
    crop_type: str = "",
    days: int = 90,
    db: Session = Depends(get_db)
):
    """
    🚀 PRODUCTION: Get historical data for province (and optionally crop)
    - If crop_type is provided: returns price data from crop_prices table
    - If crop_type is empty: returns only weather data (temperature/rainfall)
    Used by HistoricalDataChart component
    """
    try:
        # Calculate date range
        # If days > 3650 (about 10 years), get all data without date filter
        end_date = datetime.now()
        use_date_filter = days <= 3650
        start_date = end_date - timedelta(days=days) if use_date_filter else datetime(2000, 1, 1)
        
        # Query weather data from database (temperature and rainfall depend only on province)
        weather_query = db.query(WeatherData).filter(
            WeatherData.province == province
        )
        if use_date_filter:
            weather_query = weather_query.filter(
                WeatherData.date >= start_date,
                WeatherData.date <= end_date
            )
        weather_query = weather_query.order_by(WeatherData.date.desc())
        
        weather_records = weather_query.all()
        
        # If crop_type is provided, also query price data
        price_records = []
        if crop_type:
            price_query = db.query(CropPrice).filter(
                CropPrice.province == province,
                CropPrice.crop_type == crop_type
            )
            if use_date_filter:
                price_query = price_query.filter(
                    CropPrice.date >= start_date,
                    CropPrice.date <= end_date
                )
            price_query = price_query.order_by(CropPrice.date.desc())
            
            price_records = price_query.all()
        
        # Create dictionaries for quick lookup by date
        weather_by_date = {}
        for weather in weather_records:
            date_key = weather.date.strftime("%Y-%m-%d")
            weather_by_date[date_key] = {
                "temperature": float(weather.temperature_celsius) if weather.temperature_celsius else None,
                "rainfall": float(weather.rainfall_mm) if weather.rainfall_mm else None
            }
        
        # If requesting weather data only (no crop_type)
        if not crop_type:
            logger.info(f"Weather data request for {province}, found {len(weather_records)} records")
            history = []
            for weather in weather_records:
                date_str = weather.date.strftime("%Y-%m-%d")
                history.append({
                    "date": date_str,
                    "price": None,
                    "temperature": float(weather.temperature_celsius) if weather.temperature_celsius else None,
                    "rainfall": float(weather.rainfall_mm) if weather.rainfall_mm else None
                })
            
            logger.info(f"Returning {len(history)} weather records")
            return {
                "success": True,
                "history": history,
                "statistics": {
                    "avg_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "latest_price": 0,
                    "price_trend": "stable"
                },
                "total_records": len(history),
                "province": province,
                "crop_type": "",
                "days_requested": days
            }
        
        # If requesting price data but no records found
        if not price_records:
            logger.warning(f"No price data found for {crop_type} in {province}")
            return {
                "success": True,
                "history": [],
                "statistics": {
                    "avg_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "latest_price": 0,
                    "price_trend": "stable"
                },
                "total_records": 0,
                "province": province,
                "crop_type": crop_type,
                "days_requested": days
            }
        
        # Format response - combine price and weather data
        history = []
        prices = []
        
        for record in price_records:
            date_str = record.date.strftime("%Y-%m-%d") if hasattr(record, 'date') else record.get('date')
            price_value = float(record.price_per_kg) if hasattr(record, 'price_per_kg') else float(record.get('price', 0))
            
            # Get weather data for this date
            weather_data = weather_by_date.get(date_str, {"temperature": None, "rainfall": None})
            
            price_data = {
                "date": date_str,
                "price": price_value,
                "temperature": weather_data["temperature"],
                "rainfall": weather_data["rainfall"]
            }
            history.append(price_data)
            prices.append(price_value)
        
        # Calculate statistics
        if prices:
            statistics = {
                "avg_price": np.mean(prices),
                "min_price": np.min(prices),
                "max_price": np.max(prices),
                "latest_price": prices[0] if prices else 0,
                "price_trend": "increasing" if len(prices) > 1 and prices[0] > prices[-1] else "decreasing"
            }
        else:
            statistics = {
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0,
                "latest_price": 0,
                "price_trend": "stable"
            }
        
        return {
            "success": True,
            "history": history,
            "statistics": statistics,
            "total_records": len(history),
            "province": province,
            "crop_type": crop_type,
            "days_requested": days
        }
        
    except Exception as e:
        logger.error(f"Error fetching price history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price history: {str(e)}")


@router.post("/price-forecast")
def forecast_price(
    request: PriceForecastRequest,
    db: Session = Depends(get_db)
):
    """
    🚀 PRODUCTION: Forecast crop price using Model C
    
    Request body:
    {
        "province": "กรุงเทพมหานคร",
        "crop_type": "คะน้า",
        "days_ahead": 30
    }
    
    Returns:
    {
        "success": true,
        "forecast_price_median": 45.5,
        "forecast_price_q10": 38.7,
        "forecast_price_q90": 52.3,
        "confidence": 0.85,
        "price_trend": "increasing",
        "expected_change_percent": 5.2,
        "model_used": "model_c"
    }
    """
    try:
        from app.services.price_forecast_service import price_forecast_service
        
        logger.info(f"📊 Forecasting price for {request.crop_type} in {request.province}")
        logger.info(f"   Days ahead: {request.days_ahead}")
        
        # Get current price from database
        current_price_query = db.query(CropPrice).filter(
            CropPrice.province == request.province,
            CropPrice.crop_type == request.crop_type
        ).order_by(CropPrice.date.desc()).first()
        
        current_price = float(current_price_query.price_per_kg) if current_price_query else None
        
        # Get forecast
        result = price_forecast_service.forecast_price(
            province=request.province,
            crop_type=request.crop_type,
            days_ahead=request.days_ahead,
            current_price=current_price,
            db_session=db
        )
        
        logger.info(f"✅ Forecast complete: {result['forecast_price_median']:.2f} บาท/กก.")
        
        return result
        
    except Exception as e:
        logger.error(f"Error forecasting price: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to forecast price: {str(e)}"
        )

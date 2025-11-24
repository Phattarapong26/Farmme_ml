# -*- coding: utf-8 -*-
"""
Province information endpoints - API v2
Provides comprehensive province data aggregated from multiple tables
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import os
import sys

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import get_db, CropPrice, WeatherData, CropCultivation, EconomicFactors

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/provinces", tags=["provinces"])

# Pydantic models for response
class WeatherInfo(BaseModel):
    temperature_celsius: Optional[float] = None
    rainfall_mm: Optional[float] = None
    humidity_percent: Optional[float] = None
    date: Optional[str] = None
    data_age_days: Optional[int] = None

class CropCultivationInfo(BaseModel):
    crop_type: str
    crop_category: str
    planting_area_rai: float
    average_yield_kg: float
    success_rate: float
    last_harvest_date: Optional[str] = None

class CultivationData(BaseModel):
    crops: List[CropCultivationInfo]
    total_crops: int

class CropPriceInfo(BaseModel):
    crop_type: str
    price_per_kg: float
    date: str
    trend: str  # 'increasing', 'decreasing', 'stable'
    change_percent: float

class PriceData(BaseModel):
    crops: List[CropPriceInfo]
    total_crops: int

class EconomicData(BaseModel):
    fertilizer_price: Optional[float] = None
    fuel_price: Optional[float] = None
    date: Optional[str] = None

class ProvinceComprehensiveData(BaseModel):
    weather: WeatherInfo
    cultivation: CultivationData
    prices: PriceData
    economic: EconomicData

class ProvinceComprehensiveResponse(BaseModel):
    success: bool
    province: str
    data: ProvinceComprehensiveData
    timestamp: str


@router.post("/recommendations")
def get_province_recommendations(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Get crop recommendations for a province using ML model
    
    Request body:
    {
        "province": "เชียงใหม่",
        "user_profile": {
            "soil_type": "ดินร่วน",
            "water_availability": "น้ำชลประทาน",
            "budget_level": "ปานกลาง",
            "risk_tolerance": "ปานกลาง"
        }
    }
    """
    try:
        from recommendation_model_service import recommendation_model_service
        
        province = request.get("province")
        user_profile = request.get("user_profile") or {}
        
        if not province:
            raise HTTPException(status_code=400, detail="Province is required")
        
        logger.info(f"🌾 Getting recommendations for province: {province}")
        
        # Get recommendations from ML model
        result = recommendation_model_service.get_recommendations(
            province=province,
            soil_type=user_profile.get("soil_type"),
            water_availability=user_profile.get("water_availability"),
            budget_level=user_profile.get("budget_level"),
            risk_tolerance=user_profile.get("risk_tolerance")
        )
        
        # Format response for frontend
        recommendations = []
        for rec in result.get("recommendations", []):
            recommendations.append({
                "crop_type": rec["crop_type"],
                "suitability_score": rec["suitability_score"],
                "match_reason": " | ".join(rec.get("reasons", [])),
                "expected_yield": rec.get("expected_yield_kg_per_rai", 0),
                "estimated_revenue": rec.get("estimated_revenue_per_rai", 0),
                "water_requirement": rec.get("water_requirement", "ปานกลาง"),
                "risk_level": rec.get("risk_level", "ปานกลาง"),
                "growth_days": rec.get("growth_days", 60)
            })
        
        return {
            "success": True,
            "province": province,
            "recommendations": recommendations,
            "total": len(recommendations),
            "model_used": result.get("model_used", "unknown"),
            "confidence": result.get("confidence", 0.7)
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{province_name}/comprehensive", response_model=ProvinceComprehensiveResponse)
def get_comprehensive_province_data(
    province_name: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive province data aggregated from multiple tables
    
    Returns:
    - Latest weather data (temperature, rainfall, humidity)
    - Top 5 crops by cultivation area with statistics
    - Top 5 crops with best prices (highest price per kg)
    - Economic indicators (fertilizer, fuel prices)
    """
    try:
        logger.info(f"Fetching comprehensive data for province: {province_name}")
        
        # 1. Get latest weather data (last 30 days)
        weather_data = _get_weather_data(db, province_name)
        
        # 2. Get cultivation data (top 5 crops by area, last 365 days)
        cultivation_data = _get_cultivation_data(db, province_name)
        
        # 3. Get price data with trends - Top 5 crops by highest price
        logger.info(f"📊 About to call _get_price_data for {province_name}")
        price_data = _get_price_data(db, province_name)
        logger.info(f"📊 Price data result: {price_data}")
        
        # 4. Get economic factors (last 30 days)
        economic_data = _get_economic_data(db, province_name)
        
        return {
            "success": True,
            "province": province_name,
            "data": {
                "weather": weather_data,
                "cultivation": cultivation_data,
                "prices": price_data,
                "economic": economic_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching comprehensive data for {province_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch comprehensive province data: {str(e)}"
        )


def _get_weather_data(db: Session, province: str) -> Dict[str, Any]:
    """Get latest weather data"""
    try:
        # Use raw SQL to query the actual PostgreSQL database
        from sqlalchemy import text
        
        logger.info(f"🌤️ WEATHER QUERY START for province: '{province}'")
        
        query = text("""
            SELECT 
                temperature_celsius,
                rainfall_mm,
                date
            FROM weather_data
            WHERE province = :province
            ORDER BY date DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"province": province}).first()
        
        logger.info(f"🌤️ WEATHER QUERY RESULT: {result}")
        
        if result:
            data_age = (datetime.now() - result.date).days if result.date else None
            weather_data = {
                "temperature_celsius": float(result.temperature_celsius) if result.temperature_celsius is not None else None,
                "rainfall_mm": float(result.rainfall_mm) if result.rainfall_mm is not None else None,
                "humidity_percent": None,  # Not available in current schema
                "date": result.date.strftime("%Y-%m-%d") if result.date else None,
                "data_age_days": data_age
            }
            logger.info(f"🌤️ RETURNING WEATHER DATA: {weather_data}")
            return weather_data
        else:
            logger.warning(f"⚠️ No weather data found for province: '{province}'")
            return {
                "temperature_celsius": None,
                "rainfall_mm": None,
                "humidity_percent": None,
                "date": None,
                "data_age_days": None
            }
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}", exc_info=True)
        return {
            "temperature_celsius": None,
            "rainfall_mm": None,
            "humidity_percent": None,
            "date": None,
            "data_age_days": None
        }


def _get_cultivation_data(db: Session, province: str) -> Dict[str, Any]:
    """Get top 5 crops by cultivation area from last 365 days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=365)
        
        # Use raw SQL to query the actual PostgreSQL database schema
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                crop_type,
                AVG(planting_area_rai) as avg_area,
                AVG(expected_yield_kg) as avg_yield,
                MAX(date) as last_date,
                COUNT(*) as total_records,
                SUM(CASE WHEN expected_yield_kg > 0 THEN 1 ELSE 0 END) as success_records
            FROM crop_cultivation
            WHERE province = :province
                AND date >= :cutoff_date
            GROUP BY crop_type
            ORDER BY avg_area DESC
            LIMIT 5
        """)
        
        result = db.execute(query, {
            "province": province,
            "cutoff_date": cutoff_date
        })
        
        crops = []
        for row in result:
            success_rate = (row.success_records / row.total_records * 100) if row.total_records > 0 else 0
            
            crops.append({
                "crop_type": row.crop_type,
                "crop_category": row.crop_type,  # TODO: Join with crop_characteristics for actual category
                "planting_area_rai": float(row.avg_area) if row.avg_area else 0,
                "average_yield_kg": float(row.avg_yield) if row.avg_yield else 0,
                "success_rate": float(success_rate),
                "last_harvest_date": row.last_date.strftime("%Y-%m-%d") if row.last_date else None
            })
        
        return {
            "crops": crops,
            "total_crops": len(crops)
        }
        
    except Exception as e:
        logger.error(f"Error fetching cultivation data: {e}", exc_info=True)
        return {
            "crops": [],
            "total_crops": 0
        }


def _get_price_data(db: Session, province: str) -> Dict[str, Any]:
    """Get top 5 crops with best prices (highest price per kg) in the province"""
    try:
        # Use raw SQL to get top 5 crops by price
        from sqlalchemy import text
        
        logger.info(f"💰 PRICE QUERY START for province: '{province}' - Getting top 5 crops by price")
        
        # Get top 5 crops with highest average prices (simplified query)
        query = text("""
            SELECT 
                crop_type,
                AVG(price_per_kg) as current_price,
                MAX(date) as latest_date
            FROM crop_prices
            WHERE province = :province
            GROUP BY crop_type
            ORDER BY current_price DESC
            LIMIT 5
        """)
        
        result = db.execute(query, {"province": province})
        
        crops = []
        for row in result:
            current_price = float(row.current_price) if row.current_price else 0
            
            # Get previous price for trend (30 days ago)
            prev_query = text("""
                SELECT AVG(price_per_kg) as prev_price
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date < :cutoff_date
            """)
            
            cutoff_date = datetime.now() - timedelta(days=30)
            prev_result = db.execute(prev_query, {
                "province": province,
                "crop_type": row.crop_type,
                "cutoff_date": cutoff_date
            }).first()
            
            prev_price = float(prev_result.prev_price) if prev_result and prev_result.prev_price else current_price
            
            # Calculate trend
            if prev_price > 0 and current_price != prev_price:
                change_percent = ((current_price - prev_price) / prev_price) * 100
                if change_percent > 5:
                    trend = "increasing"
                elif change_percent < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                change_percent = 0
                trend = "stable"
            
            crops.append({
                "crop_type": row.crop_type,
                "price_per_kg": current_price,
                "date": row.latest_date.strftime("%Y-%m-%d") if row.latest_date else datetime.now().strftime("%Y-%m-%d"),
                "trend": trend,
                "change_percent": float(change_percent)
            })
        
        logger.info(f"💰 FOUND {len(crops)} crops with prices")
        logger.info(f"💰 PRICE DATA: {crops}")
        
        return {
            "crops": crops,
            "total_crops": len(crops)
        }
        
    except Exception as e:
        logger.error(f"💰 ERROR fetching price data: {e}", exc_info=True)
        return {
            "crops": [],
            "total_crops": 0
        }


def _get_economic_data(db: Session, province: str) -> Dict[str, Any]:
    """Get ALL economic factors (overall time) - returns both latest value and full timeline"""
    try:
        # Use raw SQL to query the actual database schema
        from sqlalchemy import text
        
        # Get ALL data (no date filter for overall time)
        query = text("""
            SELECT 
                fertilizer_price,
                fuel_price,
                date
            FROM economic_factors
            ORDER BY date ASC
        """)
        
        results = db.execute(query).fetchall()
        
        if results:
            # Return both latest value (for backward compatibility) and full timeline
            latest = results[-1]  # Last item (most recent)
            
            return {
                # Latest values (for cards)
                "fertilizer_price": float(latest.fertilizer_price) if latest.fertilizer_price else None,
                "fuel_price": float(latest.fuel_price) if latest.fuel_price else None,
                "date": latest.date.strftime("%Y-%m-%d") if latest.date else None,
                # Full timeline (for charts)
                "timeline": [
                    {
                        "fertilizer_price": float(row.fertilizer_price) if row.fertilizer_price else None,
                        "fuel_price": float(row.fuel_price) if row.fuel_price else None,
                        "date": row.date.strftime("%Y-%m-%d") if row.date else None
                    }
                    for row in results
                ],
                "total_data_points": len(results)
            }
        else:
            return {
                "fertilizer_price": None,
                "fuel_price": None,
                "date": None,
                "timeline": [],
                "total_data_points": 0
            }
        
    except Exception as e:
        logger.error(f"Error fetching economic data: {e}")
        return {
            "fertilizer_price": None,
            "fuel_price": None,
            "date": None,
            "timeline": [],
            "total_data_points": 0
        }

# -*- coding: utf-8 -*-
"""
Database query endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta
import json
import logging
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, CropPrediction, ChatSession, CropPrice, WeatherData, CropCharacteristics
from sqlalchemy import text, distinct

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["database"])

@router.get("/predictions")
def get_predictions(
    db: Session = Depends(get_db), 
    limit: int = 100,
    crop_id: Optional[int] = None,
    days_back: Optional[int] = None
):
    """Get recent predictions from database with optional filters"""
    try:
        query = db.query(CropPrediction).order_by(CropPrediction.created_at.desc())
        
        # Filter by crop_id if provided
        if crop_id is not None:
            query = query.filter(CropPrediction.crop_id == crop_id)
        
        # Filter by date range if provided
        if days_back is not None:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query = query.filter(CropPrediction.created_at >= cutoff_date)
        
        predictions = query.limit(limit).all()
        return {
            "success": True,
            "count": len(predictions),
            "predictions": [
                {
                    "id": p.id,
                    "crop_id": p.crop_id,
                    "prediction": p.prediction,
                    "created_at": p.created_at.isoformat()
                }
                for p in predictions
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-sessions")
def get_chat_sessions(db: Session = Depends(get_db), limit: int = 50):
    """Get recent chat sessions from database"""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit).all()
        return {
            "success": True,
            "count": len(sessions),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "user_query": s.user_query,
                    "crop_id": s.crop_id,
                    "created_at": s.created_at.isoformat()
                }
                for s in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-sessions/{session_id}")
def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    """Get specific chat session details"""
    try:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "user_query": session.user_query,
                "gemini_response": session.gemini_response,
                "crop_id": session.crop_id,
                "forecast_data": json.loads(session.forecast_data) if session.forecast_data else None,
                "created_at": session.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Get list of all provinces from database"""
    try:
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
            "count": len(provinces),
            "provinces": provinces
        }
    except Exception as e:
        logger.error(f"Error fetching provinces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crops")
def get_crops(db: Session = Depends(get_db)):
    """Get list of all crops from database"""
    try:
        crops = db.query(CropCharacteristics).all()
        
        return {
            "success": True,
            "count": len(crops),
            "crops": [
                {
                    "crop_type": c.crop_type,
                    "crop_category": c.crop_category,
                    "growth_days": c.growth_days,
                    "water_requirement": c.water_requirement,
                    "soil_preference": c.soil_preference,
                    "investment_cost": c.investment_cost,
                    "risk_level": c.risk_level
                }
                for c in crops
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices")
def get_prices(
    db: Session = Depends(get_db),
    province: Optional[str] = None,
    crop_type: Optional[str] = None,
    limit: int = 100
):
    """Get crop prices from database"""
    try:
        query = db.query(CropPrice).order_by(CropPrice.date.desc())
        
        if province:
            query = query.filter(CropPrice.province == province)
        if crop_type:
            query = query.filter(CropPrice.crop_type == crop_type)
        
        prices = query.limit(limit).all()
        
        return {
            "success": True,
            "count": len(prices),
            "prices": [
                {
                    "crop_type": p.crop_type,
                    "province": p.province,
                    "price_per_kg": p.price_per_kg,
                    "date": p.date.isoformat() if p.date else None
                }
                for p in prices
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather")
def get_weather(
    db: Session = Depends(get_db),
    province: Optional[str] = None,
    limit: int = 100
):
    """Get weather data from database"""
    try:
        query = db.query(WeatherData).order_by(WeatherData.date.desc())
        
        if province:
            query = query.filter(WeatherData.province == province)
        
        weather = query.limit(limit).all()
        
        return {
            "success": True,
            "count": len(weather),
            "weather": [
                {
                    "province": w.province,
                    "temperature_celsius": w.temperature_celsius,
                    "rainfall_mm": w.rainfall_mm,
                    "date": w.date.isoformat() if w.date else None
                }
                for w in weather
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

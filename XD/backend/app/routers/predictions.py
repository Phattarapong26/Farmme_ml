# -*- coding: utf-8 -*-
"""
Prediction endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import numpy as np
import json
import logging
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, CropPrediction
from cache import cache
from config import CACHE_TTL_PREDICTIONS
from unified_model_service import unified_model_service
from utils.helpers import get_crop_name_from_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["predictions"])

# Data Schemas
class PredictRequest(BaseModel):
    price_history: List[float]   # ราคาย้อนหลัง
    weather: List[float]         # [ฝน, อุณหภูมิ]
    crop_info: List[int]         # [soil_type_id, water_level, season_id]
    calendar: List[int]          # [is_festival, is_holiday, season_id]
    crop_id: Optional[int] = 0   # เลือกพืช (optional)

class ForecastRequest(PredictRequest):
    crop_id: int                 # เลือกพืช (required)

@router.post("")
def predict(data: PredictRequest, db: Session = Depends(get_db)):
    """
    🔄 UPDATED: Now uses unified model service (new model first, fallback to old)
    """
    try:
        # Create cache key from input data
        prediction_data = {
            "price_history": data.price_history,
            "weather": data.weather,
            "crop_info": data.crop_info,
            "calendar": data.calendar,
            "crop_id": data.crop_id
        }
        
        # Check cache first
        cached_result = cache.get_prediction(prediction_data)
        if cached_result:
            logger.info("✅ Returning cached prediction")
            cached_result["cached"] = True
            return cached_result
        
        # Use unified model service for prediction
        crop_name = get_crop_name_from_id(data.crop_id) if data.crop_id else "คะน้า"
        
        # Convert legacy data format to new format
        temperature = data.weather[1] if len(data.weather) > 1 else 28.0
        rainfall = data.weather[0] if len(data.weather) > 0 else 100.0
        
        prediction_result = unified_model_service.predict_price(
            province="เชียงใหม่",  # Default province
            crop_type=crop_name,
            temperature_celsius=temperature,
            rainfall_mm=rainfall,
            planting_area_rai=10.0,
            expected_yield_kg=5000.0
        )
        
        if prediction_result['success']:
            prediction_value = prediction_result['predicted_price']
            model_used = prediction_result.get('model_used', 'unified')
        else:
            # Fallback to simple calculation (no random variation)
            avg_price = np.mean(data.price_history) if data.price_history else 100.0
            prediction_value = avg_price
            model_used = "fallback"
            logger.warning(f"Unified model failed, using fallback: {prediction_result.get('error', 'Unknown error')}")
        
        # Prepare result
        result = {
            "success": True, 
            "prediction": [prediction_value],
            "cached": False,
            "model_used": model_used,
            "confidence": prediction_result.get('confidence', 0.8)
        }
        
        # Cache the result
        cache.set_prediction(prediction_data, result, CACHE_TTL_PREDICTIONS)
        
        # Save prediction to database
        prediction_record = CropPrediction(
            crop_id=data.crop_id if data.crop_id else 0,
            price_history=json.dumps(data.price_history),
            weather_data=json.dumps(data.weather),
            crop_info=json.dumps(data.crop_info),
            calendar_data=json.dumps(data.calendar),
            prediction=prediction_value,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(prediction_record)
        db.commit()
        
        logger.info(f"Unified prediction saved to database: {prediction_value} (model: {model_used})")
        return result
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/probabilities")
def predict_probabilities(data: PredictRequest):
    try:
        # Mock implementation - replace with actual model
        return {
            "success": True, 
            "probabilities": [[0.2, 0.3, 0.5]],
            "message": "Mock probabilities - implement with actual model"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/6months")
def forecast_6months(data: ForecastRequest):
    """
    ทำนายล่วงหน้า 6 เดือน (180 วัน) → Temp, Rainfall, Price
    """
    try:
        # Mock base price calculation
        base_price = np.mean(data.price_history) if data.price_history else 100.0

        forecast = []
        for i in range(180):
            date = (datetime.today() + timedelta(days=i+1)).strftime("%Y-%m-%d")

            # Use average weather values (TODO: integrate with weather forecast API)
            temp = 28.0  # Average temperature
            rain = 100.0  # Average rainfall

            # Seasonal trend (no random noise)
            price = round(base_price * (1 + np.sin(i/30) * 0.05), 2)

            forecast.append({"date": date, "temperature": temp, "rainfall": rain, "price": price})

        return {"crop_id": data.crop_id, "period_days": 180, "forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
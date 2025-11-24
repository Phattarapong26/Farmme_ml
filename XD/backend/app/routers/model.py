# -*- coding: utf-8 -*-
"""
ML Model endpoints - API v2
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
import joblib
import os
import sys

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import model utilities for compatibility
try:
    from model_utils import EnhancedFeatureEngineer
except ImportError:
    # Create dummy class if not found
    class EnhancedFeatureEngineer:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/model", tags=["ml-model"])

# Pydantic models
class PriceForecastRequest(BaseModel):
    province: str
    crop_type: str
    crop_category: Optional[str] = None
    days_ahead: int = 30

class PriceForecastResponse(BaseModel):
    success: bool
    forecast: List[Dict[str, Any]]
    model_used: str
    confidence_score: Optional[float] = None
    note: Optional[str] = None

# Model C is now handled by price_forecast_service
# No need for global model cache

def create_features_for_prediction(province: str, crop_type: str, days_ahead: int):
    """Create features for ML model prediction matching training data (20 features)"""
    
    base_date = datetime.now()
    features_list = []
    
    # Regional encoding
    region_mapping = {
        'กรุงเทพมหานคร': 'กลาง', 'นนทบุรี': 'กลาง', 'ปทุมธานี': 'กลาง',
        'เชียงใหม่': 'เหนือ', 'เชียงราย': 'เหนือ', 'ลำปาง': 'เหนือ',
        'นครราชสีมา': 'อีสาน', 'ขอนแก่น': 'อีสาน', 'อุดรธานี': 'อีสาน',
        'ชลบุรี': 'ตะวันออก', 'ระยอง': 'ตะวันออก', 'จันทบุรี': 'ตะวันออก',
        'สงขลา': 'ใต้', 'ภูเก็ต': 'ใต้', 'กระบี่': 'ใต้'
    }
    
    region = region_mapping.get(province, 'กลาง')
    
    # Economic data (simplified averages)
    fuel_price_base = 35.0
    fertilizer_price_base = 15.0
    investment_cost_base = 8000.0
    
    # Create features for each day
    for i in range(days_ahead):
        future_date = base_date + timedelta(days=i)
        month = future_date.month
        day = future_date.day
        
        # Cyclical time features
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        day_sin = np.sin(2 * np.pi * day / 31)
        day_cos = np.cos(2 * np.pi * day / 31)
        
        # Season mapping
        season_map = {12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3}
        season = season_map.get(month, 1)
        
        # Weather simulation (deterministic based on date)
        temp_base = 28 + 5 * np.sin(2 * np.pi * (month - 4) / 12)
        rainfall_base = 50 if month in [5,6,7,8,9,10] else 10
        
        # Regional adjustments
        if region == 'เหนือ':
            temp_base -= 3
        elif region == 'ใต้':
            temp_base += 2
            rainfall_base *= 1.5
        elif region == 'อีสาน':
            temp_base += 2
            rainfall_base *= 0.7
        
        # Deterministic variations based on day of year (no random)
        day_variation = np.sin(2 * np.pi * day / 31) * 1.5  # ±1.5°C based on day
        rainfall_variation = np.cos(2 * np.pi * day / 31) * 15  # ±15mm based on day
        
        temperature = temp_base + day_variation
        rainfall = max(0, rainfall_base + rainfall_variation)
        humidity = 70 + np.sin(2 * np.pi * month / 12) * 8  # 62-78% based on month
        
        # Economic features with seasonal variation (deterministic)
        fuel_price = fuel_price_base + np.sin(2 * np.pi * month / 12) * 1.5
        fertilizer_price = fertilizer_price_base + np.cos(2 * np.pi * month / 12) * 0.8
        investment_cost = investment_cost_base + np.sin(2 * np.pi * (month + 3) / 12) * 400
        
        # Derived features
        temp_rain_ratio = temperature / (rainfall + 1)
        weather_severity = (temperature / 35) + (rainfall / 100)
        economic_pressure = (fuel_price / 35) + (fertilizer_price / 15)
        input_cost_index = (fuel_price + fertilizer_price) / 50
        temp_humidity_interaction = temperature * humidity / 100
        
        # Categorical encodings (using hash for consistency)
        province_encoded = hash(province) % 100
        crop_type_encoded = hash(crop_type) % 50
        region_encoded = hash(region) % 10
        
        features = {
            # Numerical features (17)
            'temperature_celsius': temperature,
            'rainfall_mm': rainfall,
            'humidity_percent': humidity,
            'investment_cost': investment_cost,
            'fuel_price': fuel_price,
            'fertilizer_price': fertilizer_price,
            'month_sin': month_sin,
            'month_cos': month_cos,
            'day_sin': day_sin,
            'day_cos': day_cos,
            'season': season,
            'year': future_date.year,
            'temp_rain_ratio': temp_rain_ratio,
            'weather_severity': weather_severity,
            'economic_pressure': economic_pressure,
            'input_cost_index': input_cost_index,
            'temp_humidity_interaction': temp_humidity_interaction,
            # Encoded features (3) - soil_type_encoded ไม่ได้ใช้ใน model
            'province_encoded': province_encoded,
            'crop_type_encoded': crop_type_encoded,
            'region_encoded': region_encoded
        }
        
        features_list.append(features)
    
    return pd.DataFrame(features_list)

def fallback_price_prediction(province: str, crop_type: str, days_ahead: int):
    """Fallback prediction method using trend-based approach"""
    
    # Base prices for different crops (THB per kg)
    base_prices = {
    
    }
    
    base_price = base_prices.get(crop_type, 30.0)
    
    # Regional price adjustments
    regional_multipliers = {
      
    }
    
    regional_multiplier = regional_multipliers.get(province, 1.0)
    adjusted_base_price = base_price * regional_multiplier
    
    # Generate forecast
    forecast = []
    current_date = datetime.now()
    
    for i in range(days_ahead):
        future_date = current_date + timedelta(days=i)
        
        # Seasonal trend
        month = future_date.month
        seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * (month - 3) / 12)
        
        # Add trend (no random noise)
        trend_factor = 1 + (i * 0.001)  # Slight upward trend
        
        predicted_price = adjusted_base_price * seasonal_factor * trend_factor
        
        forecast.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_price": round(predicted_price, 2)
        })
    
    return forecast

@router.post("/predict-price-forecast")
async def predict_price_forecast(request: PriceForecastRequest):
    """
    🚀 PRODUCTION: ML Model Price Prediction using Model C Stratified
    Used by RealForecastChart component
    """
    logger.info(f"🔮 Price prediction request: {request.province}, {request.crop_type}, {request.days_ahead} days")
    
    # Use Model C Wrapper (Stratified Models)
    from model_c_wrapper import model_c_wrapper
    from database import SessionLocal
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Use model_c_wrapper for predictions
        result = model_c_wrapper.predict_price(
            crop_type=request.crop_type,
            province=request.province,
            days_ahead=request.days_ahead
        )
        
        # Check if prediction was successful
        if not result.get('success'):
            error_code = result.get('error', 'UNKNOWN')
            error_message = result.get('message', 'Prediction failed')
            
            logger.error(f"❌ Model C prediction failed: {error_code} - {error_message}")
            
            # Return error response with details
            return {
                "success": False,
                "error": error_code,
                "message": error_message,
                "crop_type": request.crop_type,
                "province": request.province,
                "suggestions": result.get('suggestions', []),
                "available_provinces": result.get('available_provinces', [])
            }
        
        # Get predictions from result
        predictions = result.get('predictions', [])
        
        # Convert predictions to forecast format for frontend
        current_price = result.get('current_price', 30.0)
        forecast = []
        
        # Create daily forecasts by interpolating between prediction points
        for i in range(1, request.days_ahead + 1):
            # Find matching prediction or interpolate
            predicted_price = current_price
            confidence = 0.5
            
            for pred in predictions:
                if pred['days_ahead'] == i:
                    predicted_price = pred['predicted_price']
                    confidence = pred.get('confidence', 0.8)
                    break
                elif pred['days_ahead'] == 7 and i <= 7:
                    # Interpolate for days 1-7
                    ratio = i / 7
                    predicted_price = current_price + (pred['predicted_price'] - current_price) * ratio
                    confidence = pred.get('confidence', 0.8) * (1 - (i-1) * 0.05)
                elif pred['days_ahead'] == 30 and i > 7:
                    # Interpolate for days 8-30
                    ratio = (i - 7) / (30 - 7)
                    pred_7d = next((p['predicted_price'] for p in predictions if p['days_ahead'] == 7), current_price)
                    predicted_price = pred_7d + (pred['predicted_price'] - pred_7d) * ratio
                    confidence = pred.get('confidence', 0.6) * (1 - (i-7) * 0.02)
                elif pred['days_ahead'] == 90 and i > 30:
                    # Interpolate for days 31-90
                    ratio = (i - 30) / (90 - 30)
                    pred_30d = next((p['predicted_price'] for p in predictions if p['days_ahead'] == 30), current_price)
                    predicted_price = pred_30d + (pred['predicted_price'] - pred_30d) * ratio
                    confidence = pred.get('confidence', 0.4) * (1 - (i-30) * 0.01)
            
            future_date = datetime.now() + timedelta(days=i)
            forecast.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_price": round(predicted_price, 2),
                "confidence_score": round(max(0.1, min(1.0, confidence)), 2)
            })
        
        logger.info(f"✅ Model C Stratified forecast generated: {len(forecast)} days")
        logger.info(f"📈 Price range: {forecast[0]['predicted_price']:.2f} → {forecast[-1]['predicted_price']:.2f} บาท/กก.")
        
        # Get model info
        model_info = model_c_wrapper.get_model_info()
        
        # Build response with metadata
        response = {
            "success": True,
            "forecast": forecast,
            "model_used": "model_c_stratified",
            "confidence_score": result.get('confidence', 0.8),
            "note": f"Model C Stratified prediction for {request.crop_type} in {request.province}",
            "metadata": {
                "model_name": model_info.get('model_name', 'Model C Stratified'),
                "model_version": model_info.get('version', '7.0.0'),
                "algorithm": model_info.get('algorithm', 'gradient_boosting_stratified'),
                "r2_score": model_info.get('r2', 0.7589),
                "mae": model_info.get('mae', 6.97),
                "model_used": "model_c_stratified",
                "accuracy_note": {
                    "7_days": "R² = 0.77, MAE = 2.17 baht (แม่นมาก!)",
                    "30_days": "R² = 0.34, MAE = 4.10 baht (แม่น)",
                    "90_days": "R² = 0.08, MAE = 24.01 baht (พอใช้)"
                }
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Model C Stratified forecast failed: {e}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # Return fallback forecast using trend-based method
        logger.warning("⚠️  Using FALLBACK trend-based forecast (Model C Stratified not available)")
        
        try:
            from database import SessionLocal, CropPrice
            from sqlalchemy import func
            
            db = SessionLocal()
            
            try:
                # Get historical average and trend from database
                recent_prices = db.query(CropPrice).filter(
                    CropPrice.province == request.province,
                    CropPrice.crop_type == request.crop_type
                ).order_by(CropPrice.date.desc()).limit(30).all()
                
                if recent_prices:
                    prices = [float(p.price_per_kg) for p in recent_prices]
                    base_price = np.mean(prices)
                    
                    # Calculate simple trend
                    if len(prices) >= 10:
                        recent_avg = np.mean(prices[:10])
                        older_avg = np.mean(prices[-10:])
                        trend_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                    else:
                        trend_rate = 0.001  # Default slight upward trend
                    
                    logger.info(f"📊 Using historical data: base_price={base_price:.2f}, trend={trend_rate:.4f}")
                else:
                    base_price = 50.0
                    trend_rate = 0.001
                    logger.warning(f"⚠️  No historical data, using defaults")
                
            finally:
                db.close()
                
        except Exception as db_error:
            logger.error(f"❌ Database fallback failed: {db_error}")
            base_price = 50.0
            trend_rate = 0.001
        
        # Generate forecast with trend
        forecast = []
        current_date = datetime.now()
        
        for i in range(request.days_ahead):
            future_date = current_date + timedelta(days=i+1)
            # Apply trend with deterministic seasonal variation
            seasonal_variation = np.sin(2 * np.pi * future_date.timetuple().tm_yday / 365) * 0.02  # ±2% seasonal
            predicted_price = base_price * (1 + (i * trend_rate) + seasonal_variation)
            
            forecast.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_price": round(float(predicted_price), 2)
            })
        
        return {
            "success": True,
            "forecast": forecast,
            "model_used": "fallback_trend",
            "confidence_score": 0.50,
            "note": f"⚠️ Using FALLBACK trend-based forecast (Model C Stratified not available)",
            "metadata": {
                "model_used": "fallback_trend",
                "warning": "Model C Stratified not loaded - using simple trend analysis",
                "accuracy": "Lower accuracy than ML model"
            }
        }

@router.get("/monitoring")
async def get_monitoring_metrics():
    """Get model monitoring metrics and health status"""
    try:
        from app.services.model_monitoring import model_monitoring
        
        return {
            "summary": model_monitoring.get_summary(),
            "health": model_monitoring.check_health(),
            "recent_predictions": model_monitoring.get_recent_predictions(5),
            "recent_errors": model_monitoring.get_recent_errors(5)
        }
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        return {
            "error": str(e),
            "summary": None,
            "health": {"healthy": False}
        }

@router.post("/predict-planting-window")
async def predict_planting_window(
    crop_type: str,
    province: str,
    planting_date: str
):
    """
    🌱 Model B: Predict if this is a good planting window
    
    Args:
        crop_type: Crop type (e.g., 'พริก')
        province: Province name (e.g., 'เชียงใหม่')
        planting_date: Planting date (YYYY-MM-DD)
    
    Returns:
        {
            "success": bool,
            "is_good_window": bool,
            "confidence": float,
            "recommendation": str,
            "reason": str
        }
    """
    logger.info(f"🌱 Planting window prediction: {crop_type}, {province}, {planting_date}")
    
    try:
        from model_b_wrapper import get_model_b
        
        # Get Model B instance
        model_b = get_model_b()
        
        # Predict
        result = model_b.predict_planting_window(
            crop_type=crop_type,
            province=province,
            planting_date=planting_date
        )
        
        logger.info(f"✅ Prediction: {result['is_good_window']} (confidence: {result['confidence']:.2%})")
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ Model B prediction failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@router.get("/model-status")
async def get_model_status():
    """Get Model C v3.1 status with detailed metrics"""
    try:
        from app.services.price_forecast_service import price_forecast_service
        import pickle
        from pathlib import Path
        
        info = price_forecast_service.get_model_info()
        
        # Get additional model details if loaded
        model_version = "unknown"
        feature_count = 0
        seasonal_patterns = 0
        metrics = {}
        
        if price_forecast_service.model_loaded and price_forecast_service.model_path:
            try:
                # Load model metadata
                with open(price_forecast_service.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    model_version = model_data.get('version', 'unknown')
                    feature_count = len(model_data.get('feature_names', []))
                    seasonal_patterns = len(model_data.get('seasonal_patterns', {}))
                    metrics = model_data.get('metrics', {})
            except Exception as e:
                logger.warning(f"Could not load model metadata: {e}")
        
        # Build response
        model_note = "Model C v5 - XGBoost Price Forecast" if info['model_loaded'] else "Model not loaded"
        algorithm = info.get('algorithm', 'xgboost')
        
        response = {
            "model_available": info['model_loaded'],
            "model_path": info['model_path'],
            "model_type": f"{algorithm.upper()}Regressor" if info['model_loaded'] else "error",
            "model_file": Path(info['model_path']).name if info['model_path'] else "unknown",
            "version": model_version,
            "algorithm": algorithm,
            "status": info['status'],
            "feature_count": feature_count,
            "seasonal_patterns": seasonal_patterns,
            "note": model_note
        }
        
        # Add metrics if available
        if metrics:
            response["metrics"] = {
                "rmse": round(metrics.get('rmse', 0), 4),
                "mae": round(metrics.get('mae', 0), 4),
                "mape": round(metrics.get('mape', 0), 4),
                "r2": round(metrics.get('r2', 0), 4) if metrics.get('r2') else None
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking model status: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "model_available": False,
            "model_path": None,
            "model_type": "error",
            "status": "failed",
            "error": str(e)
        }
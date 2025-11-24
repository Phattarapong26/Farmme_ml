# -*- coding: utf-8 -*-
"""
Model management endpoints
"""

from fastapi import APIRouter, HTTPException
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cache import cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/models", tags=["models"])

@router.get("")
def list_models():
    """List all available ML models"""
    try:
        # Import ML services
        from recommendation_model_service import recommendation_model_service
        from water_management_service import water_management_service
        from price_prediction_service import price_prediction_service
        from planting_model_service import planting_model_service
        
        models = [
            {
                "name": "recommendation",
                "description": "Crop Recommendation Model",
                "status": "active" if recommendation_model_service.model_loaded else "fallback",
                "info": recommendation_model_service.get_model_info()
            },
            {
                "name": "water_management",
                "description": "Water Management Model",
                "status": "active" if water_management_service.model_loaded else "fallback",
                "info": water_management_service.get_model_info()
            },
            {
                "name": "price_prediction",
                "description": "Price Prediction Model",
                "status": "active" if price_prediction_service.model_loaded else "fallback",
                "info": price_prediction_service.get_model_info()
            },
            {
                "name": "planting_calendar",
                "description": "Planting Calendar Model",
                "status": "active" if planting_model_service.model_loaded else "fallback",
                "info": planting_model_service.get_model_info()
            }
        ]
        
        return {"success": True, "models": models, "total": len(models)}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{model_type}")
def get_model_info(model_type: str):
    """Get information about a specific model type"""
    try:
        # Import ML services
        from recommendation_model_service import recommendation_model_service
        from water_management_service import water_management_service
        from price_prediction_service import price_prediction_service
        from planting_model_service import planting_model_service
        
        model_map = {
            "recommendation": recommendation_model_service,
            "water_management": water_management_service,
            "price_prediction": price_prediction_service,
            "planting_calendar": planting_model_service
        }
        
        if model_type not in model_map:
            raise HTTPException(
                status_code=404, 
                detail=f"Model type '{model_type}' not found. Available: {list(model_map.keys())}"
            )
        
        service = model_map[model_type]
        info = service.get_model_info()
        
        return {
            "success": True,
            "model_type": model_type,
            "info": info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{model_type}/reload")
def reload_model(model_type: str):
    """Reload a specific model (clears cache)"""
    try:
        # Clear cache for this model type
        cache.clear()
        
        return {
            "success": True,
            "message": f"Cache cleared for model {model_type}",
            "model_type": model_type
        }
    except Exception as e:
        logger.error(f"Error reloading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))
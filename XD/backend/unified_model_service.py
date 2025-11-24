# -*- coding: utf-8 -*-
"""
Unified Model Service for Farmme API
Combines new and legacy model services with intelligent fallback
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedModelService:
    """
    Unified model service that tries new model first, falls back to legacy
    """
    
    def __init__(self):
        self.new_model = None
        self.legacy_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize model services - now using PricePredictionModelService"""
        # Use the new PricePredictionModelService as primary
        try:
            from price_prediction_service import price_prediction_service
            self.price_prediction_service = price_prediction_service
            logger.info("✅ Price prediction model service loaded")
        except Exception as e:
            logger.warning(f"⚠️ Price prediction service not available: {e}")
            self.price_prediction_service = None
        
        # Keep legacy models as fallback
        try:
            from new_model_service import NewModelService
            self.new_model = NewModelService()
            logger.info("✅ New model service loaded")
        except Exception as e:
            logger.warning(f"⚠️ New model service not available: {e}")
        
        try:
            from model_service import ModelService
            self.legacy_model = ModelService()
            logger.info("✅ Legacy model service loaded")
        except Exception as e:
            logger.warning(f"⚠️ Legacy model service not available: {e}")
        
        if not self.price_prediction_service and not self.new_model and not self.legacy_model:
            logger.error("❌ No model services available!")
    
    def predict_price(
        self,
        province: str,
        crop_type: str,
        crop_category: str = None,
        month: int = None,
        year: int = None,
        temperature_celsius: float = 28.0,
        rainfall_mm: float = 100.0,
        planting_area_rai: float = 10.0,
        expected_yield_kg: float = 5000.0,
        days_ahead: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified price prediction - now using PricePredictionModelService
        """
        # Try PricePredictionModelService first (primary)
        if self.price_prediction_service:
            try:
                result = self.price_prediction_service.predict_price(
                    crop_type=crop_type,
                    province=province,
                    days_ahead=days_ahead,
                    planting_area_rai=planting_area_rai,
                    expected_yield_kg=expected_yield_kg
                )
                if result.get('success'):
                    logger.info(f"✅ Price prediction model: {result.get('current_price')}")
                    return result
                else:
                    logger.warning(f"⚠️ Price prediction model failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ Price prediction model error: {e}")
        
        # Fallback to new model
        if self.new_model:
            try:
                result = self.new_model.predict_price_new(
                    province=province,
                    crop_type=crop_type,
                    crop_category=crop_category,
                    month=month,
                    year=year,
                    temperature_celsius=temperature_celsius,
                    rainfall_mm=rainfall_mm,
                    planting_area_rai=planting_area_rai,
                    expected_yield_kg=expected_yield_kg,
                    **kwargs
                )
                if result.get('success'):
                    result['model_used'] = 'new_model'
                    logger.info(f"✅ New model prediction: {result.get('predicted_price')}")
                    return result
            except Exception as e:
                logger.error(f"❌ New model error: {e}")
        
        # Fallback to legacy model
        if self.legacy_model:
            try:
                result = self.legacy_model.predict_price(
                    province=province,
                    crop_type=crop_type,
                    crop_category=crop_category,
                    month=month,
                    year=year,
                    temperature_celsius=temperature_celsius,
                    rainfall_mm=rainfall_mm,
                    planting_area_rai=planting_area_rai,
                    expected_yield_kg=expected_yield_kg,
                    **kwargs
                )
                if result.get('success'):
                    result['model_used'] = 'legacy_model'
                    logger.info(f"✅ Legacy model prediction: {result.get('predicted_price')}")
                    return result
            except Exception as e:
                logger.error(f"❌ Legacy model error: {e}")
        
        # If all models fail, return error
        return {
            "success": False,
            "error": "All model services failed",
            "predicted_price": None,
            "model_used": "none"
        }
    
    def predict_price_forecast(
        self,
        province: str,
        crop_type: str,
        days_ahead: int = 180,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified price forecast - now using PricePredictionModelService
        """
        # Try PricePredictionModelService first (primary)
        if self.price_prediction_service:
            try:
                result = self.price_prediction_service.predict_price(
                    crop_type=crop_type,
                    province=province,
                    days_ahead=days_ahead,
                    **kwargs
                )
                if result.get('success'):
                    logger.info(f"✅ Price prediction forecast: {len(result.get('predictions', []))} predictions")
                    return result
            except Exception as e:
                logger.error(f"❌ Price prediction forecast error: {e}")
        
        # Fallback to new model
        if self.new_model:
            try:
                result = self.new_model.predict_price_forecast_new(
                    province=province,
                    crop_type=crop_type,
                    days_ahead=days_ahead,
                    **kwargs
                )
                if result.get('success'):
                    result['model_used'] = 'new_model'
                    return result
            except Exception as e:
                logger.error(f"❌ New model forecast error: {e}")
        
        # Fallback to legacy model
        if self.legacy_model:
            try:
                result = self.legacy_model.predict_price_forecast(
                    province=province,
                    crop_type=crop_type,
                    days_ahead=days_ahead,
                    **kwargs
                )
                if result.get('success'):
                    result['model_used'] = 'legacy_model'
                    return result
            except Exception as e:
                logger.error(f"❌ Legacy model forecast error: {e}")
        
        return {
            "success": False,
            "error": "All model services failed",
            "forecast": [],
            "model_used": "none"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "price_prediction_available": self.price_prediction_service is not None,
            "new_model_available": self.new_model is not None,
            "legacy_model_available": self.legacy_model is not None,
            "primary_model": "price_prediction" if self.price_prediction_service else "new_model" if self.new_model else "legacy_model" if self.legacy_model else "none",
            "status": "healthy" if (self.price_prediction_service or self.new_model or self.legacy_model) else "unhealthy"
        }
    
    def get_model_status(self) -> str:
        """Get current model status"""
        if self.price_prediction_service:
            return "price_prediction_primary"
        elif self.new_model and self.legacy_model:
            return "both_available"
        elif self.new_model:
            return "new_only"
        elif self.legacy_model:
            return "legacy_only"
        else:
            return "none_available"


# Global unified model service instance
unified_model_service = UnifiedModelService()

logger.info(f"🔧 Unified model service initialized - Status: {unified_model_service.get_model_status()}")

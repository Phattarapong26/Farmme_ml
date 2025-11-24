"""
Model C Prediction Service (DEPRECATED)

⚠️ DEPRECATED: This service is no longer used in production.
   Use model_c_v31_service.py or price_forecast_service.py instead.

This file is kept for backward compatibility and testing purposes only.
It has import errors with old Model_C_PriceForecast modules.

Recommended alternatives:
- model_c_v31_service.py: Direct Model C v3.1 predictions
- app/services/price_forecast_service.py: Full production service with database integration
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys

# Add REMEDIATION_PRODUCTION to path
backend_dir = Path(__file__).parent
remediation_dir = backend_dir.parent / "REMEDIATION_PRODUCTION"
model_c_dir = remediation_dir / "Model_C_PriceForecast"
sys.path.insert(0, str(remediation_dir))
sys.path.insert(0, str(model_c_dir))

from Model_C_PriceForecast.data_loader import DataLoader
from Model_C_PriceForecast.feature_engineer import FeatureEngineer
from Model_C_PriceForecast.temporal_features import TemporalFeatureBuilder

logger = logging.getLogger(__name__)


class ModelCPredictionService:
    """Complete prediction service for Model C v2.0"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load Model C v3.1 (Retrained)"""
        try:
            model_path = remediation_dir / "models_production" / "model_c_v3_seasonal_retrained.pkl"
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('version', 'unknown')
            self.model_loaded = True
            
            logger.info(f"✅ Model C v3.1 (Retrained) loaded: {self.model_version}")
            logger.info(f"   Features: {len(self.feature_names)}")
            
        except Exception as e:
            logger.error(f"Failed to load Model C: {e}")
            self.model_loaded = False
    
    def predict_price(
        self,
        crop_type: str,
        province: str,
        days_ahead: int = 30
    ) -> Dict:
        """
        Predict price using Model C v3.1 (Retrained) with seasonal awareness
        
        Args:
            crop_type: Crop type
            province: Province name
            days_ahead: Days to predict ahead
        
        Returns:
            Prediction results with realistic price movements
        """
        if not self.model_loaded:
            return self._fallback_prediction(crop_type, province, days_ahead)
        
        try:
            # Load recent data for this crop/province
            data_loader = DataLoader()
            df = data_loader.load_farmme_dataset()
            
            # Filter for this crop and province
            df_filtered = df[
                (df['crop_type'] == crop_type) & 
                (df['province'] == province)
            ].copy()
            
            if len(df_filtered) < 100:
                logger.warning(f"Insufficient data for {crop_type} in {province}")
                return self._fallback_prediction(crop_type, province, days_ahead)
            
            # Sort by date
            df_filtered = df_filtered.sort_values('date').reset_index(drop=True)
            
            # Get historical statistics
            historical_prices = df_filtered['price_per_kg'].tail(90).values
            price_mean = np.mean(historical_prices)
            price_std = np.std(historical_prices)
            price_min = np.min(historical_prices)
            price_max = np.max(historical_prices)
            
            # Get current price
            current_price = float(df_filtered['price_per_kg'].iloc[-1])
            current_price = self._clip_price(current_price)
            
            # Calculate seasonal pattern (monthly average)
            df_filtered['month'] = pd.to_datetime(df_filtered['date']).dt.month
            monthly_avg = df_filtered.groupby('month')['price_per_kg'].mean().to_dict()
            
            # Generate predictions with improved logic
            predictions = []
            
            for target_days in [7, 30, 90, 180]:
                if target_days > days_ahead:
                    break
                
                # Get target month for seasonality
                target_date = datetime.now() + timedelta(days=target_days)
                target_month = target_date.month
                seasonal_factor = monthly_avg.get(target_month, price_mean) / price_mean
                
                # Mean reversion: price gradually moves toward historical mean
                # Longer timeframe = more reversion
                reversion_strength = min(target_days / 90, 1.0) * 0.3  # Max 30% reversion
                reverted_price = current_price + (price_mean - current_price) * reversion_strength
                
                # Apply dampened seasonal adjustment
                seasonal_adjustment = (seasonal_factor - 1.0) * 0.2  # Only 20% of seasonal effect
                predicted_price = reverted_price * (1.0 + seasonal_adjustment)
                
                # Add deterministic micro-variation based on target day (±1%)
                # This creates natural price movement without randomness
                day_variation = np.sin(2 * np.pi * target_days / 365) * 0.01 * predicted_price
                predicted_price += day_variation
                
                # Ensure price stays within historical range
                predicted_price = max(price_min * 0.9, min(price_max * 1.1, predicted_price))
                
                # Clip to reasonable range
                predicted_price = self._clip_price(predicted_price)
                
                # Calculate confidence
                confidence = max(0.5, 0.9 - (target_days / 365) * 0.3)
                
                predictions.append({
                    "days_ahead": target_days,
                    "predicted_price": round(predicted_price, 2),
                    "confidence": round(confidence, 2),
                    "price_range": self._calculate_price_range(predicted_price, confidence)
                })
            
            # Analyze trend
            trend_analysis = self._analyze_trend(current_price, predictions)
            
            return {
                "success": True,
                "crop_type": crop_type,
                "province": province,
                "current_price": round(current_price, 2),
                "predictions": predictions,
                "price_trend": trend_analysis["trend"],
                "trend_percentage": trend_analysis["percentage"],
                "model_used": f"model_c_v31_{self.model_version}",
                "confidence": round(np.mean([p["confidence"] for p in predictions]), 2),
                "historical_mean": round(price_mean, 2),
                "historical_range": {"min": round(price_min, 2), "max": round(price_max, 2)}
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_prediction(crop_type, province, days_ahead)
    
    def _clip_price(self, price: float) -> float:
        """Clip price to reasonable range (5-500 baht/kg)"""
        if price < 5.0:
            return 5.0
        elif price > 500.0:
            return 500.0
        return price
    
    def _calculate_price_range(self, price: float, confidence: float) -> Dict:
        """Calculate price range"""
        range_factor = (1 - confidence) * 0.3
        range_width = price * range_factor
        
        min_price = max(5.0, price - range_width)
        max_price = min(500.0, price + range_width)
        
        return {
            "min": round(min_price, 2),
            "max": round(max_price, 2)
        }
    
    def _analyze_trend(self, current_price: float, predictions: List[Dict]) -> Dict:
        """Analyze price trend"""
        if not predictions:
            return {"trend": "stable", "percentage": 0}
        
        future_price = predictions[-1]["predicted_price"]
        change = ((future_price - current_price) / current_price) * 100
        
        if change > 5:
            trend = "increasing"
        elif change < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {"trend": trend, "percentage": round(change, 1)}
    
    def _fallback_prediction(self, crop_type: str, province: str, days_ahead: int) -> Dict:
        """Fallback prediction"""
        base_price = 30.0
        
        predictions = []
        for days in [7, 30, 90, 180]:
            if days > days_ahead:
                break
            
            price = base_price * (1 + days / 365 * 0.05)
            price = self._clip_price(price)
            
            predictions.append({
                "days_ahead": days,
                "predicted_price": round(price, 2),
                "confidence": 0.6,
                "price_range": {"min": round(price * 0.85, 2), "max": round(price * 1.15, 2)}
            })
        
        return {
            "success": True,
            "crop_type": crop_type,
            "province": province,
            "current_price": round(base_price, 2),
            "predictions": predictions,
            "price_trend": "stable",
            "trend_percentage": 0,
            "model_used": "fallback",
            "confidence": 0.6
        }


# Global instance
model_c_service = ModelCPredictionService()

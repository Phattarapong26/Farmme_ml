# -*- coding: utf-8 -*-
"""
Price Prediction Model Service for Farmme API
Uses PredictPrice_model.pkl to provide price predictions
"""

import logging
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import warnings

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)

class PricePredictionModelService:
    """Service for price prediction ML model - Using Model C Stratified v7"""
    
    def __init__(self):
        # Import Model C Wrapper (Stratified Models)
        try:
            import sys
            backend_dir = os.path.dirname(__file__)
            sys.path.insert(0, backend_dir)
            from model_c_wrapper import model_c_wrapper
            self.model_wrapper = model_c_wrapper
            self.model_loaded = model_c_wrapper.model_loaded
            logger.info("✅ Price Prediction Service initialized with Model C Stratified v7")
            
            if self.model_loaded:
                model_info = model_c_wrapper.get_model_info()
                logger.info(f"   Model: {model_info.get('model_name', 'unknown')}")
                logger.info(f"   Version: {model_info.get('version', 'unknown')}")
                logger.info(f"   R²: {model_info.get('r2', 'unknown')}")
                logger.info(f"   MAE: {model_info.get('mae', 'unknown')} baht/kg")
        except Exception as e:
            logger.error(f"Failed to load Model C Stratified: {e}")
            self.model_wrapper = None
            self.model_loaded = False
            logger.warning("⚠️ Falling back to rule-based predictions")
    
    def _load_model(self):
        """Load the price prediction ML model"""
        try:
            if os.path.exists(self.model_path):
                # Try different pickle protocols
                try:
                    with open(self.model_path, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    # Handle different model formats
                    if isinstance(model_data, dict):
                        self.model = model_data.get('model')
                        self.scaler = model_data.get('scaler')
                    else:
                        self.model = model_data
                    
                    self.model_loaded = True
                    logger.info(f"✅ Price prediction model loaded from {self.model_path}")
                except (pickle.UnpicklingError, ValueError) as e:
                    logger.warning(f"⚠️ Pickle loading failed with standard method: {e}")
                    # Try with joblib
                    try:
                        import joblib
                        model_data = joblib.load(self.model_path)
                        
                        if isinstance(model_data, dict):
                            self.model = model_data.get('model')
                            self.scaler = model_data.get('scaler')
                        else:
                            self.model = model_data
                        
                        self.model_loaded = True
                        logger.info(f"✅ Price prediction model loaded using joblib from {self.model_path}")
                    except Exception as e2:
                        logger.warning(f"⚠️ Joblib loading also failed: {e2}")
                        self.model_loaded = False
            else:
                logger.warning(f"⚠️ Model file not found: {self.model_path}")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Failed to load price prediction model: {e}")
            self.model_loaded = False
    
    def predict_price(
        self,
        crop_type: str,
        province: str,
        days_ahead: int = 30,
        planting_area_rai: float = None,
        expected_yield_kg: float = None
    ) -> Dict[str, Any]:
        """
        Predict crop price for future dates using Model C v4
        
        Args:
            crop_type: Type of crop (e.g., 'พริก', 'มะเขือเทศ')
            province: Thai province name
            days_ahead: Number of days ahead to predict (7, 30, 90, or 180)
            planting_area_rai: Planting area in rai (optional)
            expected_yield_kg: Expected yield in kg (optional)
        
        Returns:
            Dictionary with price predictions
        """
        try:
            if not self.model_loaded or not self.model_wrapper:
                logger.warning("⚠️  Model C Stratified not loaded, using fallback")
                return self._fallback_price_prediction(crop_type, province, days_ahead)
            
            logger.info(f"🔮 Using Model C Stratified for {crop_type} in {province} ({days_ahead} days)")
            
            # Use Model C Wrapper (Stratified Models)
            result = self.model_wrapper.predict_price(
                crop_type=crop_type,
                province=province,
                days_ahead=days_ahead
            )
            
            if not result.get('success'):
                logger.error(f"❌ Model C Stratified prediction failed: {result.get('error', 'unknown')}")
                return self._fallback_price_prediction(crop_type, province, days_ahead)
            
            # Get predictions from Model C Stratified
            model_predictions = result.get('predictions', [])
            current_price = result.get('current_price', 30.0)
            
            if not model_predictions:
                logger.warning("⚠️  No predictions from Model C Stratified")
                return self._fallback_price_prediction(crop_type, province, days_ahead)
            
            # Format predictions for chat response
            predictions = []
            for pred in model_predictions:
                pred_days = pred['days_ahead']
                predicted_price = pred['predicted_price']
                confidence = pred.get('confidence', 0.8)
                
                # Calculate price range based on confidence
                price_range = self._calculate_price_range(predicted_price, confidence)
                
                predictions.append({
                    "days_ahead": pred_days,
                    "predicted_price": round(float(predicted_price), 2),
                    "confidence": round(confidence, 2),
                    "price_range": {
                        "min": round(price_range[0], 2),
                        "max": round(price_range[1], 2)
                    }
                })
            
            # Analyze trend
            trend_analysis = self._analyze_price_trend(current_price, predictions)
            
            # Get model info
            model_info = self.model_wrapper.get_model_info()
            
            return {
                "success": True,
                "crop_type": crop_type,
                "province": province,
                "predictions": predictions,
                "historical_data": result.get('historical_data', []),
                "daily_forecasts": result.get('daily_forecasts', []),
                "current_price": round(float(current_price), 2),
                "price_trend": trend_analysis["trend"],
                "trend_percentage": trend_analysis["percentage"],
                "market_insights": result.get('market_insights', []),
                "best_selling_period": self._recommend_selling_period(predictions),
                "model_used": "Model C Stratified v7 (Gradient Boosting)",
                "model_version": model_info.get('version', '7.0.0'),
                "model_r2": model_info.get('r2', 0.7589),
                "model_mae": model_info.get('mae', 6.97),
                "confidence": round(np.mean([p["confidence"] for p in predictions]), 2)
            }
            
        except Exception as e:
            logger.error(f"Error in predict_price: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_price_prediction(crop_type, province, days_ahead)
    
    def _prepare_features(
        self,
        crop_type: str,
        province: str,
        days_ahead: int,
        historical_prices: List[float],
        planting_area_rai: float,
        expected_yield_kg: float
    ) -> Optional[np.ndarray]:
        """Prepare features for the ML model"""
        try:
            # Get current date
            current_date = datetime.now()
            future_date = current_date + timedelta(days=days_ahead)
            
            # Calculate features
            features_dict = {
                'crop_code': hash(crop_type) % 100,
                'province_code': hash(province) % 100,
                'month': future_date.month,
                'day_of_year': future_date.timetuple().tm_yday,
                'season': self._get_season_code(future_date.month),
                'days_ahead': days_ahead,
                'avg_historical_price': np.mean(historical_prices) if historical_prices else 50.0,
                'price_volatility': np.std(historical_prices) if len(historical_prices) > 1 else 5.0,
                'temperature': 28.0,  # Average temperature
                'rainfall': self._get_seasonal_rainfall(future_date.month),
                'planting_area': planting_area_rai if planting_area_rai else 5.0,
                'expected_yield': expected_yield_kg if expected_yield_kg else 1000.0
            }
            
            # Convert to array
            features = np.array(list(features_dict.values())).reshape(1, -1)
            
            # Scale if scaler is available
            if self.scaler:
                features = self.scaler.transform(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def _get_historical_prices(self, crop_type: str, province: str, days: int = 90) -> List[float]:
        """Get historical prices from database"""
        try:
            from database import SessionLocal, CropPrice
            from sqlalchemy import desc
            from datetime import datetime, timedelta
            
            db = SessionLocal()
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                prices = db.query(CropPrice.price_per_kg).filter(
                    CropPrice.crop_type == crop_type,
                    CropPrice.province == province,
                    CropPrice.date >= start_date,
                    CropPrice.date <= end_date
                ).order_by(desc(CropPrice.date)).limit(90).all()
                
                return [float(p[0]) for p in prices if p[0] is not None]
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting historical prices: {e}")
            return []
    
    def _calculate_confidence(self, days_ahead: int, historical_prices: List[float]) -> float:
        """Calculate prediction confidence based on data quality and timeframe"""
        # Base confidence
        base_confidence = 0.95
        
        # Confidence decreases with longer timeframes
        time_decay = days_ahead / 365 * 0.3  # Max 30% decay
        
        # Adjust for data availability
        data_quality = min(len(historical_prices) / 90, 1.0) if historical_prices else 0.5
        
        confidence = (base_confidence - time_decay) * data_quality
        
        return max(0.5, min(0.95, confidence))
    
    def _calculate_price_range(self, predicted_price: float, confidence: float) -> tuple:
        """Calculate price range based on confidence"""
        # Lower confidence = wider range
        range_factor = 1 - confidence
        range_width = predicted_price * range_factor * 0.3  # Max 30% range
        
        min_price = predicted_price - range_width
        max_price = predicted_price + range_width
        
        return (max(0, min_price), max_price)
    
    def _analyze_price_trend(self, current_price: float, predictions: List[Dict]) -> Dict:
        """Analyze price trend from predictions"""
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
        
        return {
            "trend": trend,
            "percentage": round(change, 1)
        }
    
    def _generate_market_insights(
        self,
        crop_type: str,
        predictions: List[Dict],
        trend_analysis: Dict
    ) -> List[str]:
        """Generate market insights based on predictions"""
        insights = []
        
        if trend_analysis["trend"] == "increasing":
            insights.append(f"ราคา{crop_type}มีแนวโน้มเพิ่มขึ้น {trend_analysis['percentage']:.1f}%")
            insights.append("แนะนำให้รอขายในช่วงที่ราคาสูงขึ้น")
        elif trend_analysis["trend"] == "decreasing":
            insights.append(f"ราคา{crop_type}มีแนวโน้มลดลง {abs(trend_analysis['percentage']):.1f}%")
            insights.append("แนะนำให้ขายเร็วหรือเก็บรักษาไว้ขายในฤดูกาลที่ดีกว่า")
        else:
            insights.append(f"ราคา{crop_type}มีเสถียรภาพ")
        
        # Add confidence-based insight
        if predictions:
            avg_confidence = np.mean([p["confidence"] for p in predictions])
            if avg_confidence > 0.8:
                insights.append("ความแม่นยำของการทำนายอยู่ในระดับสูง")
            elif avg_confidence < 0.6:
                insights.append("ควรติดตามราคาตลาดอย่างใกล้ชิด")
        
        return insights
    
    def _recommend_selling_period(self, predictions: List[Dict]) -> str:
        """Recommend best period to sell based on predictions"""
        if not predictions:
            return "ตามฤดูกาล"
        
        # Find period with highest price
        best_prediction = max(predictions, key=lambda x: x["predicted_price"])
        days = best_prediction["days_ahead"]
        
        if days <= 7:
            return "ภายใน 7 วัน"
        elif days <= 30:
            return "ภายใน 1 เดือน"
        elif days <= 90:
            return "ภายใน 3 เดือน"
        else:
            return "ภายใน 6 เดือน"
    
    def _fallback_price_prediction(
        self,
        crop_type: str,
        province: str,
        days_ahead: int
    ) -> Dict[str, Any]:
        """Rule-based fallback price prediction when model is not available"""
        logger.warning("Using fallback price prediction method")
        
        # Get historical average
        historical_prices = self._get_historical_prices(crop_type, province)
        
        if not historical_prices:
            base_price = 30.0  # Default
        else:
            base_price = np.mean(historical_prices)
        
        # Apply seasonal adjustment
        current_month = datetime.now().month
        seasonal_factor = self._get_seasonal_factor(current_month)
        
        # Generate historical data for chart (last 30 days)
        historical_data = []
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            # Simulate historical prices with deterministic variation
            day_variation = np.sin(2 * np.pi * i / 30) * 0.08  # ±8% based on day
            price = base_price * (1 + day_variation)
            historical_data.append({
                "date": date,
                "price": round(price, 2)
            })
        
        # Generate daily forecasts
        daily_forecasts = []
        predictions = []
        
        for day in range(1, days_ahead + 1):
            future_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            
            # Simple trend
            trend_factor = 1 + (day / 365) * 0.05  # 5% annual growth
            predicted_price = base_price * seasonal_factor * trend_factor
            
            # Add to daily forecasts
            daily_forecasts.append({
                "date": future_date,
                "predicted_price": round(predicted_price, 2)
            })
            
            # Add to predictions for specific timeframes
            if day in [7, 30, 90, 180]:
                predictions.append({
                    "days_ahead": day,
                    "predicted_price": round(predicted_price, 2),
                    "confidence": 0.6,  # Lower confidence for fallback
                    "price_range": {
                        "min": round(predicted_price * 0.85, 2),
                        "max": round(predicted_price * 1.15, 2)
                    }
                })
        
        return {
            "success": True,
            "crop_type": crop_type,
            "province": province,
            "days_ahead": days_ahead,  # เพิ่มสำหรับกราฟ
            "predictions": predictions,
            "historical_data": historical_data,  # เพิ่มสำหรับกราฟ
            "daily_forecasts": daily_forecasts,  # เพิ่มสำหรับกราฟ
            "current_price": round(base_price, 2),
            "price_trend": "stable",
            "trend_percentage": 0,
            "market_insights": ["ใช้ข้อมูลราคาเฉลี่ยในการคาดการณ์"],
            "best_selling_period": "ตามฤดูกาล",
            "model_used": "fallback",
            "confidence": 0.6
        }
    
    def _get_season_code(self, month: int) -> int:
        """Get season code for model features"""
        if month in [3, 4, 5]:
            return 1  # Hot season
        elif month in [6, 7, 8, 9, 10]:
            return 2  # Rainy season
        else:
            return 3  # Cool season
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal price factor"""
        factors = {
            1: 1.1, 2: 1.15, 3: 1.2, 4: 1.1,
            5: 0.9, 6: 0.85, 7: 0.8, 8: 0.85,
            9: 0.9, 10: 1.0, 11: 1.05, 12: 1.1
        }
        return factors.get(month, 1.0)
    
    def _get_seasonal_rainfall(self, month: int) -> float:
        """Get seasonal rainfall data"""
        rainfall_patterns = {
            1: 15.0, 2: 25.0, 3: 40.0, 4: 80.0,
            5: 150.0, 6: 180.0, 7: 200.0, 8: 220.0,
            9: 250.0, 10: 180.0, 11: 60.0, 12: 20.0
        }
        return rainfall_patterns.get(month, 100.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "price_prediction_model_service",
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "version": "1.0.0",
            "status": "active" if self.model_loaded else "fallback"
        }


# Global price prediction model service instance
price_prediction_service = PricePredictionModelService()

logger.info("📦 Price Prediction Model Service loaded successfully")

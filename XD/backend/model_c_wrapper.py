# -*- coding: utf-8 -*-
"""
Model C Wrapper for Chat Integration
Wraps Model C (Price Prediction) for use in chat
"""

import logging
import pickle
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

# Add backend to path (use current backend, not old REMEDIATION_PRODUCTION)
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

logger = logging.getLogger(__name__)

class ModelCWrapper:
    """Wrapper for Model C - Price Prediction"""
    
    def __init__(self):
        self.model = None
        self.forecast_service = None
        self.model_loaded = False
        self.model_path = None
        
        # Try to load Model C
        self._load_model()
    
    def _load_model(self):
        """Load Model C (Stratified Models - Final Version)"""
        try:
            import json
            
            # Load Stratified Models (3 models for different price ranges)
            models_dir = Path(__file__).parent / "models"
            
            model_low_path = models_dir / "model_c_stratified_low_final.pkl"
            model_medium_path = models_dir / "model_c_stratified_medium_final.pkl"
            model_high_path = models_dir / "model_c_stratified_high_final.pkl"
            thresholds_path = models_dir / "model_c_stratified_thresholds_final.json"
            features_path = models_dir / "model_c_stratified_features_final.json"
            metadata_path = models_dir / "model_c_stratified_metadata_final.json"
            
            # Check if all models exist
            if not all([model_low_path.exists(), model_medium_path.exists(), model_high_path.exists()]):
                logger.warning(f"⚠️ Stratified models not found, trying fallback...")
                self._load_fallback_model()
                return
            
            # Load all 3 models
            with open(model_low_path, 'rb') as f:
                self.model_low = pickle.load(f)
            with open(model_medium_path, 'rb') as f:
                self.model_medium = pickle.load(f)
            with open(model_high_path, 'rb') as f:
                self.model_high = pickle.load(f)
            
            # Load thresholds
            if thresholds_path.exists():
                with open(thresholds_path, 'r') as f:
                    thresholds = json.load(f)
                    self.low_threshold = thresholds['low_threshold']
                    self.high_threshold = thresholds['high_threshold']
            else:
                logger.warning("Thresholds file not found, using defaults")
                self.low_threshold = 30.74
                self.high_threshold = 56.22
            
            # Load features
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
            else:
                logger.warning("Features file not found")
                self.feature_names = []
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.model_version = "7.0.0"  # Stratified version
                    self.algorithm = "gradient_boosting_stratified"
                    self.training_date = metadata.get('trained_at', 'unknown')
                    self.model_metrics = {
                        'rmse': metadata.get('overall_test_rmse', 0),
                        'mae': metadata.get('overall_test_mae', 0),
                        'r2': metadata.get('overall_test_r2', 0)
                    }
            else:
                logger.warning("Metadata file not found")
                self.model_version = "7.0.0"
                self.algorithm = "gradient_boosting_stratified"
                self.training_date = "unknown"
                self.model_metrics = {}
                self.model_metrics = {}
            
            
            self.model_path = str(models_dir)
            self.model_loaded = True
            
            logger.info(f"✅ Model C (Stratified Version) loaded successfully")
            logger.info(f"   Version: {self.model_version}")
            logger.info(f"   Algorithm: Gradient Boosting (Stratified)")
            logger.info(f"   Models: LOW, MEDIUM, HIGH")
            logger.info(f"   Thresholds: <{self.low_threshold:.2f}, {self.low_threshold:.2f}-{self.high_threshold:.2f}, >{self.high_threshold:.2f}")
            logger.info(f"   Features: {len(self.feature_names)}")
            logger.info(f"   Overall RMSE: {self.model_metrics.get('rmse', 'N/A'):.2f} baht/kg")
            logger.info(f"   Overall MAE: {self.model_metrics.get('mae', 'N/A'):.2f} baht/kg")
            logger.info(f"   Overall R²: {self.model_metrics.get('r2', 'N/A'):.4f}")
            logger.info(f"   Training date: {self.training_date}")
                
        except Exception as e:
            logger.error(f"Error loading Stratified Model C: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("Trying fallback model...")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load fallback single model if stratified models not available"""
        try:
            import json
            
            model_path = Path(__file__).parent / "models" / "model_c_gradient_boosting.pkl"
            features_path = Path(__file__).parent / "models" / "model_c_features.json"
            
            if not model_path.exists():
                logger.error(f"❌ Fallback model also not found")
                self.model_loaded = False
                return
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            self.model_loaded = True
            self.model_version = "6.0.0"
            self.algorithm = "gradient_boosting_single"
            logger.info(f"✅ Loaded fallback model (single model)")
            
        except Exception as e:
            logger.error(f"Error loading fallback model: {e}")
            self.model_loaded = False
            self.model = None
    
    def predict_price(
        self,
        crop_type: str,
        province: str,
        days_ahead: int = 30,
        planting_area_rai: Optional[float] = None,
        expected_yield_kg: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Predict crop price for future dates using Model C
        
        Args:
            crop_type: Type of crop (e.g., 'พริก', 'มะเขือเทศ')
            province: Thai province name
            days_ahead: Number of days ahead to predict (7, 30, 90, or 180)
            planting_area_rai: Planting area in rai (optional)
            expected_yield_kg: Expected yield in kg (optional)
        
        Returns:
            Dictionary with price predictions, trends, and insights
        """
        try:
            # Check data availability FIRST (before model check)
            from data_availability_checker import data_checker
            
            availability = data_checker.check_crop_province_availability(
                crop_type, province, min_records=30
            )
            
            if not availability["available"]:
                logger.warning(f"❌ {availability['message']}")
                return {
                    "success": False,
                    "error": "DATA_NOT_AVAILABLE",
                    "message": availability["message"],
                    "crop_type": crop_type,
                    "province": province,
                    "suggestions": availability["suggestions"],
                    "available_provinces": availability["suggestions"][:5] if availability["suggestions"] else []
                }
            
            logger.info(f"✅ {availability['message']}")
            
            if not self.model_loaded:
                logger.error("Model not loaded")
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model C ยังไม่พร้อมใช้งาน",
                    "crop_type": crop_type,
                    "province": province
                }
            
            # Get database session
            from database import SessionLocal
            db = SessionLocal()
            
            try:
                # Get current price from database
                from database import CropPrice
                current_price_query = db.query(CropPrice).filter(
                    CropPrice.province == province,
                    CropPrice.crop_type == crop_type
                ).order_by(CropPrice.date.desc()).first()
                
                current_price = float(current_price_query.price_per_kg) if current_price_query else None
                
                # Use Model C v5 with proper feature engineering
                logger.info(f"Using Model C v5 ({self.algorithm}) for prediction")
                
                # Load historical data for feature engineering
                historical_prices = self._get_historical_prices(crop_type, province, days=90)
                
                if not historical_prices or len(historical_prices) < 7:
                    logger.error(f"❌ Insufficient historical data: {len(historical_prices) if historical_prices else 0} records")
                    return {
                        "success": False,
                        "error": "INSUFFICIENT_DATA",
                        "message": f"ข้อมูลไม่เพียงพอสำหรับการทำนาย (มีเพียง {len(historical_prices) if historical_prices else 0} records, ต้องการอย่างน้อย 7)",
                        "crop_type": crop_type,
                        "province": province,
                        "record_count": len(historical_prices) if historical_prices else 0
                    }
                
                # Use current price or latest from history
                if not current_price:
                    current_price = historical_prices[0] if historical_prices else 30.0
                
                # Generate predictions using Model C v5
                model_result = self._predict_with_model_v5(
                    crop_type, province, days_ahead, current_price, historical_prices
                )
                
                if not model_result:
                    logger.error("❌ Model failed to generate predictions")
                    return {
                        "success": False,
                        "error": "PREDICTION_FAILED",
                        "message": "ไม่สามารถสร้างการทำนายได้",
                        "crop_type": crop_type,
                        "province": province
                    }
                
                # Extract predictions from model result
                predictions = model_result.get("predictions", [])
                daily_forecasts = model_result.get("daily_forecasts", [])
                model_historical_data = model_result.get("historical_data", [])
                
                if not predictions:
                    logger.error("❌ No predictions in model result")
                    return {
                        "success": False,
                        "error": "PREDICTION_FAILED",
                        "message": "ไม่สามารถสร้างการทำนายได้",
                        "crop_type": crop_type,
                        "province": province
                    }
                
                # Analyze trend
                if not current_price:
                    current_price = predictions[0]["predicted_price"]
                
                trend_analysis = self._analyze_price_trend(current_price, predictions)
                
                # Use historical data from model (already generated)
                historical_data = model_historical_data if model_historical_data else []
                
                # If no historical data from model, try to get from database
                if not historical_data:
                    try:
                        historical_records = db.query(CropPrice).filter(
                            CropPrice.province == province,
                            CropPrice.crop_type == crop_type
                        ).order_by(CropPrice.date.desc()).limit(30).all()
                    
                        for record in reversed(historical_records):
                            historical_data.append({
                                "date": record.date.strftime("%Y-%m-%d"),
                                "price": float(record.price_per_kg)
                            })
                    except Exception as e:
                        logger.warning(f"Could not fetch historical data for chart: {e}")
                
                return {
                    "success": True,
                    "crop_type": crop_type,
                    "province": province,
                    "predictions": predictions,
                    "historical_data": historical_data,
                    "daily_forecasts": daily_forecasts,
                    "current_price": round(float(current_price), 2),
                    "price_trend": trend_analysis["trend"],
                    "trend_percentage": trend_analysis["percentage"],
                    "market_insights": self._generate_market_insights(crop_type, predictions, trend_analysis),
                    "best_selling_period": self._recommend_selling_period(predictions),
                    "model_used": f"model_c_stratified_{self.algorithm}",
                    "model_version": self.model_version,
                    "confidence": round(np.mean([p["confidence"] for p in predictions]), 2)
                }
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"❌ Error in predict_price: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": f"เกิดข้อผิดพลาดภายใน: {str(e)}",
                "crop_type": crop_type,
                "province": province
            }
    
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
        # Clip predicted price to reasonable range
        predicted_price = max(5.0, min(500.0, predicted_price))  # 5-500 baht/kg
        
        # Lower confidence = wider range
        range_factor = 1 - confidence
        range_width = predicted_price * range_factor * 0.3  # Max 30% range
        
        min_price = predicted_price - range_width
        max_price = predicted_price + range_width
        
        # Ensure min price is never negative or too low
        min_price = max(5.0, min_price)
        max_price = max(min_price + 1.0, max_price)
        
        return (min_price, max_price)
    
    def _clip_price(self, price: float) -> float:
        """Clip price to reasonable range"""
        # Prevent negative or unrealistic prices
        if price < 0:
            logger.warning(f"⚠️ Negative price detected: {price}, clipping to 5.0")
            return 5.0
        elif price < 5.0:
            logger.warning(f"⚠️ Very low price detected: {price}, clipping to 5.0")
            return 5.0
        elif price > 500.0:
            logger.warning(f"⚠️ Very high price detected: {price}, clipping to 500.0")
            return 500.0
        return price
    
    def _analyze_price_trend(self, current_price: float, predictions: List[Dict]) -> Dict:
        """Analyze price trend from predictions"""
        if not predictions or len(predictions) == 0:
            return {"trend": "stable", "percentage": 0}
        
        # Safely get last prediction
        try:
            future_price = predictions[-1].get("predicted_price", current_price)
        except (IndexError, KeyError, TypeError):
            return {"trend": "stable", "percentage": 0}
        
        if current_price == 0:
            return {"trend": "stable", "percentage": 0}
            
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
    

    def _predict_with_model_v5(
        self,
        crop_type: str,
        province: str,
        days_ahead: int,
        current_price: float,
        historical_prices: List[float]
    ) -> Dict:
        """
        Make predictions using Model C (Gradient Boosting - Clean Version)
        
        Args:
            crop_type: Crop type
            province: Province
            days_ahead: Days to predict ahead
            current_price: Current price
            historical_prices: List of historical prices (most recent first)
            
        Returns:
            Dictionary with predictions
        """
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Ensure we have enough historical data
            if len(historical_prices) < 30:
                logger.warning(f"Insufficient historical data: {len(historical_prices)} prices")
                return None
            
            # Reverse to chronological order (oldest first)
            prices_chrono = historical_prices[::-1]
            
            # Create features manually (same as training)
            def create_features(prices):
                """Create lagged features from price history"""
                features = {}
                
                # Price lags
                if len(prices) >= 30:
                    features['price_lag_7'] = prices[-7]
                    features['price_lag_14'] = prices[-14]
                    features['price_lag_21'] = prices[-21]
                    features['price_lag_30'] = prices[-30]
                else:
                    # Use available data
                    features['price_lag_7'] = prices[-min(7, len(prices))]
                    features['price_lag_14'] = prices[-min(14, len(prices))]
                    features['price_lag_21'] = prices[-min(21, len(prices))]
                    features['price_lag_30'] = prices[-min(30, len(prices))]
                
                # Moving averages (shifted by 7 days)
                if len(prices) >= 14:
                    features['price_ma_7'] = np.mean(prices[-14:-7])
                    features['price_std_7'] = np.std(prices[-14:-7])
                else:
                    features['price_ma_7'] = np.mean(prices)
                    features['price_std_7'] = np.std(prices)
                
                if len(prices) >= 21:
                    features['price_ma_14'] = np.mean(prices[-21:-7])
                    features['price_std_14'] = np.std(prices[-21:-7])
                else:
                    features['price_ma_14'] = features['price_ma_7']
                    features['price_std_14'] = features['price_std_7']
                
                if len(prices) >= 37:
                    features['price_ma_30'] = np.mean(prices[-37:-7])
                    features['price_std_30'] = np.std(prices[-37:-7])
                else:
                    features['price_ma_30'] = features['price_ma_14']
                    features['price_std_30'] = features['price_std_14']
                
                # Momentum
                if features['price_lag_14'] > 0:
                    features['price_momentum_7d'] = (features['price_lag_7'] - features['price_lag_14']) / features['price_lag_14']
                else:
                    features['price_momentum_7d'] = 0
                
                if features['price_lag_30'] > 0:
                    features['price_momentum_30d'] = (features['price_lag_7'] - features['price_lag_30']) / features['price_lag_30']
                else:
                    features['price_momentum_30d'] = 0
                
                # Time features
                now = datetime.now()
                features['dayofyear'] = now.timetuple().tm_yday
                features['month'] = now.month
                features['weekday'] = now.weekday()
                
                # Fill missing features with defaults
                for feat in self.feature_names:
                    if feat not in features:
                        if 'lag' in feat or 'ma' in feat or 'std' in feat:
                            features[feat] = features.get('price_lag_7', current_price)
                        else:
                            features[feat] = 0.0
                
                return features
            
            # Create features from historical data
            features = create_features(prices_chrono)
            
            # Generate daily predictions
            daily_forecasts = []
            predictions = []
            dates = [datetime.now() - timedelta(days=i) for i in range(len(historical_prices)-1, -1, -1)]
            
            for day in range(1, days_ahead + 1):
                future_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
                
                # Prepare features for prediction
                X = pd.DataFrame([features])[self.feature_names]
                
                # Make prediction using appropriate model based on current price
                if hasattr(self, 'model_low'):
                    # Use stratified models
                    if current_price < self.low_threshold:
                        pred_price = self.model_low.predict(X)[0]
                    elif current_price < self.high_threshold:
                        pred_price = self.model_medium.predict(X)[0]
                    else:
                        pred_price = self.model_high.predict(X)[0]
                else:
                    # Use single model (fallback)
                    pred_price = self.model.predict(X)[0]
                
                # Clip to reasonable range
                pred_price = self._clip_price(pred_price)
                
                # Add to daily forecasts
                daily_forecasts.append({
                    "date": future_date,
                    "predicted_price": round(float(pred_price), 2)
                })
                
                # Add to predictions for specific timeframes
                if day in [7, 30, 90, 180]:
                    confidence = self._calculate_confidence(day, historical_prices)
                    price_range = self._calculate_price_range(pred_price, confidence)
                    
                    predictions.append({
                        "days_ahead": day,
                        "predicted_price": round(float(pred_price), 2),
                        "confidence": confidence,
                        "price_range": {
                            "min": round(price_range[0], 2),
                            "max": round(price_range[1], 2)
                        }
                    })
            
            # Generate historical data for chart
            historical_data = []
            for date, price in zip(dates[-30:], historical_prices[-30:]):
                historical_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(float(price), 2)
                })
            
            return {
                "predictions": predictions,
                "daily_forecasts": daily_forecasts,
                "historical_data": historical_data
            }
            
        except Exception as e:
            logger.error(f"Error in Model C prediction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _get_historical_prices(self, crop_type: str, province: str, days: int = 90) -> List[float]:
        """Get historical prices from database (get latest available data)"""
        try:
            from database import SessionLocal, CropPrice
            from sqlalchemy import desc
            
            db = SessionLocal()
            try:
                # Get latest 90 records (don't filter by date range)
                # This works even if data is old
                prices = db.query(CropPrice.price_per_kg).filter(
                    CropPrice.crop_type == crop_type,
                    CropPrice.province == province
                ).order_by(desc(CropPrice.date)).limit(90).all()
                
                result = [float(p[0]) for p in prices if p[0] is not None]
                
                if result:
                    logger.info(f"✅ Got {len(result)} historical prices for {crop_type} in {province}")
                else:
                    logger.warning(f"⚠️  No historical prices found for {crop_type} in {province}")
                
                return result
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting historical prices: {e}")
            return []
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal price factor"""
        factors = {
            1: 1.1, 2: 1.15, 3: 1.2, 4: 1.1,
            5: 0.9, 6: 0.85, 7: 0.8, 8: 0.85,
            9: 0.9, 10: 1.0, 11: 1.05, 12: 1.1
        }
        return factors.get(month, 1.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = {
            "model_name": "Model C v6 - Price Prediction (Gradient Boosting - Clean Version)",
            "model_loaded": self.model_loaded,
            "model_path": str(self.model_path) if self.model_path else None,
            "version": self.model_version if hasattr(self, 'model_version') else "unknown",
            "algorithm": self.algorithm if hasattr(self, 'algorithm') else "unknown",
            "training_date": self.training_date if hasattr(self, 'training_date') else "unknown",
            "status": "active" if self.model_loaded else "fallback",
            "description": "No data leakage, proper time-series validation"
        }
        
        if self.model_loaded and hasattr(self, 'model_metrics'):
            info.update({
                "rmse": self.model_metrics.get('rmse'),
                "mae": self.model_metrics.get('mae'),
                "r2": self.model_metrics.get('r2'),
                "baseline_r2": self.model_metrics.get('baseline_r2'),
                "improvement": self.model_metrics.get('improvement'),
                "features": len(self.feature_names) if hasattr(self, 'feature_names') else 0
            })
        
        return info


# Global instance
model_c_wrapper = ModelCWrapper()

logger.info("📦 Model C Wrapper loaded")

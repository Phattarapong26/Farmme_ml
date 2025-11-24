# -*- coding: utf-8 -*-
"""
Price Forecast Service - Model C Integration
Provides price forecasting using trained ML model
"""

import logging
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import sys
import os

# Add paths for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))
sys.path.append(str(backend_dir.parent / "REMEDIATION_PRODUCTION"))

logger = logging.getLogger(__name__)

class PriceForecastService:
    """Service for price forecasting using Model C"""
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.seasonal_patterns = None
        self.feature_engineer = None
        self.model_version = None
        self.model_loaded = False
        self.model_path = None
        
        # Load Model C v3.1
        self._load_model()
        
        # Fallback: Simple Price Forecast
        try:
            from app.services.simple_price_forecast import simple_price_forecast
            self.simple_forecast = simple_price_forecast
            logger.info("✅ Simple Price Forecast available as fallback")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Simple Forecast: {e}")
            self.simple_forecast = None
    
    def _load_model(self):
        """Load trained Model C v5 (XGBoost with Comprehensive Features)"""
        try:
            # Load Model C v5 from production path
            model_path = backend_dir / "models" / "model_c_price_forecast.pkl"
            
            if not model_path.exists():
                logger.warning(f"⚠️ Model C v5 not found at: {model_path}")
                self.model_loaded = False
                return
            
            with open(model_path, 'rb') as f:
                model_package = pickle.load(f)
            
            self.model = model_package['model']
            self.algorithm = model_package['algorithm']
            self.feature_engineer = model_package['feature_engineer']
            self.feature_names = model_package['feature_names']
            self.feature_categories = model_package['feature_categories']
            self.model_version = model_package.get('version', '5.0.0')
            self.training_date = model_package.get('training_date', 'unknown')
            self.comparison_results = model_package.get('comparison_results', {})
            self.model_path = model_path
            self.model_loaded = True
            
            # Get metrics from comparison results
            if self.algorithm in self.comparison_results:
                algo_results = self.comparison_results[self.algorithm]
                self.model_metrics = {
                    'rmse': algo_results.get('rmse', 0),
                    'mae': algo_results.get('mae', 0),
                    'mape': algo_results.get('mape', 0),
                    'r2': algo_results.get('r2', 0)
                }
            else:
                self.model_metrics = {}
            
            logger.info(f"✅ Model C v5 loaded from: {model_path.name}")
            logger.info(f"   Version: {self.model_version}")
            logger.info(f"   Algorithm: {self.algorithm.upper()}")
            logger.info(f"   Features: {len(self.feature_names)}")
            logger.info(f"   RMSE: {self.model_metrics.get('rmse', 'N/A')} baht/kg")
            logger.info(f"   MAPE: {self.model_metrics.get('mape', 'N/A')}%")
            logger.info(f"   R²: {self.model_metrics.get('r2', 'N/A')}")
            logger.info(f"   Training date: {self.training_date}")
            
        except Exception as e:
            logger.error(f"Error loading Model C v5: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.model_loaded = False
            self.model = None
                
        except Exception as e:
            logger.error(f"❌ Error loading Model C: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.model_loaded = False
    
    def get_historical_data(
        self,
        province: str,
        crop_type: str,
        days_back: int = 30,
        db_session = None
    ) -> List[Dict]:
        """
        Get historical price data
        
        Args:
            province: Province name
            crop_type: Crop type
            days_back: Number of days to look back
            db_session: Database session
            
        Returns:
            List of {date, price} dicts
        """
        if db_session is None:
            return []
        
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT 
                    date,
                    price_per_kg as price
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date >= CURRENT_DATE - INTERVAL :days_back DAY
                ORDER BY date ASC
            """)
            
            results = db_session.execute(query, {
                "province": province,
                "crop_type": crop_type,
                "days_back": days_back
            }).fetchall()
            
            historical = [
                {
                    "date": r.date.strftime("%Y-%m-%d"),
                    "price": float(r.price)
                }
                for r in results
            ]
            
            logger.info(f"📊 Retrieved {len(historical)} historical data points")
            return historical
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def forecast_price(
        self,
        province: str,
        crop_type: str,
        days_ahead: int = 30,
        current_price: Optional[float] = None,
        db_session = None
    ) -> Dict:
        """
        Forecast crop price for multiple days ahead using iterative prediction
        
        Args:
            province: Province name
            crop_type: Crop type
            days_ahead: Days to forecast ahead
            current_price: Current market price (optional)
            db_session: Database session for fetching context
        
        Returns:
            Dict with forecast results including daily predictions and historical data
        """
        try:
            # Get historical data
            historical_data = self.get_historical_data(
                province, crop_type, days_back=30, db_session=db_session
            )
            
            # Use Model C Wrapper (no fallback!)
            from model_c_wrapper import model_c_wrapper
            
            logger.info("🔮 Using Model C Stratified for prediction")
            result = model_c_wrapper.predict_price(
                crop_type=crop_type,
                province=province,
                days_ahead=days_ahead
            )
            
            # Check if prediction was successful
            if not result.get('success'):
                error_code = result.get('error', 'UNKNOWN')
                error_message = result.get('message', 'Prediction failed')
                
                logger.error(f"❌ Model C prediction failed: {error_code} - {error_message}")
                
                # Return error response (no fallback!)
                return {
                    "success": False,
                    "error": error_code,
                    "message": error_message,
                    "suggestions": result.get('suggestions', []),
                    "available_provinces": result.get('available_provinces', [])
                }
            
            # Extract predictions from Model C result
            predictions_list = result.get('predictions', [])
            daily_forecasts = result.get('daily_forecasts', [])
            
            if not predictions_list:
                logger.error("❌ No predictions in Model C result")
                return {
                    "success": False,
                    "error": "NO_PREDICTIONS",
                    "message": "Model C ไม่สามารถสร้างการทำนายได้"
                }
            
            # Convert Model C format to price_forecast_service format
            predictions = {
                "forecast_price_median": predictions_list[0].get('predicted_price', 0),
                "confidence": result.get('confidence', 0.8),
                "price_trend": result.get('price_trend', 'stable'),
                "daily_forecasts": daily_forecasts,
                "predictions": predictions_list,
                "current_price": result.get('current_price', current_price)
            }
            
            # Confidence intervals already included in Model C daily_forecasts
            # No need to recalculate
            
            return {
                "success": True,
                "province": province,
                "crop_type": crop_type,
                "days_ahead": days_ahead,
                "historical_data": historical_data,
                **predictions,
                "model_used": result.get('model_used', 'model_c_stratified')
            }
            
        except Exception as e:
            logger.error(f"Error forecasting price: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_used": "error"
            }

    
    def _get_forecast_context(
        self,
        province: str,
        crop_type: str,
        db_session
    ) -> Dict:
        """Get context features from database for forecasting"""
        
        if db_session is None:
            logger.warning("No database session, using defaults")
            return self._get_default_context()
        
        # If no feature engineer (v2.0 model), use simplified context
        if not self.feature_engineer:
            logger.info("Using simplified context for v2.0 model")
            return self._get_v2_context(province, crop_type, db_session)
        
        try:
            from sqlalchemy import text
            
            # Get recent price data (last 60 days for proper lag30)
            price_query = text("""
                SELECT 
                    price_per_kg,
                    date
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date >= CURRENT_DATE - INTERVAL '60' DAY
                ORDER BY date ASC
            """)
            
            logger.info(f"🔍 Querying price history: province='{province}', crop_type='{crop_type}'")
            
            price_results = db_session.execute(price_query, {
                "province": province,
                "crop_type": crop_type
            }).fetchall()
            
            logger.info(f"🔍 Query returned {len(price_results) if price_results else 0} records")
            
            if price_results and len(price_results) > 0:
                # Extract prices and dates (chronological order)
                price_history = [float(r.price_per_kg) for r in price_results]
                dates_history = [r.date for r in price_results]
                
                # Use feature engineer to calculate all 31 features
                current_date = datetime.now()
                features = self.feature_engineer.calculate_all_features(
                    crop_type=crop_type,
                    province=province,
                    current_date=current_date,
                    price_history=price_history,
                    dates_history=dates_history
                )
                
                logger.info(f"✅ Calculated {len(features)} features using v3.1 feature engineer")
                logger.info(f"   Sample: lag7={features.get('price_per_kg_lag7', 0):.2f}, "
                          f"momentum_7d={features.get('price_per_kg_momentum_7d', 0):.4f}, "
                          f"seasonal_index={features.get('seasonal_index', 0):.2f}")
                
                return features
            else:
                logger.warning(f"⚠️  No price history found for {crop_type} in {province}")
                # Use feature engineer with empty history
                features = self.feature_engineer.calculate_all_features(
                    crop_type=crop_type,
                    province=province,
                    current_date=datetime.now(),
                    price_history=[],
                    dates_history=[]
                )
                return features
            
        except Exception as e:
            logger.error(f"Error getting forecast context: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_default_context()
    
    def _get_v2_context(self, province: str, crop_type: str, db_session) -> Dict:
        """Get simplified context for v2.0 model"""
        try:
            from sqlalchemy import text
            
            # Get recent price data
            price_query = text("""
                SELECT 
                    price_per_kg,
                    date
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date >= CURRENT_DATE - INTERVAL '30' DAY
                ORDER BY date DESC
                LIMIT 30
            """)
            
            price_results = db_session.execute(price_query, {
                "province": province,
                "crop_type": crop_type
            }).fetchall()
            
            if price_results and len(price_results) > 0:
                prices = [float(r.price_per_kg) for r in price_results]
                
                # Calculate basic features
                now = datetime.now()
                context = {
                    'price_per_kg': prices[0],  # Latest price
                    'month': now.month,
                    'month_sin': np.sin(2 * np.pi * now.month / 12),
                    'month_cos': np.cos(2 * np.pi * now.month / 12),
                    'crop_type_encoded': hash(crop_type) % 100,
                    'province_encoded': hash(province) % 100,
                }
                
                # Add lag features if available
                if len(prices) >= 7:
                    context['price_per_kg_lag7'] = prices[6] if len(prices) > 6 else prices[-1]
                if len(prices) >= 14:
                    context['price_per_kg_lag14'] = prices[13] if len(prices) > 13 else prices[-1]
                if len(prices) >= 30:
                    context['price_per_kg_lag30'] = prices[29] if len(prices) > 29 else prices[-1]
                
                logger.info(f"✅ v2.0 context: price={context['price_per_kg']:.2f}, month={context['month']}")
                return context
            else:
                logger.warning(f"⚠️  No price data for {crop_type} in {province}")
                return self._get_default_context()
                
        except Exception as e:
            logger.error(f"Error getting v2.0 context: {e}")
            return self._get_default_context()
    
    def _get_default_context(self) -> Dict:
        """Get default context when database is not available"""
        now = datetime.now()
        return {
            'price_per_kg': 50.0,
            'month': now.month,
            'month_sin': np.sin(2 * np.pi * now.month / 12),
            'month_cos': np.cos(2 * np.pi * now.month / 12),
            'crop_type_encoded': 0,
            'province_encoded': 0,
            'price_per_kg_lag7': 50.0,
            'price_per_kg_lag14': 50.0,
            'price_per_kg_lag30': 50.0,
        }
    
    def _predict_multi_step(
        self,
        context: Dict,
        days_ahead: int,
        current_price: Optional[float],
        crop_type: str = None,
        province: str = None
    ) -> Dict:
        """
        Make multi-step prediction using iterative forecasting
        Each day's prediction uses previous predictions as lag features
        
        Args:
            context: Feature context dictionary
            days_ahead: Number of days to forecast
            current_price: Current price
            crop_type: Crop type (for seasonal patterns)
            province: Province (for seasonal patterns)
        """
        try:
            daily_forecasts = []
            
            # Initialize price history from context
            price_history = []
            if 'price_per_kg_lag30' in context:
                # Reconstruct approximate history from lag features
                for i in range(30, 0, -1):
                    lag_key = f'price_per_kg_lag{i}'
                    if lag_key in context:
                        price_history.append(context[lag_key])
                    elif i <= 14 and 'price_per_kg_lag14' in context:
                        price_history.append(context['price_per_kg_lag14'])
                    elif i <= 7 and 'price_per_kg_lag7' in context:
                        price_history.append(context['price_per_kg_lag7'])
                    else:
                        price_history.append(current_price or 50.0)
            else:
                # Fallback: use current price
                price_history = [current_price or 50.0] * 30
            
            # Add current price
            price_history.append(current_price or price_history[-1])
            
            # Track seasonal index changes
            prev_seasonal_index = context.get('seasonal_index', 1.0)
            initial_seasonal_index = context.get('seasonal_index', 1.0)  # Store initial value for seasonal adjustment
            
            for day in range(days_ahead):
                future_date = datetime.now() + timedelta(days=day+1)
                
                # Recalculate ALL features for this future date
                # Note: We need crop_type and province, which we don't have in context
                # For now, use the context as-is and update key features
                
                # Update lag features from price history
                if len(price_history) >= 7:
                    context['price_per_kg_lag7'] = price_history[-7]
                if len(price_history) >= 14:
                    context['price_per_kg_lag14'] = price_history[-14]
                if len(price_history) >= 30:
                    context['price_per_kg_lag30'] = price_history[-30]
                
                # Update momentum features
                current_price_step = price_history[-1]
                if len(price_history) >= 7:
                    lag7 = price_history[-7]
                    context['price_per_kg_momentum_7d'] = (current_price_step - lag7) / (lag7 + 1e-6)
                if len(price_history) >= 14:
                    lag14 = price_history[-14]
                    context['price_per_kg_momentum_14d'] = (current_price_step - lag14) / (lag14 + 1e-6)
                if len(price_history) >= 30:
                    lag30 = price_history[-30]
                    context['price_per_kg_momentum_30d'] = (current_price_step - lag30) / (lag30 + 1e-6)
                
                # Update seasonal features for future date
                context['month'] = future_date.month
                context['month_sin'] = np.sin(2 * np.pi * future_date.month / 12)
                context['month_cos'] = np.cos(2 * np.pi * future_date.month / 12)
                context['week_of_year'] = future_date.isocalendar()[1]
                context['week_sin'] = np.sin(2 * np.pi * context['week_of_year'] / 52)
                context['week_cos'] = np.cos(2 * np.pi * context['week_of_year'] / 52)
                context['quarter'] = (future_date.month - 1) // 3 + 1
                context['day_of_week'] = future_date.weekday()
                context['day_of_month'] = future_date.day
                
                # Update seasonal index for future month (CRITICAL FIX!)
                if hasattr(self, 'seasonal_patterns') and self.seasonal_patterns and crop_type and province:
                    # Get seasonal pattern for this crop/province
                    # Try tuple key first (crop_type, province)
                    pattern_key = (crop_type, province)
                    if pattern_key in self.seasonal_patterns:
                        pattern_data = self.seasonal_patterns[pattern_key]
                        future_month = future_date.month
                        
                        # Pattern structure: {'seasonal_index': {1: 1.31, 2: 1.33, ...}, 'monthly_avg': {...}, 'overall_avg': ...}
                        if isinstance(pattern_data, dict) and 'seasonal_index' in pattern_data:
                            seasonal_indices = pattern_data['seasonal_index']
                            context['seasonal_index'] = seasonal_indices.get(future_month, 1.0)
                        else:
                            # Old format: pattern is directly the seasonal indices
                            context['seasonal_index'] = pattern_data.get(future_month, 1.0)
                        
                        # Log seasonal index updates for debugging
                        if day == 0 or day == days_ahead - 1 or (day > 0 and abs(context['seasonal_index'] - prev_seasonal_index) > 0.01):
                            logger.info(f"Day {day+1} ({future_date.strftime('%Y-%m-%d')}): seasonal_index = {context['seasonal_index']:.3f} (month {future_month})")
                        
                        prev_seasonal_index = context['seasonal_index']
                    else:
                        # Try string key as fallback
                        pattern_key_str = f"{crop_type}_{province}"
                        if pattern_key_str in self.seasonal_patterns:
                            pattern_data = self.seasonal_patterns[pattern_key_str]
                            future_month = future_date.month
                            
                            if isinstance(pattern_data, dict) and 'seasonal_index' in pattern_data:
                                seasonal_indices = pattern_data['seasonal_index']
                                context['seasonal_index'] = seasonal_indices.get(future_month, 1.0)
                            else:
                                context['seasonal_index'] = pattern_data.get(future_month, 1.0)
                            
                            if day == 0:
                                logger.info(f"✅ Using seasonal pattern for {pattern_key_str}, month {future_month}: {context['seasonal_index']:.3f}")
                        else:
                            # Keep original seasonal index
                            if day == 0:
                                logger.warning(f"⚠️  No seasonal pattern found for {pattern_key}, keeping original index")
                elif 'seasonal_index' not in context:
                    # Default seasonal index if not present
                    context['seasonal_index'] = 1.0
                
                # Update volatility features (recalculate from recent history)
                if len(price_history) >= 7:
                    recent_7 = price_history[-7:]
                    context['price_per_kg_volatility_7d'] = float(np.std(recent_7))
                    context['price_per_kg_cv_7d'] = context['price_per_kg_volatility_7d'] / (np.mean(recent_7) + 1e-6)
                
                if len(price_history) >= 14:
                    recent_14 = price_history[-14:]
                    context['price_per_kg_volatility_14d'] = float(np.std(recent_14))
                    context['price_per_kg_cv_14d'] = context['price_per_kg_volatility_14d'] / (np.mean(recent_14) + 1e-6)
                
                # Update trend features (recalculate from recent history)
                if len(price_history) >= 7:
                    recent_7 = price_history[-7:]
                    if len(recent_7) > 1:
                        # Simple linear trend
                        x = np.arange(len(recent_7))
                        y = np.array(recent_7)
                        slope = np.polyfit(x, y, 1)[0]
                        context['price_per_kg_trend_7d'] = float(slope / (np.mean(recent_7) + 1e-6))
                
                if len(price_history) >= 14:
                    recent_14 = price_history[-14:]
                    if len(recent_14) > 1:
                        x = np.arange(len(recent_14))
                        y = np.array(recent_14)
                        slope = np.polyfit(x, y, 1)[0]
                        context['price_per_kg_trend_14d'] = float(slope / (np.mean(recent_14) + 1e-6))
                
                if len(price_history) >= 30:
                    recent_30 = price_history[-30:]
                    if len(recent_30) > 1:
                        x = np.arange(len(recent_30))
                        y = np.array(recent_30)
                        slope = np.polyfit(x, y, 1)[0]
                        context['price_per_kg_trend_30d'] = float(slope / (np.mean(recent_30) + 1e-6))
                
                # Update market features
                if len(price_history) >= 30:
                    context['price_per_kg_historical_mean'] = float(np.mean(price_history[-30:]))
                    context['price_per_kg_distance_from_mean'] = current_price_step - context['price_per_kg_historical_mean']
                    
                    # Update percentile
                    sorted_prices = sorted(price_history[-30:])
                    rank = sum(1 for p in sorted_prices if p <= current_price_step)
                    context['price_per_kg_percentile'] = rank / len(sorted_prices)
                
                # Update seasonal interactions
                if 'month' in context and 'price_per_kg_momentum_7d' in context:
                    context['month_momentum_7d'] = context['month'] * context['price_per_kg_momentum_7d']
                if 'quarter' in context and 'price_per_kg_trend_7d' in context:
                    context['quarter_trend_7d'] = context['quarter'] * context['price_per_kg_trend_7d']
                if 'seasonal_index' in context and 'price_per_kg_lag7' in context:
                    context['seasonal_lag7'] = context['seasonal_index'] * context['price_per_kg_lag7']
                
                # Prepare features for prediction
                X_pred = pd.DataFrame([context])
                
                # Ensure all required features are present and in correct order
                for col in self.feature_names:
                    if col not in X_pred.columns:
                        X_pred[col] = 0.0
                        if day == 0:  # Only warn once
                            logger.warning(f"Missing feature: {col}, using 0.0")
                
                X_pred = X_pred[self.feature_names]
                
                # Debug: log first prediction features
                if day == 0:
                    logger.info(f"🔍 First prediction features:")
                    sample_features = {}
                    for feat in ['price_per_kg', 'price_per_kg_lag7', 'month', 'month_sin']:
                        if feat in X_pred.columns:
                            sample_features[feat] = X_pred[feat].values[0]
                    logger.info(f"   {sample_features}")
                
                # Make prediction
                pred_price_raw = self.model.predict(X_pred)[0]
                
                # Apply seasonal adjustment based on current vs initial seasonal index
                if hasattr(self, 'seasonal_patterns') and self.seasonal_patterns and crop_type and province:
                    pattern_key = (crop_type, province)
                    if pattern_key in self.seasonal_patterns:
                        pattern_data = self.seasonal_patterns[pattern_key]
                        if isinstance(pattern_data, dict) and 'seasonal_index' in pattern_data:
                            seasonal_indices = pattern_data['seasonal_index']
                            current_seasonal = seasonal_indices.get(future_date.month, 1.0)
                            
                            # Apply seasonal ratio relative to initial index
                            seasonal_ratio = current_seasonal / initial_seasonal_index
                            pred_price = pred_price_raw * seasonal_ratio
                            
                            if day == 0 or day == days_ahead - 1 or abs(seasonal_ratio - 1.0) > 0.05:
                                logger.info(f"Day {day+1} ({future_date.strftime('%Y-%m-%d')}): "
                                          f"seasonal_ratio={seasonal_ratio:.3f}, "
                                          f"pred={pred_price_raw:.2f}→{pred_price:.2f}")
                        else:
                            pred_price = pred_price_raw
                    else:
                        pred_price = pred_price_raw
                else:
                    pred_price = pred_price_raw
                
                # Add to history
                price_history.append(pred_price)
                
                # Store daily forecast
                daily_forecasts.append({
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_price": float(pred_price)
                })
            
            # Calculate overall statistics
            prices = [f['predicted_price'] for f in daily_forecasts]
            median_price = np.median(prices)
            std_price = np.std(prices)
            
            # Calculate trend
            if current_price:
                final_price = prices[-1]
                change_percent = ((final_price - current_price) / current_price) * 100
                if change_percent > 5:
                    trend = "increasing"
                elif change_percent < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                # Compare first and last
                change_percent = ((prices[-1] - prices[0]) / prices[0]) * 100
                if change_percent > 5:
                    trend = "increasing"
                elif change_percent < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            
            return {
                "daily_forecasts": daily_forecasts,
                "forecast_price_median": float(median_price),
                "forecast_price_q10": float(np.percentile(prices, 10)),
                "forecast_price_q90": float(np.percentile(prices, 90)),
                "confidence": 0.85,
                "price_trend": trend,
                "expected_change_percent": float(change_percent),
                "risk_assessment": "Medium"
            }
            
        except Exception as e:
            logger.error(f"Error in multi-step prediction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_prediction_simple(current_price, days_ahead)
    
    def _fallback_prediction(
        self,
        province: str,
        crop_type: str,
        days_ahead: int,
        current_price: Optional[float],
        db_session
    ) -> Dict:
        """Fallback prediction using historical averages"""
        try:
            if db_session is None:
                return self._fallback_prediction_simple(current_price)
            
            from sqlalchemy import text
            
            # Get historical average
            query = text("""
                SELECT 
                    AVG(price_per_kg) as avg_price,
                    STDDEV(price_per_kg) as std_price
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date >= CURRENT_DATE - INTERVAL '90' DAY
            """)
            
            result = db_session.execute(query, {
                "province": province,
                "crop_type": crop_type
            }).fetchone()
            
            if result and result.avg_price:
                avg_price = float(result.avg_price)
                std_price = float(result.std_price) if result.std_price else avg_price * 0.15
                
                return {
                    "forecast_price_median": avg_price,
                    "forecast_price_q10": avg_price - 1.28 * std_price,
                    "forecast_price_q90": avg_price + 1.28 * std_price,
                    "confidence": 0.65,
                    "price_trend": "stable",
                    "expected_change_percent": 0.0,
                    "risk_assessment": "Medium"
                }
            else:
                return self._fallback_prediction_simple(current_price)
                
        except Exception as e:
            logger.error(f"Error in fallback prediction: {e}")
            return self._fallback_prediction_simple(current_price)
    
    def _fallback_prediction_simple(self, current_price: Optional[float], days_ahead: int = 30) -> Dict:
        """Simple fallback when no data available"""
        base_price = current_price if current_price else 50.0
        
        # Generate daily forecasts with slight trend
        daily_forecasts = []
        for day in range(days_ahead):
            future_date = datetime.now() + timedelta(days=day+1)
            # Add slight seasonal variation
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * future_date.month / 12)
            price = base_price * seasonal_factor
            
            daily_forecasts.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_price": float(price)
            })
        
        return {
            "daily_forecasts": daily_forecasts,
            "forecast_price_median": base_price,
            "forecast_price_q10": base_price * 0.85,
            "forecast_price_q90": base_price * 1.15,
            "confidence": 0.50,
            "price_trend": "stable",
            "expected_change_percent": 0.0,
            "risk_assessment": "High"
        }
    
    def _get_production_context(self, province: str, crop_type: str, db_session) -> Dict:
        """Get context for production model prediction"""
        try:
            from sqlalchemy import text
            
            # Get recent price history (last 60 days for lag30)
            price_query = text("""
                SELECT 
                    price_per_kg,
                    date
                FROM crop_prices
                WHERE province = :province
                    AND crop_type = :crop_type
                    AND date >= CURRENT_DATE - INTERVAL '60' DAY
                ORDER BY date ASC
            """)
            
            price_results = db_session.execute(price_query, {
                "province": province,
                "crop_type": crop_type
            }).fetchall()
            
            if price_results and len(price_results) > 0:
                prices = [float(r.price_per_kg) for r in price_results]
                dates = [r.date for r in price_results]
                
                return {
                    'price_history': prices,
                    'dates_history': dates,
                    'current_price': prices[-1] if prices else 50.0
                }
            else:
                logger.warning(f"No price history for {crop_type} in {province}")
                return {
                    'price_history': [50.0],
                    'dates_history': [datetime.now()],
                    'current_price': 50.0
                }
                
        except Exception as e:
            logger.error(f"Error getting production context: {e}")
            return {
                'price_history': [50.0],
                'dates_history': [datetime.now()],
                'current_price': 50.0
            }
    
    def _predict_with_production_model(
        self,
        context: Dict,
        days_ahead: int,
        current_price: Optional[float],
        crop_type: str,
        province: str
    ) -> Dict:
        """Make prediction using production model with production feature engineer"""
        try:
            import pandas as pd
            from datetime import timedelta
            
            daily_forecasts = []
            
            # Get price history from context
            price_history = context.get('price_history', [])
            dates_history = context.get('dates_history', [])
            
            if not price_history:
                logger.warning("No price history, using fallback")
                return self._fallback_prediction_simple(current_price or 50.0, days_ahead)
            
            # Build historical dataframe
            df_history = pd.DataFrame({
                'date': dates_history,
                'crop_type': [crop_type] * len(dates_history),
                'province': [province] * len(dates_history),
                'price_per_kg': price_history
            })
            
            # Make predictions day by day
            for day in range(days_ahead):
                future_date = datetime.now() + timedelta(days=day+1)
                
                # Add future row
                new_row = pd.DataFrame({
                    'date': [future_date],
                    'crop_type': [crop_type],
                    'province': [province],
                    'price_per_kg': [df_history['price_per_kg'].iloc[-1]]  # Use last price
                })
                
                df_temp = pd.concat([df_history, new_row], ignore_index=True)
                
                # Apply feature engineering to the whole dataframe
                df_features = self.feature_engineer.transform(df_temp)
                
                # Get feature names
                feature_names = self.feature_engineer.get_feature_names()
                
                # Get last row (the prediction row)
                X_pred = df_features[feature_names].iloc[[-1]]
                
                # Fill NaN with 0 (for features that couldn't be calculated)
                X_pred = X_pred.fillna(0)
                
                # Make prediction
                pred_price = self.model.predict(X_pred)[0]
                
                # Clip to reasonable range
                pred_price = max(5.0, min(500.0, float(pred_price)))
                
                # Update history with prediction
                df_history = pd.concat([df_history, pd.DataFrame({
                    'date': [future_date],
                    'crop_type': [crop_type],
                    'province': [province],
                    'price_per_kg': [pred_price]
                })], ignore_index=True)
                
                # Store forecast
                daily_forecasts.append({
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_price": float(pred_price)
                })
            
            # Calculate statistics
            prices = [f['predicted_price'] for f in daily_forecasts]
            median_price = np.median(prices)
            
            # Calculate trend
            current = price_history[-1] if price_history else prices[0]
            final_price = prices[-1]
            change_percent = ((final_price - current) / current) * 100
            
            if change_percent > 5:
                trend = "increasing"
            elif change_percent < -5:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "daily_forecasts": daily_forecasts,
                "forecast_price_median": float(median_price),
                "forecast_price_q10": float(np.percentile(prices, 10)),
                "forecast_price_q90": float(np.percentile(prices, 90)),
                "confidence": 0.90,  # High confidence for production model
                "price_trend": trend,
                "expected_change_percent": float(change_percent),
                "risk_assessment": "Low" if abs(change_percent) < 10 else "Medium"
            }
            
        except Exception as e:
            logger.error(f"Error in production model prediction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback
            return self._fallback_prediction_simple(current_price or 50.0, days_ahead)
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        info = {
            "model_name": "Model C v5 - XGBoost Price Forecast",
            "model_loaded": self.model_loaded,
            "model_path": str(self.model_path) if self.model_path else None,
            "version": self.model_version if hasattr(self, 'model_version') else "unknown",
            "algorithm": self.algorithm if hasattr(self, 'algorithm') else "unknown",
            "feature_count": len(self.feature_names) if self.feature_names else 0,
            "status": "active" if self.model_loaded else "fallback"
        }
        
        if self.model_loaded and hasattr(self, 'model_metrics'):
            info.update({
                "rmse": self.model_metrics.get('rmse'),
                "mae": self.model_metrics.get('mae'),
                "mape": self.model_metrics.get('mape'),
                "r2": self.model_metrics.get('r2')
            })
        
        return info

# Global instance
price_forecast_service = PriceForecastService()

if __name__ == "__main__":
    print("✅ Price Forecast Service initialized")
    print(f"   Model loaded: {price_forecast_service.model_loaded}")
    print(f"   Model info: {price_forecast_service.get_model_info()}")

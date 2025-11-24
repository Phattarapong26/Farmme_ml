"""
Model C v3.1 Production Service
Complete prediction service with seasonal awareness
"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ModelCV31Service:
    """Production service for Model C v3.1 (Seasonal-Aware)"""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.seasonal_patterns = {}
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load Model C v3.1"""
        try:
            model_path = Path(__file__).parent.parent / "REMEDIATION_PRODUCTION" / "models_production" / "model_c_v3_seasonal_retrained.pkl"
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.seasonal_patterns = model_data.get('seasonal_patterns', {})
            self.model_version = model_data.get('version', 'unknown')
            self.model_loaded = True
            
            logger.info(f"Model C v3.1 loaded: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Failed to load Model C v3.1: {e}")
            self.model_loaded = False
    
    def predict_price(
        self,
        crop_type: str,
        province: str,
        current_price: float,
        days_ahead: List[int] = [7, 30, 90, 180],
        price_history: List[float] = None
    ) -> Dict:
        """
        Predict prices with seasonal awareness
        
        Args:
            crop_type: Crop type
            province: Province name
            current_price: Current price (baht/kg)
            days_ahead: List of days to predict
        
        Returns:
            Prediction results
        """
        if not self.model_loaded:
            return self._fallback_prediction(current_price, days_ahead)
        
        try:
            # Get seasonal patterns for this crop/province
            group_key = (crop_type, province)
            seasonal_info = self.seasonal_patterns.get(group_key, None)
            
            if not seasonal_info:
                logger.warning(f"No seasonal patterns for {crop_type} in {province}")
                # Use average patterns
                seasonal_info = self._get_average_seasonal_patterns()
            
            # Generate predictions
            predictions = []
            
            # Use provided price history or start with current price
            if price_history is None or len(price_history) == 0:
                price_history = [current_price]
            else:
                # Ensure current price is the last item
                if price_history[-1] != current_price:
                    price_history.append(current_price)
            
            for target_days in days_ahead:
                # Build features
                features = self._build_features(
                    current_price=current_price,
                    price_history=price_history,
                    seasonal_info=seasonal_info,
                    days_ahead=target_days
                )
                
                # Predict - ensure feature order matches model
                X = pd.DataFrame([features])[self.feature_names]
                pred_price = float(self.model.predict(X)[0])
                pred_price = max(5.0, min(500.0, pred_price))
                
                # Add to history
                price_history.append(pred_price)
                
                # Calculate confidence
                confidence = max(0.5, 0.9 - (target_days / 365) * 0.3)
                
                predictions.append({
                    'days_ahead': target_days,
                    'predicted_price': round(pred_price, 2),
                    'confidence': round(confidence, 2),
                    'price_range': self._calculate_price_range(pred_price, confidence)
                })
            
            # Analyze trend
            trend_analysis = self._analyze_trend(current_price, predictions)
            
            return {
                'success': True,
                'crop_type': crop_type,
                'province': province,
                'current_price': round(current_price, 2),
                'predictions': predictions,
                'price_trend': trend_analysis['trend'],
                'trend_percentage': trend_analysis['percentage'],
                'model_used': f'model_c_v31_{self.model_version}',
                'confidence': round(np.mean([p['confidence'] for p in predictions]), 2)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_prediction(current_price, days_ahead)
    
    def _build_features(
        self,
        current_price: float,
        price_history: List[float],
        seasonal_info: Dict,
        days_ahead: int
    ) -> Dict:
        """Build feature vector for prediction"""
        features = {}
        
        # Lag features
        if len(price_history) >= 7:
            features['price_per_kg_lag7'] = price_history[-7]
        else:
            features['price_per_kg_lag7'] = current_price
        
        if len(price_history) >= 14:
            features['price_per_kg_lag14'] = price_history[-14]
        else:
            features['price_per_kg_lag14'] = current_price
        
        if len(price_history) >= 30:
            features['price_per_kg_lag30'] = price_history[-30]
        else:
            features['price_per_kg_lag30'] = current_price
        
        # Momentum features
        if len(price_history) >= 7:
            features['price_per_kg_momentum_7d'] = (price_history[-1] - price_history[-7]) / (price_history[-7] + 1e-6)
        else:
            features['price_per_kg_momentum_7d'] = 0.0
        
        if len(price_history) >= 14:
            features['price_per_kg_momentum_14d'] = (price_history[-1] - price_history[-14]) / (price_history[-14] + 1e-6)
        else:
            features['price_per_kg_momentum_14d'] = 0.0
        
        if len(price_history) >= 30:
            features['price_per_kg_momentum_30d'] = (price_history[-1] - price_history[-30]) / (price_history[-30] + 1e-6)
        else:
            features['price_per_kg_momentum_30d'] = 0.0
        
        # Trend features
        features['price_per_kg_trend_7d'] = 0.05
        features['price_per_kg_trend_14d'] = 0.04
        features['price_per_kg_trend_30d'] = 0.03
        
        # Volatility features
        if len(price_history) >= 7:
            features['price_per_kg_volatility_7d'] = np.std(price_history[-7:])
            features['price_per_kg_cv_7d'] = features['price_per_kg_volatility_7d'] / (np.mean(price_history[-7:]) + 1e-6)
        else:
            features['price_per_kg_volatility_7d'] = 1.0
            features['price_per_kg_cv_7d'] = 0.05
        
        if len(price_history) >= 14:
            features['price_per_kg_volatility_14d'] = np.std(price_history[-14:])
            features['price_per_kg_cv_14d'] = features['price_per_kg_volatility_14d'] / (np.mean(price_history[-14:]) + 1e-6)
        else:
            features['price_per_kg_volatility_14d'] = 1.2
            features['price_per_kg_cv_14d'] = 0.06
        
        # Market features - calculate from actual price history
        if len(price_history) >= 30:
            overall_avg = np.mean(price_history[-90:]) if len(price_history) >= 90 else np.mean(price_history)
        else:
            overall_avg = seasonal_info.get('overall_avg', current_price)
        
        features['price_per_kg_historical_mean'] = overall_avg
        features['price_per_kg_distance_from_mean'] = price_history[-1] - overall_avg
        
        # Calculate percentile from history
        if len(price_history) >= 10:
            features['price_per_kg_percentile'] = (price_history[-1] > np.percentile(price_history, 50)) * 0.5 + 0.5
        else:
            features['price_per_kg_percentile'] = 0.6
        
        # Time features
        target_date = datetime.now() + timedelta(days=days_ahead)
        features['month'] = target_date.month
        features['quarter'] = (target_date.month - 1) // 3 + 1
        features['day_of_week'] = target_date.weekday()
        features['day_of_month'] = target_date.day
        features['week_of_year'] = target_date.isocalendar()[1]
        
        # Cyclical encoding
        features['month_sin'] = np.sin(2 * np.pi * target_date.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * target_date.month / 12)
        features['week_sin'] = np.sin(2 * np.pi * features['week_of_year'] / 52)
        features['week_cos'] = np.cos(2 * np.pi * features['week_of_year'] / 52)
        
        # Seasonal features - use actual historical mean
        seasonal_index_dict = seasonal_info.get('seasonal_index', {})
        features['seasonal_index'] = seasonal_index_dict.get(target_date.month, 1.0)
        
        # Use the calculated overall_avg from actual price history
        features['seasonal_expected_price'] = overall_avg * features['seasonal_index']
        features['seasonal_deviation'] = price_history[-1] - features['seasonal_expected_price']
        
        # Seasonal interactions
        features['month_momentum_7d'] = target_date.month * features['price_per_kg_momentum_7d']
        features['quarter_trend_7d'] = features['quarter'] * features['price_per_kg_trend_7d']
        features['seasonal_lag7'] = features['seasonal_index'] * features['price_per_kg_lag7']
        
        # Fill missing features
        for fname in self.feature_names:
            if fname not in features:
                features[fname] = 0.0
        
        return features
    
    def _get_average_seasonal_patterns(self) -> Dict:
        """Get average seasonal patterns across all crops"""
        if not self.seasonal_patterns:
            # Default seasonal pattern
            return {
                'overall_avg': 30.0,
                'seasonal_index': {
                    1: 1.05, 2: 1.03, 3: 1.0, 4: 0.98, 5: 0.95, 6: 0.97,
                    7: 0.98, 8: 1.0, 9: 1.0, 10: 1.03, 11: 1.08, 12: 1.10
                }
            }
        
        # Calculate average from all patterns
        all_indices = []
        for pattern in self.seasonal_patterns.values():
            all_indices.append(pattern.get('seasonal_index', {}))
        
        avg_index = {}
        for month in range(1, 13):
            month_values = [idx.get(month, 1.0) for idx in all_indices if month in idx]
            avg_index[month] = np.mean(month_values) if month_values else 1.0
        
        return {
            'overall_avg': 30.0,
            'seasonal_index': avg_index
        }
    
    def _calculate_price_range(self, price: float, confidence: float) -> Dict:
        """Calculate price range"""
        range_factor = (1 - confidence) * 0.3
        range_width = price * range_factor
        
        min_price = max(5.0, price - range_width)
        max_price = min(500.0, price + range_width)
        
        return {
            'min': round(min_price, 2),
            'max': round(max_price, 2)
        }
    
    def _analyze_trend(self, current_price: float, predictions: List[Dict]) -> Dict:
        """Analyze price trend"""
        if not predictions:
            return {'trend': 'stable', 'percentage': 0}
        
        future_price = predictions[-1]['predicted_price']
        change = ((future_price - current_price) / current_price) * 100
        
        if change > 5:
            trend = 'increasing'
        elif change < -5:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {'trend': trend, 'percentage': round(change, 1)}
    
    def _fallback_prediction(self, current_price: float, days_ahead: List[int]) -> Dict:
        """Fallback prediction"""
        predictions = []
        
        for days in days_ahead:
            price = current_price * (1 + days / 365 * 0.05)
            price = max(5.0, min(500.0, price))
            
            predictions.append({
                'days_ahead': days,
                'predicted_price': round(price, 2),
                'confidence': 0.6,
                'price_range': {'min': round(price * 0.85, 2), 'max': round(price * 1.15, 2)}
            })
        
        return {
            'success': True,
            'current_price': round(current_price, 2),
            'predictions': predictions,
            'price_trend': 'stable',
            'trend_percentage': 0,
            'model_used': 'fallback',
            'confidence': 0.6
        }


# Global instance
model_c_v31_service = ModelCV31Service()

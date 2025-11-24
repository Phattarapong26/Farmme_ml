"""
Model B Wrapper - Planting Window Prediction
Binary Classification: Is this a good planting window?

✅ FIXED VERSION:
- No data leakage (rule-based target)
- Complete features (17 features)
- Weather integration (4 features)
- Time-based validation

Usage:
    wrapper = ModelBWrapper()
    result = wrapper.predict_planting_window(
        crop_type='พริก',
        province='เชียงใหม่',
        planting_date='2024-06-15'
    )
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelBWrapper:
    """Wrapper for Model B - Planting Window Prediction"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Model B wrapper
        
        Args:
            model_path: Path to model file (default: backend/models/model_b_xgboost.pkl)
        """
        if model_path is None:
            model_path = Path(__file__).parent / 'models' / 'model_b_xgboost.pkl'
        
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.load_model()
        
        # Feature metadata
        self.required_features = [
            'growth_days',
            'avg_temp_prev_30d',
            'avg_rainfall_prev_30d',
            'total_rainfall_prev_30d',
            'rainy_days_prev_30d',
            'plant_month',
            'plant_quarter',
            'plant_day_of_year',
            'month_sin',
            'month_cos',
            'day_sin',
            'day_cos',
            'crop_type_encoded',
            'province_encoded',
            'season_encoded',
            'soil_preference_encoded',
            'seasonal_type_encoded'
        ]
        
        # Crop characteristics (from database)
        self.crop_characteristics = self._load_crop_characteristics()
        
        # Province mapping
        self.province_mapping = self._create_province_mapping()
        
        # Crop type mapping
        self.crop_type_mapping = self._create_crop_type_mapping()
        
        logger.info(f"✅ Model B loaded from {self.model_path}")
    
    def load_model(self):
        """Load trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                model_wrapper = pickle.load(f)
            
            # Handle both old and new format
            if isinstance(model_wrapper, dict):
                self.model = model_wrapper['model']
                self.scaler = model_wrapper['scaler']
                logger.info(f"✅ Model B loaded (version: {model_wrapper.get('version', 'unknown')})")
            else:
                # Old format (custom class)
                self.model = model_wrapper
                self.scaler = None
                logger.info(f"✅ Model B loaded (old format)")
        except Exception as e:
            logger.error(f"❌ Failed to load Model B: {e}")
            raise
    
    def _load_crop_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Load crop characteristics from database or default values"""
        # Default crop characteristics
        # In production, load from database
        return {
            'พริก': {'growth_days': 90, 'soil_preference': 'loam', 'seasonal_type': 'all_season'},
            'มะเขือเทศ': {'growth_days': 75, 'soil_preference': 'loam', 'seasonal_type': 'rainy'},
            'ข้าว': {'growth_days': 120, 'soil_preference': 'clay', 'seasonal_type': 'rainy'},
            'ข้าวโพด': {'growth_days': 90, 'soil_preference': 'loam', 'seasonal_type': 'all_season'},
            'มันสำปะหลัง': {'growth_days': 240, 'soil_preference': 'sandy', 'seasonal_type': 'all_season'},
        }
    
    def _create_province_mapping(self) -> Dict[str, int]:
        """Create province to encoded mapping"""
        provinces = [
            'กรุงเทพมหานคร', 'เชียงใหม่', 'เชียงราย', 'นครราชสีมา', 'ขอนแก่น',
            'อุบลราชธานี', 'สุราษฎร์ธานี', 'สงขลา', 'ภูเก็ต', 'ชลบุรี'
        ]
        return {province: idx for idx, province in enumerate(provinces)}
    
    def _create_crop_type_mapping(self) -> Dict[str, int]:
        """Create crop type to encoded mapping"""
        crops = list(self.crop_characteristics.keys())
        return {crop: idx for idx, crop in enumerate(crops)}
    
    def _get_season(self, month: int) -> str:
        """Get season from month"""
        if month in [3, 4, 5]:
            return 'summer'
        elif month in [6, 7, 8, 9, 10]:
            return 'rainy'
        else:
            return 'winter'
    
    def _get_season_encoded(self, season: str) -> int:
        """Encode season"""
        season_map = {'summer': 0, 'rainy': 1, 'winter': 2}
        return season_map.get(season, 1)
    
    def _get_soil_preference_encoded(self, soil_preference: str) -> int:
        """Encode soil preference"""
        soil_map = {'sandy': 0, 'loam': 1, 'clay': 2}
        return soil_map.get(soil_preference, 1)
    
    def _get_seasonal_type_encoded(self, seasonal_type: str) -> int:
        """Encode seasonal type"""
        seasonal_map = {'all_season': 0, 'rainy': 1, 'summer': 2, 'winter': 3}
        return seasonal_map.get(seasonal_type, 0)
    
    def _get_weather_features(
        self, 
        province: str, 
        planting_date: datetime,
        db_session = None
    ) -> Dict[str, float]:
        """
        Get weather features from 30 days before planting
        
        Args:
            province: Province name
            planting_date: Planting date
            db_session: Database session (optional)
        
        Returns:
            Dict with weather features
        """
        # In production, query from database
        # For now, use default values based on season
        
        month = planting_date.month
        season = self._get_season(month)
        
        # Default weather patterns by season
        if season == 'rainy':
            return {
                'avg_temp_prev_30d': 28.0,
                'avg_rainfall_prev_30d': 150.0,
                'total_rainfall_prev_30d': 4500.0,
                'rainy_days_prev_30d': 20.0
            }
        elif season == 'summer':
            return {
                'avg_temp_prev_30d': 32.0,
                'avg_rainfall_prev_30d': 50.0,
                'total_rainfall_prev_30d': 1500.0,
                'rainy_days_prev_30d': 8.0
            }
        else:  # winter
            return {
                'avg_temp_prev_30d': 25.0,
                'avg_rainfall_prev_30d': 20.0,
                'total_rainfall_prev_30d': 600.0,
                'rainy_days_prev_30d': 5.0
            }
    
    def prepare_features(
        self,
        crop_type: str,
        province: str,
        planting_date: str,
        db_session = None
    ) -> pd.DataFrame:
        """
        Prepare features for prediction
        
        Args:
            crop_type: Crop type (e.g., 'พริก')
            province: Province name (e.g., 'เชียงใหม่')
            planting_date: Planting date (YYYY-MM-DD)
            db_session: Database session (optional)
        
        Returns:
            DataFrame with 17 features
        """
        # Parse date
        if isinstance(planting_date, str):
            planting_date = datetime.strptime(planting_date, '%Y-%m-%d')
        
        # Get crop characteristics
        crop_chars = self.crop_characteristics.get(
            crop_type,
            {'growth_days': 90, 'soil_preference': 'loam', 'seasonal_type': 'all_season'}
        )
        
        # Get weather features
        weather_features = self._get_weather_features(province, planting_date, db_session)
        
        # Temporal features
        month = planting_date.month
        quarter = (month - 1) // 3 + 1
        day_of_year = planting_date.timetuple().tm_yday
        
        # Cyclic encoding
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        day_sin = np.sin(2 * np.pi * day_of_year / 365)
        day_cos = np.cos(2 * np.pi * day_of_year / 365)
        
        # Season
        season = self._get_season(month)
        
        # Encoded features
        crop_type_encoded = self.crop_type_mapping.get(crop_type, 0)
        province_encoded = self.province_mapping.get(province, 0)
        season_encoded = self._get_season_encoded(season)
        soil_preference_encoded = self._get_soil_preference_encoded(crop_chars['soil_preference'])
        seasonal_type_encoded = self._get_seasonal_type_encoded(crop_chars['seasonal_type'])
        
        # Create feature dictionary
        features = {
            'growth_days': crop_chars['growth_days'],
            'avg_temp_prev_30d': weather_features['avg_temp_prev_30d'],
            'avg_rainfall_prev_30d': weather_features['avg_rainfall_prev_30d'],
            'total_rainfall_prev_30d': weather_features['total_rainfall_prev_30d'],
            'rainy_days_prev_30d': weather_features['rainy_days_prev_30d'],
            'plant_month': month,
            'plant_quarter': quarter,
            'plant_day_of_year': day_of_year,
            'month_sin': month_sin,
            'month_cos': month_cos,
            'day_sin': day_sin,
            'day_cos': day_cos,
            'crop_type_encoded': crop_type_encoded,
            'province_encoded': province_encoded,
            'season_encoded': season_encoded,
            'soil_preference_encoded': soil_preference_encoded,
            'seasonal_type_encoded': seasonal_type_encoded
        }
        
        # Create DataFrame with correct order
        return pd.DataFrame([features])[self.required_features]
    
    def predict_planting_window(
        self,
        crop_type: str,
        province: str,
        planting_date: str,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Predict if this is a good planting window
        
        Args:
            crop_type: Crop type (e.g., 'พริก')
            province: Province name (e.g., 'เชียงใหม่')
            planting_date: Planting date (YYYY-MM-DD)
            db_session: Database session (optional)
        
        Returns:
            {
                'is_good_window': bool,
                'confidence': float,
                'probability': float,
                'recommendation': str,
                'reason': str,
                'features': dict
            }
        """
        try:
            # Prepare features
            X = self.prepare_features(crop_type, province, planting_date, db_session)
            
            # Scale if scaler available
            if self.scaler is not None:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0]
            
            is_good_window = bool(prediction == 1)
            confidence = float(probability[1])
            
            # Generate recommendation
            recommendation = self._get_recommendation(is_good_window, confidence)
            reason = self._get_reason(is_good_window, confidence, X)
            
            return {
                'is_good_window': is_good_window,
                'confidence': confidence,
                'probability': {
                    'good': float(probability[1]),
                    'bad': float(probability[0])
                },
                'recommendation': recommendation,
                'reason': reason,
                'features': {
                    'crop_type': crop_type,
                    'province': province,
                    'planting_date': planting_date,
                    'season': self._get_season(datetime.strptime(planting_date, '%Y-%m-%d').month),
                    'avg_temp': float(X['avg_temp_prev_30d'].values[0]),
                    'avg_rainfall': float(X['avg_rainfall_prev_30d'].values[0])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    def _get_recommendation(self, is_good_window: bool, confidence: float) -> str:
        """Generate recommendation text"""
        if is_good_window:
            if confidence > 0.9:
                return "แนะนำให้ปลูกในช่วงนี้ (เหมาะสมมาก)"
            elif confidence > 0.7:
                return "เหมาะสมสำหรับการปลูก"
            else:
                return "เหมาะสมสำหรับการปลูก แต่ควรระวัง"
        else:
            if confidence < 0.3:
                return "ไม่แนะนำให้ปลูกในช่วงนี้ (ไม่เหมาะสมมาก)"
            elif confidence < 0.5:
                return "ไม่แนะนำให้ปลูกในช่วงนี้"
            else:
                return "อาจไม่เหมาะสมสำหรับการปลูก"
    
    def _get_reason(self, is_good_window: bool, confidence: float, X: pd.DataFrame) -> str:
        """Generate reason text"""
        temp = X['avg_temp_prev_30d'].values[0]
        rainfall = X['avg_rainfall_prev_30d'].values[0]
        season = ['summer', 'rainy', 'winter'][int(X['season_encoded'].values[0])]
        
        reasons = []
        
        # Temperature
        if 22 <= temp <= 32:
            reasons.append(f"อุณหภูมิเหมาะสม ({temp:.1f}°C)")
        else:
            reasons.append(f"อุณหภูมิ {temp:.1f}°C")
        
        # Rainfall
        if 10 <= rainfall <= 150:
            reasons.append(f"ปริมาณฝนเหมาะสม ({rainfall:.1f}mm)")
        else:
            reasons.append(f"ปริมาณฝน {rainfall:.1f}mm")
        
        # Season
        season_thai = {'summer': 'ฤดูร้อน', 'rainy': 'ฤดูฝน', 'winter': 'ฤดูหนาว'}
        reasons.append(f"ช่วง{season_thai[season]}")
        
        return ", ".join(reasons)
    
    def predict_batch(
        self,
        data: list,
        db_session = None
    ) -> list:
        """
        Predict for multiple records
        
        Args:
            data: List of dicts with crop_type, province, planting_date
            db_session: Database session (optional)
        
        Returns:
            List of prediction results
        """
        results = []
        for record in data:
            try:
                result = self.predict_planting_window(
                    crop_type=record['crop_type'],
                    province=record['province'],
                    planting_date=record['planting_date'],
                    db_session=db_session
                )
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Batch prediction failed for {record}: {e}")
                results.append({
                    'error': str(e),
                    'record': record
                })
        
        return results

# Singleton instance
_model_b_instance = None

def get_model_b() -> ModelBWrapper:
    """Get singleton instance of Model B"""
    global _model_b_instance
    if _model_b_instance is None:
        _model_b_instance = ModelBWrapper()
    return _model_b_instance

if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("MODEL B WRAPPER - TEST")
    print("="*80)
    
    wrapper = ModelBWrapper()
    
    # Test case 1: Good window (rainy season)
    print("\n📝 Test 1: พริก - เชียงใหม่ - ฤดูฝน (มิถุนายน)")
    result = wrapper.predict_planting_window(
        crop_type='พริก',
        province='เชียงใหม่',
        planting_date='2024-06-15'
    )
    print(f"  Is Good Window: {result['is_good_window']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Reason: {result['reason']}")
    
    # Test case 2: Bad window (winter)
    print("\n📝 Test 2: พริก - เชียงใหม่ - ฤดูหนาว (มกราคม)")
    result = wrapper.predict_planting_window(
        crop_type='พริก',
        province='เชียงใหม่',
        planting_date='2024-01-15'
    )
    print(f"  Is Good Window: {result['is_good_window']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Reason: {result['reason']}")
    
    print("\n" + "="*80)
    print("✅ Model B Wrapper Test Complete")
    print("="*80)

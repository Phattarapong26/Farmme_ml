# -*- coding: utf-8 -*-
"""
Model B Prediction Engine
Core prediction logic with ML, weather-based, and rule-based methods
"""

import logging
from typing import Dict, Optional, List
import pandas as pd
import numpy as np

from model_b_core import (
    ModelBConfig,
    PredictionResult,
    ModelPredictionError,
    FeatureEngineeringError
)
from model_b_components import ModelLoader, WeatherDataCache

logger = logging.getLogger(__name__)


class PredictionEngine:
    """Core prediction logic with multiple strategies"""
    
    def __init__(
        self,
        model_loader: ModelLoader,
        weather_cache: WeatherDataCache,
        config: ModelBConfig = None
    ):
        self.model_loader = model_loader
        self.weather_cache = weather_cache
        self.config = config or ModelBConfig()
    
    def predict(
        self,
        date: pd.Timestamp,
        province: str,
        soil_type: Optional[str] = None,
        soil_ph: Optional[float] = None,
        soil_nutrients: Optional[float] = None,
        days_to_maturity: Optional[int] = None
    ) -> PredictionResult:
        """
        Main prediction method with fallback chain:
        1. Try ML model
        2. Fall back to weather-based
        3. Fall back to rule-based
        
        Args:
            date: Planting date
            province: Province name (normalized)
            soil_type: Soil type (optional)
            soil_ph: Soil pH (optional)
            soil_nutrients: Soil nutrients (optional)
            days_to_maturity: Days to maturity (optional)
        
        Returns:
            PredictionResult
        """
        # Try ML prediction first
        if self.model_loader.is_loaded():
            try:
                result = self._ml_prediction(
                    date, province, soil_type, soil_ph, soil_nutrients, days_to_maturity
                )
                if result:
                    return result
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}, falling back to weather-based")
        
        # Fall back to weather-based prediction
        weather_data = self.weather_cache.get_weather(
            province, date, use_historical=(date > pd.Timestamp.now())
        )
        
        if weather_data:
            try:
                return self._weather_based_prediction(
                    date, province, weather_data, soil_type, soil_ph, soil_nutrients
                )
            except Exception as e:
                logger.warning(f"Weather-based prediction failed: {e}, falling back to rules")
        
        # Final fallback to rule-based
        return self._rule_based_prediction(date, soil_type, soil_ph, soil_nutrients)
    
    def _ml_prediction(
        self,
        date: pd.Timestamp,
        province: str,
        soil_type: Optional[str],
        soil_ph: Optional[float],
        soil_nutrients: Optional[float],
        days_to_maturity: Optional[int]
    ) -> Optional[PredictionResult]:
        """
        ML model prediction
        
        Returns:
            PredictionResult or None if prediction fails
        """
        try:
            # Engineer features
            features_df = self._engineer_features(
                date, province, soil_type, soil_ph, soil_nutrients, days_to_maturity
            )
            
            # Scale features
            if self.model_loader.scaler:
                X_scaled = self.model_loader.scaler.transform(features_df)
            else:
                X_scaled = features_df.values
            
            # Predict
            prediction = self.model_loader.model.predict(X_scaled)[0]
            
            # Get probability
            try:
                proba = self.model_loader.model.predict_proba(X_scaled)[0]
                prob_good = float(proba[1])
                prob_bad = float(proba[0])
                confidence = float(proba[prediction])
            except:
                # Model doesn't support predict_proba
                prob_good = 0.85 if prediction == 1 else 0.15
                prob_bad = 1.0 - prob_good
                confidence = self.config.ML_MODEL_CONFIDENCE
            
            # Create result
            is_good = bool(prediction == 1)
            reasons = [f"ML Model: {'เหมาะสม' if is_good else 'ไม่เหมาะสม'} (จาก historical data)"]
            
            # Add weather context if available
            weather_data = self.weather_cache.get_weather(province, date, use_historical=True)
            if weather_data:
                reasons.extend(self._generate_weather_reasons(weather_data))
            
            return PredictionResult(
                is_good_window=is_good,
                confidence=confidence,
                probability_good=prob_good,
                probability_bad=prob_bad,
                method_used="ml_model",
                reasons=reasons,
                raw_prediction=int(prediction),
                raw_probability=proba if 'proba' in locals() else None
            )
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return None
    
    def _engineer_features(
        self,
        date: pd.Timestamp,
        province: str,
        soil_type: Optional[str],
        soil_ph: Optional[float],
        soil_nutrients: Optional[float],
        days_to_maturity: Optional[int]
    ) -> pd.DataFrame:
        """
        Engineer features for ML model (temporal + encoded)
        
        Returns:
            DataFrame with engineered features
        """
        try:
            # Temporal features
            month = date.month
            quarter = date.quarter
            day_of_year = date.dayofyear
            
            # Cyclic encoding
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            day_sin = np.sin(2 * np.pi * day_of_year / 365)
            day_cos = np.cos(2 * np.pi * day_of_year / 365)
            
            # Province encoding (simple mapping)
            province_map = {
                'กรุงเทพมหานคร': 0, 'นครปฐม': 1, 'สมุทรปราการ': 2,
                'นนทบุรี': 3, 'ปทุมธานี': 4, 'สมุทรสาคร': 5,
                'Nakhon Pathom': 1, 'Samut Prakan': 2,
                'Nonthaburi': 3, 'Pathum Thani': 4, 'Samut Sakhon': 5
            }
            province_encoded = province_map.get(province, 0)
            
            # Create feature dict
            features = {
                'plant_month': month,
                'plant_quarter': quarter,
                'plant_day_of_year': day_of_year,
                'month_sin': month_sin,
                'month_cos': month_cos,
                'day_sin': day_sin,
                'day_cos': day_cos,
                'province_encoded': province_encoded
            }
            
            # Create DataFrame
            return pd.DataFrame([features])
            
        except Exception as e:
            raise FeatureEngineeringError(f"Feature engineering failed: {e}")
    
    def _weather_based_prediction(
        self,
        date: pd.Timestamp,
        province: str,
        weather_data: Dict[str, float],
        soil_type: Optional[str],
        soil_ph: Optional[float],
        soil_nutrients: Optional[float]
    ) -> PredictionResult:
        """
        Weather-based prediction using real weather data
        
        Returns:
            PredictionResult
        """
        reasons = []
        is_good = True
        confidence = 0.70
        
        temp = weather_data['temperature']
        rainfall = weather_data['rainfall']
        humidity = weather_data['humidity']
        drought_idx = weather_data['drought_index']
        
        # Rule 1: Temperature check
        if temp > self.config.TEMP_MAX_ACCEPTABLE:
            is_good = False
            reasons.append(f"อุณหภูมิสูงเกินไป ({temp:.1f}°C)")
            confidence = 0.90
        elif temp < self.config.TEMP_MIN_ACCEPTABLE:
            is_good = False
            reasons.append(f"อุณหภูมิต่ำเกินไป ({temp:.1f}°C)")
            confidence = 0.85
        elif self.config.TEMP_MIN_GOOD <= temp <= self.config.TEMP_MAX_GOOD:
            reasons.append(f"อุณหภูมิเหมาะสม ({temp:.1f}°C)")
            confidence = 0.85
        elif self.config.TEMP_MAX_GOOD < temp <= self.config.TEMP_MAX_ACCEPTABLE:
            # High temp but check compensation
            if rainfall > 20 and humidity > 70:
                reasons.append(f"อุณหภูมิสูง ({temp:.1f}°C) แต่มีฝนชดเชย")
                confidence = 0.80
            elif drought_idx > self.config.DROUGHT_INDEX_MAX_ACCEPTABLE:
                is_good = False
                reasons.append(f"อุณหภูมิสูง ({temp:.1f}°C) + ภัยแล้ง")
                confidence = 0.85
            else:
                reasons.append(f"อุณหภูมิค่อนข้างสูง ({temp:.1f}°C)")
                confidence = 0.70
        else:
            reasons.append(f"อุณหภูมิพอใช้ได้ ({temp:.1f}°C)")
            confidence = 0.75
        
        # Rule 2: Rainfall check
        if rainfall > self.config.RAINFALL_MAX_ACCEPTABLE:
            is_good = False
            reasons.append(f"ฝนตกหนักเกินไป ({rainfall:.1f} mm)")
            confidence = 0.85
        elif rainfall < self.config.RAINFALL_MIN_DRY and humidity < 60:
            reasons.append(f"แห้งแล้ง (ฝน {rainfall:.1f} mm, ความชื้น {humidity:.1f}%)")
            if drought_idx > self.config.DROUGHT_INDEX_MAX_ACCEPTABLE:
                is_good = False
                confidence = 0.80
            else:
                confidence = max(0.65, confidence - 0.10)
        elif self.config.RAINFALL_MIN_GOOD <= rainfall <= self.config.RAINFALL_MAX_GOOD:
            reasons.append(f"ปริมาณฝนเหมาะสม ({rainfall:.1f} mm)")
            confidence = min(0.90, confidence + 0.05)
        
        # Rule 3: Humidity check
        if humidity < self.config.HUMIDITY_MIN_ACCEPTABLE:
            reasons.append(f"ความชื้นต่ำ ({humidity:.1f}%)")
            if is_good:
                confidence = max(0.65, confidence - 0.05)
        elif self.config.HUMIDITY_MIN_GOOD <= humidity <= self.config.HUMIDITY_MAX_GOOD:
            reasons.append(f"ความชื้นเหมาะสม ({humidity:.1f}%)")
            confidence = min(0.90, confidence + 0.05)
        elif humidity > self.config.HUMIDITY_MAX_ACCEPTABLE:
            reasons.append(f"ความชื้นสูง ({humidity:.1f}%) - เสี่ยงโรคพืช")
            confidence = max(0.70, confidence - 0.05)
        
        # Rule 4: Drought index
        if drought_idx > self.config.DROUGHT_INDEX_MAX_SEVERE:
            is_good = False
            reasons.append(f"ภัยแล้งรุนแรง (ดัชนี {drought_idx:.1f})")
            confidence = 0.85
        elif drought_idx > self.config.DROUGHT_INDEX_MAX_ACCEPTABLE:
            reasons.append(f"มีภัยแล้ง (ดัชนี {drought_idx:.1f})")
            if is_good:
                confidence = max(0.70, confidence - 0.10)
        
        # Rule 5: Soil checks
        if soil_type:
            if 'loam' in soil_type.lower() or 'ร่วน' in soil_type:
                reasons.append("ดินร่วน - เหมาะสม")
                confidence = min(0.95, confidence + 0.05)
            elif 'sandy' in soil_type.lower() or 'ทราย' in soil_type:
                reasons.append("ดินทราย - ต้องดูแลน้ำ")
                if rainfall < 10:
                    confidence = max(0.65, confidence - 0.10)
        
        if soil_ph is not None:
            if soil_ph < 5.5 or soil_ph > 8.0:
                is_good = False
                reasons.append(f"pH ดินไม่เหมาะสม ({soil_ph:.1f})")
                confidence = 0.85
            elif 6.0 <= soil_ph <= 7.5:
                reasons.append(f"pH ดินเหมาะสม ({soil_ph:.1f})")
                confidence = min(0.95, confidence + 0.05)
        
        if soil_nutrients is not None:
            if soil_nutrients < 40:
                is_good = False
                reasons.append(f"ธาตุอาหารต่ำ ({soil_nutrients:.0f})")
                confidence = 0.80
            elif soil_nutrients >= 60:
                reasons.append(f"ธาตุอาหารดี ({soil_nutrients:.0f})")
                confidence = min(0.95, confidence + 0.05)
        
        return PredictionResult(
            is_good_window=is_good,
            confidence=confidence,
            probability_good=confidence if is_good else (1 - confidence),
            probability_bad=(1 - confidence) if is_good else confidence,
            method_used="weather_based",
            reasons=reasons
        )
    
    def _rule_based_prediction(
        self,
        date: pd.Timestamp,
        soil_type: Optional[str],
        soil_ph: Optional[float],
        soil_nutrients: Optional[float]
    ) -> PredictionResult:
        """
        Simple rule-based fallback using season
        
        Returns:
            PredictionResult
        """
        month = date.month
        reasons = []
        
        # Season check
        if month in self.config.SUMMER_MONTHS:
            is_good = False
            reasons.append("ฤดูร้อน - อุณหภูมิสูงเกินไป")
            confidence = 0.75
        elif month in self.config.WINTER_MONTHS:
            is_good = True
            reasons.append("ฤดูหนาว - เหมาะสมสำหรับการปลูก")
            confidence = 0.80
        else:
            is_good = True
            reasons.append("ฤดูฝน - ความชื้นเพียงพอ")
            confidence = 0.75
        
        # Soil checks
        if soil_type:
            if 'loam' in soil_type.lower() or 'ร่วน' in soil_type:
                if is_good:
                    reasons.append("ดินร่วน - เหมาะสมที่สุด")
                    confidence = min(0.90, confidence + 0.10)
            elif 'sandy' in soil_type.lower() or 'ทราย' in soil_type:
                if is_good:
                    reasons.append("ดินทราย - ระบายน้ำเร็ว ต้องดูแลเป็นพิเศษ")
                    confidence = max(0.60, confidence - 0.10)
        
        if soil_ph is not None:
            if soil_ph < 5.5:
                is_good = False
                reasons.append("ค่า pH ดินต่ำเกินไป (เป็นกรด)")
                confidence = 0.85
            elif soil_ph > 8.0:
                is_good = False
                reasons.append("ค่า pH ดินสูงเกินไป (เป็นด่าง)")
                confidence = 0.85
            elif 6.0 <= soil_ph <= 7.5:
                if is_good:
                    reasons.append("ค่า pH ดินเหมาะสม")
                    confidence = min(0.90, confidence + 0.05)
        
        if soil_nutrients is not None:
            if soil_nutrients < 40:
                is_good = False
                reasons.append("ธาตุอาหารในดินต่ำ")
                confidence = 0.80
            elif soil_nutrients >= 60:
                if is_good:
                    reasons.append("ธาตุอาหารในดินดี")
                    confidence = min(0.90, confidence + 0.05)
        
        return PredictionResult(
            is_good_window=is_good,
            confidence=confidence,
            probability_good=confidence if is_good else (1 - confidence),
            probability_bad=(1 - confidence) if is_good else confidence,
            method_used="rule_based",
            reasons=reasons
        )
    
    def _generate_weather_reasons(self, weather_data: Dict) -> List[str]:
        """Generate weather context reasons"""
        reasons = []
        
        temp = weather_data.get('temperature', 0)
        rainfall = weather_data.get('rainfall', 0)
        humidity = weather_data.get('humidity', 0)
        
        if temp > 0:
            reasons.append(f"อุณหภูมิ {temp:.1f}°C")
        if rainfall > 10:
            reasons.append(f"ฝน {rainfall:.1f}mm")
        if humidity > 0:
            reasons.append(f"ความชื้น {humidity:.1f}%")
        
        return reasons

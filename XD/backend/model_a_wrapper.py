# -*- coding: utf-8 -*-
"""
Model A Wrapper with Full Personalization Features
Enhanced version with goal-based weighting, market factors, and seasonal bonuses
"""

import logging
import pickle
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add REMEDIATION_PRODUCTION to path
backend_dir = Path(__file__).parent
remediation_dir = backend_dir.parent / "REMEDIATION_PRODUCTION"
sys.path.insert(0, str(remediation_dir))
sys.path.insert(0, str(remediation_dir / "Model_A_Fixed"))

logger = logging.getLogger(__name__)

class ModelAWrapper:
    """Wrapper for Model A with Full Personalization"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.metadata = None
        self.model_loaded = False
        self.model_path = None
        self.backend_dir = backend_dir
        
        # Cache for datasets
        self.crops_df = None
        self.cultivation_df = None
        self.weather_df = None
        self.price_df = None
        
        # Load model
        self._load_model()
        
        # Load datasets
        self._load_datasets()
    
    def _load_model(self):
        """Load Model A from backend/models"""
        try:
            import joblib
            
            models_dir = self.backend_dir / "models"
            model_files = [
                "model_a_gradient_boosting.pkl",
                "model_a_xgboost.pkl",
            ]
            
            for model_file in model_files:
                model_path = models_dir / model_file
                if model_path.exists():
                    try:
                        self.model = joblib.load(model_path)
                        self.model_path = model_path
                        self.model_loaded = True
                        
                        if hasattr(self.model, 'n_features_in_'):
                            self.n_features = self.model.n_features_in_
                        else:
                            self.n_features = 13
                        
                        # Load scaler and encoders
                        scaler_path = models_dir / "model_a_scaler.pkl"
                        encoders_path = models_dir / "model_a_encoders.pkl"
                        metadata_path = models_dir / "model_a_metadata.pkl"
                        
                        if scaler_path.exists():
                            self.scaler = joblib.load(scaler_path)
                        
                        if encoders_path.exists():
                            self.encoders = joblib.load(encoders_path)
                        
                        if metadata_path.exists():
                            self.metadata = joblib.load(metadata_path)
                        
                        logger.info(f"✅ Model A Personalized loaded: {model_path.name}")
                        logger.info(f"   Features: {self.n_features}, R²: {self.metadata.get('r2_score', 'N/A') if self.metadata else 'N/A'}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load {model_file}: {e}")
                        continue
            
            logger.error("❌ Model A not found")
            
        except Exception as e:
            logger.error(f"Error loading Model A: {e}")
            self.model_loaded = False
    
    def _load_datasets(self):
        """Load datasets for personalization features"""
        try:
            import pandas as pd
            
            dataset_dir = self.backend_dir.parent / "buildingModel.py" / "Dataset"
            
            # Load crop characteristics
            crop_file = dataset_dir / "crop_characteristics.csv"
            if crop_file.exists():
                self.crops_df = pd.read_csv(crop_file, encoding='utf-8')
                logger.info(f"✅ Loaded {len(self.crops_df)} crops")
            
            # Load cultivation data (for market factors)
            cultivation_file = dataset_dir / "cultivation.csv"
            if cultivation_file.exists():
                self.cultivation_df = pd.read_csv(cultivation_file, encoding='utf-8')
                self.cultivation_df['planting_date'] = pd.to_datetime(self.cultivation_df['planting_date'])
                self.cultivation_df['plant_month'] = self.cultivation_df['planting_date'].dt.month
                logger.info(f"✅ Loaded {len(self.cultivation_df)} cultivation records")
            
            # Load weather data
            weather_file = dataset_dir / "weather.csv"
            if weather_file.exists():
                self.weather_df = pd.read_csv(weather_file, encoding='utf-8')
                self.weather_df['date'] = pd.to_datetime(self.weather_df['date'])
                logger.info(f"✅ Loaded {len(self.weather_df)} weather records")
            
            # Load price data
            price_file = dataset_dir / "price.csv"
            if price_file.exists():
                self.price_df = pd.read_csv(price_file, encoding='utf-8')
                self.price_df['date'] = pd.to_datetime(self.price_df['date'])
                logger.info(f"✅ Loaded {len(self.price_df)} price records")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load some datasets: {e}")
    
    def get_market_demand_factor(self, province: str, crop_type: str, month: int) -> float:
        """
        Calculate market demand factor based on scarcity and price
        
        Returns:
            float: Market demand factor (0.5 to 2.0)
        """
        try:
            if self.cultivation_df is None:
                return 1.0
            
            # Filter cultivation data
            crop_in_province = self.cultivation_df[
                (self.cultivation_df['province'] == province) &
                (self.cultivation_df['crop_type'] == crop_type) &
                (self.cultivation_df['plant_month'] == month)
            ]
            
            if len(crop_in_province) > 0:
                # Scarcity factor: less planting = higher demand
                scarcity_factor = 1.0 / (len(crop_in_province) + 1)
                scarcity_factor = min(scarcity_factor * 10, 1.0)  # Normalize
                
                # Price factor: higher revenue = higher demand
                if 'revenue' in crop_in_province.columns:
                    avg_revenue = crop_in_province['revenue'].mean()
                    price_factor = min(avg_revenue / 50000, 2.0)
                else:
                    price_factor = 1.0
                
                # Combined factor
                market_factor = (scarcity_factor * 0.3 + price_factor * 0.7)
                return max(0.5, min(2.0, market_factor))
            else:
                return 1.0
                
        except Exception as e:
            logger.warning(f"Error calculating market factor: {e}")
            return 1.0
    
    def get_seasonal_bonus(self, crop_type: str, month: int) -> float:
        """
        Calculate seasonal bonus based on crop's seasonal suitability
        
        Returns:
            float: Seasonal bonus (0.8 to 1.2)
        """
        try:
            if self.crops_df is None:
                return 1.0
            
            # Get season from month
            if month in [11, 12, 1, 2]:
                season = 'winter'
            elif month in [3, 4, 5]:
                season = 'summer'
            else:
                season = 'rainy'
            
            # Get crop info
            crop_info = self.crops_df[self.crops_df['crop_type'] == crop_type]
            if len(crop_info) == 0:
                return 1.0
            
            seasonal_type = crop_info.iloc[0]['seasonal_type']
            
            # Calculate bonus
            if seasonal_type == 'ได้ทุกฤดู':
                return 1.1
            elif (season == 'winter' and 'หนาว' in str(seasonal_type)) or \
                 (season == 'summer' and 'ร้อน' in str(seasonal_type)) or \
                 (season == 'rainy' and 'ฝน' in str(seasonal_type)):
                return 1.2
            else:
                return 0.8
                
        except Exception as e:
            logger.warning(f"Error calculating seasonal bonus: {e}")
            return 1.0
    
    def get_province_weather_features(self, province: str, month: int) -> Dict[str, float]:
        """
        Get actual weather data for province and month
        
        Returns:
            Dict with avg_temp, total_rain, avg_humidity
        """
        try:
            if self.weather_df is None:
                return {'avg_temp': 28.0, 'total_rain': 100.0, 'avg_humidity': 75.0}
            
            # Filter weather data
            province_weather = self.weather_df[
                (self.weather_df['province'] == province) &
                (self.weather_df['date'].dt.month == month)
            ]
            
            if len(province_weather) > 0:
                return {
                    'avg_temp': float(province_weather['temperature_celsius'].mean()),
                    'total_rain': float(province_weather['rainfall_mm'].sum()),
                    'avg_humidity': float(province_weather['humidity_percent'].mean())
                }
            else:
                return {'avg_temp': 28.0, 'total_rain': 100.0, 'avg_humidity': 75.0}
                
        except Exception as e:
            logger.warning(f"Error getting weather features: {e}")
            return {'avg_temp': 28.0, 'total_rain': 100.0, 'avg_humidity': 75.0}
    
    def get_province_price_features(self, province: str, crop_type: str) -> Dict[str, float]:
        """
        Get actual price data for province and crop
        
        Returns:
            Dict with avg_price, price_volatility
        """
        try:
            if self.price_df is None:
                return {'avg_price': 50.0, 'price_volatility': 10.0}
            
            # Filter price data
            crop_price = self.price_df[
                (self.price_df['province'] == province) &
                (self.price_df['crop_type'] == crop_type)
            ]
            
            if len(crop_price) > 0:
                return {
                    'avg_price': float(crop_price['price_per_kg'].mean()),
                    'price_volatility': float(crop_price['price_per_kg'].std())
                }
            else:
                return {'avg_price': 50.0, 'price_volatility': 10.0}
                
        except Exception as e:
            logger.warning(f"Error getting price features: {e}")
            return {'avg_price': 50.0, 'price_volatility': 10.0}
    
    def apply_goal_weighting(
        self, 
        recommendations: List[Dict], 
        goal: str, 
        month: int
    ) -> List[Dict]:
        """
        Apply goal-based weighting to recommendations
        
        Args:
            recommendations: List of crop recommendations
            goal: User goal ('profit', 'stability', 'sustainability')
            month: Current month
            
        Returns:
            List of weighted recommendations
        """
        try:
            weighted = []
            
            for rec in recommendations:
                base_roi = rec.get('predicted_roi', 0)
                weighted_roi = base_roi
                factors = {'base': base_roi}
                
                # Goal-based weighting
                if goal == 'profit':
                    # Maximize ROI
                    profit_bonus = 1.2
                    weighted_roi *= profit_bonus
                    factors['profit_bonus'] = profit_bonus
                    
                elif goal == 'stability':
                    # Prefer low risk
                    risk_level = rec.get('risk_level', 'ปานกลาง')
                    if risk_level in ['ต่ำมาก', 'ต่ำ']:
                        risk_bonus = 1.3
                    elif risk_level in ['กลาง', 'ปานกลาง']:
                        risk_bonus = 1.0
                    else:
                        risk_bonus = 0.7
                    weighted_roi *= risk_bonus
                    factors['stability_bonus'] = risk_bonus
                    
                elif goal == 'sustainability':
                    # Prefer low water requirement
                    water_req = rec.get('water_requirement', 'ปานกลาง')
                    if water_req in ['ต่ำมาก', 'ต่ำ']:
                        sustainability_bonus = 1.3
                    elif water_req == 'ปานกลาง':
                        sustainability_bonus = 1.1
                    else:
                        sustainability_bonus = 0.9
                    weighted_roi *= sustainability_bonus
                    factors['sustainability_bonus'] = sustainability_bonus
                
                # Market demand factor
                market_factor = self.get_market_demand_factor(
                    rec.get('province', ''), 
                    rec['crop_type'], 
                    month
                )
                weighted_roi *= market_factor
                factors['market_factor'] = market_factor
                
                # Seasonal bonus
                seasonal_bonus = self.get_seasonal_bonus(rec['crop_type'], month)
                weighted_roi *= seasonal_bonus
                factors['seasonal_bonus'] = seasonal_bonus
                
                # Update recommendation
                rec['weighted_roi'] = round(weighted_roi, 2)
                rec['final_score'] = round(weighted_roi, 2)
                rec['weighting_factors'] = factors
                
                weighted.append(rec)
            
            # Sort by final score
            weighted.sort(key=lambda x: x['final_score'], reverse=True)
            return weighted
            
        except Exception as e:
            logger.error(f"Error in goal weighting: {e}")
            return recommendations
    
    def get_recommendations(
        self,
        province: str,
        soil_type: Optional[str] = None,
        water_availability: Optional[str] = None,
        budget_level: Optional[str] = None,
        risk_tolerance: Optional[str] = None,
        goal: Optional[str] = 'profit',
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get personalized crop recommendations
        
        Args:
            province: จังหวัด
            soil_type: ประเภทดิน
            water_availability: แหล่งน้ำ
            budget_level: งบประมาณ
            risk_tolerance: ความเสี่ยง
            goal: เป้าหมาย ('profit', 'stability', 'sustainability')
            month: เดือน (1-12, None = current month)
            
        Returns:
            Dict with personalized recommendations
        """
        try:
            # Check if model is loaded
            if not self.model_loaded:
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model A ยังไม่พร้อมใช้งาน",
                    "recommendations": []
                }
            
            # Get current month if not provided
            if month is None:
                month = datetime.now().month
            
            # Get weather features for this province and month
            weather_features = self.get_province_weather_features(province, month)
            logger.info(f"Weather for {province} in month {month}: {weather_features}")
            
            # Use ML model with personalization
            return self._ml_recommendations_with_personalization(
                province, soil_type, water_availability, budget_level, 
                risk_tolerance, goal, month, weather_features
            )
                
        except Exception as e:
            logger.error(f"❌ Error in get_recommendations: {e}", exc_info=True)
            return {
                "success": False,
                "error": "PREDICTION_FAILED",
                "message": f"ไม่สามารถแนะนำพืชได้: {str(e)}",
                "recommendations": []
            }
    
    def _ml_recommendations_with_personalization(
        self, province: str, soil_type: str, water_availability: str,
        budget_level: str, risk_tolerance: str, goal: str, month: int,
        weather_features: Dict
    ) -> Dict[str, Any]:
        """ML-based recommendations with full personalization"""
        import pandas as pd
        import numpy as np
        
        if self.crops_df is None:
            return {
                "success": False,
                "error": "DATA_NOT_FOUND",
                "message": "ไม่พบข้อมูลพืช",
                "recommendations": []
            }
        
        crops_df = self.crops_df.copy()
        
        # Apply filters (same as before)
        if soil_type:
            # Soil filtering logic...
            pass
        
        if water_availability:
            water_mapping = {
                'น้ำฝน': ['ต่ำมาก', 'ต่ำ', 'ปานกลาง'],
                'น้ำบาดาล': ['ต่ำ', 'ปานกลาง', 'สูง'],
                'ชลประทาน': ['ต่ำมาก', 'ต่ำ', 'ปานกลาง', 'สูง', 'สูงมาก'],
                'แม่น้ำ/คลอง': ['ปานกลาง', 'สูง', 'สูงมาก']
            }
            if water_availability in water_mapping:
                allowed_water = water_mapping[water_availability]
                crops_df = crops_df[crops_df['water_requirement'].isin(allowed_water)]
        
        if len(crops_df) == 0:
            return {
                "success": True,
                "recommendations": [],
                "message": "ไม่พบพืชที่ตรงกับเงื่อนไข",
                "model_used": "model_a_personalized",
                "confidence": 0.0
            }
        
        # Prepare recommendations
        recommendations = []
        
        # Base yields
        base_yields = {
            'ข้าว': 800, 'ข้าวโพด': 1000, 'อ้อย': 10000, 'มันสำปะหลัง': 3000,
            'ถั่วเขียว': 400, 'ถั่วลิสง': 600, 'กระเทียม': 1200, 'หอมแดง': 1400,
            'มะเขือเทศ': 3500, 'พริก': 2000, 'ถั่วฝักยาว': 1200, 'แตงโม': 4000
        }
        
        for idx, crop_row in crops_df.iterrows():
            try:
                crop_name = crop_row['crop_type']
                estimated_yield = base_yields.get(crop_name, 1000)
                
                # Prepare features for ML model (13 features)
                current_month = month
                plant_quarter = (current_month - 1) // 3 + 1
                day_of_year = current_month * 30
                
                # Encode
                province_encoded = 0
                crop_encoded = 0
                season_encoded = 0
                
                if self.encoders:
                    try:
                        if current_month in [11, 12, 1, 2]:
                            season = 'winter'
                        elif current_month in [3, 4, 5]:
                            season = 'summer'
                        else:
                            season = 'rainy'
                        
                        province_encoded = self.encoders['province'].transform([province])[0] if province in self.encoders['province'].classes_ else 0
                        crop_encoded = self.encoders['crop'].transform([crop_name])[0] if crop_name in self.encoders['crop'].classes_ else 0
                        season_encoded = self.encoders['season'].transform([season])[0] if season in self.encoders['season'].classes_ else 0
                    except:
                        pass
                
                features = np.array([[
                    float(current_month),
                    float(plant_quarter),
                    float(day_of_year),
                    float(25),  # planting_area_rai
                    float(0.5),  # farm_skill
                    float(0.6),  # tech_adoption
                    float(crop_row['growth_days']),
                    float(crop_row['investment_cost']),
                    float(crop_row.get('weather_sensitivity', 0.5)),
                    float(crop_row.get('demand_elasticity', -0.5)),
                    float(province_encoded),
                    float(crop_encoded),
                    float(season_encoded),
                ]], dtype=np.float64)
                
                # Predict ROI
                if self.scaler is not None:
                    features_scaled = self.scaler.transform(features)
                    predicted_roi = float(self.model.predict(features_scaled)[0])
                else:
                    predicted_roi = float(self.model.predict(features)[0])
                
                # Get price features
                price_features = self.get_province_price_features(province, crop_name)
                
                recommendations.append({
                    "crop_type": crop_name,
                    "predicted_roi": round(predicted_roi, 2),
                    "expected_yield_kg_per_rai": estimated_yield,
                    "estimated_revenue_per_rai": int(estimated_yield * (predicted_roi / 100) * 50),
                    "water_requirement": crop_row['water_requirement'],
                    "risk_level": crop_row['risk_level'],
                    "growth_days": int(crop_row['growth_days']),
                    "soil_preference": crop_row['soil_preference'],
                    "investment_cost": int(crop_row['investment_cost']),
                    "province": province,
                    "avg_price": price_features['avg_price'],
                    "price_volatility": price_features['price_volatility']
                })
                
            except Exception as e:
                logger.warning(f"Error processing {crop_name}: {e}")
                continue
        
        if len(recommendations) == 0:
            return {
                "success": True,
                "recommendations": [],
                "message": "ไม่สามารถประมวลผลได้",
                "model_used": "model_a_personalized",
                "confidence": 0.0
            }
        
        # Apply personalization
        logger.info(f"Applying personalization: goal={goal}, month={month}")
        recommendations = self.apply_goal_weighting(recommendations, goal, month)
        
        return {
            "success": True,
            "recommendations": recommendations[:10],
            "model_used": "model_a_personalized",
            "personalization": {
                "goal": goal,
                "month": month,
                "weather": weather_features
            },
            "confidence": 0.90
        }
    
    def _calculate_suitability(self, predicted_roi, crop_row, soil_type, 
                               water_availability, budget_level, risk_tolerance):
        """Calculate suitability score"""
        score = min(predicted_roi / 300, 1.0)
        
        if crop_row['soil_preference'] == soil_type:
            score += 0.1
        
        return max(0.1, min(1.0, score))


# Global instance
model_a_wrapper = ModelAWrapper()

logger.info("📦 Model A Wrapper (with Personalization) loaded")

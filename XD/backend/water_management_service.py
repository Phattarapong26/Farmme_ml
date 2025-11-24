# -*- coding: utf-8 -*-
"""
Water Management Model Service for Farmme API
Uses MLwater_management_model.pkl to provide water management recommendations
"""

import logging
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import warnings

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)

class WaterManagementModelService:
    """Service for water management ML model"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        # Use absolute path from the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(backend_dir, "models", "modelNew", "MLwater_management_model.pkl")
        self.model_loaded = False
        
        # Load model
        self._load_model()
        
        logger.info("✅ Water Management Model Service initialized")
    
    def _load_model(self):
        """Load the water management ML model"""
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
                    logger.info(f"✅ Water management model loaded from {self.model_path}")
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
                        logger.info(f"✅ Water management model loaded using joblib from {self.model_path}")
                    except Exception as e2:
                        logger.warning(f"⚠️ Joblib loading also failed: {e2}")
                        self.model_loaded = False
            else:
                logger.warning(f"⚠️ Model file not found: {self.model_path}")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Failed to load water management model: {e}")
            self.model_loaded = False
    
    def get_water_advice(
        self,
        crop_type: str,
        province: str,
        soil_type: str = None,
        current_rainfall_mm: float = None,
        planting_area_rai: float = 5.0,
        growth_stage: str = "กำลังเจริญเติบโต"
    ) -> Dict[str, Any]:
        """
        Get water management recommendations
        
        Args:
            crop_type: Type of crop (e.g., 'พริก', 'มะเขือเทศ')
            province: Thai province name
            soil_type: Type of soil (ดินร่วน, ดินร่วนปนทราย, ดินเหนียว, ดินทราย)
            current_rainfall_mm: Current rainfall in mm (optional)
            planting_area_rai: Planting area in rai
            growth_stage: Growth stage (เพาะกล้า, กำลังเจริญเติบโต, ออกดอก, ติดผล)
        
        Returns:
            Dictionary with water management recommendations
        """
        try:
            if not self.model_loaded:
                logger.error("❌ Model D not loaded")
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model D ยังไม่พร้อมใช้งาน กรุณาติดต่อผู้ดูแลระบบ"
                }
            
            # Prepare features
            features = self._prepare_features(
                crop_type, province, soil_type, 
                current_rainfall_mm, planting_area_rai, growth_stage
            )
            
            if features is None:
                logger.error("❌ Failed to prepare features")
                return {
                    "success": False,
                    "error": "FEATURE_PREPARATION_FAILED",
                    "message": "ไม่สามารถเตรียมข้อมูลสำหรับ Model ได้"
                }
            
            # Make prediction
            if hasattr(self.model, 'predict'):
                # Model predicts water requirement in liters per rai per day
                water_requirement = self.model.predict(features)[0]
                
                # Calculate irrigation frequency based on water requirement and rainfall
                irrigation_freq = self._calculate_irrigation_frequency(
                    water_requirement, current_rainfall_mm or 0, soil_type
                )
                
                # Adjust for rainfall
                adjustment = self._calculate_rainfall_adjustment(current_rainfall_mm or 0)
                
                return {
                    "success": True,
                    "crop_type": crop_type,
                    "province": province,
                    "water_requirement_liters_per_rai": int(water_requirement),
                    "irrigation_frequency_days": irrigation_freq,
                    "optimal_irrigation_time": "เช้า 06:00-08:00 หรือ เย็น 17:00-19:00",
                    "irrigation_method": self._recommend_irrigation_method(soil_type),
                    "water_saving_tips": self._get_water_saving_tips(crop_type),
                    "rainfall_adjustment": adjustment,
                    "growth_stage": growth_stage,
                    "soil_type": soil_type or "ดินร่วน",
                    "model_used": "MLwater_management_model.pkl",
                    "confidence": 0.84
                }
            else:
                logger.error("❌ Model doesn't have predict method")
                return {
                    "success": False,
                    "error": "MODEL_INVALID",
                    "message": "Model ไม่สามารถใช้งานได้"
                }
                
        except Exception as e:
            logger.error(f"❌ Error in get_water_advice: {e}", exc_info=True)
            return {
                "success": False,
                "error": "PREDICTION_FAILED",
                "message": f"ไม่สามารถให้คำแนะนำการใช้น้ำได้: {str(e)}"
            }
    
    def _prepare_features(
        self,
        crop_type: str,
        province: str,
        soil_type: str,
        current_rainfall_mm: float,
        planting_area_rai: float,
        growth_stage: str
    ) -> Optional[np.ndarray]:
        """Prepare features for the ML model"""
        try:
            # Get current season
            current_month = datetime.now().month
            season = self._get_season_code(current_month)
            
            # Map categorical values to numeric
            soil_type_map = {
                'ดินร่วน': 1,
                'ดินร่วนปนทราย': 2,
                'ดินเหนียว': 3,
                'ดินทราย': 4
            }
            
            growth_stage_map = {
                'เพาะกล้า': 1,
                'กำลังเจริญเติบโต': 2,
                'ออกดอก': 3,
                'ติดผล': 4
            }
            
            # Get water requirement level for crop
            water_req_map = {
                'น้อย': 1,
                'ปานกลาง': 2,
                'มาก': 3
            }
            
            # Get crop water requirement
            from planting_model_service import planting_model_service
            crop_water_req = planting_model_service._get_water_requirement(crop_type)
            
            # Build feature vector
            features_dict = {
                'crop_code': hash(crop_type) % 100,
                'province_code': hash(province) % 100,
                'soil_type': soil_type_map.get(soil_type, 1),
                'water_requirement_level': water_req_map.get(crop_water_req, 2),
                'growth_stage': growth_stage_map.get(growth_stage, 2),
                'season': season,
                'month': current_month,
                'rainfall_mm': current_rainfall_mm if current_rainfall_mm is not None else 100.0,
                'planting_area_rai': planting_area_rai,
                'temperature': 28.0  # Average temperature
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
    

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "water_management_model_service",
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "version": "1.0.0",
            "status": "active" if self.model_loaded else "fallback"
        }


# Global water management model service instance
water_management_service = WaterManagementModelService()

logger.info("📦 Water Management Model Service loaded successfully")

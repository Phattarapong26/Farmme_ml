# -*- coding: utf-8 -*-
"""
Recommendation Model Service for Farmme API
Uses recommendation_model.pkl to provide crop recommendations
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

class RecommendationModelService:
    """Service for crop recommendation ML model"""
    
    def __init__(self):
        # Use Model A wrapper
        try:
            from model_a_wrapper import model_a_wrapper
            self.model_wrapper = model_a_wrapper
            self.model_loaded = model_a_wrapper.model_loaded
            logger.info(f"✅ Using Model A Wrapper (loaded: {self.model_loaded})")
        except Exception as e:
            logger.warning(f"Could not load Model A wrapper: {e}")
            self.model_wrapper = None
            self.model_loaded = False
        
        logger.info("✅ Recommendation Model Service initialized")
    
    def _load_model(self):
        """Load the recommendation ML model"""
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
                        self.encoder = model_data.get('encoder')
                    else:
                        self.model = model_data
                    
                    self.model_loaded = True
                    logger.info(f"✅ Recommendation model loaded from {self.model_path}")
                except (pickle.UnpicklingError, ValueError) as e:
                    logger.warning(f"⚠️ Pickle loading failed with standard method: {e}")
                    # Try with joblib
                    try:
                        import joblib
                        model_data = joblib.load(self.model_path)
                        
                        if isinstance(model_data, dict):
                            self.model = model_data.get('model')
                            self.scaler = model_data.get('scaler')
                            self.encoder = model_data.get('encoder')
                        else:
                            self.model = model_data
                        
                        self.model_loaded = True
                        logger.info(f"✅ Recommendation model loaded using joblib from {self.model_path}")
                    except Exception as e2:
                        logger.warning(f"⚠️ Joblib loading also failed: {e2}")
                        self.model_loaded = False
            else:
                logger.warning(f"⚠️ Model file not found: {self.model_path}")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Failed to load recommendation model: {e}")
            self.model_loaded = False
    
    def get_recommendations(
        self,
        province: str,
        soil_type: str = None,
        water_availability: str = None,
        budget_level: str = None,
        risk_tolerance: str = None
    ) -> Dict[str, Any]:
        """
        Get crop recommendations based on farmer's context
        
        Args:
            province: Thai province name
            soil_type: Type of soil (ดินร่วน, ดินร่วนปนทราย, ดินเหนียว, ดินทราย)
            water_availability: Water source (น้ำชลประทาน, น้ำฝน, น้ำบาดาล, น้ำประปา)
            budget_level: Investment budget (ต่ำ, ปานกลาง, สูง)
            risk_tolerance: Risk tolerance (ต่ำ, ปานกลาง, สูง)
        
        Returns:
            Dictionary with recommendations and metadata
        """
        try:
            logger.info(f"🤖 Model loaded status: {self.model_loaded}")
            
            # Use Model A wrapper if available
            if self.model_wrapper:
                return self.model_wrapper.get_recommendations(
                    province=province,
                    soil_type=soil_type,
                    water_availability=water_availability,
                    budget_level=budget_level,
                    risk_tolerance=risk_tolerance
                )
            
            # NO FALLBACK - Model must be loaded
            if not self.model_loaded:
                logger.error("❌ Model A not loaded - NO FALLBACK")
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model A ยังไม่พร้อมใช้งาน กรุณาติดต่อผู้ดูแลระบบเพื่อโหลด Model",
                    "recommendations": []
                }
            
            # Prepare features
            features = self._prepare_features(
                province, soil_type, water_availability, 
                budget_level, risk_tolerance
            )
            
            # NO FALLBACK - Features must be prepared
            if features is None:
                logger.error("❌ Failed to prepare features - NO FALLBACK")
                return {
                    "success": False,
                    "error": "FEATURE_PREPARATION_FAILED",
                    "message": "ไม่สามารถเตรียมข้อมูลสำหรับ Model ได้",
                    "recommendations": []
                }
            
            # Make prediction
            if hasattr(self.model, 'predict_proba'):
                # Get probabilities for all crops
                probabilities = self.model.predict_proba(features)[0]
                
                # Get top 5 crops
                top_indices = np.argsort(probabilities)[-5:][::-1]
                top_probs = probabilities[top_indices]
                
                # Get crop names if encoder is available
                if self.encoder and hasattr(self.encoder, 'classes_'):
                    crop_names = self.encoder.classes_[top_indices]
                else:
                    crop_names = [f"พืช_{i}" for i in top_indices]
                
                # Build recommendations
                recommendations = []
                for crop_name, prob in zip(crop_names, top_probs):
                    recommendations.append({
                        "crop_type": str(crop_name),
                        "suitability_score": round(float(prob), 3),
                        "expected_yield_kg_per_rai": self._estimate_yield(crop_name),
                        "estimated_revenue_per_rai": self._estimate_revenue(crop_name),
                        "water_requirement": self._get_water_requirement(crop_name),
                        "risk_level": self._get_risk_level(crop_name, risk_tolerance),
                        "growth_days": self._get_growth_days(crop_name),
                        "reasons": self._generate_reasons(crop_name, province, prob)
                    })
            else:
                # Fallback if model doesn't support predict_proba
                prediction = self.model.predict(features)[0]
                recommendations = [{
                    "crop_type": str(prediction),
                    "suitability_score": 0.8,
                    "expected_yield_kg_per_rai": self._estimate_yield(prediction),
                    "estimated_revenue_per_rai": self._estimate_revenue(prediction),
                    "water_requirement": self._get_water_requirement(prediction),
                    "risk_level": self._get_risk_level(prediction, risk_tolerance),
                    "growth_days": self._get_growth_days(prediction),
                    "reasons": self._generate_reasons(prediction, province, 0.8)
                }]
            
            return {
                "success": True,
                "recommendations": recommendations,
                "model_used": "recommendation_model.pkl",
                "confidence": round(float(np.mean([r["suitability_score"] for r in recommendations])), 3)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_recommendations: {e}", exc_info=True)
            # NO FALLBACK - Return error
            return {
                "success": False,
                "error": "PREDICTION_ERROR",
                "message": f"เกิดข้อผิดพลาดในการแนะนำพืช: {str(e)}",
                "recommendations": []
            }
    
    def _prepare_features(
        self,
        province: str,
        soil_type: str,
        water_availability: str,
        budget_level: str,
        risk_tolerance: str
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
            
            water_map = {
                'น้ำชลประทาน': 4,
                'น้ำบาดาล': 3,
                'น้ำประปา': 2,
                'น้ำฝน': 1
            }
            
            budget_map = {
                'สูง': 3,
                'ปานกลาง': 2,
                'ต่ำ': 1
            }
            
            risk_map = {
                'สูง': 3,
                'ปานกลาง': 2,
                'ต่ำ': 1
            }
            
            # Build feature vector
            features_dict = {
                'province_code': hash(province) % 100,
                'soil_type': soil_type_map.get(soil_type, 1),
                'water_availability': water_map.get(water_availability, 2),
                'budget_level': budget_map.get(budget_level, 2),
                'risk_tolerance': risk_map.get(risk_tolerance, 2),
                'season': season,
                'month': current_month
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
    
    # FALLBACK REMOVED - Model A must be loaded and working
    # No rule-based fallback to avoid confusing users
    
    def _get_region_from_province(self, province: str) -> str:
        """Get region from province name"""
        PROVINCE_REGION_MAP = {
            'เชียงใหม่': 'เหนือ', 'ลำพูน': 'เหนือ', 'ลำปาง': 'เหนือ', 'อุตรดิตถ์': 'เหนือ',
            'แพร่': 'เหนือ', 'น่าน': 'เหนือ', 'พะเยา': 'เหนือ', 'เชียงราย': 'เหนือ',
            'แม่ฮ่องสอน': 'เหนือ', 'ตาก': 'เหนือ', 'สุโขทัย': 'เหนือ', 'พิษณุโลก': 'เหนือ',
            'พิจิตร': 'เหนือ', 'กำแพงเพชร': 'เหนือ', 'นครสวรรค์': 'เหนือ', 'อุทัยธานี': 'เหนือ',
            'เพชรบูรณ์': 'เหนือ',
            'กรุงเทพมหานคร': 'กลาง', 'สมุทรปราการ': 'กลาง', 'นนทบุรี': 'กลาง', 'ปทุมธานี': 'กลาง',
            'พระนครศรีอยุธยา': 'กลาง', 'อ่างทอง': 'กลาง', 'ลพบุรี': 'กลาง', 'สิงห์บุรี': 'กลาง',
            'ชัยนาท': 'กลาง', 'สระบุรี': 'กลาง', 'นครปฐม': 'กลาง', 'สมุทรสาคร': 'กลาง',
            'สมุทรสงคราม': 'กลาง', 'ราชบุรี': 'กลาง', 'กาญจนบุรี': 'กลาง', 'เพชรบุรี': 'กลาง',
            'ประจวบคีรีขันธ์': 'กลาง', 'สุพรรณบุรี': 'กลาง', 'นครนายก': 'กลาง',
            'ปราจีนบุรี': 'ตะวันออก', 'ฉะเชิงเทรา': 'ตะวันออก', 'ชลบุรี': 'ตะวันออก',
            'ระยอง': 'ตะวันออก', 'จันทบุรี': 'ตะวันออก', 'ตราด': 'ตะวันออก', 'สระแก้ว': 'ตะวันออก',
            'นครราชสีมา': 'อีสาน', 'บุรีรัมย์': 'อีสาน', 'สุรินทร์': 'อีสาน', 'ศรีสะเกษ': 'อีสาน',
            'อุบลราชธานี': 'อีสาน', 'ยโสธร': 'อีสาน', 'อำนาจเจริญ': 'อีสาน', 'หนองบัวลำภู': 'อีสาน',
            'ขอนแก่น': 'อีสาน', 'อุดรธานี': 'อีสาน', 'เลย': 'อีสาน', 'หนองคาย': 'อีสาน',
            'บึงกาฬ': 'อีสาน', 'มหาสารคาม': 'อีสาน', 'ร้อยเอ็ด': 'อีสาน', 'กาฬสินธุ์': 'อีสาน',
            'สกลนคร': 'อีสาน', 'นครพนม': 'อีสาน', 'มุกดาหาร': 'อีสาน', 'ชัยภูมิ': 'อีสาน',
            'ชุมพร': 'ใต้', 'ระนอง': 'ใต้', 'สุราษฎร์ธานี': 'ใต้', 'พังงา': 'ใต้',
            'ภูเก็ต': 'ใต้', 'กระบี่': 'ใต้', 'นครศรีธรรมราช': 'ใต้', 'ตรัง': 'ใต้',
            'พัทลุง': 'ใต้', 'สงขลา': 'ใต้', 'สตูล': 'ใต้', 'ปัตตานี': 'ใต้',
            'ยะลา': 'ใต้', 'นราธิวาส': 'ใต้'
        }
        return PROVINCE_REGION_MAP.get(province, 'กลาง')
    
    def _get_season_code(self, month: int) -> int:
        """Get season code for model features"""
        if month in [3, 4, 5]:
            return 1  # Hot season
        elif month in [6, 7, 8, 9, 10]:
            return 2  # Rainy season
        else:
            return 3  # Cool season
    
    def _get_season_name(self, month: int) -> str:
        """Get season name from month"""
        if month in [3, 4, 5]:
            return "ฤดูร้อน"
        elif month in [6, 7, 8, 9, 10]:
            return "ฤดูฝน"
        else:
            return "ฤดูหนาว"
    
    def _estimate_yield(self, crop_type: str) -> int:
        """Estimate yield in kg per rai"""
        yield_map = {
            'พริก': 800, 'มะเขือเทศ': 1200, 'แตงกวา': 1500, 'บวบ': 1000,
            'ฟักทอง': 1800, 'มะระ': 900, 'ผักบุ้ง': 600, 'คะน้า': 700,
            'กวางตุ้ง': 650, 'ผักกาด': 600, 'ผักสลัด': 500, 'กะหล่ำปลี': 2000,
            'บรอกโคลี': 1500, 'แครอท': 1800, 'หัวไชเท้า': 2200, 'หอมแดง': 1000,
            'กระเทียม': 800, 'ข้าวโพด': 2500, 'ถั่วเหลือง': 400, 'ถั่วฝักยาว': 800,
            'ข้าวโพดหวาน': 2000
        }
        return yield_map.get(crop_type, 1000)
    
    def _estimate_revenue(self, crop_type: str) -> int:
        """Estimate revenue in THB per rai"""
        price_map = {
            'พริก': 60, 'มะเขือเทศ': 40, 'แตงกวา': 30, 'บวบ': 25,
            'ฟักทอง': 20, 'มะระ': 35, 'ผักบุ้ง': 20, 'คะน้า': 25,
            'กวางตุ้ง': 30, 'ผักกาด': 25, 'ผักสลัด': 35, 'กะหล่ำปลี': 20,
            'บรอกโคลี': 40, 'แครอท': 30, 'หัวไชเท้า': 25, 'หอมแดง': 50,
            'กระเทียม': 80, 'ข้าวโพด': 15, 'ถั่วเหลือง': 25, 'ถั่วฝักยาว': 40,
            'ข้าวโพดหวาน': 20
        }
        yield_kg = self._estimate_yield(crop_type)
        price_per_kg = price_map.get(crop_type, 30)
        return yield_kg * price_per_kg
    
    def _get_water_requirement(self, crop_type: str) -> str:
        """Get water requirement for crop"""
        requirements = {
            'พริก': 'ปานกลาง', 'มะเขือเทศ': 'มาก', 'แตงกวา': 'มาก', 'บวบ': 'มาก',
            'ฟักทอง': 'ปานกลาง', 'มะระ': 'ปานกลาง', 'ผักบุ้ง': 'มาก', 'คะน้า': 'มาก',
            'กวางตุ้ง': 'มาก', 'ผักกาด': 'มาก', 'ผักสลัด': 'มาก', 'กะหล่ำปลี': 'มาก',
            'บรอกโคลี': 'มาก', 'แครอท': 'ปานกลาง', 'หัวไชเท้า': 'ปานกลาง', 'หอมแดง': 'น้อย',
            'กระเทียม': 'น้อย', 'ข้าวโพด': 'ปานกลาง', 'ถั่วเหลือง': 'น้อย', 'ถั่วฝักยาว': 'ปานกลาง',
            'ข้าวโพดหวาน': 'มาก'
        }
        return requirements.get(crop_type, 'ปานกลาง')
    
    def _get_risk_level(self, crop_type: str, risk_tolerance: str) -> str:
        """Get risk level for crop"""
        risk_map = {
            'พริก': 'ปานกลาง', 'มะเขือเทศ': 'ปานกลาง', 'แตงกวา': 'ต่ำ', 'บวบ': 'ต่ำ',
            'ฟักทอง': 'ต่ำ', 'มะระ': 'ปานกลาง', 'ผักบุ้ง': 'ต่ำ', 'คะน้า': 'ต่ำ',
            'กวางตุ้ง': 'ต่ำ', 'ผักกาด': 'ต่ำ', 'ผักสลัด': 'ปานกลาง', 'กะหล่ำปลี': 'ปานกลาง',
            'บรอกโคลี': 'สูง', 'แครอท': 'ปานกลาง', 'หัวไชเท้า': 'ปานกลาง', 'หอมแดง': 'สูง',
            'กระเทียม': 'สูง', 'ข้าวโพด': 'ปานกลาง', 'ถั่วเหลือง': 'ปานกลาง', 'ถั่วฝักยาว': 'ต่ำ',
            'ข้าวโพดหวาน': 'ปานกลาง'
        }
        return risk_map.get(crop_type, 'ปานกลาง')
    
    def _get_growth_days(self, crop_type: str) -> int:
        """Get growth days for crop"""
        growth_days_map = {
            'พริก': 75, 'มะเขือเทศ': 55, 'แตงกวา': 45, 'บวบ': 50,
            'ฟักทอง': 60, 'มะระ': 50, 'ผักบุ้ง': 25, 'คะน้า': 45,
            'กวางตุ้ง': 30, 'ผักกาด': 35, 'ผักสลัด': 35, 'กะหล่ำปลี': 70,
            'บรอกโคลี': 65, 'แครอท': 90, 'หัวไชเท้า': 60, 'หอมแดง': 120,
            'กระเทียม': 150, 'ข้าวโพด': 90, 'ถั่วเหลือง': 90, 'ถั่วฝักยาว': 60,
            'ข้าวโพดหวาน': 75
        }
        return growth_days_map.get(crop_type, 60)
    
    def _generate_reasons(self, crop_type: str, province: str, score: float) -> List[str]:
        """Generate reasons for recommendation"""
        reasons = []
        
        if score > 0.8:
            reasons.append(f"เหมาะสมอย่างยิ่งสำหรับ{province}")
        elif score > 0.6:
            reasons.append(f"เหมาะสมสำหรับ{province}")
        else:
            reasons.append(f"พอใช้สำหรับ{province}")
        
        # Add season-based reason
        current_month = datetime.now().month
        season = self._get_season_name(current_month)
        reasons.append(f"เหมาะกับ{season}")
        
        # Add market demand reason
        if score > 0.7:
            reasons.append("ความต้องการในตลาดสูง")
        
        return reasons
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "recommendation_model_service",
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "version": "1.0.0",
            "status": "active" if self.model_loaded else "fallback"
        }


# Global recommendation model service instance
recommendation_model_service = RecommendationModelService()

logger.info("📦 Recommendation Model Service loaded successfully")

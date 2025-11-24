# -*- coding: utf-8 -*-
"""
Model A Wrapper for Chat Integration
Wraps Model A (Crop Recommendation) for use in chat
"""

import logging
import pickle
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add REMEDIATION_PRODUCTION to path
backend_dir = Path(__file__).parent
remediation_dir = backend_dir.parent / "REMEDIATION_PRODUCTION"
sys.path.insert(0, str(remediation_dir))  # Use insert(0) to prioritize this path

# Add Model_A_Fixed to path (required for loading pickled model)
sys.path.insert(0, str(remediation_dir / "Model_A_Fixed"))

logger = logging.getLogger(__name__)

class ModelAWrapper:
    """Wrapper for Model A - Crop Recommendation"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_path = None
        
        # Try to load Model A
        self._load_model()
    
    def _load_model(self):
        """Load Model A from backend/models"""
        try:
            # Try different Model A variants (prioritize new Gradient Boosting model)
            model_files = [
                "model_a_xgboost.pkl",  # Now contains Gradient Boosting (deployed)
                "model_a_gradboost_large.pkl",  # Backup: Gradient Boosting
                "model_a_xgboost_large.pkl",  # Alternative: XGBoost
                "model_a_rf_ensemble_large.pkl",  # Alternative: RF + ElasticNet
            ]
            
            # Try backend/models first (production location)
            models_dir = backend_dir / "models"
            
            for model_file in model_files:
                model_path = models_dir / model_file
                if model_path.exists():
                    try:
                        with open(model_path, 'rb') as f:
                            self.model = pickle.load(f)
                        
                        self.model_path = model_path
                        self.model_loaded = True
                        
                        # Check if model requires 19 features (new model) or 6 features (old model)
                        if hasattr(self.model, 'n_features_in_'):
                            self.n_features = self.model.n_features_in_
                        else:
                            self.n_features = 6  # Assume old model
                        
                        logger.info(f"✅ Model A loaded from: {model_path}")
                        logger.info(f"   Model type: {type(self.model).__name__}")
                        logger.info(f"   Features required: {self.n_features}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load {model_file}: {e}")
                        continue
            
            logger.error("❌ Model A not found - NO FALLBACK AVAILABLE")
            
        except Exception as e:
            logger.error(f"Error loading Model A: {e}")
            self.model_loaded = False
    
    def get_recommendations(
        self,
        province: str,
        soil_type: Optional[str] = None,
        water_availability: Optional[str] = None,
        budget_level: Optional[str] = None,
        risk_tolerance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get crop recommendations using Model A
        
        Args:
            province: จังหวัด
            soil_type: ประเภทดิน
            water_availability: แหล่งน้ำ
            budget_level: งบประมาณ
            risk_tolerance: ความเสี่ยง
            
        Returns:
            Dict with recommendations
        """
        try:
            # Check if model is loaded
            if not self.model_loaded:
                logger.error("❌ Model A not loaded")
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model A ยังไม่พร้อมใช้งาน กรุณาติดต่อผู้ดูแลระบบ",
                    "recommendations": []
                }
            
            # Use ML Model (no fallback!)
            logger.info("✅ Using ML Model A")
            return self._ml_recommendations_with_filtering(
                province, soil_type, water_availability, budget_level, risk_tolerance
            )
                
        except Exception as e:
            logger.error(f"❌ Error in get_recommendations: {e}", exc_info=True)
            return {
                "success": False,
                "error": "PREDICTION_FAILED",
                "message": f"ไม่สามารถแนะนำพืชได้: {str(e)}",
                "recommendations": []
            }
    
    def _ml_recommendations_with_filtering(
        self, province: str, soil_type: str = None,
        water_availability: str = None, budget_level: str = None,
        risk_tolerance: str = None
    ) -> Dict[str, Any]:
        """ML-based recommendations with filtering"""
        import pandas as pd
        import numpy as np
        
        # Load crop characteristics
        crop_file = backend_dir.parent / "buildingModel.py" / "Dataset" / "crop_characteristics.csv"
        if not crop_file.exists():
            logger.error(f"❌ Crop characteristics not found at: {crop_file}")
            return {
                "success": False,
                "error": "DATA_NOT_FOUND",
                "message": "ไม่พบข้อมูลลักษณะพืช กรุณาติดต่อผู้ดูแลระบบ",
                "recommendations": []
            }
        
        crops_df = pd.read_csv(crop_file, encoding='utf-8')
        logger.info(f"Loaded {len(crops_df)} crops from database")
        
        # Use fuzzy matching for soil type (fix encoding issues)
        def fuzzy_match_soil(input_soil, available_soils):
            """Match soil type using fuzzy logic to handle encoding issues"""
            if not input_soil:
                return available_soils
            
            # Remove all non-alphanumeric Thai characters for comparison
            def normalize_thai(text):
                # Keep only Thai consonants and vowels, remove tone marks
                import re
                # Remove tone marks and other diacritics
                text = re.sub(r'[\u0E31-\u0E3A\u0E47-\u0E4E]', '', text)
                return text.strip()
            
            normalized_input = normalize_thai(input_soil)
            
            # Try to match
            matched = []
            for soil in available_soils:
                normalized_soil = normalize_thai(soil)
                # Check if they match after normalization
                if normalized_input in normalized_soil or normalized_soil in normalized_input:
                    matched.append(soil)
            
            return matched if matched else available_soils
        
        # Filter by soil type with fuzzy matching
        if soil_type:
            available_soil_types = crops_df['soil_preference'].unique().tolist()
            
            # Fuzzy match to find the right soil type
            matched_soils = fuzzy_match_soil(soil_type, available_soil_types)
            
            # If we found matches, also include compatible soils
            if matched_soils:
                # Expand to include compatible soils
                all_allowed = set(matched_soils)
                
                # Add compatible soils based on what we matched
                for matched in matched_soils:
                    if 'ร่วน' in matched and 'ปน' not in matched:
                        # ดินร่วน -> also allow ดินร่วนปนทราย, ดินร่วนปนเหนียว
                        all_allowed.update([s for s in available_soil_types if 'ร่วนปน' in s])
                    elif 'ทราย' in matched and 'ปน' not in matched:
                        # ดินทราย -> also allow ดินร่วนปนทราย
                        all_allowed.update([s for s in available_soil_types if 'ร่วนปนทราย' in s])
                    elif 'เหนียว' in matched and 'ปน' not in matched:
                        # ดินเหนียว -> also allow ดินร่วนปนเหนียว
                        all_allowed.update([s for s in available_soil_types if 'ร่วนปนเหนียว' in s])
                
                crops_df = crops_df[crops_df['soil_preference'].isin(all_allowed)]
                logger.info(f"After soil filter ({soil_type} -> {matched_soils}): {len(crops_df)} crops")
        
        # Filter by water availability
        if water_availability:
            # Map water source to allowed water requirement levels (as text)
            water_mapping = {
                'น้ำฝน': ['ต่ำมาก', 'ต่ำ', 'ปานกลาง'],
                'น้ำบาดาล': ['ต่ำ', 'ปานกลาง', 'สูง'],
                'ชลประทาน': ['ต่ำมาก', 'ต่ำ', 'ปานกลาง', 'สูง', 'สูงมาก'],
                'แม่น้ำ/คลอง': ['ปานกลาง', 'สูง', 'สูงมาก']
            }
            
            if water_availability in water_mapping:
                allowed_water = water_mapping[water_availability]
                crops_df = crops_df[crops_df['water_requirement'].isin(allowed_water)]
                logger.info(f"After water filter ({water_availability}): {len(crops_df)} crops")
        
        if len(crops_df) == 0:
            logger.warning("⚠️ No crops match the specified filters")
            return {
                "success": True,
                "recommendations": [],
                "message": "ไม่พบพืชที่ตรงกับเงื่อนไขที่กำหนด กรุณาลองปรับเงื่อนไขใหม่",
                "model_used": "model_a",
                "confidence": 0.0
            }
        
        # Prepare features for ML prediction
        recommendations = []
        errors = []
        
        # Base yields for estimation
        base_yields = {
            'ข้าว': 800, 'ข้าวโพด': 1000, 'ข้าวโพดเลี้ยงสัตว์': 1000, 'ข้าวโพดหวาน': 1200,
            'อ้อย': 10000, 'มันสำปะหลัง': 3000,
            'ถั่วเขียว': 400, 'ถั่วลิสง': 600, 'ถั่วเหลือง': 400, 'งา': 300,
            'กระเทียม': 1200, 'หอมแดง': 1400, 'หอมหัวใหญ่': 1500,
            'มะเขือเทศ': 3500, 'มะเขือเทศเชอร์รี': 2000, 'พริก': 2000, 'พริกหวาน': 2500,
            'ถั่วฝักยาว': 1200, 'แตงโม': 4000, 'สับปะรด': 3000, 'มะพร้าว': 2000,
            'แตงกวา': 2500, 'ฟักทอง': 2000, 'คะน้า': 1000, 'กวางตุ้ง': 1000,
            'ผักบุ้ง': 800, 'ผักกาดหอม': 900, 'ผักกาดขาว': 900
        }
        
        for idx, crop_row in crops_df.iterrows():
            try:
                crop_name = crop_row['crop_type']
                estimated_yield = base_yields.get(crop_name, 1000)
                
                # Convert text fields to numbers for ML model
                water_req_map = {'ต่ำมาก': 1, 'ต่ำ': 2, 'ปานกลาง': 3, 'สูง': 4, 'สูงมาก': 5}
                water_req_num = water_req_map.get(crop_row['water_requirement'], 3)
                
                risk_map = {'ต่ำมาก': 0.1, 'ต่ำ': 0.3, 'กลาง': 0.5, 'ปานกลาง': 0.5, 'สูง': 0.7, 'สูงมาก': 0.9}
                risk_num = risk_map.get(crop_row['risk_level'], 0.5)
                
                # Create feature vector based on model requirements
                if hasattr(self, 'n_features') and self.n_features == 19:
                    # New model (19 features) - includes market, weather, and economic factors
                    features = np.array([[
                        float(25),  # planting_area_rai (default)
                        float(estimated_yield),  # expected_yield_kg
                        float(crop_row['growth_days']),
                        float(water_req_num),  # water_requirement as number
                        float(crop_row['investment_cost']),
                        float(risk_num),  # risk_level as number
                        float(45.0),  # base_price (default)
                        float(0.5),  # inventory_level (default)
                        float(0.7),  # supply_level (default)
                        float(-0.5),  # demand_elasticity (default)
                        float(28.0),  # temperature_celsius (default)
                        float(100.0),  # rainfall_mm (default)
                        float(75.0),  # humidity_percent (default)
                        float(50.0),  # drought_index (default)
                        float(40.0),  # fuel_price (default)
                        float(900.0),  # fertilizer_price (default)
                        float(2.0),  # inflation_rate (default)
                        float(3.0),  # gdp_growth (default)
                        float(1.5),  # unemployment_rate (default)
                    ]], dtype=np.float64)
                else:
                    # Old model (6 features)
                    features = np.array([[
                        float(25),  # planting_area_rai (default)
                        float(estimated_yield),  # expected_yield_kg
                        float(crop_row['growth_days']),
                        float(water_req_num),  # water_requirement as number
                        float(crop_row['investment_cost']),
                        float(risk_num)  # risk_level as number
                    ]], dtype=np.float64)
                
                # Predict ROI using ML model
                predicted_roi = float(self.model.predict(features)[0])
                
                # Calculate suitability score based on prediction and filters
                suitability = self._calculate_suitability(
                    predicted_roi, crop_row, soil_type, water_availability,
                    budget_level, risk_tolerance
                )
                
                # Water requirement is already text in the CSV
                water_text = crop_row['water_requirement']
                
                # Risk level is already text in the CSV
                risk_text = crop_row['risk_level']
                
                # Generate reasons
                reasons = []
                if crop_row['soil_preference'] == soil_type:
                    reasons.append(f"เหมาะมากกับ{soil_type}")
                elif soil_type:
                    reasons.append(f"ปลูกได้ใน{soil_type}")
                
                if predicted_roi > 200:
                    reasons.append("ผลตอบแทนสูง")
                elif predicted_roi > 100:
                    reasons.append("ผลตอบแทนดี")
                
                if risk_num < 0.3:
                    reasons.append("ความเสี่ยงต่ำ")
                
                # Calculate revenue from predicted ROI
                estimated_revenue = int(estimated_yield * (predicted_roi / 100) * 50)
                
                recommendations.append({
                    "crop_type": crop_name,
                    "suitability_score": round(suitability, 2),
                    "expected_yield_kg_per_rai": estimated_yield,
                    "estimated_revenue_per_rai": estimated_revenue,
                    "water_requirement": water_text,
                    "risk_level": risk_text,
                    "growth_days": int(crop_row['growth_days']),
                    "soil_preference": crop_row['soil_preference'],
                    "investment_cost": int(crop_row['investment_cost']),
                    "predicted_roi": round(predicted_roi, 2),
                    "reasons": reasons if reasons else ["เหมาะสมกับพื้นที่"]
                })
                
            except Exception as e:
                # Log full error for first crop only
                if len(errors) == 0:
                    import traceback
                    logger.error(f"Full error for {crop_name}:")
                    logger.error(traceback.format_exc())
                errors.append(f"{crop_name}: {str(e)[:80]}")
                continue
        
        # Log summary
        if errors:
            logger.warning(f"Errors in {len(errors)}/{len(crops_df)} crops. First 3: {errors[:3]}")
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # If no recommendations, use fallback
        if len(recommendations) == 0:
            logger.warning("⚠️ ML model produced no recommendations")
            return {
                "success": True,
                "recommendations": [],
                "message": "ไม่พบพืชที่เหมาะสมสำหรับเงื่อนไขนี้",
                "model_used": "model_a",
                "confidence": 0.0
            }
        
        return {
            "success": True,
            "recommendations": recommendations[:10],
            "model_used": f"ml_model_with_filtering ({self.model_path.name})",
            "confidence": 0.85
        }
    
    def _calculate_suitability(self, predicted_roi, crop_row, soil_type, 
                               water_availability, budget_level, risk_tolerance):
        """Calculate suitability score based on ML prediction and filters"""
        score = min(predicted_roi / 300, 1.0)  # Base score from ROI (max at 300%)
        
        # Soil match bonus
        if crop_row['soil_preference'] == soil_type:
            score += 0.1
        
        # Water match bonus
        water_mapping = {
            'น้ำฝน': [1, 2, 3],
            'น้ำบาดาล': [2, 3, 4],
            'ชลประทาน': [1, 2, 3, 4, 5],
            'แม่น้ำ/คลอง': [3, 4, 5]
        }
        
        if water_availability and water_availability in water_mapping:
            if crop_row['water_requirement'] in water_mapping[water_availability]:
                score += 0.05
        
        # Budget compatibility
        if budget_level:
            budget_ranges = {'ต่ำ': (0, 50000), 'ปานกลาง': (30000, 150000), 'สูง': (100000, float('inf'))}
            if budget_level in budget_ranges:
                min_b, max_b = budget_ranges[budget_level]
                if min_b <= crop_row['investment_cost'] <= max_b:
                    score += 0.05
        
        # Risk compatibility
        if risk_tolerance:
            risk_ranges = {'ต่ำ': (0, 0.3), 'ปานกลาง': (0.2, 0.7), 'สูง': (0.5, 1.0)}
            if risk_tolerance in risk_ranges:
                min_r, max_r = risk_ranges[risk_tolerance]
                # Convert risk_level to number if it's a string
                risk_val = crop_row['risk_level']
                if isinstance(risk_val, str):
                    risk_map = {'ต่ำมาก': 0.1, 'ต่ำ': 0.3, 'กลาง': 0.5, 'ปานกลาง': 0.5, 'สูง': 0.7, 'สูงมาก': 0.9}
                    risk_val = risk_map.get(risk_val, 0.5)
                if min_r <= risk_val <= max_r:
                    score += 0.05
        
        return max(0.1, min(1.0, score))
    



# Global instance
model_a_wrapper = ModelAWrapper()

logger.info("📦 Model A Wrapper loaded")

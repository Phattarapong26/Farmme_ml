# -*- coding: utf-8 -*-
"""
Production-Ready Planting Calendar Model Service
Uses the actual planting_calendar_modelUpdate.pkl model
Compatible with planplantfarmmeml_complete.py training script
"""

import logging
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path
import warnings

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)

class PlantingCalendarModelService:
    """Production service for planting calendar predictions using the actual ML model"""
    
    def __init__(self):
        self.model = None
        # Use absolute path from the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(backend_dir, "models", "planting_calendar_modelUpdate.pkl")
        self.dataset_path = os.path.join(backend_dir, "models", "farmme_77_provinces_dataset.csv")
        self.provinces_data = None
        self.model_loaded = False
        
        # Load model and data
        self._load_model()
        self._load_dataset()
        
        logger.info("✅ Planting Calendar Model Service initialized")
    
    def _load_model(self):
        """Load the planting calendar ML model"""
        try:
            if os.path.exists(self.model_path):
                # Try different pickle protocols
                try:
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    self.model_loaded = True
                    logger.info(f"✅ Planting calendar model loaded from {self.model_path}")
                except (pickle.UnpicklingError, ValueError) as e:
                    logger.warning(f"⚠️ Pickle loading failed with standard method: {e}")
                    # Try with different encoding
                    try:
                        import joblib
                        self.model = joblib.load(self.model_path)
                        self.model_loaded = True
                        logger.info(f"✅ Planting calendar model loaded using joblib from {self.model_path}")
                    except Exception as e2:
                        logger.warning(f"⚠️ Joblib loading also failed: {e2}")
                        self.model_loaded = False
            else:
                logger.warning(f"⚠️ Model file not found: {self.model_path}")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Failed to load planting calendar model: {e}")
            self.model_loaded = False
    
    def _load_dataset(self):
        """Load the provinces dataset for reference"""
        try:
            if os.path.exists(self.dataset_path):
                self.provinces_data = pd.read_csv(self.dataset_path)
                logger.info(f"✅ Provinces dataset loaded: {len(self.provinces_data)} records")
            else:
                logger.warning(f"⚠️ Dataset file not found: {self.dataset_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load provinces dataset: {e}")
    
    def get_available_provinces(self) -> List[str]:
        """Get list of available provinces from the dataset"""
        try:
            if self.provinces_data is not None and 'province' in self.provinces_data.columns:
                provinces = self.provinces_data['province'].unique().tolist()
                return sorted(provinces)
            else:
                # Fallback to common Thai provinces
                return [
                   
                ]
        except Exception as e:
            logger.error(f"Error getting provinces: {e}")
            return ["เชียงใหม่", "กรุงเทพมหานคร", "นครราชสีมา"]
    
    def get_provinces_for_crop(self, crop_type: str) -> List[str]:
        """Get list of provinces that have a specific crop in the dataset"""
        try:
            if self.provinces_data is not None and 'province' in self.provinces_data.columns and 'crop_type' in self.provinces_data.columns:
                # Filter dataset for this crop
                crop_data = self.provinces_data[self.provinces_data['crop_type'] == crop_type]
                if len(crop_data) > 0:
                    provinces = crop_data['province'].unique().tolist()
                    logger.info(f"Found {len(provinces)} provinces for crop '{crop_type}'")
                    return sorted(provinces)
                else:
                    logger.warning(f"No provinces found for crop '{crop_type}'")
                    return []
            else:
                logger.warning("Dataset not available for province filtering")
                return self.get_available_provinces()
        except Exception as e:
            logger.error(f"Error getting provinces for crop '{crop_type}': {e}")
            return self.get_available_provinces()
    
    def get_available_crops(self) -> List[Dict[str, Any]]:
        """Get list of available crops with their characteristics"""
        try:
            if self.provinces_data is not None and 'crop_type' in self.provinces_data.columns:
                crops_info = []
                unique_crops = self.provinces_data['crop_type'].unique()
                
                for crop in unique_crops:
                    crop_data = self.provinces_data[self.provinces_data['crop_type'] == crop].iloc[0]
                    crops_info.append({
                        "name": crop,
                        "crop_type": crop,
                        "growth_days": int(crop_data.get('growth_days', 90)),
                        "category": self._get_crop_category(crop),
                        "water_requirement": self._get_water_requirement(crop),
                        "soil_type": "ดินร่วน",
                        "season": "ตลอดปี"
                    })
                
                return sorted(crops_info, key=lambda x: x['name'])
            else:
                # Fallback crop data
                return [
                    
                ]
        except Exception as e:
            logger.error(f"Error getting crops: {e}")
            return []
    
    def predict_planting_schedule(
        self,
        province: str,
        crop_type: str,
        growth_days: int = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Predict optimal planting schedule using the ML model
        """
        try:
            if not self.model_loaded:
                logger.error("❌ Model B not loaded")
                return {
                    "success": False,
                    "error": "MODEL_NOT_LOADED",
                    "message": "Model B ยังไม่พร้อมใช้งาน กรุณาติดต่อผู้ดูแลระบบ",
                    "recommendations": []
                }
            
            # Auto-fill growth_days if not provided
            if growth_days is None:
                growth_days = self._get_growth_days(crop_type)
            
            # Set date range if not provided
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=365)
            
            recommendations = []
            current_date = start_date
            
            # ✅ FIXED: Generate predictions for different planting dates (monthly for better variation)
            # Check monthly instead of weekly to get more diverse dates
            while current_date <= end_date and len(recommendations) < top_n * 2:
                try:
                    # Prepare features for the model
                    features = self._prepare_features(province, crop_type, current_date, growth_days)
                    
                    if features is not None:
                        # Make prediction using the actual model
                        prediction = self._make_model_prediction(features, crop_type)
                        
                        if prediction is not None:
                            harvest_date = current_date + timedelta(days=growth_days)
                            
                            recommendations.append({
                                "planting_date": current_date.strftime("%Y-%m-%d"),
                                "harvest_date": harvest_date.strftime("%Y-%m-%d"),
                                "predicted_price": prediction.get('price', 25.0),
                                "confidence": prediction.get('confidence', 0.8),
                                "risk_score": prediction.get('risk_score', 0.2),
                                "weather_suitability": prediction.get('weather_suitability', 0.8),
                                "market_timing": prediction.get('market_timing', 0.7),
                                "total_score": prediction.get('total_score', 0.75),
                                "recommendation": self._generate_recommendation(prediction),
                                "season": self._get_season_name(current_date.month),
                                "rainfall": self._get_seasonal_rainfall(current_date.month)
                            })
                
                except Exception as e:
                    logger.warning(f"Error predicting for date {current_date}: {e}")
                
                current_date += timedelta(days=30)  # ✅ FIXED: Check monthly for better date diversity
            
            # ✅ FIXED: Sort by total score and take top N (now with more diverse dates)
            recommendations.sort(key=lambda x: x.get('total_score', 0), reverse=True)
            recommendations = recommendations[:top_n]
            
            # Calculate statistics
            if recommendations:
                prices = [r['predicted_price'] for r in recommendations]
                statistics = {
                    "max_price": max(prices),
                    "min_price": min(prices),
                    "avg_price": sum(prices) / len(prices),
                    "total_dates_analyzed": len(recommendations)
                }
            else:
                statistics = {"max_price": 0, "min_price": 0, "avg_price": 0, "total_dates_analyzed": 0}
            
            return {
                "success": True,
                "province": province,
                "crop_type": crop_type,
                "growth_days": growth_days,
                "recommendations": recommendations,
                "statistics": statistics,
                "model_used": "planting_calendar_ml_model",
                "model_version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in predict_planting_schedule: {e}", exc_info=True)
            return {
                "success": False,
                "error": "PREDICTION_FAILED",
                "message": f"ไม่สามารถทำนายตารางปลูกได้: {str(e)}",
                "recommendations": []
            }
    
    def _prepare_features(self, province: str, crop_type: str, planting_date: datetime, growth_days: int) -> Optional[np.ndarray]:
        """Prepare features for the ML model (compatible with planplantfarmmeml_complete.py)"""
        try:
            if not isinstance(self.model, dict) or 'preprocessor' not in self.model:
                logger.error("❌ Model preprocessor not found")
                return None
            
            preprocessor = self.model['preprocessor']
            scaler = preprocessor.get('scaler')
            onehot_encoder = preprocessor.get('onehot_encoder')
            numeric_features = preprocessor.get('numeric_features', [])
            categorical_features = preprocessor.get('categorical_features', [])
            
            if not scaler or not onehot_encoder:
                logger.error("❌ Scaler or encoder not found")
                return None
            
            # Get region from province
            region = self._get_region_from_province(province)
            
            # Prepare base data matching training script structure
            # ✅ FIXED: Use dynamic values based on planting_date for variation
            base_data = {
                'month': planting_date.month,
                'day_of_year': planting_date.timetuple().tm_yday,
                'week_of_year': planting_date.isocalendar().week,
                'temperature_celsius': self._get_seasonal_temperature(planting_date.month),  # Dynamic temperature
                'rainfall_mm': self._get_seasonal_rainfall(planting_date.month),  # Already dynamic
                'humidity_percent': self._get_seasonal_humidity(planting_date.month),  # Dynamic humidity
                'is_rainy_season': 1 if planting_date.month in [6, 7, 8, 9, 10] else 0,
                'is_winter': 1 if planting_date.month in [11, 12, 1, 2] else 0,
                'growth_days': growth_days,
                'planting_area_rai': 5.0,  # Default value
                'crop_type': crop_type,
                'region': region,
                'crop_category': self._get_crop_category(crop_type),
                'water_requirement': self._get_water_requirement(crop_type)
            }
            
            # Create DataFrame for consistent processing
            input_df = pd.DataFrame([base_data])
            
            # Prepare numeric features
            numeric_data = []
            for feature in numeric_features:
                if feature in input_df.columns:
                    numeric_data.append(input_df[feature].iloc[0])
                else:
                    # Provide default values for missing features
                    default_values = {
                        'month': planting_date.month,
                        'day_of_year': planting_date.timetuple().tm_yday,
                        'week_of_year': planting_date.isocalendar().week,
                        'temperature_celsius': 28.0,
                        'rainfall_mm': 100.0,
                        'humidity_percent': 70.0,
                        'is_rainy_season': 0,
                        'is_winter': 0,
                        'growth_days': growth_days,
                        'planting_area_rai': 5.0
                    }
                    numeric_data.append(default_values.get(feature, 0.0))
            
            # Scale numeric features
            numeric_array = np.array(numeric_data).reshape(1, -1)
            numeric_scaled = scaler.transform(numeric_array)
            
            # Prepare categorical features
            categorical_data = []
            for feature in categorical_features:
                if feature in input_df.columns:
                    categorical_data.append(input_df[feature].iloc[0])
                else:
                    # Provide default values for missing categorical features
                    default_values = {
                        'crop_type': crop_type,
                        'region': region,
                        'crop_category': 'ผักใบ',
                        'water_requirement': 'ปานกลาง'
                    }
                    categorical_data.append(default_values.get(feature, 'Unknown'))
            
            # Encode categorical features
            categorical_df = pd.DataFrame([dict(zip(categorical_features, categorical_data))])
            categorical_encoded = onehot_encoder.transform(categorical_df)
            
            # Combine features
            features = np.hstack([numeric_scaled, categorical_encoded])
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error preparing features: {e}", exc_info=True)
            return None
    
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
    
    def _make_model_prediction(self, features: np.ndarray, crop_type: str) -> Optional[Dict[str, Any]]:
        """Make prediction using the loaded ML model (compatible with planplantfarmmeml_complete.py)"""
        try:
            if self.model is None:
                return None
            
            # Handle dictionary model structure from planplantfarmmeml_complete.py
            if isinstance(self.model, dict):
                if 'best_model' in self.model:
                    actual_model = self.model['best_model']
                    preprocessor = self.model.get('preprocessor', {})
                    
                    # Make prediction using the actual model
                    if hasattr(actual_model, 'predict'):
                        # The model predicts suitability score (0-100)
                        suitability_score = actual_model.predict(features)[0]
                        
                        # Convert suitability score to price using realistic mapping
                        # Higher suitability = better timing = higher price
                        # ✅ FIXED: Use crop-specific base price instead of fixed 50.0
                        base_price = self._get_base_price(crop_type)
                        price_multiplier = 0.5 + (suitability_score / 100.0) * 1.5  # 0.5x to 2.0x
                        predicted_price = base_price * price_multiplier
                        
                        # Calculate confidence based on model performance
                        model_performance = self.model.get('performance', {})
                        base_confidence = model_performance.get('cv_mean', 0.8)
                        confidence = min(0.95, max(0.6, base_confidence))
                        
                        # Calculate risk score (inverse of suitability)
                        risk_score = max(0.1, min(0.9, 1.0 - (suitability_score / 100.0)))
                        
                        # Calculate total score
                        total_score = (suitability_score / 100.0) * confidence
                        
                        return {
                            'price': round(predicted_price, 2),
                            'suitability_score': round(suitability_score, 2),
                            'confidence': round(confidence, 3),
                            'risk_score': round(risk_score, 3),
                            'total_score': round(total_score, 3),
                            'weather_suitability': min(1.0, suitability_score / 80.0),
                            'market_timing': min(1.0, suitability_score / 90.0)
                        }
                    else:
                        logger.warning("Best model doesn't have predict method")
                        return None
                else:
                    logger.warning("Model dictionary doesn't contain 'best_model'")
                    return None
            else:
                # Handle direct model object (fallback)
                if hasattr(self.model, 'predict'):
                    prediction = self.model.predict(features)[0]
                    price = float(prediction) if prediction > 0 else 25.0
                    return {
                        'price': price,
                        'suitability_score': 50.0,
                        'confidence': 0.8,
                        'risk_score': 0.2,
                        'total_score': 0.75,
                        'weather_suitability': 0.8,
                        'market_timing': 0.7
                    }
                else:
                    logger.warning("Model doesn't have predict method")
                    return None
                
        except Exception as e:
            logger.error(f"Error making model prediction: {e}")
            return None
    

    def _get_crop_category(self, crop_type: str) -> str:
        """Get crop category"""
        categories = {
            'ข่า': 'สมุนไพร', 'ขมิ้นชัน': 'สมุนไพร', 'มะกรูด': 'สมุนไพร', 'กระชาย': 'สมุนไพร',
            'คะน้า': 'ผักใบ', 'กวางตุ้ง': 'ผักใบ', 'ผักบุ้ง': 'ผักใบ', 'ผักสลัด': 'ผักใบ',
            'พริก': 'ผักผล', 'มะเขือเทศ': 'ผักผล', 'มะเขือพวง': 'ผักผล', 'บวบ': 'ผักผล',
            'กะหล่ำปลี': 'ผักตระกูลกะหล่ำ', 'บรอกโคลี': 'ผักตระกูลกะหล่ำ',
            'แครอท': 'ผักหัว', 'หัวไชเท้า': 'ผักหัว', 'หอมแดง': 'ผักหัว'
        }
        return categories.get(crop_type, 'ผักอื่นๆ')
    
    def _get_water_requirement(self, crop_type: str) -> str:
        """Get water requirement for crop"""
        requirements = {
            'ข่า': 'น้อย', 'ขมิ้นชัน': 'ปานกลาง', 'มะกรูด': 'ปานกลาง', 'กระชาย': 'น้อย',
            'คะน้า': 'มาก', 'กวางตุ้ง': 'มาก', 'ผักบุ้ง': 'มาก', 'ผักสลัด': 'มาก',
            'พริก': 'ปานกลาง', 'มะเขือเทศ': 'มาก', 'มะเขือพวง': 'ปานกลาง', 'บวบ': 'มาก',
            'กะหล่ำปลี': 'มาก', 'บรอกโคลี': 'มาก',
            'แครอท': 'น้อย', 'หัวไชเท้า': 'ปานกลาง', 'หอมแดง': 'น้อย'
        }
        return requirements.get(crop_type, 'ปานกลาง')
    
    def _get_growth_days(self, crop_type: str) -> int:
        """Get growth days for crop"""
        growth_days_map = {
            'ข่า': 180, 'ขมิ้นชัน': 210, 'มะกรูด': 365, 'กระชาย': 150,
            'คะน้า': 45, 'กวางตุ้ง': 30, 'ผักบุ้ง': 25, 'ผักสลัด': 35,
            'พริก': 75, 'มะเขือเทศ': 55, 'มะเขือพวง': 60, 'บวบ': 50,
            'กะหล่ำปลี': 70, 'บรอกโคลี': 65,
            'แครอท': 90, 'หัวไชเท้า': 60, 'หอมแดง': 120
        }
        return growth_days_map.get(crop_type, 90)
    
    def _get_base_price(self, crop_type: str) -> float:
        """Get base price for crop"""
        prices = {
            'ข่า': 120, 'ขมิ้นชัน': 80, 'มะกรูด': 150, 'กระชาย': 100,
            'คะน้า': 25, 'กวางตุ้ง': 30, 'ผักบุ้ง': 20, 'ผักสลัด': 35,
            'พริก': 60, 'มะเขือเทศ': 40, 'มะเขือพวง': 35, 'บวบ': 30,
            'กะหล่ำปลี': 45, 'บรอกโคลี': 55,
            'แครอท': 50, 'หัวไชเท้า': 35, 'หอมแดง': 70
        }
        return prices.get(crop_type, 50.0)
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal price factor"""
        factors = {
            1: 1.1, 2: 1.15, 3: 1.2, 4: 1.1,
            5: 0.9, 6: 0.85, 7: 0.8, 8: 0.85,
            9: 0.9, 10: 1.0, 11: 1.05, 12: 1.1
        }
        return factors.get(month, 1.0)
    
    def _get_season_name(self, month: int) -> str:
        """Get season name from month"""
        if month in [3, 4, 5]:
            return "ฤดูร้อน"
        elif month in [6, 7, 8, 9, 10]:
            return "ฤดูฝน"
        else:
            return "ฤดูหนาว"
    
    def _get_season_code(self, month: int) -> int:
        """Get season code for model features"""
        if month in [3, 4, 5]:
            return 1  # Hot season
        elif month in [6, 7, 8, 9, 10]:
            return 2  # Rainy season
        else:
            return 3  # Cool season
    
    def _get_seasonal_rainfall(self, month: int) -> float:
        """Get seasonal rainfall data based on Thai climate patterns"""
        # Thai rainfall patterns (mm/month average)
        rainfall_patterns = {
            1: 15.0,   # มกราคม - ฤดูหนาว (แห้ง)
            2: 25.0,   # กุมภาพันธ์ - ฤดูหนาว (แห้ง)
            3: 40.0,   # มีนาคม - ฤดูร้อน (เริ่มฝน)
            4: 80.0,   # เมษายน - ฤดูร้อน (ฝนเล็กน้อย)
            5: 150.0,  # พฤษภาคม - เริ่มฤดูฝน
            6: 180.0,  # มิถุนายน - ฤดูฝน
            7: 200.0,  # กรกฎาคม - ฤดูฝนหนัก
            8: 220.0,  # สิงหาคม - ฤดูฝนหนัก
            9: 250.0,  # กันยายน - ฤดูฝนหนักสุด
            10: 180.0, # ตุลาคม - ฤดูฝนลดลง
            11: 60.0,  # พฤศจิกายน - หลังฤดูฝน
            12: 20.0   # ธันวาคม - ฤดูหนาว (แห้ง)
        }
        return rainfall_patterns.get(month, 100.0)
    
    def _get_seasonal_temperature(self, month: int) -> float:
        """Get seasonal temperature data based on Thai climate patterns"""
        # Thai temperature patterns (Celsius average)
        temperature_patterns = {
            1: 26.0,   # มกราคม - ฤดูหนาว (เย็น)
            2: 28.0,   # กุมภาพันธ์ - ฤดูหนาว (เริ่มร้อน)
            3: 30.0,   # มีนาคม - ฤดูร้อน
            4: 32.0,   # เมษายน - ฤดูร้อน (ร้อนสุด)
            5: 31.0,   # พฤษภาคม - ฤดูร้อน
            6: 29.0,   # มิถุนายน - ฤดูฝน (เย็นลง)
            7: 28.5,   # กรกฎาคม - ฤดูฝน
            8: 28.5,   # สิงหาคม - ฤดูฝน
            9: 28.0,   # กันยายน - ฤดูฝน
            10: 28.0,  # ตุลาคม - หลังฤดูฝน
            11: 27.0,  # พฤศจิกายน - ฤดูหนาว
            12: 26.0   # ธันวาคม - ฤดูหนาว (เย็น)
        }
        return temperature_patterns.get(month, 28.0)
    
    def _get_seasonal_humidity(self, month: int) -> float:
        """Get seasonal humidity data based on Thai climate patterns"""
        # Thai humidity patterns (percent average)
        humidity_patterns = {
            1: 65.0,   # มกราคม - ฤดูหนาว (แห้ง)
            2: 65.0,   # กุมภาพันธ์ - ฤดูหนาว
            3: 68.0,   # มีนาคม - ฤดูร้อน
            4: 70.0,   # เมษายน - ฤดูร้อน
            5: 75.0,   # พฤษภาคม - เริ่มฤดูฝน
            6: 78.0,   # มิถุนายน - ฤดูฝน
            7: 80.0,   # กรกฎาคม - ฤดูฝน (ชื้นสุด)
            8: 80.0,   # สิงหาคม - ฤดูฝน
            9: 82.0,   # กันยายน - ฤดูฝน (ชื้นสุด)
            10: 78.0,  # ตุลาคม - หลังฤดูฝน
            11: 72.0,  # พฤศจิกายน - ฤดูหนาว
            12: 68.0   # ธันวาคม - ฤดูหนาว
        }
        return humidity_patterns.get(month, 70.0)
    
    def _generate_recommendation(self, prediction: Dict[str, Any]) -> str:
        """Generate recommendation text based on prediction"""
        score = prediction.get('total_score', 0.5)
        price = prediction.get('price', 25.0)
        
        if score >= 0.8:
            return f"แนะนำอย่างยิ่ง - คาดการณ์ราคา {price:.1f} ฿/กก."
        elif score >= 0.6:
            return f"แนะนำ - คาดการณ์ราคา {price:.1f} ฿/กก."
        elif score >= 0.4:
            return f"พอใช้ - คาดการณ์ราคา {price:.1f} ฿/กก."
        else:
            return f"ไม่แนะนำ - คาดการณ์ราคา {price:.1f} ฿/กก."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "planting_calendar_model_service",
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
            "dataset_path": self.dataset_path,
            "dataset_loaded": self.provinces_data is not None,
            "dataset_records": len(self.provinces_data) if self.provinces_data is not None else 0,
            "available_provinces": len(self.get_available_provinces()),
            "available_crops": len(self.get_available_crops()),
            "version": "1.0.0",
            "status": "active" if self.model_loaded else "fallback"
        }

# Global planting model service instance
planting_model_service = PlantingCalendarModelService()

logger.info("📦 Planting Calendar Model Service loaded successfully")
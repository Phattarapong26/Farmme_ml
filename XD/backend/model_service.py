# -*- coding: utf-8 -*-
"""
Legacy Model Service for Farmme API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class ModelService:
    """Legacy model service for ML predictions"""
    
    def __init__(self):
        logger.info("✅ Legacy Model Service initialized")
    
    def predict_price(
        self,
        province: str,
        crop_type: str,
        crop_category: str = None,
        month: int = None,
        year: int = None,
        temperature_celsius: float = 28.0,
        rainfall_mm: float = 100.0,
        planting_area_rai: float = 10.0,
        expected_yield_kg: float = 5000.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy price prediction method
        """
        try:
            # Mock price calculation based on inputs
            base_price = self._get_base_price(crop_type)
            
            # Weather factor
            weather_factor = 1.0
            if temperature_celsius > 35:
                weather_factor *= 0.9  # Too hot reduces price
            elif temperature_celsius < 20:
                weather_factor *= 0.95  # Too cold reduces price
            
            if rainfall_mm > 200:
                weather_factor *= 0.85  # Too much rain reduces price
            elif rainfall_mm < 50:
                weather_factor *= 0.9   # Too little rain reduces price
            
            # Seasonal factor
            seasonal_factor = self._get_seasonal_factor(month or datetime.now().month)
            
            # Area and yield factor
            yield_per_rai = expected_yield_kg / planting_area_rai if planting_area_rai > 0 else 500
            yield_factor = min(1.2, max(0.8, yield_per_rai / 500))  # Normalize around 500kg/rai
            
            # Calculate final price
            predicted_price = base_price * weather_factor * seasonal_factor * yield_factor
            
            # Add deterministic variation based on date (no randomness)
            date_variation = np.sin(2 * np.pi * (month or datetime.now().month) / 12) * 0.03
            predicted_price *= (1 + date_variation)
            
            return {
                "success": True,
                "predicted_price": round(predicted_price, 2),
                "confidence": 0.75,
                "factors": {
                    "base_price": base_price,
                    "weather_factor": weather_factor,
                    "seasonal_factor": seasonal_factor,
                    "yield_factor": yield_factor
                }
            }
            
        except Exception as e:
            logger.error(f"Legacy price prediction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "predicted_price": None
            }
    
    def predict_price_forecast(
        self,
        province: str,
        crop_type: str,
        crop_category: str = None,
        days_ahead: int = 180,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy price forecast method
        """
        try:
            base_price = self._get_base_price(crop_type)
            forecast = []
            
            for i in range(days_ahead):
                date = datetime.now() + timedelta(days=i+1)
                
                # Seasonal trend
                seasonal_factor = self._get_seasonal_factor(date.month)
                
                # Deterministic trend with seasonal variation
                trend = 1 + (i / days_ahead) * 0.1  # Slight upward trend
                day_variation = np.sin(2 * np.pi * date.timetuple().tm_yday / 365) * 0.02
                
                price = base_price * seasonal_factor * trend * (1 + day_variation)
                
                forecast.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_price": round(price, 2)
                })
            
            return {
                "success": True,
                "forecast": forecast,
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Legacy price forecast failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "forecast": []
            }
    
    def recommend_best_planting_dates(
        self,
        province: str,
        crop_type: str,
        growth_days: int = 90,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        top_n: int = 5,
        min_price_threshold: float = 10.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy planting date recommendation
        """
        try:
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=365)
            
            recommendations = []
            current_date = start_date
            
            while current_date <= end_date and len(recommendations) < top_n * 2:
                harvest_date = current_date + timedelta(days=growth_days)
                
                # Calculate expected price at harvest
                seasonal_factor = self._get_seasonal_factor(harvest_date.month)
                base_price = self._get_base_price(crop_type)
                expected_price = base_price * seasonal_factor
                
                if expected_price >= min_price_threshold:
                    recommendations.append({
                        "planting_date": current_date.strftime("%Y-%m-%d"),
                        "harvest_date": harvest_date.strftime("%Y-%m-%d"),
                        "expected_price": round(expected_price, 2),
                        "confidence": 0.7,
                        "season": self._get_season_name(current_date.month)
                    })
                
                current_date += timedelta(days=7)  # Check weekly
            
            # Sort by expected price and take top N
            recommendations.sort(key=lambda x: x["expected_price"], reverse=True)
            recommendations = recommendations[:top_n]
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_evaluated": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Legacy planting date recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def recommend_crop_by_profile(
        self,
        water_availability: str = "ปานกลาง",
        budget_level: str = "กลาง",
        risk_tolerance: str = "กลาง",
        preference: str = "ผักใบ",
        experience_crops: List[str] = None,
        time_constraint: int = 90,
        top_n: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy crop recommendation by profile
        """
        try:
            if experience_crops is None:
                experience_crops = []
            
            # Mock crop database
            crops = [
                {"name": "คะน้า", "category": "ผักใบ", "growth_days": 45, "difficulty": "ง่าย", "water_need": "ปานกลาง", "profit": 8000},
                {"name": "ผักบุ้ง", "category": "ผักใบ", "growth_days": 25, "difficulty": "ง่าย", "water_need": "มาก", "profit": 6000},
                {"name": "พริก", "category": "ผักผล", "growth_days": 75, "difficulty": "ปานกลาง", "water_need": "ปานกลาง", "profit": 12000},
                {"name": "มะเขือเทศ", "category": "ผักผล", "growth_days": 55, "difficulty": "ปานกลาง", "water_need": "ปานกลาง", "profit": 10000},
                {"name": "แครอท", "category": "ผักหัว", "growth_days": 90, "difficulty": "ปานกลาง", "water_need": "น้อย", "profit": 9000},
                {"name": "ข่า", "category": "สมุนไพร", "growth_days": 180, "difficulty": "ยาก", "water_need": "ปานกลาง", "profit": 15000},
            ]
            
            recommendations = []
            
            for crop in crops:
                score = 0
                
                # Time constraint matching
                if crop["growth_days"] <= time_constraint:
                    score += 30
                
                # Category preference matching
                if crop["category"] == preference:
                    score += 25
                
                # Water availability matching
                if crop["water_need"] == water_availability:
                    score += 20
                
                # Experience bonus
                if crop["name"] in experience_crops:
                    score += 15
                
                # Risk tolerance matching
                if risk_tolerance == "สูง" and crop["profit"] > 10000:
                    score += 10
                elif risk_tolerance == "ต่ำ" and crop["difficulty"] == "ง่าย":
                    score += 10
                
                if score > 0:
                    recommendations.append({
                        "crop_name": crop["name"],
                        "category": crop["category"],
                        "growth_days": crop["growth_days"],
                        "expected_profit": crop["profit"],
                        "difficulty": crop["difficulty"],
                        "score": score,
                        "confidence": min(0.9, score / 100)
                    })
            
            # Sort by score and take top N
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            recommendations = recommendations[:top_n]
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_evaluated": len(crops)
            }
            
        except Exception as e:
            logger.error(f"Legacy crop recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def _get_base_price(self, crop_type: str) -> float:
        """Get base price for crop type"""
        prices = {
            'ข่า': 120, 'ขมิ้นชัน': 80, 'มะกรูด': 150, 'กระชาย': 100,
            'คะน้า': 25, 'กวางตุ้ง': 30, 'ผักบุ้ง': 20, 'ผักสลัด': 35,
            'พริก': 60, 'มะเขือเทศ': 40, 'มะเขือพวง': 35, 'บวบ': 30,
            'กะหล่ำปลี': 45, 'บรอกโคลี': 55,
            'แครอท': 50, 'หัวไชเท้า': 35, 'หอมแดง': 70,
            'ข้าวโพดเลี้ยงสัตว์': 15, 'มันสำปะหลัง': 8, 'อ้อย': 12,
            'ลำไย': 80, 'สับปะรด': 25
        }
        return prices.get(crop_type, 50.0)
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal price factor"""
        # Mock seasonal factors (higher in off-season)
        factors = {
            1: 1.1, 2: 1.15, 3: 1.2, 4: 1.1,  # Hot season - higher prices
            5: 0.9, 6: 0.85, 7: 0.8, 8: 0.85,  # Rainy season - lower prices
            9: 0.9, 10: 1.0, 11: 1.05, 12: 1.1  # Cool season - moderate prices
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "legacy_model_service",
            "version": "1.0.0",
            "capabilities": [
                "price_prediction",
                "price_forecast", 
                "planting_date_recommendation",
                "crop_recommendation"
            ],
            "status": "active"
        }

logger.info("📦 Legacy Model Service loaded successfully")
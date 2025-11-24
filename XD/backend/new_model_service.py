# -*- coding: utf-8 -*-
"""
New Model Service for Farmme API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class NewModelService:
    """New advanced model service for ML predictions"""
    
    def __init__(self):
        logger.warning("⚠️ New Model Service initialized - NO REAL ML MODEL")
        logger.warning("⚠️ This service uses MOCK DATA and FORMULAS only")
        logger.warning("⚠️ Results are NOT from trained ML models")
    
    def predict_price_new(
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
        New advanced price prediction method
        """
        try:
            # Enhanced price calculation with more factors
            base_price = self._get_base_price_enhanced(crop_type, province)
            
            # Advanced weather modeling
            weather_score = self._calculate_weather_score(temperature_celsius, rainfall_mm, crop_type)
            
            # Market demand factor
            market_factor = self._get_market_demand_factor(crop_type, month or datetime.now().month)
            
            # Supply chain factor
            supply_factor = self._get_supply_chain_factor(province, crop_type)
            
            # Quality factor based on growing conditions
            quality_factor = self._calculate_quality_factor(temperature_celsius, rainfall_mm, crop_type)
            
            # Calculate final price with advanced modeling
            predicted_price = (
                base_price * 
                weather_score * 
                market_factor * 
                supply_factor * 
                quality_factor
            )
            
            # Add deterministic variation based on date (no randomness)
            date_variation = np.sin(2 * np.pi * (month or datetime.now().month) / 12) * 0.02
            predicted_price *= (1 + date_variation)
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(
                weather_score, market_factor, supply_factor, quality_factor
            )
            
            return {
                "success": True,
                "predicted_price": round(predicted_price, 2),
                "confidence": confidence,
                "factors": {
                    "base_price": base_price,
                    "weather_score": weather_score,
                    "market_factor": market_factor,
                    "supply_factor": supply_factor,
                    "quality_factor": quality_factor
                },
                "model_version": "2.0.0",
                "warning": "⚠️ ข้อมูลนี้มาจาก FORMULA ไม่ใช่ ML Model จริง - ใช้เพื่ออ้างอิงเท่านั้น"
            }
            
        except Exception as e:
            logger.error(f"New price prediction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "predicted_price": None
            }
    
    def predict_price_forecast_new(
        self,
        province: str,
        crop_type: str,
        days_ahead: int = 180,
        **kwargs
    ) -> Dict[str, Any]:
        """
        New advanced price forecast method
        """
        try:
            base_price = self._get_base_price_enhanced(crop_type, province)
            forecast = []
            
            # Advanced forecasting with multiple trends
            for i in range(days_ahead):
                date = datetime.now() + timedelta(days=i+1)
                
                # Seasonal trend with harmonics
                seasonal_factor = self._get_advanced_seasonal_factor(date.month, date.day)
                
                # Market cycle trend
                market_cycle = self._get_market_cycle_factor(i, days_ahead)
                
                # Economic trend
                economic_trend = 1 + (i / days_ahead) * 0.05  # Gradual increase
                
                # Deterministic weather variation based on day of year
                weather_variation = np.sin(2 * np.pi * date.timetuple().tm_yday / 365) * 0.015
                
                # Supply-demand dynamics
                supply_demand = self._get_supply_demand_dynamics(date, crop_type)
                
                price = (
                    base_price * 
                    seasonal_factor * 
                    market_cycle * 
                    economic_trend * 
                    (1 + weather_variation) * 
                    supply_demand
                )
                
                # Calculate prediction interval
                std_dev = price * 0.1  # 10% standard deviation
                lower_bound = price - 1.96 * std_dev
                upper_bound = price + 1.96 * std_dev
                
                forecast.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_price": round(price, 2),
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                    "confidence": max(0.5, 0.9 - (i / days_ahead) * 0.3)  # Decreasing confidence
                })
            
            return {
                "success": True,
                "forecast": forecast,
                "model_version": "2.0.0",
                "forecast_quality": "high"
            }
            
        except Exception as e:
            logger.error(f"New price forecast failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "forecast": []
            }
    
    def recommend_planting_dates_new(
        self,
        province: str,
        crop_type: str,
        growth_days: int = 90,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        top_n: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        New advanced planting date recommendation
        """
        try:
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=365)
            
            recommendations = []
            current_date = start_date
            
            while current_date <= end_date:
                harvest_date = current_date + timedelta(days=growth_days)
                
                # Advanced scoring system
                weather_suitability = self._calculate_planting_weather_score(current_date, crop_type)
                market_timing_score = self._calculate_market_timing_score(harvest_date, crop_type)
                risk_score = self._calculate_planting_risk_score(current_date, harvest_date, crop_type)
                
                # Combined score
                total_score = (
                    weather_suitability * 0.4 +
                    market_timing_score * 0.4 +
                    risk_score * 0.2
                )
                
                if total_score > 0.6:  # Only recommend good options
                    expected_price = self._get_base_price_enhanced(crop_type, province)
                    expected_price *= self._get_advanced_seasonal_factor(harvest_date.month, harvest_date.day)
                    
                    recommendations.append({
                        "planting_date": current_date.strftime("%Y-%m-%d"),
                        "harvest_date": harvest_date.strftime("%Y-%m-%d"),
                        "expected_price": round(expected_price, 2),
                        "total_score": round(total_score, 3),
                        "weather_suitability": round(weather_suitability, 3),
                        "market_timing": round(market_timing_score, 3),
                        "risk_score": round(risk_score, 3),
                        "confidence": min(0.95, total_score),
                        "season": self._get_season_name(current_date.month)
                    })
                
                current_date += timedelta(days=3)  # Check every 3 days for better precision
            
            # Sort by total score and take top N
            recommendations.sort(key=lambda x: x["total_score"], reverse=True)
            recommendations = recommendations[:top_n]
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_evaluated": len(recommendations),
                "model_version": "2.0.0"
            }
            
        except Exception as e:
            logger.error(f"New planting date recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def recommend_crops_new(
        self,
        province: str = "เชียงใหม่",
        water_availability: str = "ปานกลาง",
        budget_level: str = "กลาง",
        risk_tolerance: str = "กลาง",
        experience_level: str = "ปานกลาง",
        time_constraint: int = 90,
        soil_type: str = "ดินร่วน",
        preference: str = "ผักใบ",
        season: str = "หนาว",
        top_n: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        New advanced crop recommendation
        """
        try:
            # Enhanced crop database with more attributes
            crops = [
                {
                    "name": "คะน้า", "category": "ผักใบ", "growth_days": 45, "difficulty": "ง่าย",
                    "water_need": "ปานกลาง", "profit": 8000, "soil_types": ["ดินร่วน", "ดินเหนียว"],
                    "seasons": ["หนาว", "ฝน"], "investment": 5000, "market_demand": "สูง"
                },
                {
                    "name": "ผักบุ้ง", "category": "ผักใบ", "growth_days": 25, "difficulty": "ง่าย",
                    "water_need": "มาก", "profit": 6000, "soil_types": ["ดินร่วน"],
                    "seasons": ["ฝน"], "investment": 3000, "market_demand": "ปานกลาง"
                },
                {
                    "name": "พริก", "category": "ผักผล", "growth_days": 75, "difficulty": "ปานกลาง",
                    "water_need": "ปานกลาง", "profit": 12000, "soil_types": ["ดินร่วน", "ดินทราย"],
                    "seasons": ["ร้อน", "หนาว"], "investment": 8000, "market_demand": "สูง"
                },
                {
                    "name": "มะเขือเทศ", "category": "ผักผล", "growth_days": 55, "difficulty": "ปานกลาง",
                    "water_need": "ปานกลาง", "profit": 10000, "soil_types": ["ดินร่วน"],
                    "seasons": ["หนาว", "ร้อน"], "investment": 7000, "market_demand": "สูง"
                },
                {
                    "name": "แครอท", "category": "ผักหัว", "growth_days": 90, "difficulty": "ปานกลาง",
                    "water_need": "น้อย", "profit": 9000, "soil_types": ["ดินทราย", "ดินร่วน"],
                    "seasons": ["หนาว"], "investment": 6000, "market_demand": "ปานกลาง"
                },
                {
                    "name": "ข่า", "category": "สมุนไพร", "growth_days": 180, "difficulty": "ยาก",
                    "water_need": "ปานกลาง", "profit": 15000, "soil_types": ["ดินร่วน"],
                    "seasons": ["ฝน", "หนาว"], "investment": 10000, "market_demand": "สูง"
                },
            ]
            
            recommendations = []
            
            for crop in crops:
                score = 0
                factors = {}
                
                # Time constraint (30 points)
                if crop["growth_days"] <= time_constraint:
                    time_score = 30 * (1 - (crop["growth_days"] / time_constraint) * 0.5)
                    score += time_score
                    factors["time_match"] = time_score
                
                # Category preference (25 points)
                if crop["category"] == preference:
                    score += 25
                    factors["category_match"] = 25
                
                # Water availability (20 points)
                water_match = self._calculate_water_match(crop["water_need"], water_availability)
                score += water_match
                factors["water_match"] = water_match
                
                # Soil type (15 points)
                if soil_type in crop["soil_types"]:
                    score += 15
                    factors["soil_match"] = 15
                
                # Season suitability (15 points)
                if season in crop["seasons"]:
                    score += 15
                    factors["season_match"] = 15
                
                # Experience level (10 points)
                exp_match = self._calculate_experience_match(crop["difficulty"], experience_level)
                score += exp_match
                factors["experience_match"] = exp_match
                
                # Budget consideration (10 points)
                budget_match = self._calculate_budget_match(crop["investment"], budget_level)
                score += budget_match
                factors["budget_match"] = budget_match
                
                # Risk tolerance (10 points)
                risk_match = self._calculate_risk_match(crop, risk_tolerance)
                score += risk_match
                factors["risk_match"] = risk_match
                
                # Market demand bonus (5 points)
                if crop["market_demand"] == "สูง":
                    score += 5
                    factors["market_bonus"] = 5
                
                if score > 30:  # Only recommend decent matches
                    recommendations.append({
                        "crop_name": crop["name"],
                        "category": crop["category"],
                        "growth_days": crop["growth_days"],
                        "expected_profit": crop["profit"],
                        "investment_needed": crop["investment"],
                        "difficulty": crop["difficulty"],
                        "market_demand": crop["market_demand"],
                        "total_score": round(score, 1),
                        "score_factors": factors,
                        "confidence": min(0.95, score / 125),  # Max possible score ~125
                        "roi": round((crop["profit"] / crop["investment"]) * 100, 1)
                    })
            
            # Sort by score and take top N
            recommendations.sort(key=lambda x: x["total_score"], reverse=True)
            recommendations = recommendations[:top_n]
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_evaluated": len(crops),
                "model_version": "2.0.0",
                "recommendation_quality": "high"
            }
            
        except Exception as e:
            logger.error(f"New crop recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    # Helper methods for advanced calculations
    
    def _get_base_price_enhanced(self, crop_type: str, province: str) -> float:
        """Enhanced base price with regional factors"""
        base_prices = {
            'ข่า': 120, 'ขมิ้นชัน': 80, 'มะกรูด': 150, 'กระชาย': 100,
            'คะน้า': 25, 'กวางตุ้ง': 30, 'ผักบุ้ง': 20, 'ผักสลัด': 35,
            'พริก': 60, 'มะเขือเทศ': 40, 'มะเขือพวง': 35, 'บวบ': 30,
            'กะหล่ำปลี': 45, 'บรอกโคลี': 55,
            'แครอท': 50, 'หัวไชเท้า': 35, 'หอมแดง': 70,
            'ข้าวโพดเลี้ยงสัตว์': 15, 'มันสำปะหลัง': 8, 'อ้อย': 12,
            'ลำไย': 80, 'สับปะรด': 25
        }
        
        base_price = base_prices.get(crop_type, 50.0)
        
        # Regional price adjustment
        regional_factors = {
            "เชียงใหม่": 1.1, "กรุงเทพ": 1.2, "ขอนแก่น": 0.9,
            "สุราษฎร์ธานี": 0.95, "นครราชสีมา": 1.0
        }
        
        return base_price * regional_factors.get(province, 1.0)
    
    def _calculate_weather_score(self, temp: float, rainfall: float, crop_type: str) -> float:
        """Calculate weather suitability score"""
        # Optimal ranges for different crop types
        temp_ranges = {
            "ผักใบ": (20, 30), "ผักผล": (25, 35), "สมุนไพร": (22, 32),
            "ผักหัว": (18, 28), "พืชไร่": (25, 35)
        }
        
        rain_ranges = {
            "ผักใบ": (80, 150), "ผักผล": (100, 200), "สมุนไพร": (120, 180),
            "ผักหัว": (60, 120), "พืชไร่": (80, 160)
        }
        
        crop_category = self._get_crop_category(crop_type)
        temp_range = temp_ranges.get(crop_category, (20, 35))
        rain_range = rain_ranges.get(crop_category, (80, 200))
        
        # Temperature score
        temp_score = 1.0
        if temp < temp_range[0] or temp > temp_range[1]:
            temp_score = max(0.5, 1 - abs(temp - np.mean(temp_range)) / 10)
        
        # Rainfall score
        rain_score = 1.0
        if rainfall < rain_range[0] or rainfall > rain_range[1]:
            rain_score = max(0.5, 1 - abs(rainfall - np.mean(rain_range)) / 50)
        
        return (temp_score + rain_score) / 2
    
    def _get_crop_category(self, crop_type: str) -> str:
        """Get crop category"""
        categories = {
            'ข่า': 'สมุนไพร', 'ขมิ้นชัน': 'สมุนไพร', 'มะกรูด': 'สมุนไพร', 'กระชาย': 'สมุนไพร',
            'คะน้า': 'ผักใบ', 'กวางตุ้ง': 'ผักใบ', 'ผักบุ้ง': 'ผักใบ', 'ผักสลัด': 'ผักใบ',
            'พริก': 'ผักผล', 'มะเขือเทศ': 'ผักผล', 'มะเขือพวง': 'ผักผล', 'บวบ': 'ผักผล',
            'กะหล่ำปลี': 'ผักตระกูลกะหล่ำ', 'บรอกโคลี': 'ผักตระกูลกะหล่ำ',
            'แครอท': 'ผักหัว', 'หัวไชเท้า': 'ผักหัว', 'หอมแดง': 'ผักหัว',
            'ข้าวโพดเลี้ยงสัตว์': 'พืชไร่', 'มันสำปะหลัง': 'พืชไร่', 'อ้อย': 'พืชไร่',
            'ลำไย': 'พืชสวน', 'สับปะรด': 'พืชสวน'
        }
        return categories.get(crop_type, 'ผักอื่นๆ')
    
    def _get_market_demand_factor(self, crop_type: str, month: int) -> float:
        """Calculate market demand factor"""
        # Mock market demand patterns
        high_demand_months = {
            'คะน้า': [11, 12, 1, 2], 'พริก': [10, 11, 12, 1, 2, 3],
            'มะเขือเทศ': [11, 12, 1, 2, 3], 'ข่า': [10, 11, 12, 1]
        }
        
        if crop_type in high_demand_months and month in high_demand_months[crop_type]:
            return 1.2
        return 1.0
    
    def _get_supply_chain_factor(self, province: str, crop_type: str) -> float:
        """Calculate supply chain efficiency factor"""
        # Mock supply chain factors
        major_provinces = ["เชียงใหม่", "กรุงเทพ", "นครราชสีมา"]
        return 1.1 if province in major_provinces else 1.0
    
    def _calculate_quality_factor(self, temp: float, rainfall: float, crop_type: str) -> float:
        """Calculate quality factor based on growing conditions"""
        weather_score = self._calculate_weather_score(temp, rainfall, crop_type)
        return 0.9 + (weather_score * 0.2)  # Quality ranges from 0.9 to 1.1
    
    def _calculate_confidence(self, *factors) -> float:
        """Calculate prediction confidence"""
        avg_factor = np.mean(factors)
        return min(0.95, max(0.6, avg_factor))
    
    def _get_advanced_seasonal_factor(self, month: int, day: int) -> float:
        """Advanced seasonal factor with daily precision"""
        base_factor = self._get_seasonal_factor(month)
        # Add daily variation
        day_factor = 1 + 0.02 * np.sin(2 * np.pi * day / 30)
        return base_factor * day_factor
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal price factor"""
        factors = {
            1: 1.1, 2: 1.15, 3: 1.2, 4: 1.1,
            5: 0.9, 6: 0.85, 7: 0.8, 8: 0.85,
            9: 0.9, 10: 1.0, 11: 1.05, 12: 1.1
        }
        return factors.get(month, 1.0)
    
    def _get_market_cycle_factor(self, day: int, total_days: int) -> float:
        """Calculate market cycle factor"""
        cycle_position = (day / total_days) * 2 * np.pi
        return 1 + 0.05 * np.sin(cycle_position)
    
    def _get_supply_demand_dynamics(self, date: datetime, crop_type: str) -> float:
        """Calculate supply-demand dynamics"""
        # Mock implementation
        return 1 + 0.03 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
    
    def _calculate_planting_weather_score(self, date: datetime, crop_type: str) -> float:
        """Calculate weather suitability for planting"""
        # Mock weather suitability based on season
        month = date.month
        if month in [11, 12, 1, 2]:  # Cool season
            return 0.9
        elif month in [6, 7, 8, 9]:  # Rainy season
            return 0.7
        else:  # Hot season
            return 0.6
    
    def _calculate_market_timing_score(self, harvest_date: datetime, crop_type: str) -> float:
        """Calculate market timing score"""
        month = harvest_date.month
        # Higher scores for off-season harvests
        if month in [1, 2, 11, 12]:
            return 0.9
        elif month in [3, 4, 10]:
            return 0.8
        else:
            return 0.7
    
    def _calculate_planting_risk_score(self, plant_date: datetime, harvest_date: datetime, crop_type: str) -> float:
        """Calculate planting risk score"""
        # Lower risk for shorter growing periods
        growth_days = (harvest_date - plant_date).days
        if growth_days < 60:
            return 0.9
        elif growth_days < 120:
            return 0.8
        else:
            return 0.7
    
    def _get_season_name(self, month: int) -> str:
        """Get season name"""
        if month in [3, 4, 5]:
            return "ฤดูร้อน"
        elif month in [6, 7, 8, 9, 10]:
            return "ฤดูฝน"
        else:
            return "ฤดูหนาว"
    
    def _calculate_water_match(self, crop_need: str, availability: str) -> float:
        """Calculate water requirement match"""
        water_levels = {"น้อย": 1, "ปานกลาง": 2, "มาก": 3}
        need_level = water_levels.get(crop_need, 2)
        avail_level = water_levels.get(availability, 2)
        
        if need_level == avail_level:
            return 20
        elif abs(need_level - avail_level) == 1:
            return 15
        else:
            return 5
    
    def _calculate_experience_match(self, difficulty: str, experience: str) -> float:
        """Calculate experience level match"""
        diff_levels = {"ง่าย": 1, "ปานกลาง": 2, "ยาก": 3}
        exp_levels = {"น้อย": 1, "ปานกลาง": 2, "มาก": 3}
        
        diff_level = diff_levels.get(difficulty, 2)
        exp_level = exp_levels.get(experience, 2)
        
        if exp_level >= diff_level:
            return 10
        else:
            return max(0, 10 - (diff_level - exp_level) * 3)
    
    def _calculate_budget_match(self, investment: int, budget_level: str) -> float:
        """Calculate budget match"""
        budget_ranges = {"น้อย": 5000, "กลาง": 10000, "สูง": 20000}
        max_budget = budget_ranges.get(budget_level, 10000)
        
        if investment <= max_budget:
            return 10
        elif investment <= max_budget * 1.2:
            return 7
        else:
            return 3
    
    def _calculate_risk_match(self, crop: dict, risk_tolerance: str) -> float:
        """Calculate risk tolerance match"""
        if risk_tolerance == "สูง":
            return 10 if crop["profit"] > 10000 else 5
        elif risk_tolerance == "ต่ำ":
            return 10 if crop["difficulty"] == "ง่าย" else 5
        else:  # ปานกลาง
            return 8
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "service_type": "new_model_service",
            "version": "2.0.0",
            "capabilities": [
                "advanced_price_prediction",
                "price_forecast_with_intervals",
                "smart_planting_date_recommendation",
                "intelligent_crop_recommendation"
            ],
            "features": [
                "weather_modeling",
                "market_dynamics",
                "supply_chain_analysis",
                "quality_factors",
                "confidence_scoring"
            ],
            "status": "active"
        }

logger.info("📦 New Model Service loaded successfully")
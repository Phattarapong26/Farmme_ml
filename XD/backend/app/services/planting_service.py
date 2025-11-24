# -*- coding: utf-8 -*-
"""
Planting Recommendation Service
Handles all planting-related business logic
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os
from sqlalchemy import func

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class PlantingRecommendationService:
    """Service for handling planting recommendations"""
    
    def __init__(self):
        self.planting_model_service = None
        self._load_model_service()
    
    def _load_model_service(self):
        """Load the planting model service"""
        try:
            from planting_model_service import planting_model_service
            self.planting_model_service = planting_model_service
            logger.info("✅ Planting model service loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load planting model service: {e}")
            self.planting_model_service = None
    
    def get_recommendations(
        self,
        crop_type: str,
        province: str,
        growth_days: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        top_n: int = 10,
        db = None  # ✅ Add db parameter for historical data
    ) -> Dict[str, Any]:
        """Get planting recommendations"""
        try:
            if not self.planting_model_service:
                raise Exception("Planting model service not available")
            
            # Use the actual ML model service
            result = self.planting_model_service.predict_planting_schedule(
                province=province,
                crop_type=crop_type,
                growth_days=growth_days,
                start_date=start_date,
                end_date=end_date,
                top_n=top_n
            )
            
            if not result["success"]:
                raise Exception("Model prediction failed")
            
            # Transform to format expected by frontend
            recommendations = []
            for rec in result["recommendations"]:
                recommendations.append({
                    "planting_date": rec["planting_date"],
                    "harvest_date": rec["harvest_date"],
                    "predicted_price": rec["predicted_price"],
                    "price": rec["predicted_price"],  # Alternative field name
                    "confidence": rec["confidence"],
                    "risk_score": rec["risk_score"],
                    "planting_score": 1 - rec["risk_score"],  # Inverse of risk
                    "recommendation": rec["recommendation"],
                    "season": rec.get("season", "ตลอดปี"),
                    "weather_suitability": rec.get("weather_suitability", 0.8),
                    "market_timing": rec.get("market_timing", 0.7),
                    "total_score": rec.get("total_score", 0.75),
                    "rainfall": rec.get("rainfall", self._get_seasonal_rainfall(
                        datetime.strptime(rec["planting_date"], "%Y-%m-%d").month
                    ))
                })
            
            # Analyze recommendations (pass db for historical data)
            analysis = self._analyze_recommendations(recommendations, crop_type, province, growth_days, db)
            
            # Transform recommendations to ml_scenarios format for frontend
            ml_scenarios = []
            for idx, rec in enumerate(recommendations):
                planting_dt = datetime.strptime(rec["planting_date"], "%Y-%m-%d")
                harvest_dt = datetime.strptime(rec["harvest_date"], "%Y-%m-%d")
                
                ml_scenarios.append({
                    "scenario_num": idx + 1,
                    "planting_date": rec["planting_date"],
                    "harvest_date": rec["harvest_date"],
                    "harvest_month": self._get_thai_month(harvest_dt.month),
                    "ml_predicted_price": rec["predicted_price"],
                    "confidence": rec["confidence"]
                })
            
            return {
                "success": True,
                "recommendations": recommendations,
                "crop_type": crop_type,
                "province": province,
                "growth_days": growth_days,
                "statistics": result["statistics"],
                "model_info": result.get("model_info", {}),
                "generated_at": datetime.now().isoformat(),
                "ml_scenarios": ml_scenarios,  # Add ml_scenarios for frontend
                **analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise
    
    def _analyze_recommendations(
        self, 
        recommendations: List[Dict], 
        crop_type: str, 
        province: str, 
        growth_days: int,
        db = None  # ✅ Add db parameter
    ) -> Dict[str, Any]:
        """Analyze recommendations and generate insights"""
        if not recommendations:
            return {
                "recommendation": {
                    "level": "poor",
                    "text": f"ML Model ไม่สามารถหาคำแนะนำได้สำหรับ {crop_type} ในจังหวัด {province}",
                    "expected_harvest_date": "",
                    "expected_harvest_month": "",
                    "optimal_planting_month": "",
                    "best_harvest_month": "",
                    "warning_planting_month": "",
                    "worst_harvest_month": ""
                },
                "price_analysis": {
                    "predicted_price": 0,
                    "best_price": 0,
                    "worst_price": 0,
                    "average_price": 0,
                    "price_diff_from_best_percent": 0
                },
                "monthly_price_trend": [],  # Empty - no mock data
                "combined_timeline": self._generate_timeline_from_model(crop_type, province, growth_days, db),  # Still generate timeline even without recommendations
                "historical_prices": [],  # Empty - no mock data
                "ml_forecast": [],  # Empty - no mock data
                "ml_scenarios": [],  # Empty scenarios when no recommendations
                "total_scenarios_analyzed": 0
            }
        
        # Get best and worst recommendations for analysis
        best_rec = max(recommendations, key=lambda x: x["predicted_price"])
        worst_rec = min(recommendations, key=lambda x: x["predicted_price"])
        avg_price = sum(r["predicted_price"] for r in recommendations) / len(recommendations)
        
        # Calculate recommendation level based on best price
        best_price = best_rec["predicted_price"]
        current_price = recommendations[0]["predicted_price"]  # First recommendation
        price_diff_percent = ((current_price - avg_price) / avg_price) * 100
        
        if price_diff_percent >= 15:
            level = "excellent"
        elif price_diff_percent >= 5:
            level = "good"
        elif price_diff_percent >= -5:
            level = "moderate"
        else:
            level = "poor"
        
        # Generate recommendation text
        best_harvest_date = datetime.strptime(best_rec["harvest_date"], "%Y-%m-%d")
        worst_harvest_date = datetime.strptime(worst_rec["harvest_date"], "%Y-%m-%d")
        current_harvest_date = datetime.strptime(recommendations[0]["harvest_date"], "%Y-%m-%d")
        
        recommendation_text = f"แนะนำให้ปลูก{crop_type}ในจังหวัด{province} "
        if level == "excellent":
            recommendation_text += f"ในช่วงนี้เพื่อเก็บเกี่ยวในเดือน{self._get_thai_month(current_harvest_date.month)} คาดการณ์ราคาสูง {current_price:.1f} ฿/กก."
        elif level == "good":
            recommendation_text += f"ช่วงเวลานี้เหมาะสม คาดการณ์ราคา {current_price:.1f} ฿/กก."
        elif level == "moderate":
            recommendation_text += f"ช่วงเวลานี้พอใช้ได้ คาดการณ์ราคา {current_price:.1f} ฿/กก."
        else:
            recommendation_text += f"ช่วงเวลานี้ไม่เหมาะสม คาดการณ์ราคาต่ำ {current_price:.1f} ฿/กก."
        
        return {
            "recommendation": {
                "level": level,
                "text": recommendation_text,
                "expected_harvest_date": recommendations[0]["harvest_date"],
                "expected_harvest_month": self._get_thai_month(current_harvest_date.month),
                "optimal_planting_month": self._get_thai_month(datetime.strptime(recommendations[0]["planting_date"], "%Y-%m-%d").month),
                "best_harvest_month": self._get_thai_month(best_harvest_date.month),
                "warning_planting_month": self._get_thai_month((worst_harvest_date - timedelta(days=growth_days)).month),
                "worst_harvest_month": self._get_thai_month(worst_harvest_date.month)
            },
            "price_analysis": {
                "predicted_price": current_price,
                "best_price": best_price,
                "worst_price": worst_rec["predicted_price"],
                "average_price": avg_price,
                "price_diff_from_best_percent": price_diff_percent
            },
            "monthly_price_trend": self._generate_monthly_trend_from_model(crop_type, province),
            "combined_timeline": self._generate_timeline_from_model(crop_type, province, growth_days, db),  # Pass db for historical data
            "historical_prices": self._generate_historical_from_model(crop_type, province),
            "ml_forecast": self._generate_ml_forecast_from_model(crop_type, province),
            "total_scenarios_analyzed": len(recommendations)
        }
    
    def _get_thai_month(self, month_num: int) -> str:
        """Convert month number to Thai month name"""
        months = {
            1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
            5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
            9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
        }
        return months.get(month_num, "มกราคม")
    
    def _get_seasonal_rainfall(self, month: int) -> float:
        """Get seasonal rainfall data based on Thai climate patterns"""
        rainfall_patterns = {
            1: 15.0, 2: 25.0, 3: 40.0, 4: 80.0, 5: 150.0, 6: 180.0,
            7: 200.0, 8: 220.0, 9: 250.0, 10: 180.0, 11: 60.0, 12: 20.0
        }
        return rainfall_patterns.get(month, 100.0)
    
    def _generate_monthly_trend_from_model(self, crop_type: str, province: str) -> List[Dict]:
        """Generate monthly price trend data using ML model predictions only"""
        try:
            if not self.planting_model_service:
                return []  # Return empty list instead of fallback
            
            months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
            trend_data = []
            current_year = datetime.now().year
            
            for i, month in enumerate(months):
                month_date = datetime(current_year, i + 1, 15)
                
                result = self.planting_model_service.predict_planting_schedule(
                    province=province,
                    crop_type=crop_type,
                    growth_days=self.planting_model_service._get_growth_days(crop_type),
                    start_date=month_date,
                    end_date=month_date + timedelta(days=7),
                    top_n=1
                )
                
                # Only use real ML predictions, no fallback data
                if result["success"] and result["recommendations"]:
                    price = result["recommendations"][0]["predicted_price"]
                    trend_data.append({
                        "month": month,
                        "average_price": round(price, 1)
                    })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error generating monthly trend from model: {e}")
            return []  # Return empty list instead of fallback
    
    def _generate_timeline_from_model(self, crop_type: str, province: str, growth_days: int, db = None) -> List[Dict]:
        """Generate combined timeline data with both historical (from DB) and forecast (from ML) data"""
        try:
            timeline_data = []
            now = datetime.now()
            
            # ✅ Part 1: Get REAL historical data from database (past 12 months)
            if db:
                try:
                    # Import from correct location
                    try:
                        from app.models.database import CropPrice
                    except ImportError:
                        from database import CropPrice
                    
                    # Query historical prices from database
                    start_date = now - timedelta(days=365)
                    
                    logger.info(f"🔍 Querying historical data: crop={crop_type}, province={province}, from={start_date.date()}")
                    
                    historical_prices = db.query(CropPrice).filter(
                        CropPrice.crop_type == crop_type,
                        CropPrice.province == province,
                        CropPrice.date >= start_date,
                        CropPrice.date < now
                    ).order_by(CropPrice.date).all()
                    
                    # Add historical data from database
                    for price_record in historical_prices:
                        timeline_data.append({
                            "date": price_record.date.strftime("%Y-%m-%d"),
                            "average_price": round(price_record.average_price, 1),
                            "type": "historical"
                        })
                    
                    logger.info(f"✅ Loaded {len(historical_prices)} historical records from database")
                    
                    if len(historical_prices) == 0:
                        # Try to check what data exists
                        all_crops = db.query(CropPrice.crop_type).distinct().limit(10).all()
                        all_provinces = db.query(CropPrice.province).distinct().limit(10).all()
                        logger.warning(f"⚠️ No historical data found. Available crops: {[c[0] for c in all_crops]}")
                        logger.warning(f"⚠️ Available provinces: {[p[0] for p in all_provinces]}")
                    
                except Exception as e:
                    logger.error(f"❌ Error loading historical data from database: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # ✅ Part 2: Generate ML forecast for future (next 12 months)
            if self.planting_model_service:
                try:
                    future_start = now
                    
                    # Generate monthly forecasts for next 12 months
                    for i in range(0, 365, 30):  # Monthly sampling
                        date = future_start + timedelta(days=i)
                        
                        result = self.planting_model_service.predict_planting_schedule(
                            province=province,
                            crop_type=crop_type,
                            growth_days=growth_days,
                            start_date=date,
                            end_date=date + timedelta(days=1),
                            top_n=1
                        )
                        
                        if result["success"] and result["recommendations"]:
                            price = result["recommendations"][0]["predicted_price"]
                            
                            timeline_data.append({
                                "date": date.strftime("%Y-%m-%d"),
                                "average_price": round(price, 1),
                                "type": "ml_forecast"
                            })
                    
                    logger.info(f"✅ Generated {12} ML forecast points")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not generate ML forecast: {e}")
            
            # Sort by date
            timeline_data.sort(key=lambda x: x["date"])
            
            logger.info(f"📊 Timeline data: {len([d for d in timeline_data if d['type'] == 'historical'])} historical + {len([d for d in timeline_data if d['type'] == 'ml_forecast'])} forecast")
            
            return timeline_data
            
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            return []
    
    def _generate_historical_from_model(self, crop_type: str, province: str) -> List[Dict]:
        """No historical data - only real ML predictions"""
        return []  # Return empty list - no mock historical data
    
    def _generate_ml_forecast_from_model(self, crop_type: str, province: str) -> List[Dict]:
        """No ML forecast data - only use recommendations from main request"""
        return []  # Return empty list - use only recommendations from main request
    
    # No fallback methods - only real ML data

# Global service instance
planting_service = PlantingRecommendationService()
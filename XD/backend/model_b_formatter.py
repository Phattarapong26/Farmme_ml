# -*- coding: utf-8 -*-
"""
Model B Response Formatter
Formats predictions into standardized responses for LLM consumption
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from model_b_core import ModelBConfig, PredictionResult

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format predictions into standard responses"""
    
    def __init__(self, config: ModelBConfig = None):
        self.config = config or ModelBConfig()
    
    def format_success(
        self,
        prediction_result: PredictionResult,
        weather_data: Optional[Dict],
        province: str,
        planting_date: str,
        prediction_time_ms: float
    ) -> Dict[str, Any]:
        """
        Format successful prediction
        
        Args:
            prediction_result: PredictionResult from engine
            weather_data: Weather data dict (optional)
            province: Province name
            planting_date: Planting date string
            prediction_time_ms: Prediction time in milliseconds
        
        Returns:
            Standardized response dict
        """
        # Generate recommendation
        recommendation = self._generate_recommendation(
            prediction_result.is_good_window,
            prediction_result.confidence
        )
        
        # Generate Thai explanation
        reason = " | ".join(prediction_result.reasons)
        
        # Add disclaimer if low confidence
        if prediction_result.confidence < self.config.LOW_CONFIDENCE_THRESHOLD:
            reason += f" | ⚠️ ความมั่นใจต่ำ ({prediction_result.confidence*100:.0f}%)"
        
        # Build response
        response = {
            "success": True,
            "data": {
                "is_good_window": prediction_result.is_good_window,
                "confidence": round(prediction_result.confidence, 2),
                "recommendation": recommendation,
                "reason": reason,
                "province": province,
                "planting_date": planting_date,
                "probability": {
                    "good": round(prediction_result.probability_good, 2),
                    "bad": round(prediction_result.probability_bad, 2)
                }
            },
            "metadata": {
                "model_version": self.config.MODEL_VERSION,
                "model_used": prediction_result.method_used,
                "prediction_time_ms": round(prediction_time_ms, 2),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Add weather data if available
        if weather_data:
            response["data"]["weather"] = {
                "temperature": round(weather_data.get('temperature', 0), 1),
                "rainfall": round(weather_data.get('rainfall', 0), 1),
                "humidity": round(weather_data.get('humidity', 0), 1),
                "drought_index": round(weather_data.get('drought_index', 0), 1),
                "data_type": weather_data.get('data_type', 'unknown')
            }
        
        # Add warning if using fallback
        if prediction_result.method_used != "ml_model":
            response["metadata"]["warning"] = self._get_fallback_warning(
                prediction_result.method_used
            )
        
        return response
    
    def format_error(
        self,
        error_message: str,
        error_type: str = "ValidationError"
    ) -> Dict[str, Any]:
        """
        Format error response
        
        Args:
            error_message: Error message
            error_type: Error type (class name)
        
        Returns:
            Standardized error response
        """
        return {
            "success": False,
            "error": error_message,
            "error_type": error_type,
            "metadata": {
                "model_version": self.config.MODEL_VERSION,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def format_calendar(
        self,
        monthly_predictions: List[Dict],
        good_windows: List[Dict],
        best_windows: List[Dict],
        province: str,
        crop_type: str,
        months_ahead: int,
        prediction_time_ms: float
    ) -> Dict[str, Any]:
        """
        Format planting calendar response
        
        Args:
            monthly_predictions: List of monthly prediction dicts
            good_windows: List of good planting windows
            best_windows: List of best consecutive windows
            province: Province name
            crop_type: Crop type
            months_ahead: Number of months analyzed
            prediction_time_ms: Total prediction time
        
        Returns:
            Standardized calendar response
        """
        # Generate summary
        summary = self._create_calendar_summary(monthly_predictions, best_windows)
        
        return {
            "success": True,
            "data": {
                "province": province,
                "crop_type": crop_type,
                "analysis_period": f"{months_ahead} months",
                "monthly_predictions": monthly_predictions,
                "good_windows": good_windows,
                "best_windows": best_windows,
                "summary": summary
            },
            "metadata": {
                "model_version": self.config.MODEL_VERSION,
                "prediction_time_ms": round(prediction_time_ms, 2),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_recommendation(
        self,
        is_good: bool,
        confidence: float,
        alternative_months: Optional[List[str]] = None
    ) -> str:
        """
        Generate actionable recommendation
        
        Args:
            is_good: Whether window is good
            confidence: Confidence score
            alternative_months: Alternative months to suggest (optional)
        
        Returns:
            Thai recommendation string
        """
        if is_good:
            if confidence >= 0.85:
                return "ดีมาก - แนะนำให้ปลูกในช่วงนี้"
            elif confidence >= 0.75:
                return "ดี - แนะนำให้ปลูกในช่วงนี้"
            else:
                return "พอใช้ได้ - สามารถปลูกได้แต่ควรระวัง"
        else:
            base = "ไม่ดี - ควรรอช่วงเวลาที่เหมาะสมกว่า"
            if alternative_months:
                base += f" (แนะนำ: {', '.join(alternative_months)})"
            return base
    
    def _get_fallback_warning(self, method: str) -> str:
        """Get warning message for fallback method"""
        warnings = {
            "weather_based": "ML model unavailable, using weather-based prediction",
            "rule_based": "Weather data unavailable, using rule-based prediction"
        }
        return warnings.get(method, f"Using fallback method: {method}")
    
    def _create_calendar_summary(
        self,
        monthly_predictions: List[Dict],
        best_windows: List[Dict]
    ) -> str:
        """
        Create human-readable calendar summary
        
        Args:
            monthly_predictions: List of monthly predictions
            best_windows: List of best windows
        
        Returns:
            Thai summary string
        """
        good_count = sum(1 for m in monthly_predictions if m.get('is_good', False))
        
        if len(best_windows) == 0:
            return f"ไม่พบช่วงเวลาที่เหมาะสมในช่วง {len(monthly_predictions)} เดือนข้างหน้า"
        
        best = best_windows[0]
        summary = f"ช่วงที่ดีที่สุด: {best['start_month']} - {best['end_month']} "
        summary += f"({best['duration_months']} เดือน, ความมั่นใจ {best['avg_confidence']*100:.0f}%)"
        
        if len(best_windows) > 1:
            summary += f" | มีทั้งหมด {len(best_windows)} ช่วงที่เหมาะสม"
        
        return summary

# -*- coding: utf-8 -*-
"""
Response Formatter Service
จัดรูปแบบ response จาก Gemini และแยกข้อมูลกราฟ
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Service สำหรับจัดรูปแบบ response และแยกข้อมูลกราฟ"""
    
    def __init__(self):
        logger.info("✅ ResponseFormatter initialized")
    
    def format_with_chart(
        self,
        text_response: str,
        function_result: Optional[Dict],
        function_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        จัดรูปแบบ response พร้อมข้อมูลกราฟ
        
        Args:
            text_response: คำตอบจาก Gemini
            function_result: ผลลัพธ์จาก function call
            function_name: ชื่อ function ที่ถูกเรียก
            
        Returns:
            {
                "text": str,
                "chart_data": Optional[Dict],
                "has_chart": bool
            }
        """
        chart_data = None
        
        # แยกข้อมูลกราฟถ้ามี
        if function_result and function_name:
            chart_data = self.extract_chart_data(function_result, function_name)
        
        return {
            "text": text_response,
            "chart_data": chart_data,
            "has_chart": chart_data is not None
        }
    
    def extract_chart_data(
        self,
        function_result: Dict,
        function_name: str
    ) -> Optional[Dict]:
        """
        แยกข้อมูลกราฟจาก function result
        
        Args:
            function_result: ผลลัพธ์จาก function
            function_name: ชื่อ function
            
        Returns:
            Chart data dict หรือ None ถ้าไม่มีข้อมูลกราฟ
        """
        # ตรวจสอบว่า function สำเร็จหรือไม่
        if not function_result.get("success"):
            logger.warning(f"Function {function_name} failed, no chart data")
            return None
        
        # แยกข้อมูลกราฟตาม function type
        if function_name == "get_price_prediction":
            return self._extract_price_forecast_chart(function_result)
        
        # Functions อื่นๆ ยังไม่มีกราฟ
        return None
    
    def _extract_price_forecast_chart(self, result: Dict) -> Optional[Dict]:
        """
        แยกข้อมูลกราฟจาก price prediction result
        
        Args:
            result: ผลลัพธ์จาก get_price_prediction
            
        Returns:
            Chart data สำหรับ price forecast
        """
        try:
            # ตรวจสอบว่ามีข้อมูลที่จำเป็น
            if not result.get("historical_data") or not result.get("daily_forecasts"):
                logger.warning("Missing historical_data or daily_forecasts")
                return None
            
            historical = result.get("historical_data", [])
            forecasts = result.get("daily_forecasts", [])
            
            # Validate data
            if not self._validate_chart_data(historical, forecasts):
                logger.warning("Invalid chart data")
                return None
            
            # สร้าง chart data structure
            chart_data = {
                "type": "price_forecast",
                "data": {
                    "historical": [
                        {
                            "date": item["date"],
                            "price": float(item["price"])
                        }
                        for item in historical
                    ],
                    "forecast": [
                        {
                            "date": item["date"],
                            "price": float(item["predicted_price"]),
                            "confidence_low": float(item.get("confidence_low", item["predicted_price"] * 0.9)),
                            "confidence_high": float(item.get("confidence_high", item["predicted_price"] * 1.1))
                        }
                        for item in forecasts
                    ],
                    "metadata": {
                        "crop_type": result.get("crop_type", ""),
                        "province": result.get("province", ""),
                        "days_ahead": result.get("days_ahead", 30),
                        "model_used": result.get("model_used", "unknown"),
                        "confidence": result.get("confidence", 0.0),
                        "price_trend": result.get("price_trend", "stable")
                    }
                }
            }
            
            logger.info(f"📊 Chart data extracted: {len(historical)} historical + {len(forecasts)} forecast points")
            return chart_data
            
        except Exception as e:
            logger.error(f"Error extracting price forecast chart: {e}")
            return None
    
    def _validate_chart_data(
        self,
        historical: List[Dict],
        forecasts: List[Dict]
    ) -> bool:
        """
        ตรวจสอบความถูกต้องของข้อมูลกราฟ
        
        Args:
            historical: ข้อมูลย้อนหลัง
            forecasts: ข้อมูลทำนาย
            
        Returns:
            True ถ้าข้อมูลถูกต้อง
        """
        # ต้องมีข้อมูลอย่างน้อย 1 จุด
        if not historical or not forecasts:
            return False
        
        # ตรวจสอบ historical data
        for item in historical:
            if not item.get("date") or not item.get("price"):
                logger.warning(f"Invalid historical item: {item}")
                return False
            try:
                float(item["price"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid price in historical: {item['price']}")
                return False
        
        # ตรวจสอบ forecast data
        for item in forecasts:
            if not item.get("date") or not item.get("predicted_price"):
                logger.warning(f"Invalid forecast item: {item}")
                return False
            try:
                float(item["predicted_price"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid predicted_price: {item['predicted_price']}")
                return False
        
        return True


# Global instance
response_formatter = ResponseFormatter()

if __name__ == "__main__":
    # ทดสอบ service
    test_result = {
        "success": True,
        "crop_type": "พริก",
        "province": "เชียงใหม่",
        "days_ahead": 30,
        "model_used": "model_c",
        "confidence": 0.85,
        "price_trend": "increasing",
        "historical_data": [
            {"date": "2024-01-01", "price": 50.0},
            {"date": "2024-01-02", "price": 52.0},
        ],
        "daily_forecasts": [
            {"date": "2024-01-03", "predicted_price": 55.0},
            {"date": "2024-01-04", "predicted_price": 57.0},
        ]
    }
    
    chart_data = response_formatter.extract_chart_data(test_result, "get_price_prediction")
    print(f"Chart data: {chart_data}")

# -*- coding: utf-8 -*-
"""
Gemini Function Calling Definitions and Handlers
Defines all functions that Gemini can call to access ML models
"""

import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Function Definitions for Gemini - Using correct format
GEMINI_FUNCTIONS = [
    {
        "name": "get_price_prediction",
        "description": "ทำนายราคาพืชในอนาคตโดยใช้ ML Model ใช้เมื่อผู้ใช้ถามเรื่องราคาในอนาคต แนวโน้มราคา หรือช่วงเวลาที่เหมาะสมในการขาย",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ', 'คะน้า'"
                },
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "days_ahead": {
                    "type_": "INTEGER",
                    "description": "จำนวนวันข้างหน้าที่ต้องการทำนาย (7, 30, 90, หรือ 180)"
                },
                "planting_area_rai": {
                    "type_": "NUMBER",
                    "description": "พื้นที่ปลูก (ไร่) - ไม่บังคับ"
                },
                "expected_yield_kg": {
                    "type_": "NUMBER",
                    "description": "ผลผลิตที่คาดหวัง (กิโลกรัม) - ไม่บังคับ"
                }
            },
            "required": ["crop_type", "province", "days_ahead"]
        }
    },
    {
        "name": "get_crop_recommendations",
        "description": "แนะนำพืชที่เหมาะสมสำหรับเกษตรกรตามข้อมูลพื้นที่และความต้องการ ใช้เมื่อผู้ใช้ถามว่าควรปลูกพืชอะไร หรือต้องการคำแนะนำการเลือกพืช",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย เช่น 'เชียงใหม่', 'กรุงเทพมหานคร'"
                },
                "soil_type": {
                    "type_": "STRING",
                    "description": "ประเภทดิน: ดินร่วน, ดินร่วนปนทราย, ดินเหนียว, ดินทราย"
                },
                "water_availability": {
                    "type_": "STRING",
                    "description": "แหล่งน้ำที่มี: น้ำชลประทาน, น้ำฝน, น้ำบาดาล, น้ำประปา"
                },
                "budget_level": {
                    "type_": "STRING",
                    "description": "ระดับงบประมาณ: ต่ำ, ปานกลาง, สูง"
                },
                "risk_tolerance": {
                    "type_": "STRING",
                    "description": "ความยอมรับความเสี่ยง: ต่ำ, ปานกลาง, สูง"
                }
            },
            "required": ["province"]
        }
    },
    {
        "name": "get_water_management_advice",
        "description": "ให้คำแนะนำการจัดการน้ำสำหรับพืช รวมถึงความต้องการน้ำ ความถี่การให้น้ำ และวิธีการให้น้ำที่เหมาะสม ใช้เมื่อผู้ใช้ถามเรื่องการรดน้ำ การให้น้ำ หรือการจัดการน้ำ",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ', 'คะน้า'"
                },
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "soil_type": {
                    "type_": "STRING",
                    "description": "ประเภทดิน: ดินร่วน, ดินร่วนปนทราย, ดินเหนียว, ดินทราย"
                },
                "current_rainfall_mm": {
                    "type_": "NUMBER",
                    "description": "ปริมาณฝนปัจจุบัน (มิลลิเมตร)"
                },
                "planting_area_rai": {
                    "type_": "NUMBER",
                    "description": "พื้นที่ปลูก (ไร่)"
                },
                "growth_stage": {
                    "type_": "STRING",
                    "description": "ระยะการเจริญเติบโต: เพาะกล้า, กำลังเจริญเติบโต, ออกดอก, ติดผล"
                }
            },
            "required": ["crop_type", "province"]
        }
    },
    {
        "name": "get_planting_window_advice",
        "description": "ให้คำแนะนำเกี่ยวกับช่วงเวลาที่เหมาะสมในการปลูกพืช ใช้เมื่อผู้ใช้ถามว่า ควรปลูกเมื่อไหร่ เดือนไหนดีสำหรับปลูก หรือช่วงไหนดีสำหรับปลูก (fallback function)",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ', 'คะน้า'"
                },
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "soil_type": {
                    "type_": "STRING",
                    "description": "ประเภทดิน: ดินร่วน, ดินร่วนปนทราย, ดินเหนียว, ดินทราย"
                },
                "planting_month": {
                    "type_": "INTEGER",
                    "description": "เดือนที่ต้องการปลูก (1-12) ถ้าไม่ระบุจะใช้เดือนปัจจุบัน"
                }
            },
            "required": ["crop_type", "province"]
        }
    },
    {
        "name": "get_harvest_decision",
        "description": "ตัดสินใจว่าควรเก็บเกี่ยวเลยหรือรอเพื่อให้ได้กำไรสูงสุด ใช้เมื่อผู้ใช้ถามว่าควรเก็บเกี่ยวเมื่อไหร่ ขายเลยหรือรอ",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ', 'คะน้า'"
                },
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "current_price": {
                    "type_": "NUMBER",
                    "description": "ราคาปัจจุบัน (บาท/กก.)"
                },
                "expected_yield_kg": {
                    "type_": "NUMBER",
                    "description": "ผลผลิตที่คาดหวัง (กิโลกรัม)"
                },
                "plant_health_score": {
                    "type_": "NUMBER",
                    "description": "คะแนนสุขภาพพืช (0-1) ถ้าไม่ระบุจะใช้ 0.8"
                }
            },
            "required": ["crop_type", "province"]
        }
    },
    {
        "name": "check_planting_window",
        "description": "ตรวจสอบว่าวันที่กำหนดเหมาะสมสำหรับการปลูกพืชหรือไม่ โดยใช้ AI Model B วิเคราะห์สภาพอากาศ อุณหภูมิ ปริมาณฝน และฤดูกาล ใช้เมื่อผู้ใช้ถามว่า วันนี้เหมาะปลูกไหม วันที่กำหนดเหมาะปลูกไหม ตอนนี้เหมาะปลูกไหม หรือควรปลูกเมื่อไหร่",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "planting_date": {
                    "type_": "STRING",
                    "description": "วันที่ต้องการปลูก (YYYY-MM-DD) ถ้าไม่ระบุจะใช้วันนี้"
                },
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ' - ไม่บังคับ"
                },
                "soil_type": {
                    "type_": "STRING",
                    "description": "ประเภทดิน เช่น 'ดินร่วน', 'ดินเหนียว', 'ดินทราย' - ไม่บังคับ"
                },
                "soil_ph": {
                    "type_": "NUMBER",
                    "description": "ค่า pH ของดิน (0-14) - ไม่บังคับ"
                },
                "soil_nutrients": {
                    "type_": "NUMBER",
                    "description": "ระดับธาตุอาหารในดิน (0-100) - ไม่บังคับ"
                }
            },
            "required": ["province"]
        }
    },
    {
        "name": "get_planting_calendar",
        "description": "ดูปฏิทินการปลูกที่แนะนำสำหรับพืชในจังหวัดนั้นๆ แสดงช่วงเวลาที่เหมาะสมตลอดทั้งปี โดยใช้ AI Model B วิเคราะห์รายเดือน ใช้เมื่อผู้ใช้ถามว่า ช่วงไหนเหมาะปลูก ปฏิทินการปลูก เดือนไหนเหมาะปลูก หรือช่วงเวลาที่ดีสำหรับปลูก",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "province": {
                    "type_": "STRING",
                    "description": "ชื่อจังหวัดภาษาไทย"
                },
                "crop_type": {
                    "type_": "STRING",
                    "description": "ชื่อพืชภาษาไทย เช่น 'พริก', 'มะเขือเทศ' ถ้าไม่ระบุจะใช้ 'พริก'"
                },
                "months_ahead": {
                    "type_": "INTEGER",
                    "description": "จำนวนเดือนที่ต้องการดู (1-24) ถ้าไม่ระบุจะใช้ 12"
                },
                "soil_type": {
                    "type_": "STRING",
                    "description": "ประเภทดิน - ไม่บังคับ"
                },
                "soil_ph": {
                    "type_": "NUMBER",
                    "description": "ค่า pH ของดิน - ไม่บังคับ"
                },
                "soil_nutrients": {
                    "type_": "NUMBER",
                    "description": "ระดับธาตุอาหารในดิน - ไม่บังคับ"
                }
            },
            "required": ["province"]
        }
    }
]


class GeminiFunctionHandler:
    """Handler for executing Gemini function calls"""
    
    def __init__(self):
        try:
            from recommendation_model_service import recommendation_model_service
        except ImportError:
            logger.warning("⚠️ recommendation_model_service not available")
            recommendation_model_service = None
        
        try:
            from water_management_service import water_management_service
        except ImportError:
            logger.warning("⚠️ water_management_service not available")
            water_management_service = None
        
        try:
            from price_prediction_service import price_prediction_service
        except ImportError:
            logger.warning("⚠️ price_prediction_service not available")
            price_prediction_service = None
        
        self.recommendation_service = recommendation_model_service
        self.water_service = water_management_service
        self.price_service = price_prediction_service
        
        logger.info("✅ Gemini Function Handler initialized")
    
    def execute_function(self, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call from Gemini with error handling and validation
        
        Args:
            function_name: Name of the function to execute
            function_args: Arguments for the function
            
        Returns:
            Result from the function execution
        """
        try:
            # Validate function name
            valid_functions = ["get_price_prediction", "get_crop_recommendations", "get_water_management_advice", "get_planting_window_advice", "get_harvest_decision", "check_planting_window", "get_planting_calendar"]
            if function_name not in valid_functions:
                logger.error(f"❌ Unknown function: {function_name}")
                return {
                    "success": False,
                    "error": f"ไม่รู้จักฟังก์ชัน: {function_name}"
                }
            
            # Validate required arguments
            validation_error = self._validate_function_args(function_name, function_args)
            if validation_error:
                logger.error(f"❌ Validation error: {validation_error}")
                return {
                    "success": False,
                    "error": validation_error
                }
            
            # Execute function (removed signal timeout as it doesn't work in threads)
            logger.info(f"🔧 Executing function: {function_name}")
            logger.info(f"📥 Function args: {function_args}")
            
            if function_name == "get_price_prediction":
                result = self._handle_price_prediction(function_args)
            elif function_name == "get_crop_recommendations":
                result = self._handle_crop_recommendations(function_args)
            elif function_name == "get_water_management_advice":
                result = self._handle_water_management(function_args)
            elif function_name == "get_planting_window_advice":
                result = self._handle_planting_window(function_args)
            elif function_name == "get_harvest_decision":
                result = self._handle_harvest_decision(function_args)
            elif function_name == "check_planting_window":
                result = self._handle_check_planting_window(function_args)
            elif function_name == "get_planting_calendar":
                result = self._handle_get_planting_calendar(function_args)
            
            # Log result before returning to LLM
            logger.info(f"📤 Function result (before LLM):")
            logger.info(f"   Success: {result.get('success', 'N/A')}")
            if result.get('is_good_window') is not None:
                logger.info(f"   Is Good Window: {result.get('is_good_window')}")
                logger.info(f"   Confidence: {result.get('confidence', 0):.2%}")
                logger.info(f"   Recommendation: {result.get('recommendation', 'N/A')}")
            elif result.get('summary'):
                logger.info(f"   Summary: {result.get('summary')}")
            elif result.get('predictions'):
                logger.info(f"   Predictions: {len(result.get('predictions', []))} items")
            elif result.get('recommendations'):
                logger.info(f"   Recommendations: {len(result.get('recommendations', []))} items")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def _validate_function_args(self, function_name: str, args: Dict[str, Any]) -> Optional[str]:
        """Validate function arguments"""
        if function_name == "get_price_prediction":
            if not args.get("crop_type"):
                return "ต้องระบุชื่อพืช"
            if not args.get("province"):
                return "ต้องระบุจังหวัด"
            if not args.get("days_ahead"):
                return "ต้องระบุจำนวนวันข้างหน้า"
        
        elif function_name == "get_crop_recommendations":
            if not args.get("province"):
                return "ต้องระบุจังหวัด"
        
        elif function_name == "get_water_management_advice":
            if not args.get("crop_type"):
                return "ต้องระบุชื่อพืช"
            if not args.get("province"):
                return "ต้องระบุจังหวัด"
        
        return None
    
    def _handle_price_prediction(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price prediction function call with error handling"""
        try:
            logger.info(f"💰 Executing get_price_prediction with args: {args}")
            
            # Call price prediction service
            days_ahead = args.get("days_ahead", 30)
            # Convert to int if it's a float
            if isinstance(days_ahead, float):
                days_ahead = int(days_ahead)
            
            result = self.price_service.predict_price(
                crop_type=args.get("crop_type"),
                province=args.get("province"),
                days_ahead=days_ahead,
                planting_area_rai=args.get("planting_area_rai"),
                expected_yield_kg=args.get("expected_yield_kg")
            )
            
            # Validate result
            if not result:
                logger.error("❌ Price prediction service returned None")
                return {
                    "success": False,
                    "error": "ไม่สามารถทำนายราคาได้"
                }
            
            # Log Model C response
            if not result.get("success"):
                logger.warning(f"⚠️ Model C returned error: {result.get('error')}")
            else:
                predictions = result.get('predictions', [])
                logger.info(f"💰 Model C (Price Prediction) Response:")
                logger.info(f"   Crop: {args.get('crop_type')}")
                logger.info(f"   Province: {args.get('province')}")
                logger.info(f"   Days Ahead: {args.get('days_ahead')}")
                logger.info(f"   Predictions: {len(predictions)} timeframes")
                if predictions:
                    logger.info(f"   Current Price: {result.get('current_price', 'N/A')} บาท/กก.")
                    for pred in predictions[:3]:  # Show first 3
                        logger.info(f"   - {pred.get('days_ahead')}d: {pred.get('predicted_price', 0):.2f} บาท/กก. (confidence: {pred.get('confidence', 0):.1%})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in price prediction: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการทำนายราคา: {str(e)}"
            }
    
    def _handle_crop_recommendations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crop recommendation function call with error handling"""
        try:
            logger.info(f"🌱 Executing get_crop_recommendations with args: {args}")
            
            # Call recommendation service
            result = self.recommendation_service.get_recommendations(
                province=args.get("province"),
                soil_type=args.get("soil_type"),
                water_availability=args.get("water_availability"),
                budget_level=args.get("budget_level"),
                risk_tolerance=args.get("risk_tolerance")
            )
            
            # Validate result
            if not result:
                logger.error("❌ Recommendation service returned None")
                return {
                    "success": False,
                    "error": "ไม่สามารถสร้างคำแนะนำได้"
                }
            
            # Log Model A response
            if not result.get("success"):
                logger.warning(f"⚠️ Model A returned error: {result.get('error')}")
            else:
                recommendations = result.get('recommendations', [])
                logger.info(f"🌾 Model A (Crop Recommendation) Response:")
                logger.info(f"   Province: {args.get('province')}")
                logger.info(f"   Budget: {args.get('budget_level', 'N/A')}")
                logger.info(f"   Water: {args.get('water_availability', 'N/A')}")
                logger.info(f"   Recommendations: {len(recommendations)} crops")
                for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                    logger.info(f"   {i}. {rec.get('crop_name', 'N/A')} (score: {rec.get('suitability_score', 0):.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in crop recommendations: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการแนะนำพืช: {str(e)}"
            }
    
    def _handle_water_management(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle water management function call with error handling"""
        try:
            logger.info(f"💧 Executing get_water_management_advice with args: {args}")
            
            # Call water management service
            result = self.water_service.get_water_advice(
                crop_type=args.get("crop_type"),
                province=args.get("province"),
                soil_type=args.get("soil_type"),
                current_rainfall_mm=args.get("current_rainfall_mm"),
                planting_area_rai=args.get("planting_area_rai", 5.0),
                growth_stage=args.get("growth_stage", "กำลังเจริญเติบโต")
            )
            
            # Validate result
            if not result:
                logger.error("❌ Water management service returned None")
                return {
                    "success": False,
                    "error": "ไม่สามารถสร้างคำแนะนำการจัดการน้ำได้"
                }
            
            # Log Model D response
            if not result.get("success"):
                logger.warning(f"⚠️ Model D returned error: {result.get('error')}")
            else:
                logger.info(f"💧 Model D (Water Management) Response:")
                logger.info(f"   Crop: {args.get('crop_type')}")
                logger.info(f"   Province: {args.get('province')}")
                logger.info(f"   Soil Type: {args.get('soil_type', 'N/A')}")
                logger.info(f"   Current Rainfall: {args.get('current_rainfall_mm', 'N/A')} mm")
                logger.info(f"   Recommendation: {result.get('recommendation', 'N/A')}")
                logger.info(f"   Water Needed: {result.get('water_needed_liters', 'N/A')} L")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in water management: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการแนะนำการจัดการน้ำ: {str(e)}"
            }
    
    def _handle_planting_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle planting window function call with error handling"""
        try:
            logger.info(f"🌱 Executing get_planting_window_advice with args: {args}")
            
            # Simple fallback for now - will integrate Model B later
            from datetime import datetime
            
            crop_type = args.get("crop_type")
            province = args.get("province")
            planting_month = args.get("planting_month", datetime.now().month)
            
            # Simple logic based on season
            good_months = {
                'พริก': [3, 4, 5, 10, 11],
                'มะเขือเทศ': [6, 7, 8, 9, 10],
                'คะน้า': [1, 2, 10, 11, 12],
                'ข้าวโพดเลี้ยงสัตว์': [3, 4, 5, 6],
            }
            
            is_good = planting_month in good_months.get(crop_type, [1,2,3,4,5,6,7,8,9,10,11,12])
            
            result = {
                "success": True,
                "crop_type": crop_type,
                "province": province,
                "planting_month": planting_month,
                "is_good_window": is_good,
                "confidence": 0.7,
                "recommendation": "เหมาะสมในการปลูก" if is_good else "ไม่เหมาะสมในการปลูก",
                "reasons": [
                    f"เดือน {planting_month} {'เหมาะสม' if is_good else 'ไม่เหมาะสม'}กับ{crop_type}",
                    f"สภาพอากาศใน{province}{'เอื้ออำนวย' if is_good else 'ไม่เอื้ออำนวย'}"
                ],
                "best_months": good_months.get(crop_type, []),
                "model_used": "Model B (fallback)"
            }
            
            # Log fallback planting advice
            logger.info(f"🌱 Planting Window Advice (Fallback) Response:")
            logger.info(f"   Crop: {crop_type}")
            logger.info(f"   Province: {province}")
            logger.info(f"   Month: {planting_month}")
            logger.info(f"   Is Good: {result['is_good_window']}")
            logger.info(f"   Confidence: {result['confidence']:.1%}")
            logger.info(f"   Recommendation: {result['recommendation']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in planting window: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการทำนายช่วงเวลาปลูก: {str(e)}"
            }
    
    def _handle_harvest_decision(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle harvest decision function call with error handling"""
        try:
            logger.info(f"🌾 Executing get_harvest_decision with args: {args}")
            
            crop_type = args.get("crop_type")
            province = args.get("province")
            current_price = args.get("current_price", 50.0)
            expected_yield_kg = args.get("expected_yield_kg", 1000.0)
            plant_health_score = args.get("plant_health_score", 0.8)
            
            # Get price forecast from Model C
            try:
                price_forecast = self.price_service.predict_price(
                    crop_type=crop_type,
                    province=province,
                    days_ahead=7
                )
            except:
                price_forecast = None
            
            # Simple decision logic (will integrate Model D later)
            # Calculate profit for each action
            storage_cost_per_day = 2.0  # baht per kg per day
            
            # Action 1: Harvest Now
            profit_now = current_price * expected_yield_kg
            
            # Action 2: Wait 3 Days
            price_3days = current_price * 1.02 if not price_forecast else current_price * 1.05  # Assume 2-5% increase
            cost_3days = storage_cost_per_day * 3 * expected_yield_kg
            profit_3days = (price_3days * expected_yield_kg) - cost_3days
            
            # Action 3: Wait 7 Days
            price_7days = current_price * 1.05 if not price_forecast else current_price * 1.08  # Assume 5-8% increase
            cost_7days = storage_cost_per_day * 7 * expected_yield_kg
            profit_7days = (price_7days * expected_yield_kg) - cost_7days
            
            # Adjust for plant health
            profit_3days *= plant_health_score
            profit_7days *= (plant_health_score ** 2)  # More penalty for waiting longer
            
            # Find best action
            actions = [
                {"action": "harvest_now", "profit": profit_now, "days_wait": 0},
                {"action": "wait_3_days", "profit": profit_3days, "days_wait": 3},
                {"action": "wait_7_days", "profit": profit_7days, "days_wait": 7}
            ]
            
            best_action = max(actions, key=lambda x: x["profit"])
            
            result = {
                "success": True,
                "crop_type": crop_type,
                "province": province,
                "recommended_action": best_action["action"],
                "recommended_action_thai": {
                    "harvest_now": "เก็บเกี่ยวเลย",
                    "wait_3_days": "รอ 3 วัน",
                    "wait_7_days": "รอ 7 วัน"
                }[best_action["action"]],
                "expected_profit": round(best_action["profit"], 2),
                "profit_projections": [
                    {
                        "action": "เก็บเกี่ยวเลย",
                        "profit": round(profit_now, 2),
                        "days_wait": 0
                    },
                    {
                        "action": "รอ 3 วัน",
                        "profit": round(profit_3days, 2),
                        "days_wait": 3
                    },
                    {
                        "action": "รอ 7 วัน",
                        "profit": round(profit_7days, 2),
                        "days_wait": 7
                    }
                ],
                "confidence": 0.75,
                "factors": {
                    "current_price": current_price,
                    "expected_yield_kg": expected_yield_kg,
                    "plant_health_score": plant_health_score,
                    "storage_cost_per_day": storage_cost_per_day
                },
                "model_used": "Model D (Thompson Sampling - fallback)"
            }
            
            # Log harvest decision
            logger.info(f"🌾 Harvest Decision Response:")
            logger.info(f"   Crop: {args.get('crop_type')}")
            logger.info(f"   Province: {args.get('province')}")
            logger.info(f"   Current Price: {args.get('current_price', 'N/A')} บาท/กก.")
            logger.info(f"   Action: {result['recommended_action_thai']}")
            logger.info(f"   Confidence: {result['confidence']:.1%}")
            logger.info(f"   Reason: {result['reason_thai']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in harvest decision: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการตัดสินใจเก็บเกี่ยว: {str(e)}"
            }
    
    def _handle_check_planting_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle check planting window function call - Using Model B"""
        try:
            logger.info(f"🌱 Executing check_planting_window with args: {args}")
            
            # Import Model B wrapper (new version)
            import sys
            from pathlib import Path
            backend_dir = Path(__file__).parent
            sys.path.insert(0, str(backend_dir))
            from model_b_wrapper import get_model_b
            
            # Get planting date (default to today)
            from datetime import datetime
            planting_date = args.get("planting_date")
            if not planting_date:
                planting_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get Model B instance
            model_b = get_model_b()
            
            # Call Model B (new API)
            result = model_b.predict_planting_window(
                crop_type=args.get("crop_type", "พริก"),
                province=args.get("province"),
                planting_date=planting_date
            )
            
            # Format response for Gemini
            response = {
                "success": True,
                "is_good_window": result['is_good_window'],
                "confidence": result['confidence'],
                "recommendation": result['recommendation'],
                "reason": result['reason'],
                "planting_date": planting_date,
                "province": args.get("province"),
                "crop_type": args.get("crop_type", "พริก")
            }
            
            # Log Model B response
            logger.info(f"🌱 Model B Response:")
            logger.info(f"   Crop: {response['crop_type']}")
            logger.info(f"   Province: {response['province']}")
            logger.info(f"   Date: {response['planting_date']}")
            logger.info(f"   Is Good: {response['is_good_window']}")
            logger.info(f"   Confidence: {response['confidence']:.2%}")
            logger.info(f"   Recommendation: {response['recommendation']}")
            logger.info(f"   Reason: {response['reason']}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in check planting window: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการตรวจสอบช่วงเวลาปลูก: {str(e)}"
            }
    
    def _handle_get_planting_calendar(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get planting calendar function call - Using Model B"""
        try:
            logger.info(f"📅 Executing get_planting_calendar with args: {args}")
            
            # Use API endpoint instead of direct wrapper call
            import requests
            from datetime import datetime, timedelta
            
            # Get Model B instance
            import sys
            from pathlib import Path
            backend_dir = Path(__file__).parent
            sys.path.insert(0, str(backend_dir))
            from model_b_wrapper import get_model_b
            
            model_b = get_model_b()
            
            # Generate calendar predictions
            province = args.get("province")
            crop_type = args.get("crop_type", "พริก")
            months_ahead = args.get("months_ahead", 12)
            
            monthly_predictions = []
            good_windows = []
            
            current_date = datetime.now()
            
            for month_offset in range(months_ahead):
                target_date = current_date + timedelta(days=30 * month_offset)
                date_str = target_date.strftime('%Y-%m-%d')
                
                # Predict for this date
                result = model_b.predict_planting_window(
                    crop_type=crop_type,
                    province=province,
                    planting_date=date_str
                )
                
                monthly_predictions.append({
                    'month': target_date.strftime('%Y-%m'),
                    'date': date_str,
                    'is_good_window': result['is_good_window'],
                    'confidence': result['confidence'],
                    'recommendation': result['recommendation']
                })
                
                if result['is_good_window']:
                    good_windows.append({
                        'month': target_date.strftime('%Y-%m'),
                        'confidence': result['confidence']
                    })
            
            # Generate summary
            good_count = len(good_windows)
            total_count = len(monthly_predictions)
            
            if good_count == 0:
                summary = f"ไม่พบช่วงเวลาที่เหมาะสมสำหรับการปลูก{crop_type}ใน{province}ในช่วง {months_ahead} เดือนข้างหน้า"
            elif good_count == total_count:
                summary = f"ทุกเดือนเหมาะสมสำหรับการปลูก{crop_type}ใน{province}"
            else:
                summary = f"พบ {good_count} เดือนที่เหมาะสมจาก {total_count} เดือน ({good_count/total_count*100:.0f}%) สำหรับการปลูก{crop_type}ใน{province}"
            
            response = {
                "success": True,
                "monthly_predictions": monthly_predictions,
                "good_windows": good_windows,
                "summary": summary,
                "crop_type": crop_type,
                "province": province
            }
            
            # Log Model B calendar response
            logger.info(f"📅 Model B Calendar Response:")
            logger.info(f"   Crop: {crop_type}")
            logger.info(f"   Province: {province}")
            logger.info(f"   Months Analyzed: {len(monthly_predictions)}")
            logger.info(f"   Good Windows: {len(good_windows)}")
            logger.info(f"   Summary: {summary}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in get planting calendar: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการสร้างปฏิทินการปลูก: {str(e)}"
            }


# Global function handler instance
function_handler = GeminiFunctionHandler()

logger.info("📦 Gemini Functions loaded successfully")

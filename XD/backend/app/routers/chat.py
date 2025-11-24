# -*- coding: utf-8 -*-
"""
Chat endpoints with Gemini AI
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
import logging
import re
from sqlalchemy.orm import Session
import google.generativeai as genai
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, ChatSession, User
from cache import cache
from config import GEMINI_API_KEY
from utils.constants import AGRI_PERSONA
from utils.helpers import get_crop_name_from_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Import Gemini functions
from gemini_functions import GEMINI_FUNCTIONS, function_handler

# Import services
from app.services.prompt_builder_service import prompt_builder_service
from app.services.response_formatter_service import response_formatter

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Data Schemas
class ChatRequest(BaseModel):
    query: str                   # คำถามจากผู้ใช้
    crop_id: int                 # เลือกพืช (required)
    price_history: List[float]   # ราคาย้อนหลัง
    weather: List[float]         # [ฝน, อุณหภูมิ]
    crop_info: List[int]         # [soil_type_id, water_level, season_id]
    calendar: List[int]          # [is_festival, is_holiday, season_id]
    user_id: Optional[int] = None  # User ID for personalization

@router.post("")
def chat_with_gemini(data: ChatRequest, db: Session = Depends(get_db)):
    """
    Enhanced Chat Q&A with user profile integration and Redis caching
    """
    try:
        # 1. Get user profile if user_id provided
        user_profile = None
        user_context = ""
        
        if data.user_id:
            # Try to get from Redis cache first
            cached_session = cache.get_session_data(data.user_id)
            
            if cached_session:
                user_profile = cached_session.get("user_profile")
                logger.info(f"Using cached session data for user {data.user_id}")
            else:
                # Get from database
                user = db.query(User).filter(User.id == data.user_id).first()
                if user:
                    user_profile = {
                        "full_name": user.full_name,
                        "province": user.province,
                        "water_availability": user.water_availability,
                        "budget_level": user.budget_level,
                        "experience_crops": json.loads(user.experience_crops) if user.experience_crops else [],
                        "risk_tolerance": user.risk_tolerance,
                        "time_constraint": user.time_constraint,
                        "preference": user.preference,
                        "soil_type": user.soil_type
                    }
                    
                    # Cache the session data
                    session_data = {
                        "user_profile": user_profile,
                        "last_updated": datetime.now().isoformat()
                    }
                    cache.set_session_data(data.user_id, session_data, ttl_hours=24)
                    logger.info(f"Cached session data for user {data.user_id}")
            
            # Build user context for Gemini
            if user_profile:
                user_context = f"""
**ข้อมูลเกษตรกร:**
- ชื่อ: {user_profile.get('full_name', 'N/A')}
- จังหวัด: {user_profile.get('province', 'N/A')}
- แหล่งน้ำ: {user_profile.get('water_availability', 'N/A')}
- งบประมาณ: {user_profile.get('budget_level', 'N/A')}
- ประสบการณ์ปลูก: {', '.join(user_profile.get('experience_crops', [])) if user_profile.get('experience_crops') else 'ยังไม่มีข้อมูล'}
- ความเสี่ยง: {user_profile.get('risk_tolerance', 'N/A')}
- ประเภทดิน: {user_profile.get('soil_type', 'N/A')}
"""

        # 2. Get conversation history from database (last 3 messages)
        conversation_history = []
        if data.user_id:
            try:
                recent_chats = db.query(ChatSession)\
                    .filter(ChatSession.user_query.isnot(None))\
                    .order_by(ChatSession.created_at.desc())\
                    .limit(3)\
                    .all()
                
                for chat in reversed(recent_chats):  # Reverse to get chronological order
                    conversation_history.append({
                        "role": "user",
                        "content": chat.user_query
                    })
                    conversation_history.append({
                        "role": "assistant",
                        "content": chat.gemini_response[:200]  # Limit length
                    })
                
                logger.info(f"📜 Loaded {len(conversation_history)} conversation history items")
            except Exception as e:
                logger.warning(f"Could not load conversation history: {e}")
        
        # 3. Build context using PromptBuilderService
        crop_name = get_crop_name_from_id(data.crop_id)
        context = prompt_builder_service.build_context(
            query=data.query,
            user_profile=user_profile,
            conversation_history=conversation_history,
            crop_name=crop_name
        )

        # 4. Check Gemini API key
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            logger.error("❌ Gemini API key not configured!")
            return {
                "text": "ขออภัยครับ ระบบ AI ยังไม่ได้ตั้งค่า API key กรุณาติดต่อผู้ดูแลระบบ",
                "chart_data": None,
                "function_called": None,
                "function_result": None,
                "session_id": None,
                "cached_data_used": False
            }
        
        # 5. Initialize Gemini WITH function calling
        try:
            # Use gemini-pro for v1beta API (supports function calling)
            gemini_model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=AGRI_PERSONA,
                tools=GEMINI_FUNCTIONS
            )
            logger.info(f"✅ Gemini model initialized with {len(GEMINI_FUNCTIONS)} functions")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            return {
                "text": "ขออภัยครับ ระบบ AI ไม่สามารถใช้งานได้ในขณะนี้ กรุณาลองใหม่ภายหลัง",
                "chart_data": None,
                "function_called": None,
                "function_result": None,
                "session_id": None,
                "cached_data_used": False
            }
        
        # 6. Send to Gemini with function calling (but format response ourselves)
        function_called = None
        function_result = None
        formatted_response = ""
        
        try:
            response = gemini_model.generate_content(
                context,
                request_options={"timeout": 30}
            )
            
            if not response:
                raise Exception("ไม่ได้รับคำตอบจาก Gemini")
            
            # Check if Gemini wants to call a function
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        logger.info(f"🔧 Gemini called function: {function_name}")
                        logger.info(f"📝 Function args: {function_args}")
                        
                        # Execute the function
                        function_result = function_handler.execute_function(function_name, function_args)
                        function_called = function_name
                        
                        # Send result back to LLM using SIMPLE PROMPT (not function response protocol)
                        # This avoids the format response error
                        if function_result.get("success"):
                            logger.info(f"✅ Function executed successfully, sending to LLM for formatting")
                            
                            # Create simple prompt with function result
                            simple_prompt = f"""คุณเป็นผู้ช่วยด้านเกษตรที่เป็นมิตร ได้รับข้อมูลจาก ML Model แล้ว กรุณาอธิบายผลลัพธ์ให้เกษตรกรฟังอย่างเข้าใจง่าย เป็นกันเอง และให้คำแนะนำที่เป็นประโยชน์

คำถามเดิม: {data.query}

ข้อมูลจาก ML Model ({function_name}):
{json.dumps(function_result, ensure_ascii=False, indent=2)}

กรุณาตอบเป็นภาษาไทยที่เข้าใจง่าย ไม่ต้องแสดง JSON ให้อธิบายเป็นประโยคธรรมดา"""
                            
                            try:
                                # Send to LLM with simple prompt
                                llm_response = gemini_model.generate_content(
                                    simple_prompt,
                                    request_options={"timeout": 30}
                                )
                                formatted_response = llm_response.text.strip()
                                logger.info(f"✅ LLM formatted response successfully")
                            except Exception as e:
                                logger.error(f"❌ LLM formatting failed: {e}")
                                # Fallback to JSON if LLM fails
                                formatted_response = f"ได้รับข้อมูลจาก ML Model แล้ว:\n\n{json.dumps(function_result, ensure_ascii=False, indent=2)}"
                        else:
                            formatted_response = f"ขออภัยครับ เกิดข้อผิดพลาด: {function_result.get('error', 'Unknown error')}"
                            logger.warning(f"⚠️ Function returned error")
                        
                        break
                else:
                    # No function call - direct response
                    formatted_response = response.text.strip() if response.text else "ขออภัยครับ ไม่สามารถสร้างคำตอบได้"
            else:
                formatted_response = response.text.strip() if response.text else "ขออภัยครับ ไม่สามารถสร้างคำตอบได้"
                
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}", exc_info=True)
            formatted_response = f"ขออภัยครับ ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"
        
        # 7. Format response for better readability
        # Remove excessive blank lines (more than 2 consecutive)
        formatted_response = re.sub(r'\n{3,}', '\n\n', formatted_response)
        
        # 8. Format response with chart data
        response_data = response_formatter.format_with_chart(
            text_response=formatted_response,
            function_result=function_result,
            function_name=function_called
        )

        # 9. Save chat session to database
        session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        chat_record = ChatSession(
            session_id=session_id,
            user_query=data.query,
            gemini_response=response_data["text"],
            crop_id=data.crop_id,
            forecast_data=json.dumps(response_data["chart_data"]) if response_data["chart_data"] else None,
            created_at=datetime.now()
        )
        db.add(chat_record)
        db.commit()

        logger.info(f"Chat session saved: {session_id}")
        logger.info(f"📊 Chart data included: {response_data['has_chart']}")
        
        return {
            "session_id": session_id,
            "query": data.query,
            "gemini_answer": response_data["text"],
            "chart_data": response_data["chart_data"],
            "function_called": function_called,
            "function_result": function_result if function_called else None,
            "user_profile_used": user_profile is not None,
            "cached_data_used": cached_session is not None if data.user_id else False
        }
    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return error response instead of raising exception
        return {
            "session_id": None,
            "query": data.query if hasattr(data, 'query') else "",
            "gemini_answer": f"ขออภัย เกิดข้อผิดพลาดในการประมวลผล: {type(e).__name__} - {str(e)}",
            "chart_data": None,
            "function_called": None,
            "function_result": None,
            "user_profile_used": False,
            "cached_data_used": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
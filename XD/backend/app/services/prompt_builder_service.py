# -*- coding: utf-8 -*-
"""
Prompt Builder Service
สร้าง context และวิเคราะห์ความตั้งใจของคำถามสำหรับ Gemini AI
"""

import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Intent patterns สำหรับวิเคราะห์ความตั้งใจ
INTENT_PATTERNS = {
    "price_prediction": [
        r"ราคา.{0,20}(?:จะ|คาด|ทำนาย|พยากรณ์|อนาคต|ข้างหน้า)",
        r"(?:ขาย|เก็บเกี่ยว).{0,20}(?:เมื่อไหร่|ตอนไหน|ช่วงไหน|เวลาไหน)",
        r"แนวโน้ม.{0,10}ราคา",
        r"ราคา.{0,20}(?:ขึ้น|ลง|เป็นยังไง|เท่าไหร่|เท่าไร)",
        r"(?:ควร|น่าจะ).{0,10}ขาย.{0,10}(?:เมื่อไหร่|ตอนไหน)",
        r"ราคา.{0,10}(?:30|60|90|180).{0,10}วัน",
        r"ราคา.{0,10}(?:เดือน|สัปดาห์).{0,10}(?:หน้า|ข้างหน้า)",
    ],
    "crop_recommendation": [
        r"(?:ควร|น่าจะ|แนะนำ).{0,20}ปลูก.{0,10}(?:อะไร|ไหน|พืช)",
        r"ปลูก.{0,20}(?:ดี|เหมาะสม|คุ้ม|ได้กำไร)",
        r"พืช.{0,20}(?:เหมาะสม|แนะนำ|ดี)",
        r"(?:อยาก|จะ).{0,10}ปลูก.{0,10}(?:อะไร|พืช)",
        r"เลือก.{0,10}พืช",
    ],
    "water_management": [
        r"(?:รด|ให้|จัดการ).{0,10}น้ำ",
        r"น้ำ.{0,20}(?:บ่อย|ครั้ง|วัน|เท่าไหร่|เท่าไร)",
        r"(?:ความถี่|ปริมาณ).{0,10}(?:รด|ให้).{0,10}น้ำ",
        r"ระบบ.{0,10}(?:รด|ให้).{0,10}น้ำ",
    ],
    "planting_window": [
        r"(?:ควร|น่าจะ).{0,10}ปลูก.{0,10}(?:เมื่อไหร่|ตอนไหน|ช่วงไหน)",
        r"(?:ช่วง|เวลา).{0,10}(?:ปลูก|เพาะ)",
        r"ปลูก.{0,10}(?:ตอนนี้|เดี๋ยวนี้|ตอนนี้).{0,10}(?:ได้|ดี|เหมาะสม)",
        r"(?:เหมาะสม|ดี).{0,10}(?:ปลูก|เพาะ)",
        r"ฤดู.{0,10}(?:ปลูก|เพาะ)",
    ],
    "harvest_decision": [
        r"(?:ควร|น่าจะ).{0,10}(?:เก็บเกี่ยว|เก็บ|ขาย).{0,10}(?:เมื่อไหร่|ตอนไหน|เลย|รอ)",
        r"(?:เก็บเกี่ยว|เก็บ).{0,10}(?:เลย|ตอนนี้|รอ)",
        r"ขาย.{0,10}(?:เลย|ตอนนี้|รอ)",
        r"รอ.{0,10}(?:ขาย|เก็บเกี่ยว)",
        r"(?:กำไร|ได้เงิน).{0,10}(?:สูงสุด|มากสุด)",
    ]
}

# คำที่บ่งบอกว่าต้องการเห็นกราฟ
CHART_KEYWORDS = [
    "กราฟ", "แสดง", "ดู", "เห็น", "chart", "graph", "show", "visualize",
    "แนวโน้ม", "trend", "เปรียบเทียบ", "compare"
]


class PromptBuilderService:
    """Service สำหรับสร้าง prompt และวิเคราะห์ความตั้งใจของคำถาม"""
    
    def __init__(self):
        logger.info("✅ PromptBuilderService initialized")
    
    def build_context(
        self,
        query: str,
        user_profile: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
        crop_name: Optional[str] = None
    ) -> str:
        """
        สร้าง context ที่สมบูรณ์สำหรับ Gemini
        
        Args:
            query: คำถามจากผู้ใช้
            user_profile: ข้อมูลโปรไฟล์ผู้ใช้
            conversation_history: ประวัติการสนทนา (list of {role, content})
            crop_name: ชื่อพืชที่สนใจ
            
        Returns:
            Context string ที่จัดรูปแบบแล้ว
        """
        context_parts = []
        
        # 1. คำถามหลัก
        context_parts.append(f"คำถามจากเกษตรกร: {query}")
        
        # 2. ประวัติการสนทนา (3 ข้อความล่าสุด)
        if conversation_history and len(conversation_history) > 0:
            context_parts.append("\nบริบทการสนทนาก่อนหน้า:")
            for msg in conversation_history[-3:]:
                role = "เกษตรกร" if msg.get("role") == "user" else "AI"
                content = msg.get("content", "")[:100]  # จำกัดความยาว
                context_parts.append(f"- {role}: {content}")
        
        # 3. ข้อมูลโปรไฟล์ผู้ใช้
        if user_profile:
            profile_info = []
            if user_profile.get("full_name"):
                profile_info.append(f"ชื่อ: {user_profile['full_name']}")
            if user_profile.get("province"):
                profile_info.append(f"จังหวัด: {user_profile['province']}")
            if user_profile.get("soil_type"):
                profile_info.append(f"ประเภทดิน: {user_profile['soil_type']}")
            if user_profile.get("water_availability"):
                profile_info.append(f"แหล่งน้ำ: {user_profile['water_availability']}")
            if user_profile.get("budget_level"):
                profile_info.append(f"งบประมาณ: {user_profile['budget_level']}")
            
            if profile_info:
                context_parts.append("\nข้อมูลเกษตรกร:")
                context_parts.append(", ".join(profile_info))
        
        # 4. พืชที่สนใจ
        if crop_name:
            context_parts.append(f"\nพืชที่สนใจ: {crop_name}")
        
        # 5. วิเคราะห์ความตั้งใจและให้คำแนะนำ
        intent = self.analyze_intent(query)
        instructions = self.format_response_instruction(intent)
        context_parts.append(f"\n{instructions}")
        
        return "\n".join(context_parts)
    
    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        วิเคราะห์ความตั้งใจของคำถาม
        
        Args:
            query: คำถามจากผู้ใช้
            
        Returns:
            {
                "intent": str,  # "price_prediction", "crop_recommendation", "water_management", "general"
                "confidence": float,  # 0.0 - 1.0
                "requires_chart": bool,
                "entities": dict  # ข้อมูลที่แยกได้จากคำถาม
            }
        """
        query_lower = query.lower()
        intent_scores = {}
        
        # คำนวณคะแนนสำหรับแต่ละ intent
        for intent_type, patterns in INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent_type] = score
        
        # หา intent ที่มีคะแนนสูงสุด
        if max(intent_scores.values()) > 0:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / len(INTENT_PATTERNS[primary_intent]), 1.0)
        else:
            primary_intent = "general"
            confidence = 0.5
        
        # ตรวจสอบว่าต้องการกราฟหรือไม่
        requires_chart = any(keyword in query_lower for keyword in CHART_KEYWORDS)
        
        # ถ้าถามเรื่องราคา มักจะต้องการกราฟ
        if primary_intent == "price_prediction":
            requires_chart = True
        
        # แยก entities จากคำถาม
        entities = self._extract_entities(query)
        
        result = {
            "intent": primary_intent,
            "confidence": confidence,
            "requires_chart": requires_chart,
            "entities": entities
        }
        
        logger.info(f"🔍 Intent analysis: {result}")
        return result
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """แยกข้อมูลสำคัญจากคำถาม เช่น จำนวนวัน, จังหวัด"""
        entities = {}
        
        # แยกจำนวนวัน
        days_patterns = [
            r"(\d+)\s*วัน",
            r"(\d+)\s*days?",
        ]
        for pattern in days_patterns:
            match = re.search(pattern, query)
            if match:
                entities["days_ahead"] = int(match.group(1))
                break
        
        # แยกช่วงเวลา (เดือน, สัปดาห์)
        if "เดือน" in query or "month" in query.lower():
            if not entities.get("days_ahead"):
                entities["days_ahead"] = 30
        elif "สัปดาห์" in query or "week" in query.lower():
   
          if not entities.get("days_ahead"):
                entities["days_ahead"] = 7
        
        return entities
    
    def format_response_instruction(self, intent: Dict[str, Any]) -> str:
        """
        สร้างคำแนะนำการตอบตามความตั้งใจ
        
        Args:
            intent: ผลจากการวิเคราะห์ความตั้งใจ
            
        Returns:
            คำแนะนำสำหรับ Gemini
        """
        intent_type = intent.get("intent", "general")
        requires_chart = intent.get("requires_chart", False)
        
        instructions = []
        
        # คำแนะนำทั่วไป
        instructions.append("วิธีการตอบ:")
        instructions.append("• อ่านโทนและความยาวของคำถาม")
        instructions.append("• ถ้าคำถามสั้น (1-5 คำ) ตอบสั้นๆ 1-2 ประโยค")
        instructions.append("• ถ้าคำถามยาวหรือซับซ้อน ตอบละเอียดแต่แบ่งเป็นหัวข้อย่อย")
        instructions.append("• ใช้ภาษาพูดที่เป็นธรรมชาติ ไม่เป็นทางการเกินไป")
        instructions.append("• ห้ามใช้ markdown formatting (**, __, etc.)")
        instructions.append("• ใช้อิโมจิเพื่อเน้นจุดสำคัญ (🌾 ☀️ 💧 📊 ✅ ⚠️)")
        
        # คำแนะนำเฉพาะตาม intent
        if intent_type == "price_prediction":
            instructions.append("\n⚠️ คำถามนี้เกี่ยวกับการทำนายราคา:")
            instructions.append("• ⚡ สำคัญ: ถ้ามีข้อมูล province ในโปรไฟล์ผู้ใช้ ให้เรียกใช้ function get_price_prediction ทันที")
            instructions.append("• ถ้าไม่มี province ให้ใช้ province จากโปรไฟล์ผู้ใช้ หรือใช้ 'กรุงเทพมหานคร' เป็นค่าเริ่มต้น")
            instructions.append("• ระบุ crop_type (จากพืชที่สนใจ), province, และ days_ahead (ถ้าไม่ระบุใช้ 30)")
            instructions.append("• อธิบายแนวโน้มราคาอย่างชัดเจน")
            instructions.append("• แนะนำช่วงเวลาที่เหมาะสมในการขาย")
            if requires_chart:
                instructions.append("• ระบบจะแสดงกราฟให้ผู้ใช้เห็นโดยอัตโนมัติ")
        
        elif intent_type == "crop_recommendation":
            instructions.append("\n⚠️ คำถามนี้เกี่ยวกับการแนะนำพืช:")
            instructions.append("• เรียกใช้ function get_crop_recommendations")
            instructions.append("• ใช้ข้อมูลโปรไฟล์ผู้ใช้ (province, soil_type, water_availability, budget_level)")
            instructions.append("• แนะนำพืช 2-3 ชนิดที่เหมาะสม")
            instructions.append("• อธิบายเหตุผลว่าทำไมเหมาะสม")
        
        elif intent_type == "water_management":
            instructions.append("\n⚠️ คำถามนี้เกี่ยวกับการจัดการน้ำ:")
            instructions.append("• เรียกใช้ function get_water_management_advice")
            instructions.append("• ระบุ crop_type และ province")
            instructions.append("• แนะนำความถี่และปริมาณน้ำ")
            instructions.append("• แนะนำวิธีการให้น้ำที่เหมาะสม")
        
        elif intent_type == "planting_window":
            instructions.append("\n⚠️ คำถามนี้เกี่ยวกับช่วงเวลาปลูก:")
            instructions.append("• เรียกใช้ function get_planting_window_advice")
            instructions.append("• ระบุ crop_type และ province")
            instructions.append("• บอกว่าช่วงนี้เหมาะสมหรือไม่")
            instructions.append("• แนะนำช่วงเวลาที่ดีที่สุด")
        
        elif intent_type == "harvest_decision":
            instructions.append("\n⚠️ คำถามนี้เกี่ยวกับการตัดสินใจเก็บเกี่ยว:")
            instructions.append("• เรียกใช้ function get_harvest_decision")
            instructions.append("• ระบุ crop_type, province, และ current_price (ถ้ามี)")
            instructions.append("• แนะนำว่าควรเก็บเกี่ยวเลยหรือรอ")
            instructions.append("• อธิบายกำไรที่คาดหวังจากแต่ละทางเลือก")
        
        else:
            instructions.append("\n💬 คำถามทั่วไป:")
            instructions.append("• ตอบด้วยความรู้ทั่วไปเกี่ยวกับการเกษตร")
            instructions.append("• ไม่จำเป็นต้องเรียกใช้ function")
            instructions.append("• ให้คำแนะนำที่เป็นประโยชน์และปฏิบัติได้จริง")
        
        return "\n".join(instructions)
    
    def should_use_function(self, intent: Dict[str, Any]) -> bool:
        """
        ตรวจสอบว่าควรเรียกใช้ function หรือไม่
        
        Args:
            intent: ผลจากการวิเคราะห์ความตั้งใจ
            
        Returns:
            True ถ้าควรเรียกใช้ function
        """
        intent_type = intent.get("intent", "general")
        confidence = intent.get("confidence", 0.0)
        
        # ถ้า confidence ต่ำเกินไป ไม่ควรเรียกใช้ function
        if confidence < 0.3:
            return False
        
        # Intent ที่ควรเรียกใช้ function
        function_intents = ["price_prediction", "crop_recommendation", "water_management"]
        
        return intent_type in function_intents


# Global instance
prompt_builder_service = PromptBuilderService()

if __name__ == "__main__":
    # ทดสอบ service
    test_queries = [
        "ราคาพริกอีก 30 วันจะเป็นยังไง",
        "ควรปลูกอะไรดี",
        "รดน้ำบ่อยแค่ไหน",
        "สวัสดีครับ",
        "แสดงกราฟราคามะเขือเทศให้หน่อย",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        intent = prompt_builder_service.analyze_intent(query)
        print(f"Intent: {intent['intent']} (confidence: {intent['confidence']:.2f})")
        print(f"Requires chart: {intent['requires_chart']}")
        print(f"Should use function: {prompt_builder_service.should_use_function(intent)}")

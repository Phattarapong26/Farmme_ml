# Design Document

## Overview

ออกแบบการปรับปรุงระบบ Chat AI ให้มีความเป็นธรรมชาติมากขึ้นและสามารถแสดงกราฟทำนายราคาได้ โดยแบ่งเป็น 3 ส่วนหลัก:

1. **Prompt Engineering** - ปรับปรุง system prompt และ context building
2. **Chart Visualization** - สร้าง component แสดงกราฟใน chat
3. **Response Enhancement** - ปรับปรุงการจัดการ response จาก Gemini

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
├─────────────────────────────────────────────────────────────┤
│  ChatInterface                                               │
│    ├─ MessageList                                           │
│    │   ├─ TextMessage                                       │
│    │   └─ ChartMessage (NEW)                                │
│    │       └─ PriceForecastChart                            │
│    └─ ChatInput                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /chat
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│  chat.py (Router)                                           │
│    ├─ Enhanced Prompt Builder (NEW)                         │
│    ├─ Context Analyzer (NEW)                                │
│    └─ Response Formatter (ENHANCED)                         │
│                                                              │
│  Gemini Function Calling                                    │
│    ├─ get_price_prediction                                  │
│    ├─ get_crop_recommendations                              │
│    └─ get_water_management_advice                           │
│                                                              │
│  Services                                                    │
│    ├─ price_forecast_service.py                             │
│    ├─ recommendation_model_service.py                        │
│    └─ water_management_service.py                           │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Enhanced Prompt System

#### 1.1 Prompt Builder Service

```python
class PromptBuilderService:
    """สร้าง prompt ที่เหมาะสมตามบริบทของคำถาม"""
    
    def build_context(
        self,
        query: str,
        user_profile: Optional[Dict],
        conversation_history: List[Dict]
    ) -> str:
        """
        สร้าง context สำหรับ Gemini
        
        Returns:
            Formatted context string
        """
        pass
    
    def analyze_intent(self, query: str) -> Dict:
        """
        วิเคราะห์ความตั้งใจของคำถาม
        
        Returns:
            {
                "intent": "price_prediction" | "crop_recommendation" | "water_management" | "general",
                "entities": {
                    "crop_type": str,
                    "province": str,
                    "timeframe": int
                },
                "requires_chart": bool
            }
        """
        pass
    
    def format_response_instruction(self, intent: Dict) -> str:
        """สร้างคำแนะนำการตอบตามความตั้งใจ"""
        pass
```

#### 1.2 Enhanced System Persona

ปรับปรุง `AGRI_PERSONA` ใน `utils/constants.py`:

- เพิ่มความเป็นธรรมชาติในการสนทนา
- ลดการใช้ markdown formatting
- เพิ่มความสามารถในการเข้าใจบริบท
- ปรับความยาวคำตอบให้เหมาะสมกับคำถาม

### 2. Chart Visualization Component

#### 2.1 ChartMessage Component (Frontend)

```typescript
interface ChartMessageProps {
  chartData: {
    type: 'price_forecast';
    data: {
      historical: Array<{date: string; price: number}>;
      forecast: Array<{date: string; price: number; confidence_low: number; confidence_high: number}>;
      metadata: {
        crop_type: string;
        province: string;
        days_ahead: number;
      };
    };
  };
  textResponse: string;
}

const ChartMessage: React.FC<ChartMessageProps> = ({ chartData, textResponse }) => {
  // แสดงข้อความและกราฟ
  return (
    <div className="chart-message">
      <div className="text-content">{textResponse}</div>
      <div className="chart-container">
        <PriceForecastChart data={chartData.data} />
      </div>
    </div>
  );
};
```

#### 2.2 PriceForecastChart Component

```typescript
interface PriceForecastChartProps {
  data: {
    historical: Array<{date: string; price: number}>;
    forecast: Array<{date: string; price: number; confidence_low: number; confidence_high: number}>;
    metadata: {
      crop_type: string;
      province: string;
      days_ahead: number;
    };
  };
}

const PriceForecastChart: React.FC<PriceForecastChartProps> = ({ data }) => {
  // ใช้ Recharts หรือ Chart.js
  // แสดงกราฟแบบ line chart พร้อม confidence interval
  // มี bridge point เชื่อมต่อระหว่างข้อมูลจริงและทำนาย
};
```

### 3. Response Enhancement

#### 3.1 Response Formatter

```python
class ResponseFormatter:
    """จัดรูปแบบ response จาก Gemini"""
    
    def format_with_chart(
        self,
        text_response: str,
        function_result: Dict,
        function_name: str
    ) -> Dict:
        """
        จัดรูปแบบ response พร้อมข้อมูลกราฟ
        
        Returns:
            {
                "text": str,
                "chart_data": Optional[Dict],
                "has_chart": bool
            }
        """
        pass
    
    def extract_chart_data(self, function_result: Dict) -> Optional[Dict]:
        """แยกข้อมูลกราฟจาก function result"""
        pass
```

#### 3.2 Enhanced Chat Response

```python
{
    "session_id": str,
    "query": str,
    "gemini_answer": str,
    "chart_data": Optional[{
        "type": "price_forecast",
        "data": {
            "historical": [...],
            "forecast": [...],
            "metadata": {...}
        }
    }],
    "function_called": Optional[str],
    "user_profile_used": bool
}
```

## Data Models

### Chat Response Model

```python
class ChatResponse(BaseModel):
    session_id: str
    query: str
    gemini_answer: str
    chart_data: Optional[ChartData] = None
    function_called: Optional[str] = None
    user_profile_used: bool = False
    cached_data_used: bool = False

class ChartData(BaseModel):
    type: Literal["price_forecast"]
    data: PriceForecastData

class PriceForecastData(BaseModel):
    historical: List[PricePoint]
    forecast: List[ForecastPoint]
    metadata: ChartMetadata

class PricePoint(BaseModel):
    date: str
    price: float

class ForecastPoint(BaseModel):
    date: str
    price: float
    confidence_low: float
    confidence_high: float

class ChartMetadata(BaseModel):
    crop_type: str
    province: str
    days_ahead: int
    model_used: str
    confidence: float
```

## Prompt Engineering Strategy

### 1. Natural Conversation Patterns

**ปัจจุบัน:**
```
คำแนะนำในการตอบ:
1. ใช้ข้อมูลโปรไฟล์เกษตรกรเพื่อให้คำแนะนำที่เหมาะสม
2. ถ้าผู้ใช้ถามเรื่องการแนะนำพืช ให้เรียกใช้ function...
```

**ปรับปรุงเป็น:**
```
วิธีการสนทนา:
• อ่านโทนและบริบทของคำถาม
• ถ้าคำถามสั้น (1-5 คำ) ตอบสั้นๆ 1-2 ประโยค
• ถ้าคำถามยาวหรือซับซ้อน ตอบละเอียดแต่แบ่งเป็นหัวข้อย่อย
• ใช้ภาษาพูดที่เป็นธรรมชาติ ไม่เป็นทางการเกินไป
• แสดงความเห็นอกเห็นใจและให้กำลังใจ

ตัวอย่างการตอบ:
❌ ไม่ดี: "ตามข้อมูลที่วิเคราะห์จากระบบ พบว่าราคาพริกมีแนวโน้มเพิ่มขึ้น 15% ในช่วง 30 วันข้างหน้า..."
✅ ดี: "ราคาพริกน่าจะขึ้นนะครับ ประมาณ 15% ในเดือนหน้า ถ้าเก็บเกี่ยวได้แล้วอาจจะรอขายอีกสักพักดีกว่า"
```

### 2. Intent Recognition

เพิ่มความสามารถในการเข้าใจคำถามที่หลากหลาย:

```python
INTENT_PATTERNS = {
    "price_prediction": [
        r"ราคา.*(?:จะ|คาด|ทำนาย|พยากรณ์)",
        r"(?:ขาย|เก็บเกี่ยว).*(?:เมื่อไหร่|ตอนไหน)",
        r"แนวโน้ม.*ราคา",
        r"ราคา.*(?:ขึ้น|ลง|เป็นยังไง)",
    ],
    "crop_recommendation": [
        r"(?:ควร|น่าจะ|แนะนำ).*ปลูก.*(?:อะไร|ไหน)",
        r"ปลูก.*(?:ดี|เหมาะสม|คุ้ม)",
        r"พืช.*(?:เหมาะสม|แนะนำ)",
    ],
    "water_management": [
        r"(?:รด|ให้).*น้ำ",
        r"น้ำ.*(?:บ่อย|ครั้ง|วัน)",
        r"จัดการ.*น้ำ",
    ]
}
```

### 3. Context Building

```python
def build_enhanced_context(query, user_profile, history):
    context_parts = []
    
    # 1. User query with emphasis
    context_parts.append(f"คำถามจากเกษตรกร: {query}")
    
    # 2. Conversation history (last 3 messages)
    if history:
        context_parts.append("\nบริบทการสนทนาก่อนหน้า:")
        for msg in history[-3:]:
            context_parts.append(f"- {msg['role']}: {msg['content'][:100]}")
    
    # 3. User profile (if available)
    if user_profile:
        context_parts.append(f"\nข้อมูลเกษตรกร: {user_profile['full_name']} จาก {user_profile['province']}")
    
    # 4. Intent-specific instructions
    intent = analyze_intent(query)
    if intent['requires_chart']:
        context_parts.append("\n⚠️ คำถามนี้ต้องการข้อมูลกราฟ - เรียกใช้ function ที่เหมาะสม")
    
    return "\n".join(context_parts)
```

## Error Handling

### 1. Gemini API Errors

```python
try:
    response = gemini_model.generate_content(context, request_options={"timeout": 30})
except Exception as e:
    if "quota" in str(e).lower():
        return fallback_response("ระบบ AI ใช้งานหนักในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    elif "timeout" in str(e).lower():
        return fallback_response("ระบบตอบสนองช้า กรุณารอสักครู่แล้วลองใหม่")
    else:
        return fallback_response("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง")
```

### 2. Function Call Errors

```python
if not function_result.get("success"):
    # ให้ Gemini จัดการ error แทนที่จะ return error ทันที
    # Gemini จะอธิบายปัญหาด้วยภาษาที่เป็นธรรมชาติ
    pass
```

### 3. Chart Data Errors

```python
if chart_data and not validate_chart_data(chart_data):
    logger.warning("Invalid chart data, removing from response")
    chart_data = None
```

## Testing Strategy

### 1. Unit Tests

- Test prompt builder service
- Test intent recognition
- Test response formatter
- Test chart data extraction

### 2. Integration Tests

- Test chat endpoint with various queries
- Test function calling flow
- Test chart data generation
- Test error handling

### 3. User Acceptance Tests

- Test natural conversation flow
- Test chart visualization
- Test mobile responsiveness
- Test various question patterns

## Performance Considerations

### 1. Response Time

- Gemini API timeout: 30 seconds
- Function execution timeout: 15 seconds
- Total response time target: < 5 seconds

### 2. Caching

- Cache user profiles (24 hours)
- Cache conversation history (session-based)
- Cache ML model predictions (1 hour)

### 3. Frontend Performance

- Lazy load chart library
- Debounce user input
- Show loading indicators
- Progressive rendering

## Security Considerations

1. **Input Validation**: Validate all user inputs before processing
2. **SQL Injection**: Use parameterized queries
3. **XSS Protection**: Sanitize text responses
4. **Rate Limiting**: Limit requests per user
5. **API Key Protection**: Never expose Gemini API key to frontend

## Deployment Strategy

### Phase 1: Backend Enhancement
- Deploy prompt improvements
- Deploy response formatter
- Test with existing frontend

### Phase 2: Frontend Enhancement
- Deploy chart components
- Deploy enhanced chat interface
- A/B test with users

### Phase 3: Optimization
- Monitor performance
- Gather user feedback
- Iterate on improvements

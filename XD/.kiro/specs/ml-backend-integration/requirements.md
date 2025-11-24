# Requirements Document

## Introduction

ระบบ ML Backend Integration เป็นการแทนที่ legacy models และ mock data ใน Backend FastAPI ด้วยโมเดล ML จริงทั้ง 4 ตัว (Model A: Crop Recommendation, Model B: Planting Window, Model C: Price Forecast, Model D: Harvest Decision) จาก REMEDIATION_PRODUCTION เพื่อให้ Frontend ได้รับคำแนะนำที่แม่นยำและมีประสิทธิภาพสูงจากโมเดลที่ผ่านการ train และ validate แล้ว โดยจะแทนที่ existing model services (recommendation_model_service, planting_model_service, price_prediction_service) และ legacy ModelService

## Glossary

- **Backend_API**: FastAPI application ที่อยู่ใน backend/ folder
- **REMEDIATION_PRODUCTION**: โฟลเดอร์ที่เก็บโมเดล ML ทั้ง 4 ตัวที่ train เสร็จแล้ว
- **Model_A**: Crop Recommendation System (NSGA-II, XGBoost, Random Forest)
- **Model_B**: Planting Window Classifier (XGBoost, Temporal GB, Logistic)
- **Model_C**: Price Forecast System (Time series forecasting)
- **Model_D**: Harvest Decision Engine (Thompson Sampling)
- **Model_Service**: Service class ที่ wrap โมเดล ML และให้ interface สำหรับ API endpoints
- **API_Endpoint**: REST API route ที่ Frontend เรียกใช้
- **Request_Model**: Pydantic model สำหรับ validate request data
- **Response_Model**: Pydantic model สำหรับ format response data
- **Model_Loading**: การโหลดโมเดลที่ train แล้วจาก .pkl files
- **Error_Handling**: การจัดการ error และ fallback mechanisms
- **CORS**: Cross-Origin Resource Sharing สำหรับให้ Frontend เรียก API ได้

## Requirements

### Requirement 1: Model A Integration - Replace Crop Recommendation Service

**User Story:** ในฐานะ Frontend Developer ฉันต้องการให้ existing crop recommendation endpoint ใช้โมเดล ML จริง เพื่อให้เกษตรกรได้รับคำแนะนำที่แม่นยำขึ้น

#### Acceptance Criteria

1. THE Backend_API SHALL replace recommendation_model_service.py implementation ด้วย Model A จาก REMEDIATION_PRODUCTION
2. THE Backend_API SHALL maintain existing endpoint interface ที่ Frontend เรียกใช้อยู่
3. WHEN Frontend ส่ง request พร้อม farm_size_rai, soil_type, soil_ph, budget_baht, farmer_experience_years, THE Backend_API SHALL return top 3 crop recommendations พร้อม roi_percent, risk_score, total_profit_baht, confidence
4. THE Backend_API SHALL load Model_A trained models จาก REMEDIATION_PRODUCTION/trained_models/ (model_a_xgboost.pkl, model_a_rf_ensemble.pkl, model_a_nsga2.pkl)
5. THE Backend_API SHALL use ModelA_XGBoost as primary algorithm และ SHALL fallback to Random Forest ถ้า XGBoost fails
6. THE Backend_API SHALL validate input data using Pydantic Request_Model และ SHALL return 422 error ถ้า validation fails
7. THE Backend_API SHALL return response ภายใน 3 วินาที
8. THE Backend_API SHALL log all requests และ errors ไปยัง backend/logs/model_a.log

### Requirement 2: Model B Integration - Replace Planting Calendar Service

**User Story:** ในฐานะ Frontend Developer ฉันต้องการให้ existing planting date recommendation endpoint ใช้โมเดล ML จริง เพื่อให้เกษตรกรได้รับคำแนะนำช่วงเวลาปลูกที่แม่นยำขึ้น

#### Acceptance Criteria

1. THE Backend_API SHALL replace planting_model_service.py implementation ด้วย Model B จาก REMEDIATION_PRODUCTION
2. THE Backend_API SHALL maintain existing endpoint `/recommend-planting-date` ที่ Frontend เรียกใช้อยู่
3. WHEN Frontend ส่ง request พร้อม crop_type, province, growth_days, start_date, end_date, THE Backend_API SHALL return planting date recommendations พร้อม classification (Good/Bad), confidence, expected_germination_rate, harvest_date
4. THE Backend_API SHALL load Model_B trained models จาก REMEDIATION_PRODUCTION/trained_models/ (model_b_xgboost.pkl, model_b_temporal_gb.pkl)
5. THE Backend_API SHALL use ModelB_XGBoost as primary algorithm
6. THE Backend_API SHALL add temporal features (month_sin, month_cos, day_sin, day_cos) automatically จาก planting date
7. THE Backend_API SHALL integrate กับ weather data และ soil conditions จาก database
8. THE Backend_API SHALL return response ภายใน 2 วินาที
9. THE Backend_API SHALL cache results สำหรับ same inputs ภายใน 1 ชั่วโมง

### Requirement 3: Model C Integration - Replace Price Prediction Service

**User Story:** ในฐานะ Frontend Developer ฉันต้องการให้ existing price prediction endpoint ใช้โมเดล ML จริง เพื่อให้เกษตรกรได้รับการคาดการณ์ราคาที่แม่นยำขึ้น

#### Acceptance Criteria

1. THE Backend_API SHALL replace price_prediction_service.py implementation ด้วย Model C จาก REMEDIATION_PRODUCTION
2. THE Backend_API SHALL maintain existing price prediction endpoints ที่ Frontend เรียกใช้อยู่
3. WHEN Frontend ส่ง request พร้อม crop_type, province, days_ahead, THE Backend_API SHALL return forecast_price_median, forecast_price_q10, forecast_price_q90, confidence, price_trend, expected_change_percent, expected_revenue
4. THE Backend_API SHALL load Model_C trained model จาก REMEDIATION_PRODUCTION/trained_models/model_c_price_forecast.pkl
5. THE Backend_API SHALL support forecast สำหรับ 1-180 days ahead
6. THE Backend_API SHALL integrate กับ historical price data จาก database (crop_prices table)
7. THE Backend_API SHALL return response ภายใน 2 วินาที
8. THE Backend_API SHALL update model daily โดยอัตโนมัติ ถ้ามี new price data ใน database

### Requirement 4: Model D Integration - Add Harvest Decision Endpoint (New Feature)

**User Story:** ในฐานะ Frontend Developer ฉันต้องการ API endpoint ใหม่สำหรับตัดสินใจเก็บเกี่ยว เพื่อให้เกษตรกรทราบว่าควรเก็บเกี่ยวเลยหรือรอ

#### Acceptance Criteria

1. THE Backend_API SHALL provide NEW POST endpoint `/api/v1/harvest-decision` ที่รับ current context data
2. WHEN Frontend ส่ง request พร้อม current_price, forecast_price_median, forecast_price_std, plant_health_score, yield_kg, storage_cost_per_day, THE Backend_API SHALL return recommended_action (Harvest Now/Wait 3 Days/Wait 7 Days), action_confidence, profit_projections, reasons
3. THE Backend_API SHALL load Model_D trained model จาก REMEDIATION_PRODUCTION/trained_models/model_d_thompson_sampling.pkl
4. THE Backend_API SHALL use Thompson Sampling algorithm สำหรับ decision making
5. THE Backend_API SHALL calculate profit projections สำหรับทั้ง 3 actions
6. THE Backend_API SHALL integrate กับ Model C เพื่อ get price forecast automatically
7. THE Backend_API SHALL return response ภายใน 2 วินาที
8. THE Backend_API SHALL update belief states เมื่อได้รับ feedback จาก actual outcomes (optional endpoint)

### Requirement 5: Model Service Layer

**User Story:** ในฐานะ Backend Developer ฉันต้องการ service layer ที่ wrap โมเดล ML เพื่อให้ง่ายต่อการใช้งานและ maintain

#### Acceptance Criteria

1. THE Backend_API SHALL provide MLModelService class ที่มี methods: load_models(), get_crop_recommendation(), get_planting_window(), get_price_forecast(), get_harvest_decision()
2. THE MLModelService SHALL load all models ตอน application startup
3. THE MLModelService SHALL implement lazy loading ถ้า model ไม่ถูกใช้งาน
4. THE MLModelService SHALL provide get_model_info() method ที่ return model metadata (version, performance metrics, last_updated)
5. THE MLModelService SHALL implement model caching เพื่อไม่ต้อง reload ทุกครั้ง
6. THE MLModelService SHALL handle model loading errors gracefully และ SHALL log errors
7. THE MLModelService SHALL provide health check method ที่ตรวจสอบว่า models loaded successfully

### Requirement 6: Request and Response Models

**User Story:** ในฐานะ Backend Developer ฉันต้องการ Pydantic models สำหรับ validate requests และ format responses เพื่อให้ API มี type safety

#### Acceptance Criteria

1. THE Backend_API SHALL define CropRecommendationRequest model พร้อม fields: farm_size_rai, soil_type, soil_ph, soil_nitrogen, soil_phosphorus, soil_potassium, avg_temperature, avg_rainfall, humidity, budget_baht, farmer_experience_years, water_availability
2. THE Backend_API SHALL define PlantingWindowRequest model พร้อม fields: crop_type, soil_moisture_percent, recent_rainfall_mm, temperature_c, humidity_percent, soil_temperature_c, wind_speed_kmh
3. THE Backend_API SHALL define PriceForecastRequest model พร้อม fields: crop_type, days_ahead, current_price (optional)
4. THE Backend_API SHALL define HarvestDecisionRequest model พร้อม fields: current_price, forecast_price_median, forecast_price_std, plant_health_score, plant_age_days, storage_cost_per_day, yield_kg
5. THE Backend_API SHALL define corresponding Response models สำหรับแต่ละ endpoint
6. THE Backend_API SHALL validate all numeric fields มี reasonable ranges (e.g., farm_size_rai: 1-1000, soil_ph: 4.0-8.5)
7. THE Backend_API SHALL return clear validation error messages เมื่อ input ไม่ valid

### Requirement 7: Error Handling and Fallback

**User Story:** ในฐานะ Backend Developer ฉันต้องการ error handling ที่ดี เพื่อให้ระบบไม่ crash เมื่อเกิด error

#### Acceptance Criteria

1. WHEN model loading fails, THE Backend_API SHALL log error และ SHALL use fallback mock model
2. WHEN prediction fails, THE Backend_API SHALL retry once และ SHALL return error response ถ้ายัง fail
3. THE Backend_API SHALL return HTTP 500 พร้อม error message เมื่อ internal error เกิดขึ้น
4. THE Backend_API SHALL return HTTP 422 พร้อม validation details เมื่อ input validation fails
5. THE Backend_API SHALL return HTTP 404 เมื่อ requested resource ไม่พบ
6. THE Backend_API SHALL implement timeout (10 seconds) สำหรับ model predictions
7. THE Backend_API SHALL log all errors พร้อม stack trace และ request context

### Requirement 8: Model Path Configuration

**User Story:** ในฐานะ DevOps Engineer ฉันต้องการ configuration ที่ชัดเจนสำหรับ model paths เพื่อให้ deploy ได้ง่าย

#### Acceptance Criteria

1. THE Backend_API SHALL read model paths จาก environment variables (MODEL_A_PATH, MODEL_B_PATH, MODEL_C_PATH, MODEL_D_PATH)
2. THE Backend_API SHALL use default paths ถ้า environment variables ไม่ได้ set (../REMEDIATION_PRODUCTION/trained_models/)
3. THE Backend_API SHALL validate ว่า model files exist ก่อน load
4. THE Backend_API SHALL support both absolute และ relative paths
5. THE Backend_API SHALL log model paths ที่ใช้งานตอน startup
6. THE Backend_API SHALL provide /models/paths endpoint ที่ return current model paths
7. THE Backend_API SHALL allow hot reload models โดยไม่ต้อง restart application

### Requirement 9: Replace Existing Legacy Models

**User Story:** ในฐานะ Backend Developer ฉันต้องการแทนที่ legacy models ด้วย ML models จริง เพื่อให้ existing endpoints ใช้โมเดลที่มีประสิทธิภาพสูงขึ้น

#### Acceptance Criteria

1. THE Backend_API SHALL replace recommendation_model_service.py ด้วย MLModelService ที่ใช้ Model A
2. THE Backend_API SHALL replace planting_model_service.py ด้วย MLModelService ที่ใช้ Model B
3. THE Backend_API SHALL replace price_prediction_service.py ด้วย MLModelService ที่ใช้ Model C
4. THE Backend_API SHALL replace legacy ModelService methods ด้วย real ML predictions
5. THE Backend_API SHALL maintain existing endpoint paths (/recommend-planting-date, /models, /predictions) โดยเปลี่ยนเฉพาะ implementation
6. THE Backend_API SHALL use existing database connection สำหรับ historical data
7. THE Backend_API SHALL use existing logging configuration และ CORS middleware
8. THE Backend_API SHALL ensure existing Frontend code ยังทำงานได้โดยไม่ต้องแก้ไข

### Requirement 10: Performance and Caching

**User Story:** ในฐานะ Backend Developer ฉันต้องการให้ API มี performance ดี เพื่อให้ user experience ดี

#### Acceptance Criteria

1. THE Backend_API SHALL cache model predictions สำหรับ identical inputs ภายใน 1 ชั่วโมง
2. THE Backend_API SHALL use in-memory cache (Redis optional) สำหรับ frequently accessed data
3. THE Backend_API SHALL implement request batching ถ้ามี multiple requests พร้อมกัน
4. THE Backend_API SHALL return cached response ภายใน 100ms
5. THE Backend_API SHALL monitor response times และ SHALL log slow requests (> 5 seconds)
6. THE Backend_API SHALL implement rate limiting (100 requests per minute per IP)
7. THE Backend_API SHALL provide /metrics endpoint สำหรับ monitoring

### Requirement 11: Testing and Validation

**User Story:** ในฐานะ QA Engineer ฉันต้องการ tests ที่ครอบคลุม เพื่อให้มั่นใจว่า integration ทำงานถูกต้อง

#### Acceptance Criteria

1. THE Backend_API SHALL provide unit tests สำหรับ MLModelService class
2. THE Backend_API SHALL provide integration tests สำหรับแต่ละ API endpoint
3. THE Backend_API SHALL test error handling scenarios (model not found, invalid input, timeout)
4. THE Backend_API SHALL test fallback mechanisms
5. THE Backend_API SHALL validate response formats match Pydantic models
6. THE Backend_API SHALL test with real model files จาก REMEDIATION_PRODUCTION
7. THE Backend_API SHALL achieve test coverage > 80%

### Requirement 12: Documentation

**User Story:** ในฐานะ Frontend Developer ฉันต้องการ API documentation ที่ชัดเจน เพื่อให้เรียกใช้ API ได้ถูกต้อง

#### Acceptance Criteria

1. THE Backend_API SHALL provide OpenAPI/Swagger documentation ที่ `/docs`
2. THE Backend_API SHALL document all request parameters พร้อม types, ranges, และ examples
3. THE Backend_API SHALL document all response fields พร้อม descriptions
4. THE Backend_API SHALL provide example requests และ responses สำหรับแต่ละ endpoint
5. THE Backend_API SHALL document error codes และ error messages
6. THE Backend_API SHALL provide README.md ใน backend/ folder ที่อธิบาย ML integration
7. THE Backend_API SHALL document environment variables และ configuration options

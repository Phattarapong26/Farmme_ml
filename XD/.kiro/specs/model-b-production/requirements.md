# Requirements Document - Model B Production Wrapper

## Introduction

ปรับปรุง Model B Wrapper (Planting Window Classifier) ให้พร้อมใช้งาน production และทำงานร่วมกับ /chat LLM endpoint ได้อย่างมีประสิทธิภาพ โดยเน้นความเสถียร ความเร็ว และ user experience ที่ดี

## Glossary

- **Model B Wrapper**: Python class ที่ wrap Model B (Gradient Boosting classifier) สำหรับทำนายช่วงเวลาปลูกพืชที่เหมาะสม
- **LLM Chat Endpoint**: FastAPI endpoint `/chat` ที่รับคำถามจากผู้ใช้และตอบกลับผ่าน LLM
- **Weather Data**: ข้อมูลสภาพอากาศจาก weather.csv ที่ใช้ในการทำนาย
- **Planting Window**: ช่วงเวลาที่เหมาะสมสำหรับการปลูกพืช
- **Production-Ready**: โค้ดที่พร้อมใช้งานจริง มี error handling, validation, logging, และ testing ครบถ้วน

## Requirements

### Requirement 1: Code Quality and Maintainability

**User Story:** As a developer, I want clean and maintainable code, so that I can easily debug and extend the wrapper

#### Acceptance Criteria

1. THE Model B Wrapper SHALL remove all duplicate code blocks and consolidate logic into reusable methods
2. THE Model B Wrapper SHALL use consistent naming conventions for all methods and variables
3. THE Model B Wrapper SHALL include docstrings for all public methods with parameter descriptions and return types
4. THE Model B Wrapper SHALL separate concerns by creating dedicated methods for data loading, prediction, and formatting
5. THE Model B Wrapper SHALL remove commented-out code and unused imports

### Requirement 2: Input Validation and Error Handling

**User Story:** As a system, I want robust input validation, so that invalid requests are caught early with clear error messages

#### Acceptance Criteria

1. WHEN a user provides invalid date format, THE Model B Wrapper SHALL return an error response with message "Invalid date format. Expected YYYY-MM-DD"
2. WHEN a user provides missing required parameter (province or planting_date), THE Model B Wrapper SHALL return an error response listing missing parameters
3. WHEN a user provides invalid province name, THE Model B Wrapper SHALL return a warning and use fallback prediction
4. WHEN soil_ph is outside range 0-14, THE Model B Wrapper SHALL return an error response with message "Invalid soil_ph. Must be between 0 and 14"
5. WHEN soil_nutrients is negative, THE Model B Wrapper SHALL return an error response with message "Invalid soil_nutrients. Must be non-negative"
6. THE Model B Wrapper SHALL wrap all prediction logic in try-except blocks with detailed error logging
7. THE Model B Wrapper SHALL never raise unhandled exceptions to the caller

### Requirement 3: Performance Optimization

**User Story:** As a user, I want fast response times, so that I can get recommendations quickly in chat

#### Acceptance Criteria

1. THE Model B Wrapper SHALL cache weather data in memory after first load to avoid repeated file reads
2. THE Model B Wrapper SHALL implement lazy loading for the ML model (load only when first prediction is requested)
3. WHEN weather data is requested for the same province and month multiple times, THE Model B Wrapper SHALL return cached results
4. THE Model B Wrapper SHALL complete a single prediction request within 200 milliseconds on average
5. THE Model B Wrapper SHALL log performance metrics (prediction time) for monitoring

### Requirement 4: Response Format Consistency

**User Story:** As an LLM, I want consistent response format, so that I can reliably parse and present results to users

#### Acceptance Criteria

1. THE Model B Wrapper SHALL return responses in a standardized dictionary format with keys: success, data, error, metadata
2. WHEN prediction is successful, THE Model B Wrapper SHALL include fields: is_good_window, confidence, recommendation, reason, weather, province
3. WHEN prediction fails, THE Model B Wrapper SHALL include fields: success=False, error (message), error_type, timestamp
4. THE Model B Wrapper SHALL format all numeric values to 2 decimal places for consistency
5. THE Model B Wrapper SHALL include metadata in all responses: model_version, prediction_time_ms, model_used

### Requirement 5: Weather Data Integration

**User Story:** As a system, I want reliable weather data access, so that predictions are based on real environmental conditions

#### Acceptance Criteria

1. THE Model B Wrapper SHALL load weather data from CSV file on initialization with error handling
2. WHEN weather data file is missing, THE Model B Wrapper SHALL log a warning and use fallback prediction mode
3. WHEN requesting weather for future dates, THE Model B Wrapper SHALL use historical monthly averages
4. THE Model B Wrapper SHALL normalize province names (handle Thai and English variants) for weather lookup
5. THE Model B Wrapper SHALL support province alias mapping (e.g. กรุงเทพ → กรุงเทพมหานคร, นครปฐม → Nakhon Pathom)
6. THE Model B Wrapper SHALL return weather context (temperature, rainfall, humidity, drought_index) in all predictions

### Requirement 6: LLM-Friendly Output

**User Story:** As an LLM, I want clear and structured output, so that I can generate natural language responses for users

#### Acceptance Criteria

1. THE Model B Wrapper SHALL provide Thai language explanations in the "reason" field
2. THE Model B Wrapper SHALL include actionable recommendations in the "recommendation" field
3. WHEN confidence is below 0.70, THE Model B Wrapper SHALL include a disclaimer in the response
4. THE Model B Wrapper SHALL provide alternative suggestions when prediction is negative (bad window)
5. THE Model B Wrapper SHALL format dates in Thai Buddhist calendar format when requested

### Requirement 7: Logging and Monitoring

**User Story:** As a DevOps engineer, I want comprehensive logging, so that I can monitor system health and debug issues

#### Acceptance Criteria

1. THE Model B Wrapper SHALL log all prediction requests with parameters (excluding sensitive data)
2. THE Model B Wrapper SHALL log model loading status (success/failure) with file path and model type
3. WHEN prediction fails, THE Model B Wrapper SHALL log full error traceback at ERROR level
4. THE Model B Wrapper SHALL log performance metrics (prediction time) at INFO level
5. THE Model B Wrapper SHALL use structured logging with consistent format: timestamp, level, component, message

### Requirement 8: Testing and Validation

**User Story:** As a QA engineer, I want comprehensive tests, so that I can verify the wrapper works correctly

#### Acceptance Criteria

1. THE Model B Wrapper SHALL have a test file (test_model_b_wrapper.py) with unit tests for all public methods
2. THE Model B Wrapper SHALL have tests for valid input scenarios with expected outputs
3. THE Model B Wrapper SHALL have tests for invalid input scenarios with expected error responses
4. THE Model B Wrapper SHALL have tests for edge cases (missing weather data, future dates, extreme values)
5. THE Model B Wrapper SHALL achieve at least 80% code coverage in tests

### Requirement 9: Planting Calendar Feature

**User Story:** As a farmer, I want to see a planting calendar for the next 12 months, so that I can plan my planting schedule

#### Acceptance Criteria

1. THE Model B Wrapper SHALL provide a get_planting_calendar method that analyzes the next N months
2. THE Model B Wrapper SHALL return monthly predictions with confidence scores for each month
3. THE Model B Wrapper SHALL identify consecutive good months as "best planting windows"
4. THE Model B Wrapper SHALL include weather forecasts (historical averages) for each month
5. THE Model B Wrapper SHALL provide a summary in Thai language highlighting the best planting periods

### Requirement 10: Fallback Mechanisms

**User Story:** As a system, I want graceful degradation, so that the service remains available even when ML model fails

#### Acceptance Criteria

1. WHEN ML model fails to load, THE Model B Wrapper SHALL use rule-based prediction as fallback
2. WHEN weather data is unavailable, THE Model B Wrapper SHALL use season-based rules for prediction
3. THE Model B Wrapper SHALL clearly indicate in response which prediction method was used (ml_model, weather_based, rule_based)
4. THE Model B Wrapper SHALL adjust confidence scores based on prediction method (ML: 0.85, Weather: 0.75, Rules: 0.65)
5. THE Model B Wrapper SHALL implement rate limiting on fallback usage to prevent infinite fallback loops (max 3 consecutive fallbacks per minute)
6. THE Model B Wrapper SHALL log fallback usage for monitoring and alerting

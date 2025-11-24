# Requirements Document

## Introduction

สร้าง Model C Wrapper เพื่อให้มี pattern การใช้งานที่สอดคล้องกับ Model A, B และ D Wrappers โดย Model C เป็น Price Prediction Model ที่ใช้ XGBoost และ Hash Encoding ในการทำนายราคาพืชผลในอนาคต ปัจจุบัน Model C ถูกใช้งานผ่าน `price_prediction_service.py` ซึ่งเป็น service layer แต่ไม่มี wrapper ที่เป็นมาตรฐานเหมือน model อื่นๆ

## Glossary

- **Model C**: Price Prediction Model ที่ใช้ XGBoost และ Hash Encoding สำหรับทำนายราคาพืชผล
- **Wrapper**: Class ที่ห่อหุ้ม ML model เพื่อให้ interface ที่สะดวกในการใช้งาน
- **Price Forecast Service**: Service ที่ให้บริการทำนายราคาจาก Model C v4
- **Fallback Prediction**: การทำนายแบบ rule-based เมื่อ ML model ไม่สามารถใช้งานได้
- **Hash Encoding**: เทคนิคการ encode categorical features ที่ใช้ใน Model C

## Requirements

### Requirement 1

**User Story:** As a developer, I want a standardized Model C wrapper, so that I can use it consistently with other model wrappers (A, B, D)

#### Acceptance Criteria

1. THE Model C Wrapper SHALL provide a class named `ModelCWrapper` that follows the same pattern as `ModelAWrapper`, `ModelBWrapper`, and `ModelDWrapper`
2. THE Model C Wrapper SHALL load the trained model from `REMEDIATION_PRODUCTION/trained_models/model_c_ultimate.pkl`
3. THE Model C Wrapper SHALL provide a method `predict_price()` that accepts crop_type, province, and days_ahead as parameters
4. THE Model C Wrapper SHALL return predictions in a standardized dictionary format with success status, predicted prices, and confidence scores
5. THE Model C Wrapper SHALL implement fallback prediction logic when the ML model fails to load or predict

### Requirement 2

**User Story:** As a developer, I want the wrapper to integrate with existing price forecast service, so that I can leverage the current Model C v4 implementation

#### Acceptance Criteria

1. THE Model C Wrapper SHALL integrate with `app.services.price_forecast_service` for actual price predictions
2. THE Model C Wrapper SHALL handle both historical data and daily forecasts from the price forecast service
3. THE Model C Wrapper SHALL provide price predictions for multiple timeframes (7, 30, 90, 180 days)
4. THE Model C Wrapper SHALL include historical price data in the response for chart visualization
5. THE Model C Wrapper SHALL calculate confidence scores that decrease with longer prediction timeframes

### Requirement 3

**User Story:** As a developer, I want proper error handling and logging, so that I can debug issues and ensure system reliability

#### Acceptance Criteria

1. THE Model C Wrapper SHALL log model loading status with appropriate log levels (info, warning, error)
2. THE Model C Wrapper SHALL catch and handle exceptions during model loading and prediction
3. THE Model C Wrapper SHALL provide detailed error messages in the response when predictions fail
4. THE Model C Wrapper SHALL automatically fall back to rule-based predictions when ML model is unavailable
5. THE Model C Wrapper SHALL log full stack traces for debugging when errors occur

### Requirement 4

**User Story:** As a developer, I want the wrapper to provide market insights and recommendations, so that users can make informed selling decisions

#### Acceptance Criteria

1. THE Model C Wrapper SHALL analyze price trends (increasing, decreasing, stable) from predictions
2. THE Model C Wrapper SHALL calculate trend percentages comparing current and future prices
3. THE Model C Wrapper SHALL generate market insights based on price trends and confidence levels
4. THE Model C Wrapper SHALL recommend the best selling period based on predicted prices
5. THE Model C Wrapper SHALL provide price ranges (min, max) for each prediction timeframe

### Requirement 5

**User Story:** As a developer, I want the wrapper to be easily instantiable and testable, so that I can use it in different contexts (API, chat, testing)

#### Acceptance Criteria

1. THE Model C Wrapper SHALL be instantiable as a global singleton instance named `model_c_wrapper`
2. THE Model C Wrapper SHALL provide a `get_model_info()` method that returns model status and metadata
3. THE Model C Wrapper SHALL work independently without requiring database connections for basic operations
4. THE Model C Wrapper SHALL be compatible with the existing `unified_model_service.py` architecture
5. THE Model C Wrapper SHALL follow Python best practices with proper type hints and docstrings

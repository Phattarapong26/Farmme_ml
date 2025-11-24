# Implementation Plan

- [ ] 1. Setup project structure and dependencies
  - Create backend/app/services/ directory for ML model services
  - Create backend/app/models/ml_models.py for Pydantic request/response models
  - Create backend/app/utils/error_handlers.py for error handling utilities
  - Create backend/app/utils/feature_engineering.py for feature preparation
  - Create backend/app/routers/harvest.py for Model D endpoint
  - Update backend/requirements.txt with ML dependencies (scikit-learn, xgboost, numpy, pandas)
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 2. Implement Model Loader and Caching
- [ ] 2.1 Create ModelLoader class
  - Implement backend/app/services/model_loader.py with ModelLoader class
  - Implement _get_base_path() to read ML_MODELS_PATH from environment or use default ../REMEDIATION_PRODUCTION/trained_models
  - Implement load_model(model_name, cache=True) to load .pkl files with pickle
  - Implement clear_cache() and get_model_info() methods
  - Add logging for model loading success/failure
  - _Requirements: 5.2, 5.3, 5.5, 8.1, 8.2, 8.3_

- [ ] 2.2 Add configuration for model paths
  - Update backend/config.py with ML_MODELS_PATH and individual model paths
  - Add MODEL_A_XGBOOST_PATH, MODEL_A_RF_PATH, MODEL_B_LOGISTIC_PATH, MODEL_B_XGBOOST_PATH, MODEL_C_PATH, MODEL_D_PATH
  - Add MODEL_CONFIDENCE_THRESHOLD, MODEL_PREDICTION_TIMEOUT, ENABLE_FALLBACK settings
  - Create backend/.env.example with ML configuration examples
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [ ] 3. Implement Model A Service - Crop Recommendation
- [ ] 3.1 Create ModelAService class
  - Implement backend/app/services/model_a_service.py with ModelAService class
  - Implement __init__() to load model_a_xgboost.pkl (primary) and model_a_rf_ensemble.pkl (fallback)
  - Implement _load_models() with error handling and logging
  - Implement get_recommendations() that returns format compatible with existing API
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 3.2 Implement feature preparation for Model A
  - Implement _prepare_features() to convert farm profile to numpy array
  - Add feature encoding for province, soil_type, water_availability
  - Add seasonal features from current date
  - Handle missing optional features with defaults
  - _Requirements: 1.5, 6.1, 6.6_

- [ ] 3.3 Implement prediction and formatting for Model A
  - Implement _format_recommendations() to convert model output to API response format
  - Calculate roi_percent, risk_score, total_profit_baht, confidence for each crop
  - Return top 3 recommendations sorted by suitability score
  - Implement _fallback_recommendations() using legacy recommendation_model_service
  - _Requirements: 1.2, 1.6, 7.1, 7.2_

- [ ] 4. Implement Model B Service - Planting Calendar
- [ ] 4.1 Create ModelBService class
  - Implement backend/app/services/model_b_service.py with ModelBService class
  - Implement __init__() to load model_b_logistic.pkl (primary, F1=0.868), model_b_xgboost.pkl (fallback 1), model_b_temporal_gb.pkl (fallback 2)
  - Implement _load_models() with error handling and logging
  - Implement get_planting_recommendations() that returns format compatible with /recommend-planting-date
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4.2 Implement feature preparation for Model B
  - Implement _prepare_features() to add temporal features (month_sin, month_cos, day_sin, day_cos)
  - Get weather data from database or use seasonal averages
  - Add soil moisture, rainfall, temperature, humidity features
  - Encode categorical features (crop_type, province)
  - _Requirements: 2.5, 2.7, 6.2, 6.6_

- [ ] 4.3 Implement prediction and classification for Model B
  - Implement prediction loop to evaluate multiple planting dates (weekly intervals)
  - Use Logistic Regression model to predict Good/Bad classification with confidence
  - Filter for "Good" windows only and calculate expected_germination_rate
  - Sort by total_score and return top N recommendations
  - Implement _fallback_planting_recommendations() using legacy planting_model_service
  - _Requirements: 2.2, 2.4, 2.6, 2.8, 7.1, 7.2_

- [ ] 5. Implement Model C Service - Price Forecast
- [ ] 5.1 Create ModelCService class
  - Implement backend/app/services/model_c_service.py with ModelCService class
  - Implement __init__() to load model_c_price_forecast.pkl
  - Implement _load_model() with error handling and logging
  - Implement predict_price() that returns format compatible with existing price prediction API
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 5.2 Implement feature preparation and prediction for Model C
  - Implement _prepare_features() for time series forecasting
  - Implement _get_historical_prices() to query database for historical price data
  - Generate predictions for multiple timeframes (7, 30, 90, 180 days)
  - Calculate confidence based on data quality and timeframe
  - Calculate price_range (min, max) based on confidence
  - _Requirements: 3.5, 3.6, 6.3, 6.6_

- [ ] 5.3 Implement trend analysis and insights for Model C
  - Implement _analyze_price_trend() to determine increasing/decreasing/stable trend
  - Implement _generate_market_insights() based on trend and confidence
  - Implement _recommend_selling_period() to find best selling timeframe
  - Implement _fallback_price_prediction() using legacy price_prediction_service
  - _Requirements: 3.4, 3.7, 7.1, 7.2_

- [ ] 6. Implement Model D Service - Harvest Decision (NEW)
- [ ] 6.1 Create ModelDService class
  - Implement backend/app/services/model_d_service.py with ModelDService class
  - Implement __init__() to load model_d_thompson_sampling.pkl
  - Implement _load_model() with error handling and logging
  - Implement get_harvest_decision() that returns recommended action and profit projections
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6.2 Implement Thompson Sampling decision logic for Model D
  - Prepare context dict with current_price, forecast_price, plant_health, yield_kg, storage_cost
  - Call model.decide(context) to get Thompson Sampling recommendation
  - Return recommended_action (Harvest Now/Wait 3 Days/Wait 7 Days) with confidence
  - Calculate profit_projections for all 3 actions
  - Calculate profit_difference vs harvest now
  - _Requirements: 4.5, 4.6, 6.4, 6.6_

- [ ] 6.3 Implement fallback for Model D
  - Implement _fallback_harvest_decision() with simple rule-based logic
  - Calculate profit for each action: profit = (price * yield) - (storage_cost * days) - (spoilage_penalty)
  - Select action with highest profit
  - Return result with lower confidence (0.7) to indicate fallback
  - _Requirements: 4.7, 7.1, 7.2_

- [ ] 7. Create Pydantic Request/Response Models
- [ ] 7.1 Create request models
  - Implement backend/app/models/ml_models.py with CropRecommendationRequest
  - Implement PlantingWindowRequest with validation for soil_moisture, temperature, humidity ranges
  - Implement PriceForecastRequest with days_ahead validation (1-180)
  - Implement HarvestDecisionRequest with field validations (price > 0, health_score 0-100)
  - Add @validator decorators for custom validation (e.g., soil_type must be in valid list)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 7.2 Create response models
  - Implement CropRecommendation and CropRecommendationResponse models
  - Implement PlantingWindowResponse model
  - Implement PricePrediction and PriceForecastResponse models
  - Implement HarvestDecisionResponse model
  - All response models should have success: bool field
  - _Requirements: 6.5, 6.7_

- [ ] 8. Implement Error Handling and Fallback Mechanisms
- [ ] 8.1 Create error handling utilities
  - Implement backend/app/utils/error_handlers.py with @with_fallback decorator
  - Implement @with_timeout decorator for prediction timeout (10 seconds)
  - Define custom exceptions: ModelError, ModelLoadError, ModelPredictionError, FeaturePreparationError
  - Add logging for all errors with stack trace and request context
  - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7_

- [ ] 8.2 Implement fallback mechanisms in all services
  - Ensure all service methods have try-except blocks
  - Call legacy service methods when ML model fails
  - Return success=False with error message when both primary and fallback fail
  - Log all fallback activations with reason
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [ ] 9. Create Feature Engineering Utilities
  - Implement backend/app/utils/feature_engineering.py with FeatureEngineer class
  - Implement add_temporal_features() for cyclic encoding (month_sin, month_cos, day_sin, day_cos)
  - Implement encode_province() and encode_crop_type() for categorical encoding
  - Implement get_region_from_province() with province-region mapping
  - Implement get_seasonal_weather() with temperature and rainfall patterns by month
  - _Requirements: 2.5, 2.7_

- [ ] 10. Update API Endpoints to Use New Services
- [ ] 10.1 Update main.py to initialize services
  - Update backend/app/main.py lifespan function to initialize model_a_service, model_b_service, model_c_service, model_d_service
  - Add error handling for service initialization failures
  - Log service initialization status (loaded/fallback)
  - Make services available globally or via dependency injection
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10.2 Update /recommend-planting-date endpoint
  - Update backend/app/main.py recommend_planting_date() function
  - Check if model_b_service.model_loaded, if yes use model_b_service.get_planting_recommendations()
  - If model not loaded, fallback to legacy planting_service.get_recommendations()
  - Maintain existing request/response format for backward compatibility
  - Add logging for which service was used (ML model or legacy)
  - _Requirements: 2.1, 2.2, 9.5, 9.8_

- [ ] 10.3 Create /api/v1/harvest-decision endpoint (NEW)
  - Create backend/app/routers/harvest.py with router for /api/v1/harvest-decision
  - Implement POST endpoint that accepts HarvestDecisionRequest
  - Call model_d_service.get_harvest_decision() with request parameters
  - Return HarvestDecisionResponse with recommended action and profit projections
  - Add error handling and logging
  - Register router in app/main.py
  - _Requirements: 4.1, 4.2, 9.2, 9.6_

- [ ] 11. Update Configuration and Environment
- [ ] 11.1 Update configuration files
  - Update backend/config.py with all ML model configuration variables
  - Add ML_MODELS_PATH, MODEL_A_XGBOOST_PATH, MODEL_B_LOGISTIC_PATH, MODEL_C_PATH, MODEL_D_PATH
  - Add MODEL_CONFIDENCE_THRESHOLD, MODEL_PREDICTION_TIMEOUT, ENABLE_FALLBACK, CACHE_ML_PREDICTIONS
  - Update backend/.env.example with ML configuration examples
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ] 11.2 Update requirements.txt
  - Add scikit-learn, xgboost, numpy, pandas to backend/requirements.txt if not already present
  - Specify compatible versions (e.g., scikit-learn>=1.0.0, xgboost>=1.5.0)
  - _Requirements: 9.1_

- [ ]* 12. Create Unit Tests
- [ ]* 12.1 Test Model A Service
  - Create backend/tests/test_model_services.py with TestModelAService class
  - Test model loading (test_model_loading)
  - Test get_recommendations with valid inputs (test_get_recommendations)
  - Test fallback mechanism when model not loaded (test_fallback_mechanism)
  - _Requirements: 11.1, 11.2, 11.3_

- [ ]* 12.2 Test Model B Service
  - Add TestModelBService class to test_model_services.py
  - Test planting recommendations (test_planting_recommendations)
  - Test classification output format (test_classification_format)
  - Test fallback mechanism
  - _Requirements: 11.1, 11.2, 11.3_

- [ ]* 12.3 Test Model C Service
  - Add TestModelCService class to test_model_services.py
  - Test price prediction (test_price_prediction)
  - Test trend analysis (test_trend_analysis)
  - Test fallback mechanism
  - _Requirements: 11.1, 11.2, 11.3_

- [ ]* 12.4 Test Model D Service
  - Add TestModelDService class to test_model_services.py
  - Test harvest decision (test_harvest_decision)
  - Test profit projections (test_profit_projections)
  - Test fallback mechanism
  - _Requirements: 11.1, 11.2, 11.3_

- [ ]* 13. Create Integration Tests
- [ ]* 13.1 Test API endpoints
  - Create backend/tests/test_api_integration.py with TestAPIIntegration class
  - Test /recommend-planting-date endpoint with ML model (test_planting_date_endpoint)
  - Test /api/v1/harvest-decision endpoint (test_harvest_decision_endpoint)
  - Test /models endpoint returns ML model info (test_models_list_endpoint)
  - _Requirements: 11.4, 11.5_

- [ ]* 13.2 Test error handling
  - Test invalid input validation (test_invalid_input_validation)
  - Test timeout handling (test_timeout_handling)
  - Test fallback activation (test_fallback_activation)
  - _Requirements: 11.3, 11.4_

- [ ]* 14. Create Documentation
- [ ]* 14.1 Update README
  - Update backend/README.md with ML integration section
  - Document how to configure ML_MODELS_PATH
  - Document available endpoints and their usage
  - Add examples of API requests and responses
  - _Requirements: 12.1, 12.2, 12.3, 12.6_

- [ ]* 14.2 Update API documentation
  - Ensure OpenAPI/Swagger docs at /docs include new endpoints
  - Add descriptions and examples for all request/response models
  - Document error codes and error messages
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 15. Performance Optimization
- [ ]* 15.1 Implement caching
  - Add prediction result caching using existing cache module
  - Cache identical requests for 1 hour (CACHE_TTL_ML_PREDICTIONS)
  - Add cache key generation based on request parameters
  - _Requirements: 10.1, 10.2, 10.4_

- [ ]* 15.2 Add monitoring
  - Create backend/app/utils/monitoring.py with MLModelMonitor class
  - Log prediction duration, success/failure for each model
  - Calculate average response time per model
  - Provide /metrics endpoint for monitoring (optional)
  - _Requirements: 10.5, 10.6_


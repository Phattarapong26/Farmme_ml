# Implementation Plan - Model B Production Wrapper

- [x] 1. Create core component classes and data models


  - Create PredictionResult dataclass for standardized prediction output
  - Create error hierarchy classes (ModelBError and subclasses)
  - Create configuration class (ModelBConfig) with all settings
  - _Requirements: 1.4, 2.7, 4.3_

- [x] 2. Implement InputValidator component

  - [x] 2.1 Create InputValidator class with province alias mapping

    - Implement PROVINCE_ALIASES dictionary with Thai/English mappings
    - Implement normalize_province() method with alias lookup
    - _Requirements: 2.3, 5.4, 5.5_

  - [x] 2.2 Implement input validation methods

    - Implement validate_date() with format checking and parsing
    - Implement validate_soil_params() for pH (0-14) and nutrients (>=0)
    - Implement validate_prediction_input() that orchestrates all validations
    - Return clear error messages for each validation failure
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [x] 3. Implement WeatherDataCache component

  - [x] 3.1 Create WeatherDataCache class with caching infrastructure

    - Initialize cache dictionaries (_cache, _monthly_cache)
    - Implement load() method to read weather CSV with error handling
    - Add logging for load success/failure
    - _Requirements: 3.1, 5.1, 5.2_

  - [x] 3.2 Implement weather data retrieval methods

    - Implement get_weather() with exact date lookup
    - Implement _get_monthly_average() with caching
    - Implement _calculate_monthly_average() for future dates
    - Handle missing data gracefully
    - _Requirements: 3.2, 5.3, 5.6_

- [x] 4. Implement ModelLoader component

  - [x] 4.1 Create ModelLoader class with model priority list

    - Define MODEL_PRIORITY list with (filename, type) tuples
    - Implement load() method with priority-based loading
    - Handle pickle loading errors gracefully
    - _Requirements: 3.2, 10.1_

  - [x] 4.2 Add model metadata and status methods

    - Implement is_loaded() status check
    - Implement get_model_info() returning model metadata
    - Log model loading status with file path and type
    - _Requirements: 7.2_

- [x] 5. Implement FallbackManager component

  - Create FallbackManager class with rate limiting
  - Implement should_allow_fallback() with MAX_FALLBACKS_PER_MINUTE check
  - Implement record_fallback() to track usage with timestamps
  - Implement _cleanup_old_records() to remove entries older than 1 minute
  - Implement get_stats() for monitoring
  - _Requirements: 10.5, 10.6_

- [x] 6. Implement PredictionEngine component


  - [x] 6.1 Create PredictionEngine class structure

    - Initialize with ModelLoader and WeatherDataCache dependencies
    - Create predict() method as main entry point
    - Implement fallback chain: ML → Weather → Rules
    - _Requirements: 1.4, 10.1, 10.2, 10.3_


  - [x] 6.2 Implement ML prediction method

    - Implement _ml_prediction() using loaded model and scaler
    - Implement _engineer_features() for temporal and categorical encoding
    - Extract prediction and probability from model output
    - Return PredictionResult with method="ml_model"
    - _Requirements: 3.4, 10.4_

  - [x] 6.3 Implement weather-based prediction method

    - Implement _weather_based_prediction() using real weather data
    - Apply temperature rules (15-36°C optimal range)
    - Apply rainfall rules (5-100mm optimal range)
    - Apply humidity rules (50-90% optimal range)
    - Apply drought index rules (<120 acceptable)
    - Combine soil parameters if provided
    - Return PredictionResult with method="weather_based"
    - _Requirements: 5.6, 10.2, 10.4_

  - [x] 6.4 Implement rule-based fallback method

    - Implement _rule_based_prediction() using season rules
    - Apply season logic (Winter=good, Summer=bad, Rainy=good)
    - Apply soil pH rules (5.5-8.0 acceptable)
    - Apply soil nutrients rules (>=40 acceptable)
    - Return PredictionResult with method="rule_based"
    - _Requirements: 10.2, 10.4_

- [x] 7. Implement ResponseFormatter component

  - [x] 7.1 Create ResponseFormatter class with formatting methods

    - Implement format_success() for successful predictions
    - Implement format_error() for error responses
    - Add MODEL_VERSION constant
    - Include metadata in all responses (model_version, timestamp, prediction_time_ms)
    - _Requirements: 4.1, 4.2, 4.3, 4.5_

  - [x] 7.2 Implement Thai language generation methods

    - Implement _generate_thai_explanation() combining weather and soil context
    - Implement _generate_recommendation() with actionable advice
    - Add disclaimer when confidence < 0.70
    - Provide alternative suggestions for bad windows
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8. Refactor ModelBWrapper as facade



  - [x] 8.1 Update ModelBWrapper initialization

    - Initialize all component instances (Validator, Engine, Cache, Loader, Formatter, FallbackMgr)
    - Remove duplicate code from old implementation
    - Add lazy loading for ML model
    - _Requirements: 1.1, 1.5, 3.2_


  - [ ] 8.2 Refactor predict_planting_window() method
    - Use InputValidator to validate and normalize inputs
    - Use PredictionEngine to get prediction
    - Use WeatherDataCache to get weather context
    - Use ResponseFormatter to format response
    - Add try-except with FallbackManager
    - Add performance timing (start/end)
    - Log all requests and responses
    - _Requirements: 2.6, 3.4, 7.1, 7.4_


  - [ ] 8.3 Refactor get_planting_calendar() method
    - Reuse predict_planting_window() for each month
    - Batch weather data retrieval for efficiency
    - Identify consecutive good months as best windows
    - Generate Thai summary

    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 8.4 Add comprehensive docstrings
    - Add module-level docstring
    - Add class-level docstring
    - Add method docstrings with Args, Returns, Raises sections
    - Document all public methods
    - _Requirements: 1.3_

- [ ] 9. Implement error handling and logging
  - [ ] 9.1 Add error handling to all methods
    - Wrap all external calls in try-except blocks
    - Use custom error classes from error hierarchy
    - Never raise unhandled exceptions to caller
    - _Requirements: 2.6, 2.7_

  - [ ] 9.2 Add comprehensive logging
    - Log all prediction requests with parameters (sanitized)
    - Log model loading status
    - Log fallback usage with reason
    - Log performance metrics (prediction time)
    - Log errors with full traceback at ERROR level
    - Use structured logging format
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 10. Create comprehensive test suite
  - [ ] 10.1 Create test_input_validator.py
    - Test valid inputs (dates, provinces, soil params)
    - Test invalid date formats
    - Test invalid soil parameters (pH out of range, negative nutrients)
    - Test province normalization with aliases
    - Test missing required parameters
    - _Requirements: 8.1, 8.2_

  - [ ] 10.2 Create test_weather_cache.py
    - Test load weather data from CSV
    - Test get exact date weather
    - Test get monthly average for future dates
    - Test handle missing province data
    - Test cache hit performance
    - _Requirements: 8.3_

  - [ ] 10.3 Create test_model_loader.py
    - Test load valid model file
    - Test handle missing model files
    - Test model priority order
    - Test is_loaded() status
    - _Requirements: 8.4_

  - [ ] 10.4 Create test_prediction_engine.py
    - Test ML prediction with valid features
    - Test weather-based prediction
    - Test rule-based fallback
    - Test feature engineering
    - Test fallback chain
    - _Requirements: 8.2_

  - [ ] 10.5 Create test_response_formatter.py
    - Test format success response structure
    - Test format error response structure
    - Test Thai explanation generation
    - Test metadata inclusion
    - Test confidence disclaimer
    - _Requirements: 8.2_

  - [ ] 10.6 Create test_fallback_manager.py
    - Test rate limiting (max 3 per minute)
    - Test fallback tracking
    - Test statistics
    - Test cleanup old records
    - _Requirements: 8.2_

  - [ ] 10.7 Create test_model_b_wrapper_integration.py
    - Test end-to-end valid prediction request
    - Test end-to-end with ML fallback to weather
    - Test end-to-end with weather fallback to rules
    - Test invalid input returns validation error
    - Test missing weather data triggers fallback
    - Test prediction time < 200ms
    - Test planting calendar generation
    - _Requirements: 8.3, 8.4_

- [ ] 11. Performance optimization and validation
  - [ ] 11.1 Add performance monitoring
    - Add timing decorator for prediction methods
    - Log prediction time for each request
    - Track cache hit rate
    - _Requirements: 3.4, 3.5_

  - [ ] 11.2 Validate performance targets
    - Run benchmark: single prediction < 200ms
    - Run benchmark: calendar (12 months) < 2 seconds
    - Verify cache hit rate > 80% after warmup
    - Verify memory usage < 500MB
    - _Requirements: 3.4_

- [ ] 12. Documentation and deployment preparation
  - [ ] 12.1 Update README and documentation
    - Document new architecture and components
    - Add usage examples for predict_planting_window()
    - Add usage examples for get_planting_calendar()
    - Document error responses and handling
    - Document configuration options

  - [ ] 12.2 Create deployment checklist
    - Verify all tests pass
    - Verify model files exist in trained_models/
    - Verify weather.csv exists and is readable
    - Verify logging configuration
    - Create monitoring dashboard queries

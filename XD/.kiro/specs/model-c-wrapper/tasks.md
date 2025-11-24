# Implementation Plan

- [x] 1. Create Model C Wrapper file structure


  - Create `backend/model_c_wrapper.py` file
  - Add necessary imports (logging, pickle, sys, Path, typing, datetime)
  - Add path configuration for REMEDIATION_PRODUCTION directory
  - _Requirements: 1.1, 1.2_




- [ ] 2. Implement ModelCWrapper class initialization
  - [ ] 2.1 Create ModelCWrapper class with __init__ method
    - Initialize model, forecast_service, model_loaded, and model_path attributes

    - Call _load_model() method during initialization
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.2 Implement _load_model() method
    - Import price_forecast_service from app.services
    - Set forecast_service reference




    - Set model_loaded flag based on service status
    - Log initialization status with appropriate log levels
    - Handle exceptions and log errors with stack traces
    - _Requirements: 1.2, 2.1, 3.1, 3.2_


- [ ] 3. Implement core prediction functionality
  - [ ] 3.1 Create predict_price() method signature
    - Define parameters: crop_type, province, days_ahead, planting_area_rai, expected_yield_kg
    - Add type hints for all parameters and return type
    - Add comprehensive docstring
    - _Requirements: 1.3, 1.4, 5.5_
  

  - [ ] 3.2 Implement ML-based prediction logic
    - Get database session from SessionLocal
    - Query current price from CropPrice table
    - Call forecast_service.forecast_price() with parameters
    - Extract historical_data and daily_forecasts from result

    - Format predictions for multiple timeframes (7, 30, 90, 180 days)

    - Calculate confidence scores for each timeframe
    - _Requirements: 1.3, 1.4, 2.1, 2.2, 2.3, 2.5_
  
  - [ ] 3.3 Add error handling and fallback logic
    - Wrap prediction calls in try-except blocks

    - Log errors with context information
    - Call _fallback_prediction() when ML model fails
    - Ensure database session is properly closed
    - _Requirements: 1.5, 3.2, 3.3, 3.4_


- [ ] 4. Implement analysis and insights generation
  - [ ] 4.1 Create _analyze_price_trend() method
    - Calculate price change percentage
    - Classify trend as increasing (>5%), decreasing (<-5%), or stable
    - Return dictionary with trend type and percentage

    - _Requirements: 4.1, 4.2_
  
  - [ ] 4.2 Create _generate_market_insights() method
    - Generate insights based on price trends

    - Add confidence-based insights

    - Return list of Thai language insight strings
    - _Requirements: 4.3_
  
  - [ ] 4.3 Create _recommend_selling_period() method
    - Find prediction with highest price
    - Map days_ahead to Thai language period strings
    - Return recommendation string
    - _Requirements: 4.4_
  

  - [ ] 4.4 Implement _calculate_price_range() helper method
    - Calculate min/max price range based on confidence
    - Use confidence to determine range width
    - Return tuple of (min_price, max_price)

    - _Requirements: 4.5_


- [ ] 5. Implement fallback prediction mechanism
  - [ ] 5.1 Create _fallback_prediction() method
    - Query historical prices from database

    - Calculate base price from historical average
    - Apply seasonal adjustments
    - Generate historical_data for charts

    - Generate daily_forecasts with trend
    - Create predictions for standard timeframes
    - Return same structure as predict_price()
    - _Requirements: 1.5, 3.4_
  





  - [ ] 5.2 Add seasonal factor calculations
    - Implement _get_seasonal_factor() helper method
    - Define monthly seasonal factors
    - Return appropriate factor for given month

    - _Requirements: 1.5_

- [ ] 6. Implement utility methods
  - [ ] 6.1 Create get_model_info() method
    - Return dictionary with model metadata
    - Include model_loaded, model_path, version, status

    - _Requirements: 5.2_
  
  - [ ] 6.2 Add helper methods for data retrieval
    - Implement _get_historical_prices() if needed
    - Add proper error handling
    - _Requirements: 2.4_



- [ ] 7. Create global instance and module-level code
  - Create global singleton instance `model_c_wrapper`
  - Add module-level logger message
  - Ensure proper initialization on import
  - _Requirements: 5.1_

- [ ] 8. Integration and validation
  - [ ] 8.1 Test wrapper initialization
    - Verify model loads correctly
    - Check logging output
    - Test fallback mode when model unavailable
    - _Requirements: 3.1, 3.4_
  
  - [ ] 8.2 Test predict_price() with various inputs
    - Test with different crop types (พริก, มะเขือเทศ, etc.)
    - Test with different provinces
    - Test with different timeframes (7, 30, 90, 180 days)
    - Verify response structure matches design
    - _Requirements: 1.3, 1.4, 2.2, 2.3, 2.4_
  
  - [ ] 8.3 Test error handling and fallback
    - Test with invalid inputs
    - Test when database unavailable
    - Test when ML model fails
    - Verify fallback predictions work correctly
    - _Requirements: 1.5, 3.2, 3.3, 3.4_
  
  - [ ] 8.4 Verify integration with unified_model_service
    - Check compatibility with existing service architecture
    - Test import and usage from other modules
    - _Requirements: 5.4_

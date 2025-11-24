# Implementation Plan

- [x] 1. Setup project structure and data validation
  - Create directory structure for REMEDIATION_PRODUCTION with Model_A_Fixed, Model_B_Fixed, Model_C_PriceForecast, Model_D_L4_Bandit, Pipeline_Integration, Real_World_Tests, outputs, logs folders
  - Create DataLoaderClean class that loads data from Dataset/ folder and validates no post-outcome features
  - Implement validate_no_leakage() method to check for forbidden features (actual_yield_kg, success_rate, harvest_timing_adjustment, yield_efficiency for Model A; harvest_date, actual_yield_kg, success_rate for Model B; actual_harvest_date, future_price for Model D)
  - Implement get_feature_correlations() method to analyze feature-target relationships
  - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.6, 7.7_

- [x] 2. Implement Model A - Crop Recommendation System
- [x] 2.1 Create Model A core algorithms
  - Implement ModelA_NSGA2 class with train(), predict(), and evaluate() methods for multi-objective optimization (maximize ROI, minimize risk, maximize stability)
  - Implement ModelA_XGBoost class with train(), predict(), evaluate(), and get_feature_importance() methods
  - Implement ModelA_RandomForest class with same interface as XGBoost
  - Use only pre-planting features: farm_size_rai, soil_type, soil_ph, soil_nitrogen, soil_phosphorus, soil_potassium, avg_temperature, avg_rainfall, humidity, budget_baht, farmer_experience_years, water_availability
  - Return top 3 crop recommendations with ROI percentage, risk score, stability score, total profit projection, investment required, days to maturity, confidence, and reasons
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [x] 2.2 Train and validate Model A
  - Load cultivation data from Dataset/ using DataLoaderClean
  - Split data into train/val/test sets (60/20/20)
  - Train NSGA-II, XGBoost, and Random Forest models
  - Validate R² score is between 0.45-0.55 (honest metrics without leakage)
  - Check for overfitting by comparing train vs validation metrics (gap should be < 15%)
  - Generate and save evaluation plots: feature importance, learning curves, residual plots to outputs/model_a_evaluation/ with metadata (model_name, evaluation_type, timestamp)
  - _Requirements: 1.4, 7.3, 7.4, 7.8, 7.9, 7.10_

- [x] 3. Implement Model B - Planting Window Classifier
- [x] 3.1 Create Model B core algorithms
  - Implement ModelB_XGBoost classifier with train(), predict(), predict_proba(), and evaluate() methods
  - Implement ModelB_LogisticRegression with same interface
  - Use only pre-planting observable features: soil_moisture_percent, recent_rainfall_mm, temperature_c, humidity_percent, soil_temperature_c, wind_speed_kmh, month, day_of_year, month_sin, month_cos, day_sin, day_cos, crop_type
  - Return classification (Good/Bad), confidence percentage, optimal time range, expected germination rate, risk level, reasons, and weather warnings
  - _Requirements: 2.1, 2.2_

- [x] 3.2 Train and validate Model B with time-aware split
  - Load planting window data from Dataset/ using DataLoaderClean
  - Implement time-aware data split: train on past data, validate on intermediate period, test on future data with 7-day embargo period between sets
  - Train XGBoost and Logistic Regression classifiers
  - Validate F1 score is between 0.70-0.75, precision ~0.75, recall ~0.68
  - Check for overfitting by comparing train vs validation F1 scores
  - Generate and save evaluation plots: confusion matrix, ROC curve, precision-recall curve to outputs/model_b_evaluation/ with metadata
  - _Requirements: 2.3, 2.4, 2.5, 6.5, 7.2, 7.8, 7.9, 7.10_


- [x] 4. Implement Model C - Price Forecast System
- [x] 4.1 Create Model C price forecasting algorithm
  - Implement ModelC_PriceForecast class with train(), predict(), evaluate(), and update_daily() methods
  - Use time series forecasting (Prophet or ARIMA) with features: crop_type, current_price, historical_prices (90 days), days_to_harvest, season, market_demand_index, supply_forecast, export_volume
  - Return forecast_price_median, forecast_price_q10, forecast_price_q90, confidence, price_trend, expected_change_percent, expected_revenue, risk_assessment
  - _Requirements: 3.1, 3.2_

- [x] 4.2 Train and validate Model C
  - Load price history data from Dataset/ 
  - Train time series model on historical price data
  - Validate R² score > 0.99, RMSE < 0.30 baht/kg, MAPE < 0.5%
  - Implement daily update mechanism for incremental learning
  - Generate and save evaluation plots: forecast vs actual, residual plot, confidence intervals to outputs/model_c_evaluation/ with metadata
  - _Requirements: 3.3, 3.4, 3.5, 7.9, 7.10_

- [x] 5. Implement Model D - Harvest Decision Engine (Thompson Sampling)
- [x] 5.1 Create Thompson Sampling bandit algorithm
  - Implement HarvestDecisionEngine class with __init__(n_actions=3, alpha=1.0, beta=1.0)
  - Implement decide(context) method that samples from Beta distributions for 3 actions (Harvest Now, Wait 3 Days, Wait 7 Days) and selects action with highest sampled value
  - Implement update_beliefs(action_idx, reward) method to update Beta parameters based on actual outcomes
  - Implement calculate_profit(action, context) method using formula: profit = (price * yield) - (storage_cost * days) - (risk_penalty)
  - Use only observable pre-decision features: current_price, forecast_price_median, forecast_price_std, plant_health_score, plant_age_days, storage_cost_per_day, yield_kg, weather_risk_7d, market_volatility
  - Return recommended_action, action_confidence, profit_projections for all 3 actions, profit_difference vs harvest now, risk_assessment, reasons
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 5.2 Test and validate Model D
  - Create test scenarios with different price contexts
  - Validate decision accuracy ~68%, profit estimates within ±20% of actual
  - Test belief update mechanism with simulated outcomes
  - Save belief states to Model_D_L4_Bandit/belief_states/
  - Generate and save evaluation plots: action probability evolution, reward distribution, regret analysis to outputs/model_d_evaluation/ with metadata
  - _Requirements: 4.4, 4.5, 7.9, 7.10_

- [ ] 6. Implement Pipeline Integration System
- [ ] 6.1 Create FarmingPipeline class
  - Implement __init__(farmer_id, farm_size_rai, budget_baht) with state management
  - Implement stage_1_crop_selection(farm_profile) that calls Model A and updates state
  - Implement stage_2_planting_window(current_conditions) that calls Model B and updates state
  - Implement stage_3_price_forecast(days_to_harvest) that calls Model C and updates state
  - Implement stage_4_harvest_decision(current_context) that calls Model D and updates state
  - Implement get_current_stage(), get_state_summary(), print_summary() methods
  - Implement save_state(filepath) and load_state(filepath) for persistence
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 6.2 Add error handling and fallback mechanisms
  - Implement execute_with_fallback() method that tries primary model and falls back to secondary if error occurs
  - Add input validation for all pipeline stages using validate_farm_profile() and similar validators
  - Implement graceful degradation when models fail
  - Add comprehensive logging for all stages using Python logging module
  - _Requirements: 9.5, 9.6_

- [ ] 7. Implement monitoring and logging system
  - Create PerformanceMonitor class to track predictions, average time, and errors for each model
  - Create DriftDetector class to detect model performance degradation (threshold 10%)
  - Configure logging to both file (logs/pipeline.log) and console with timestamps
  - Log all critical events: stage starts, warnings for low confidence, errors with context
  - _Requirements: 10.1, 10.2_

- [x] 8. Create real-world test scenario
  - Implement test_real_world_scenario.py that simulates Farmer Somchai through all 4 stages
  - Stage 1: Farm profile (25 rai, 150,000 baht budget) → expect Cassava recommendation with ~48.5% ROI
  - Stage 2: Soil moisture 78%, rainfall 35mm → expect Good window with ~93% confidence
  - Stage 3: 75 days to harvest → expect price forecast ~3.15 baht/kg
  - Stage 4: Current price 2.95, forecast 3.15 → expect Wait 7 Days recommendation
  - Validate all outputs are sensible and consistent with inputs
  - Make script executable via command line: python -m REMEDIATION_PRODUCTION.Real_World_Tests.test_real_world_scenario
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 9. Create configuration and deployment files
  - Create config.py with all configuration parameters (paths, model hyperparameters, thresholds)
  - Set DATA_PATH = 'Dataset/', MODEL_PATH = 'trained_models/', OUTPUT_PATH = 'outputs/', LOG_PATH = 'logs/'
  - Use relative paths throughout, no hard-coded absolute paths
  - Create requirements.txt with all dependencies (numpy, pandas, scikit-learn, xgboost, matplotlib, seaborn, etc.)
  - _Requirements: 9.7, 10.3_

- [ ]* 10. Create comprehensive documentation
  - Write Documentation/README.md with overview, architecture diagram, getting started guide
  - Write Documentation/QUICK_START.md with 10-step tutorial for training and using models
  - Write Documentation/TECHNICAL_GUIDE.md with implementation details, class interfaces, data formats
  - Write Documentation/LEAKAGE_PREVENTION.md with guidelines on avoiding data leakage, list of forbidden features per model
  - Write Documentation/ALGORITHM_COMPARISON.md with performance metrics comparison between algorithms
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ]* 11. Performance optimization and caching
  - Implement ModelCache class with LRU cache for crop characteristics and historical prices
  - Implement BatchProcessor class for processing multiple predictions efficiently
  - Add caching to reduce data loading time
  - _Requirements: 10.3, 10.4_

- [ ]* 12. Create API endpoints for future integration
  - Implement FastAPI endpoints: /api/v1/crop-recommendation, /api/v1/planting-window, /api/v1/price-forecast, /api/v1/harvest-decision
  - Add request validation using Pydantic models
  - Add error handling and logging for API requests
  - _Requirements: 10.2_

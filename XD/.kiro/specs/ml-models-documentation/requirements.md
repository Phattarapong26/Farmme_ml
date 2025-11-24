# Requirements Document - ML Models Documentation & Feature Analysis

## Introduction

This specification defines the requirements for creating comprehensive documentation and analysis of the four machine learning models (Model A, B, C, D) used in the agricultural prediction system. The documentation will explain the datasets used, feature selection methodology, feature engineering processes, and the rationale behind each model's design decisions.

## Glossary

- **Model A**: Crop Recommendation System - predicts expected ROI for crop selection decisions
- **Model B**: Planting Window Classifier - binary classification for optimal planting timing
- **Model C**: Price Forecast System - time series forecasting for crop prices at harvest
- **Model D**: Harvest Decision Engine - contextual bandit for optimal harvest timing
- **Feature Engineering**: The process of creating, transforming, and selecting features from raw data
- **Feature Selection**: The process of identifying and selecting the most relevant features for model training
- **Data Leakage**: When information from outside the training dataset is used to create the model, leading to overly optimistic performance
- **Target Variable**: The variable that the model is trying to predict
- **Pre-planting Features**: Features available before planting occurs (no future information)
- **Post-outcome Features**: Features only available after harvest (causes data leakage if used for training)

## Requirements

### Requirement 1: Model A Documentation

**User Story:** As a data scientist, I want comprehensive documentation of Model A's dataset usage and feature selection, so that I can understand and validate the crop recommendation system.

#### Acceptance Criteria

1. THE Documentation System SHALL document all datasets used by Model A including cultivation.csv, farmer_profiles.csv, crop_characteristics.csv, weather.csv, and price.csv
2. THE Documentation System SHALL list all features used by Model A with their data types and sources
3. THE Documentation System SHALL explain why each feature was selected for Model A based on domain knowledge and statistical analysis
4. THE Documentation System SHALL document the target variable (expected_roi_percent) and explain why it was chosen for crop recommendation
5. THE Documentation System SHALL identify and document all forbidden post-outcome features that were removed to prevent data leakage

### Requirement 2: Model B Documentation

**User Story:** As a data scientist, I want comprehensive documentation of Model B's dataset usage and feature selection, so that I can understand and validate the planting window classifier.

#### Acceptance Criteria

1. THE Documentation System SHALL document all datasets used by Model B including cultivation.csv and weather.csv
2. THE Documentation System SHALL list all temporal features created for Model B including cyclic encodings
3. THE Documentation System SHALL explain the binary classification target (is_good_window) and the success_rate threshold of 0.75
4. THE Documentation System SHALL document why temporal features are critical for planting window prediction
5. THE Documentation System SHALL identify pre-planting features used and post-outcome features removed

### Requirement 3: Model C Documentation

**User Story:** As a data scientist, I want comprehensive documentation of Model C's dataset usage and feature selection, so that I can understand and validate the price forecast system.

#### Acceptance Criteria

1. THE Documentation System SHALL document the price.csv dataset structure with 2,289,492 records across date, province, and crop_type dimensions
2. THE Documentation System SHALL list all lagged price features (price_lag1, price_lag7, price_lag30) and explain their time-safety
3. THE Documentation System SHALL document temporal features including cyclic encodings for seasonality
4. THE Documentation System SHALL explain why hash encoding was used for categorical features (crop_type, province)
5. THE Documentation System SHALL document the target variable (price) and explain the forecasting objective

### Requirement 4: Model D Documentation

**User Story:** As a data scientist, I want comprehensive documentation of Model D's algorithm and decision-making process, so that I can understand and validate the harvest timing system.

#### Acceptance Criteria

1. THE Documentation System SHALL document the Thompson Sampling algorithm used by Model D
2. THE Documentation System SHALL explain the three decision options (Harvest Now, Wait 3 Days, Wait 7 Days)
3. THE Documentation System SHALL document the reward function and how it incorporates profit calculations
4. THE Documentation System SHALL explain the contextual features used (current_price, forecast_price, yield_kg, plant_health, storage_cost)
5. THE Documentation System SHALL document the exploration-exploitation strategy with epsilon-greedy approach

### Requirement 5: Feature Engineering Analysis

**User Story:** As a data scientist, I want detailed analysis of feature engineering techniques used across all models, so that I can understand the data transformation pipeline.

#### Acceptance Criteria

1. THE Analysis System SHALL document all feature creation techniques including lagged features, temporal features, and cyclic encodings
2. THE Analysis System SHALL document all feature transformation techniques including standardization and encoding methods
3. THE Analysis System SHALL explain the rationale for each feature engineering decision based on domain knowledge
4. THE Analysis System SHALL document how feature engineering prevents data leakage through time-aware splits
5. THE Analysis System SHALL provide code examples for each feature engineering technique

### Requirement 6: Feature Selection Validation

**User Story:** As a data scientist, I want statistical validation of feature selection decisions, so that I can verify that selected features are truly important for model performance.

#### Acceptance Criteria

1. THE Validation System SHALL calculate correlation coefficients between features and target variables for Models A, B, and C
2. THE Validation System SHALL compute feature importance scores using tree-based methods (XGBoost feature importance)
3. THE Validation System SHALL perform mutual information analysis to measure feature-target dependencies
4. THE Validation System SHALL conduct variance threshold analysis to identify low-variance features
5. THE Validation System SHALL generate visualizations (heatmaps, bar charts) for all feature selection metrics

### Requirement 7: Feature Selection Methodology Documentation

**User Story:** As a data scientist, I want documentation of feature selection methodologies used, so that I can understand the systematic approach to feature selection.

#### Acceptance Criteria

1. THE Documentation System SHALL document filter methods used including correlation analysis and variance thresholds
2. THE Documentation System SHALL document embedded methods used including tree-based feature importance from XGBoost and Random Forest
3. THE Documentation System SHALL explain why wrapper methods (RFE, forward/backward selection) were not used
4. THE Documentation System SHALL document the advantages and disadvantages of each feature selection method
5. THE Documentation System SHALL provide recommendations for when to use each feature selection method

### Requirement 8: Data Leakage Prevention Analysis

**User Story:** As a data scientist, I want analysis of data leakage prevention measures, so that I can verify model validity and generalization.

#### Acceptance Criteria

1. THE Analysis System SHALL identify all post-outcome features in the raw datasets (actual_yield_kg, success_rate, harvest_timing_adjustment, yield_efficiency)
2. THE Analysis System SHALL verify that no post-outcome features are present in training data for Models A, B, and C
3. THE Analysis System SHALL document time-aware splitting strategies used to prevent temporal leakage
4. THE Analysis System SHALL explain how Model C's lagged features prevent look-ahead bias
5. THE Analysis System SHALL provide validation code that checks for data leakage in the training pipeline

### Requirement 9: Model Performance vs Feature Selection

**User Story:** As a data scientist, I want analysis of how feature selection impacts model performance, so that I can optimize the feature set.

#### Acceptance Criteria

1. THE Analysis System SHALL compare model performance with all features vs selected features for Models A, B, and C
2. THE Analysis System SHALL measure the impact of removing low-importance features on R², F1, and RMSE metrics
3. THE Analysis System SHALL analyze the trade-off between model complexity and performance
4. THE Analysis System SHALL document the optimal feature set size for each model
5. THE Analysis System SHALL provide recommendations for feature selection thresholds

### Requirement 10: Documentation Structure and Accessibility

**User Story:** As a developer, I want well-organized documentation in a dedicated folder, so that I can easily find and reference model information.

#### Acceptance Criteria

1. THE Documentation System SHALL create a Documentation folder at the project root level
2. THE Documentation System SHALL create separate markdown files for each model (Model_A_Documentation.md, Model_B_Documentation.md, Model_C_Documentation.md, Model_D_Documentation.md)
3. THE Documentation System SHALL create a comprehensive Feature_Engineering_Guide.md document
4. THE Documentation System SHALL create a Feature_Selection_Methodology.md document
5. THE Documentation System SHALL create a master README.md in the Documentation folder with navigation links

### Requirement 11: Test and Evaluation Scripts

**User Story:** As a data scientist, I want executable test scripts that validate feature selection decisions, so that I can reproduce the analysis.

#### Acceptance Criteria

1. THE Test System SHALL create a test_evaluate folder with Python scripts for feature analysis
2. THE Test System SHALL create correlation_analysis.py to compute and visualize feature correlations
3. THE Test System SHALL create feature_importance_analysis.py to compute tree-based feature importance
4. THE Test System SHALL create mutual_information_analysis.py to measure feature-target dependencies
5. THE Test System SHALL create data_leakage_validation.py to verify no post-outcome features are used

### Requirement 12: Visualization and Reporting

**User Story:** As a stakeholder, I want visual reports of feature analysis results, so that I can understand model decisions without deep technical knowledge.

#### Acceptance Criteria

1. THE Reporting System SHALL generate correlation heatmaps for each model's features
2. THE Reporting System SHALL generate feature importance bar charts for Models A, B, and C
3. THE Reporting System SHALL generate mutual information plots showing feature-target relationships
4. THE Reporting System SHALL save all visualizations as PNG files in the test_evaluate/outputs folder
5. THE Reporting System SHALL create a summary report PDF combining all visualizations and key findings

# Implementation Plan

- [x] 1. Create minimal data loader with stratified sampling


  - Create `minimal_data_loader.py` with MinimalDataLoader class
  - Implement `load_and_sample()` method that loads full dataset and samples maximum 1000 records using stratified sampling by crop_id
  - Implement `validate_sample()` method to check that sample maintains crop distribution
  - Add logging for original vs sampled dataset statistics
  - _Requirements: 1.5, 4.1, 4.2, 4.3, 4.4_

- [x] 2. Create three-algorithm trainer


  - Create `three_algorithm_trainer.py` with ThreeAlgorithmTrainer class
  - Implement XGBoost algorithm with regularization (max_depth=3, learning_rate=0.05, reg_alpha=0.1, reg_lambda=1.0)
  - Implement Random Forest + ElasticNet ensemble (existing implementation)
  - Implement Gradient Boosting Regressor from sklearn (n_estimators=100, max_depth=3, learning_rate=0.05)
  - Add training time tracking for each algorithm using time.time()
  - Implement `train_all()` method that trains all 3 algorithms and returns TrainingResult objects
  - _Requirements: 1.1, 1.2, 4.5, 5.2_

- [x] 3. Create bubble chart generator


  - Create `bubble_chart_generator.py` with BubbleChartGenerator class
  - Implement `generate_bubble_chart()` method that creates bubble chart with R² on x-axis and RMSE on y-axis
  - Implement `_calculate_bubble_sizes()` method that normalizes training times to bubble sizes (100-1000 range)
  - Use distinct colors for each algorithm (Blue for XGBoost, Green for RF+ElasticNet, Orange for GradBoost)
  - Add algorithm name labels and key metrics (R², RMSE) to each bubble
  - Save chart as high-resolution PNG (300 DPI)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Create detailed evaluation plotter


  - Create `detailed_plotter.py` with DetailedEvaluationPlotter class
  - Implement `generate_algorithm_plot()` method that creates 2x2 subplot figure for one algorithm
  - Add actual vs predicted scatter plot in subplot (0,0)
  - Add residual plot in subplot (0,1)
  - Add R² comparison bar chart (train vs test) in subplot (1,0) with overfitting check
  - Add metrics table in subplot (1,1) showing R², RMSE, MAE for train and test sets
  - Save each algorithm's plot as separate PNG file
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Create main training script


  - Create `train_model_a_minimal.py` as main entry point
  - Implement ModelAMinimalTrainer class that orchestrates the training workflow
  - Add `load_data()` method that uses MinimalDataLoader to load and sample data
  - Add `split_data()` method that uses TimeAwareSplit for time-aware splitting
  - Add `train_models()` method that uses ThreeAlgorithmTrainer to train all algorithms
  - Add `evaluate_models()` method that evaluates all algorithms on train, val, and test sets
  - Add `generate_plots()` method that calls BubbleChartGenerator and DetailedEvaluationPlotter
  - Add `save_models()` method that saves all trained models as .pkl files
  - Add `save_results()` method that saves evaluation metrics as JSON
  - Implement comprehensive logging throughout the workflow
  - _Requirements: 1.3, 1.4, 5.1, 5.3, 5.4, 5.5_

- [x] 6. Update config file with new parameters


  - Add MODEL_A_MINIMAL_SAMPLES = 1000 to config.py
  - Add MODEL_A_ALGORITHMS = ['xgboost', 'rf_ensemble', 'gradboost'] to config.py
  - Add BUBBLE_CHART_DPI = 300 to config.py
  - Add BUBBLE_SIZE_MIN = 100 and BUBBLE_SIZE_MAX = 1000 to config.py
  - _Requirements: 4.1_

- [x] 7. Run training and generate all visualizations



  - Execute `train_model_a_minimal.py` to train all 3 algorithms
  - Verify that all 3 models are saved as .pkl files
  - Verify that bubble comparison chart is generated
  - Verify that detailed evaluation plots are generated for all 3 algorithms
  - Verify that evaluation metrics JSON is saved
  - Review bubble chart to compare algorithm performance
  - Review detailed plots to understand individual algorithm behavior
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 5.5_

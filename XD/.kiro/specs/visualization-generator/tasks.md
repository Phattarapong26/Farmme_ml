# Implementation Plan

- [x] 1. Setup project structure and dependencies


  - Create `documentation/visualization-generator/` directory
  - Create `visualizers/` subdirectory with `__init__.py`
  - Create `requirements.txt` with matplotlib, seaborn, pandas, numpy, scikit-learn, Pillow
  - Create `outputs/` directory structure
  - _Requirements: 6.1, 7.1, 7.2_





- [ ] 2. Implement base visualizer class
  - [ ] 2.1 Create `base_visualizer.py` with BaseVisualizer class
    - Implement `__init__` with output directory and DPI configuration
    - Implement `_setup_style()` for consistent matplotlib styling

    - Implement `save_figure()` for saving with consistent settings
    - Configure Thai font support (Sarabun or fallback to system fonts)
    - _Requirements: 1.2, 1.3, 7.4_

  - [x] 2.2 Implement shared chart generation methods



    - Implement `create_heatmap()` for correlation matrices
    - Implement `create_bar_chart()` for metrics comparison
    - Implement `create_line_plot()` for time series
    - Add color scheme configuration

    - _Requirements: 1.1, 1.4, 2.1_

- [ ] 3. Implement Model A visualizer
  - [ ] 3.1 Create `model_a_viz.py` with ModelAVisualizer class
    - Inherit from BaseVisualizer



    - Implement `generate_all()` orchestration method
    - _Requirements: 1.1, 3.1_

  - [x] 3.2 Implement Model A specific visualizations

    - Implement `correlation_heatmap()` for feature correlations
    - Implement `feature_importance()` bar chart for top 15 features
    - Implement `performance_metrics()` comparing XGBoost, RF, NSGA2
    - Implement `prediction_scatter()` for predicted vs actual
    - _Requirements: 1.1, 1.5, 2.1, 3.1, 3.2, 3.3_




- [ ] 4. Implement Model B visualizer
  - [ ] 4.1 Create `model_b_viz.py` with ModelBVisualizer class
    - Inherit from BaseVisualizer

    - Implement `generate_all()` orchestration method
    - _Requirements: 5.1, 5.2_

  - [ ] 4.2 Implement Model B specific visualizations
    - Implement `confusion_matrix()` heatmap with normalized percentages



    - Implement `roc_curve()` with AUC score
    - Implement `feature_importance()` from logistic regression coefficients
    - Implement `classification_metrics()` bar chart for F1, Precision, Recall
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 2.1, 2.2, 3.1_


- [ ] 5. Implement Model C visualizer
  - [ ] 5.1 Create `model_c_viz.py` with ModelCVisualizer class
    - Inherit from BaseVisualizer



    - Implement `generate_all()` orchestration method
    - _Requirements: 4.1, 4.2_

  - [x] 5.2 Implement Model C specific visualizations

    - Implement `price_forecast_plot()` time series with confidence intervals
    - Implement `residual_plot()` for prediction errors
    - Implement `feature_importance()` from XGBoost
    - Implement `performance_metrics()` bar chart for R², RMSE, MAE, MAPE



    - _Requirements: 4.1, 4.2, 4.3, 2.1, 2.5, 3.1_

- [ ] 6. Implement Model D visualizer
  - [ ] 6.1 Create `model_d_viz.py` with ModelDVisualizer class
    - Inherit from BaseVisualizer

    - Implement `generate_all()` orchestration method
    - _Requirements: 4.1_

  - [ ] 6.2 Implement Model D specific visualizations
    - Implement `convergence_plot()` for Thompson Sampling arm selection
    - Implement `profit_distribution()` box plot or violin plot

    - Implement `decision_confidence()` posterior probability distributions
    - _Requirements: 4.1, 4.2, 3.1_

- [ ] 7. Implement comparison visualizer
  - [x] 7.1 Create `comparison_viz.py` with ComparisonVisualizer class

    - Inherit from BaseVisualizer

    - Implement `generate_all()` orchestration method
    - _Requirements: 2.1, 2.2_

  - [ ] 7.2 Implement cross-model comparison visualizations
    - Implement `performance_comparison()` grouped bar chart with normalized metrics
    - Implement `complexity_vs_performance()` scatter plot

    - Add metric normalization logic for fair comparison
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 8. Implement main orchestrator script



  - [ ] 8.1 Create `generate_all_visualizations.py` main script
    - Implement `setup_directories()` with timestamp-based folder creation
    - Implement `load_model_data()` to load .pkl files and evaluation JSONs
    - Add progress logging with clear status messages

    - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.2, 7.4_

  - [ ] 8.2 Implement visualization generation workflow
    - Call each model visualizer's `generate_all()` method
    - Call comparison visualizer's `generate_all()` method




    - Implement error handling to continue on individual failures
    - Track execution time and ensure completion within 5 minutes
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

  - [ ] 8.3 Implement output documentation
    - Generate `README.md` listing all created visualizations with descriptions

    - Generate `index.html` for browser-based preview of all charts
    - Save execution log to file
    - Print summary of generated files to console
    - _Requirements: 7.3, 7.5_

- [ ] 9. Add error handling and logging
  - [ ] 9.1 Implement comprehensive error handling
    - Add try-except blocks for missing model files
    - Add try-except blocks for missing evaluation JSONs
    - Add try-except blocks for visualization generation failures
    - Log warnings for skipped visualizations
    - _Requirements: 6.5_

  - [ ] 9.2 Configure logging system
    - Setup logging to both file and console
    - Add timestamp and log level to messages
    - Create separate log file in output directory
    - _Requirements: 6.3_

- [ ] 10. Create execution script and documentation
  - [ ] 10.1 Create batch file for Windows execution
    - Create `run_visualizations.bat` to activate venv and run script
    - Add error checking and pause at end
    - _Requirements: 6.1, 6.4_

  - [ ] 10.2 Create user documentation
    - Create `README.md` in visualization-generator root with usage instructions
    - Document required model files and their locations
    - Document output structure and file naming conventions
    - Add troubleshooting section for common issues
    - _Requirements: 7.3_

- [ ] 11. Test and validate
  - [ ] 11.1 Test with actual model files
    - Run script with real Model A, B, C, D files
    - Verify all visualizations are generated correctly
    - Check image quality and DPI
    - Verify Thai text rendering if applicable
    - _Requirements: 1.2, 6.4_

  - [ ] 11.2 Test error scenarios
    - Test with missing model files
    - Test with corrupted evaluation JSONs
    - Verify script continues on individual failures
    - Check error messages are clear and helpful
    - _Requirements: 6.5_

# Requirements Document

## Introduction

ระบบ retrain Model A (Crop Recommendation) ใหม่โดยเพิ่มจำนวน algorithms จาก 2 เป็น 3 algorithms และสร้างกราฟ bubble comparison chart สำหรับเปรียบเทียบประสิทธิภาพของแต่ละ algorithm โดยใช้ minimal dataset เพื่อความรวดเร็วในการทดสอบ

## Glossary

- **Model A**: โมเดล Crop Recommendation ที่ใช้ทำนาย ROI (Return on Investment) ของพืชแต่ละชนิด
- **Algorithm**: วิธีการ machine learning ที่ใช้ในการ train model
- **Bubble Comparison Chart**: กราฟแบบ bubble chart ที่แสดงการเปรียบเทียบ algorithms โดยใช้ 3 มิติ (R², RMSE, และขนาด bubble แทน training time หรือ complexity)
- **Minimal Dataset**: ชุดข้อมูลขนาดเล็กที่ใช้สำหรับการทดสอบและ visualization
- **Training System**: ระบบที่ใช้ train และ evaluate models
- **Evaluation System**: ระบบที่ใช้ประเมินประสิทธิภาพของ models

## Requirements

### Requirement 1

**User Story:** As a data scientist, I want to train Model A with 3 different algorithms, so that I can compare their performance comprehensively

#### Acceptance Criteria

1. WHEN the Training System executes, THE Training System SHALL train Model A using exactly 3 algorithms (XGBoost, Random Forest + ElasticNet, and Gradient Boosting)
2. WHEN training completes, THE Training System SHALL evaluate each algorithm on train, validation, and test sets
3. WHEN evaluation completes, THE Training System SHALL save evaluation metrics (R², RMSE, MAE) for each algorithm
4. WHEN saving models, THE Training System SHALL save each trained algorithm as a separate .pkl file
5. WHERE minimal dataset mode is enabled, THE Training System SHALL use a reduced dataset (maximum 1000 samples) for faster training

### Requirement 2

**User Story:** As a data scientist, I want to see bubble comparison charts for all algorithms, so that I can quickly understand their trade-offs

#### Acceptance Criteria

1. WHEN evaluation completes, THE Evaluation System SHALL generate a bubble comparison chart with R² on x-axis and RMSE on y-axis
2. WHEN generating bubble chart, THE Evaluation System SHALL represent each algorithm as a bubble with size proportional to training time or model complexity
3. WHEN generating bubble chart, THE Evaluation System SHALL use distinct colors for each algorithm
4. WHEN generating bubble chart, THE Evaluation System SHALL add labels showing algorithm names and key metrics
5. THE Evaluation System SHALL save the bubble comparison chart as a high-resolution PNG file (minimum 300 DPI)

### Requirement 3

**User Story:** As a data scientist, I want to see detailed evaluation plots for each algorithm, so that I can understand individual algorithm performance

#### Acceptance Criteria

1. WHEN generating evaluation plots, THE Evaluation System SHALL create a 2x2 subplot figure for each algorithm
2. WHEN creating subplots, THE Evaluation System SHALL include actual vs predicted scatter plot in the first subplot
3. WHEN creating subplots, THE Evaluation System SHALL include residual plot in the second subplot
4. WHEN creating subplots, THE Evaluation System SHALL include R² comparison bar chart (train vs test) in the third subplot
5. WHEN creating subplots, THE Evaluation System SHALL include metrics table in the fourth subplot

### Requirement 4

**User Story:** As a data scientist, I want the training process to use minimal data efficiently, so that I can iterate quickly during development

#### Acceptance Criteria

1. WHEN minimal dataset mode is enabled, THE Training System SHALL sample maximum 1000 records from the full dataset
2. WHEN sampling data, THE Training System SHALL maintain time-aware split ratios (70% train, 20% validation, 10% test)
3. WHEN sampling data, THE Training System SHALL preserve the distribution of crop types in the sample
4. THE Training System SHALL log the dataset size and split information to the console
5. WHEN training completes, THE Training System SHALL report total training time for all algorithms

### Requirement 5

**User Story:** As a data scientist, I want clear logging and progress indicators, so that I can monitor the training process

#### Acceptance Criteria

1. WHEN training starts, THE Training System SHALL log the start time and dataset information
2. WHEN training each algorithm, THE Training System SHALL log progress messages indicating which algorithm is being trained
3. WHEN evaluation completes, THE Training System SHALL log metrics for each algorithm in a formatted table
4. WHEN generating plots, THE Training System SHALL log the output directory path
5. WHEN training completes, THE Training System SHALL log a summary showing the best algorithm and its metrics

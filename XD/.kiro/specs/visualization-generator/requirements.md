# Requirements Document

## Introduction

This document outlines the requirements for a visualization generation system that creates various charts, graphs, and heatmaps from the FarmMe ML models and datasets. These visualizations will be used to support the academic documentation and thesis materials.

## Glossary

- **Visualization System**: The automated script-based system that generates charts and graphs from model data
- **Heatmap**: A graphical representation of data where values are depicted by color
- **Correlation Matrix**: A table showing correlation coefficients between variables
- **Model Metrics**: Performance indicators such as accuracy, precision, recall, F1-score
- **Feature Importance**: Statistical measures indicating the relevance of input features to model predictions
- **Output Directory**: The folder structure where generated visualizations are stored

## Requirements

### Requirement 1

**User Story:** As a researcher, I want to generate correlation heatmaps for all models, so that I can analyze feature relationships in the academic document

#### Acceptance Criteria

1. WHEN the visualization script executes, THE Visualization System SHALL generate correlation heatmaps for Model A, Model B, Model C, and Model D
2. THE Visualization System SHALL save each heatmap as a high-resolution PNG file with minimum 300 DPI
3. THE Visualization System SHALL include axis labels and color bars in each heatmap
4. THE Visualization System SHALL organize output files in a structured directory hierarchy by model type
5. WHEN correlation values exceed 0.8, THE Visualization System SHALL highlight these values in the heatmap

### Requirement 2

**User Story:** As a researcher, I want to visualize model performance metrics, so that I can compare model effectiveness in the thesis

#### Acceptance Criteria

1. THE Visualization System SHALL generate bar charts showing accuracy, precision, recall, and F1-score for each model
2. THE Visualization System SHALL create comparison charts displaying all four models side-by-side
3. WHEN generating performance charts, THE Visualization System SHALL include error bars where applicable
4. THE Visualization System SHALL export performance metrics to both PNG and CSV formats
5. THE Visualization System SHALL use consistent color schemes across all performance visualizations

### Requirement 3

**User Story:** As a researcher, I want to generate feature importance plots, so that I can explain which variables drive model predictions

#### Acceptance Criteria

1. THE Visualization System SHALL create horizontal bar charts showing top 15 features by importance for each model
2. THE Visualization System SHALL sort features in descending order of importance
3. THE Visualization System SHALL normalize importance values to a 0-1 scale for consistency
4. WHEN feature importance data is unavailable, THE Visualization System SHALL log a warning and skip that visualization
5. THE Visualization System SHALL include feature names as readable labels on the y-axis

### Requirement 4

**User Story:** As a researcher, I want to visualize training history and learning curves, so that I can demonstrate model convergence

#### Acceptance Criteria

1. THE Visualization System SHALL generate line plots showing training and validation loss over epochs
2. THE Visualization System SHALL create accuracy curves for both training and validation sets
3. THE Visualization System SHALL include grid lines and legends in all learning curve plots
4. WHEN generating learning curves, THE Visualization System SHALL use different line styles for training versus validation
5. THE Visualization System SHALL save learning curves with timestamps in the filename

### Requirement 5

**User Story:** As a researcher, I want to generate confusion matrices for classification models, so that I can analyze prediction patterns

#### Acceptance Criteria

1. THE Visualization System SHALL create confusion matrix heatmaps for Model A and Model D
2. THE Visualization System SHALL display both raw counts and normalized percentages in confusion matrices
3. THE Visualization System SHALL label axes with actual class names rather than numeric indices
4. THE Visualization System SHALL use a diverging color scheme for confusion matrices
5. WHEN class imbalance exists, THE Visualization System SHALL annotate the confusion matrix with class distribution statistics

### Requirement 6

**User Story:** As a researcher, I want an automated script to generate all visualizations at once, so that I can efficiently update documentation materials

#### Acceptance Criteria

1. THE Visualization System SHALL provide a single executable script that generates all required visualizations
2. WHEN the script executes, THE Visualization System SHALL create a timestamped output directory
3. THE Visualization System SHALL log progress messages indicating which visualization is being generated
4. THE Visualization System SHALL complete execution within 5 minutes for all visualizations
5. IF any visualization fails, THE Visualization System SHALL continue processing remaining visualizations and log the error

### Requirement 7

**User Story:** As a researcher, I want visualizations organized by chapter and model, so that I can easily locate graphics for specific document sections

#### Acceptance Criteria

1. THE Visualization System SHALL create subdirectories for each model (Model_A, Model_B, Model_C, Model_D)
2. THE Visualization System SHALL create a summary directory containing cross-model comparison charts
3. THE Visualization System SHALL generate a README file listing all created visualizations with descriptions
4. THE Visualization System SHALL use consistent naming conventions following the pattern: modelname_visualizationtype_timestamp.png
5. THE Visualization System SHALL create an index HTML file for easy preview of all generated visualizations

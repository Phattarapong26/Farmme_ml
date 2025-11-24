# Design Document - ML Models Documentation & Feature Analysis

## Overview

This design document outlines the architecture and implementation approach for creating comprehensive documentation and analysis of the four ML models (A, B, C, D) in the agricultural prediction system. The system will analyze datasets, features, feature engineering techniques, and feature selection methodologies used by each model, providing both documentation and executable validation scripts.

## Architecture

### High-Level Architecture

```
Project Root
├── Documentation/
│   ├── README.md (Master index)
│   ├── Model_A_Documentation.md
│   ├── Model_B_Documentation.md
│   ├── Model_C_Documentation.md
│   ├── Model_D_Documentation.md
│   ├── Feature_Engineering_Guide.md
│   ├── Feature_Selection_Methodology.md
│   └── Data_Leakage_Prevention.md
│
└── test_evaluate/
    ├── correlation_analysis.py
    ├── feature_importance_analysis.py
    ├── mutual_information_analysis.py
    ├── data_leakage_validation.py
    ├── feature_selection_comparison.py
    └── outputs/
        ├── model_a/
        ├── model_b/
        ├── model_c/
        └── model_d/
```

### Component Architecture

1. **Documentation Layer**: Markdown files with comprehensive model explanations
2. **Analysis Layer**: Python scripts for statistical validation
3. **Visualization Layer**: Matplotlib/Seaborn plots for feature analysis
4. **Validation Layer**: Scripts to verify data leakage prevention

## Components and Interfaces

### 1. Documentation Components

#### 1.1 Model Documentation Template

Each model documentation file will follow this structure:

```markdown
# Model X Documentation

## 1. Model Overview
- Purpose and objective
- Target variable and why it was chosen
- Model type (regression/classification/time series/bandit)

## 2. Datasets Used
- List of all datasets with row counts
- Schema for each dataset
- Relationships between datasets

## 3. Features Used
- Complete list of features with data types
- Feature sources (which dataset)
- Feature descriptions

## 4. Feature Engineering
- Feature creation techniques
- Feature transformations
- Temporal features and cyclic encodings
- Categorical encoding methods

## 5. Feature Selection Rationale
- Why each feature was selected
- Domain knowledge justification
- Statistical evidence (correlation, importance)
- Features removed and why

## 6. Data Leakage Prevention
- Post-outcome features identified
- Time-aware splitting strategy
- Validation of no leakage

## 7. Model Performance
- Current metrics (R², F1, RMSE, etc.)
- Expected performance ranges
- Overfitting analysis
```

#### 1.2 Feature Engineering Guide Structure

```markdown
# Feature Engineering Guide

## 1. Introduction to Feature Engineering
- Definition and importance
- Goals: improve model performance, prevent overfitting, enable interpretability

## 2. Feature Creation Techniques
- Lagged features (time series)
- Interaction features
- Polynomial features
- Domain-specific features

## 3. Feature Transformation Techniques
- Standardization (StandardScaler)
- Normalization
- Log transformation
- Cyclic encoding (sin/cos for temporal features)

## 4. Feature Encoding Techniques
- One-Hot Encoding
- Label Encoding
- Hash Encoding (for high cardinality)
- Target Encoding

## 5. Temporal Feature Engineering
- Time-aware feature creation
- Preventing look-ahead bias
- Lagged features for time series
- Rolling window statistics

## 6. Code Examples
- Python implementations for each technique
- Usage in Models A, B, C, D
```

#### 1.3 Feature Selection Methodology Structure

```markdown
# Feature Selection Methodology

## 1. Introduction to Feature Selection
- Why feature selection matters
- Problems it solves (overfitting, computational cost, interpretability)

## 2. Filter Methods
- Variance Threshold
- Correlation Analysis
- Chi-Square Test
- ANOVA F-test
- Mutual Information

## 3. Wrapper Methods
- Forward Selection
- Backward Elimination
- Recursive Feature Elimination (RFE)

## 4. Embedded Methods
- Lasso (L1 Regularization)
- Ridge (L2 Regularization)
- Tree-based Feature Importance (Random Forest, XGBoost)

## 5. Comparison of Methods
- Advantages and disadvantages
- When to use each method
- Computational complexity

## 6. Application to Models A, B, C, D
- Which methods were used
- Results and findings
- Optimal feature sets
```

### 2. Analysis Components

#### 2.1 Correlation Analysis Module

**Purpose**: Compute and visualize feature-target correlations

**Interface**:
```python
class CorrelationAnalyzer:
    def __init__(self, model_name: str, data_path: str)
    def load_data(self) -> pd.DataFrame
    def compute_correlations(self, target: str) -> pd.DataFrame
    def plot_correlation_heatmap(self, output_path: str)
    def plot_top_features(self, n: int, output_path: str)
    def generate_report(self) -> dict
```

**Key Methods**:
- `compute_correlations()`: Calculate Pearson correlation coefficients
- `plot_correlation_heatmap()`: Generate heatmap of feature correlations
- `plot_top_features()`: Bar chart of top N correlated features
- `generate_report()`: Summary statistics and findings

#### 2.2 Feature Importance Analysis Module

**Purpose**: Compute tree-based feature importance scores

**Interface**:
```python
class FeatureImportanceAnalyzer:
    def __init__(self, model_name: str, model_path: str)
    def load_model(self) -> object
    def compute_importance(self) -> pd.DataFrame
    def plot_importance(self, top_n: int, output_path: str)
    def compare_algorithms(self, algorithms: list) -> pd.DataFrame
    def generate_report(self) -> dict
```

**Key Methods**:
- `compute_importance()`: Extract feature importance from trained models
- `plot_importance()`: Bar chart of feature importance scores
- `compare_algorithms()`: Compare importance across XGBoost, Random Forest, etc.
- `generate_report()`: Summary of most important features

#### 2.3 Mutual Information Analysis Module

**Purpose**: Measure feature-target dependencies using mutual information

**Interface**:
```python
class MutualInformationAnalyzer:
    def __init__(self, model_name: str, data_path: str)
    def load_data(self) -> pd.DataFrame
    def compute_mutual_information(self, target: str, discrete: bool) -> pd.DataFrame
    def plot_mi_scores(self, output_path: str)
    def compare_with_correlation(self) -> pd.DataFrame
    def generate_report(self) -> dict
```

**Key Methods**:
- `compute_mutual_information()`: Calculate MI scores for all features
- `plot_mi_scores()`: Bar chart of MI scores
- `compare_with_correlation()`: Compare MI vs correlation for feature ranking
- `generate_report()`: Summary of findings

#### 2.4 Data Leakage Validation Module

**Purpose**: Verify no post-outcome features are used in training

**Interface**:
```python
class DataLeakageValidator:
    def __init__(self, model_name: str, config_path: str)
    def load_forbidden_features(self) -> list
    def check_training_data(self, df: pd.DataFrame) -> dict
    def validate_time_splits(self, train_dates, test_dates) -> bool
    def check_lagged_features(self, df: pd.DataFrame) -> dict
    def generate_report(self) -> dict
```

**Key Methods**:
- `load_forbidden_features()`: Load list of post-outcome features from config
- `check_training_data()`: Verify no forbidden features in training set
- `validate_time_splits()`: Ensure no future information in training
- `check_lagged_features()`: Verify lagged features don't cause look-ahead bias
- `generate_report()`: Validation report with pass/fail status

#### 2.5 Feature Selection Comparison Module

**Purpose**: Compare different feature selection methods

**Interface**:
```python
class FeatureSelectionComparator:
    def __init__(self, model_name: str, data_path: str)
    def apply_variance_threshold(self, threshold: float) -> list
    def apply_correlation_filter(self, threshold: float) -> list
    def apply_mutual_information(self, k: int) -> list
    def apply_tree_importance(self, threshold: float) -> list
    def compare_methods(self) -> pd.DataFrame
    def plot_venn_diagram(self, output_path: str)
    def evaluate_performance(self, feature_sets: dict) -> pd.DataFrame
    def generate_report(self) -> dict
```

**Key Methods**:
- `apply_*()`: Apply different feature selection methods
- `compare_methods()`: Compare selected features across methods
- `plot_venn_diagram()`: Visualize overlap between methods
- `evaluate_performance()`: Train models with different feature sets and compare
- `generate_report()`: Comprehensive comparison report

### 3. Visualization Components

#### 3.1 Visualization Standards

All visualizations will follow these standards:
- **Figure size**: 12x8 inches for single plots, 16x10 for multi-panel
- **DPI**: 300 for publication quality
- **Color scheme**: Seaborn 'viridis' or 'RdYlGn' for heatmaps
- **Font sizes**: Title 14pt bold, labels 12pt, ticks 10pt
- **Grid**: Light gray, alpha 0.3
- **File format**: PNG with transparent background

#### 3.2 Visualization Types

1. **Correlation Heatmaps**
   - Annotated with correlation coefficients
   - Color-coded by strength (-1 to 1)
   - Hierarchical clustering for feature grouping

2. **Feature Importance Bar Charts**
   - Horizontal bars sorted by importance
   - Color-coded by importance threshold
   - Error bars for ensemble methods

3. **Mutual Information Plots**
   - Bar chart with MI scores
   - Comparison with correlation scores
   - Threshold lines for selection

4. **Venn Diagrams**
   - Show overlap between feature selection methods
   - Labeled with feature counts
   - Color-coded by method

5. **Performance Comparison Plots**
   - Line plots showing metric vs number of features
   - Bar charts comparing different feature sets
   - Box plots for cross-validation results

## Data Models

### 1. Feature Metadata Schema

```python
{
    "feature_name": str,
    "data_type": str,  # "numeric", "categorical", "temporal"
    "source_dataset": str,
    "description": str,
    "engineering_method": str,  # "raw", "lagged", "encoded", "transformed"
    "is_pre_planting": bool,
    "correlation_with_target": float,
    "importance_score": float,
    "mutual_information": float,
    "selected": bool,
    "selection_method": str
}
```

### 2. Model Analysis Results Schema

```python
{
    "model_name": str,
    "analysis_date": str,
    "datasets_used": [
        {
            "name": str,
            "path": str,
            "row_count": int,
            "column_count": int,
            "columns": list
        }
    ],
    "features": [
        # Feature metadata objects
    ],
    "target_variable": {
        "name": str,
        "type": str,
        "description": str,
        "statistics": dict
    },
    "feature_selection_results": {
        "correlation_analysis": dict,
        "feature_importance": dict,
        "mutual_information": dict,
        "selected_features": list,
        "removed_features": list
    },
    "data_leakage_check": {
        "passed": bool,
        "forbidden_features_found": list,
        "warnings": list
    },
    "performance_metrics": dict
}
```

## Error Handling

### 1. Data Loading Errors

- **Missing datasets**: Provide clear error message with expected path
- **Schema mismatch**: Warn if expected columns are missing
- **Empty datasets**: Raise error if dataset has no rows

### 2. Analysis Errors

- **Insufficient data**: Warn if sample size too small for analysis
- **High missing values**: Warn if >5% missing values in features
- **Multicollinearity**: Warn if features highly correlated (>0.95)
- **Zero variance**: Warn if features have zero or near-zero variance

### 3. Validation Errors

- **Data leakage detected**: Raise error with list of forbidden features found
- **Time leakage**: Raise error if test dates before train dates
- **Look-ahead bias**: Warn if lagged features computed incorrectly

## Testing Strategy

### 1. Unit Tests

- Test each analysis module independently
- Mock data for consistent testing
- Verify calculations (correlation, MI, importance)
- Test error handling for edge cases

### 2. Integration Tests

- Test full pipeline from data loading to report generation
- Verify all visualizations are created
- Check output file structure
- Validate JSON schema for results

### 3. Validation Tests

- Compare analysis results with known ground truth
- Verify feature importance matches XGBoost's built-in importance
- Check correlation calculations against pandas.corr()
- Validate MI scores against sklearn.feature_selection

### 4. Documentation Tests

- Verify all markdown files are created
- Check internal links work correctly
- Validate code examples run without errors
- Ensure all sections are complete

## Implementation Phases

### Phase 1: Documentation Creation
1. Create Documentation folder structure
2. Write Model A documentation
3. Write Model B documentation
4. Write Model C documentation
5. Write Model D documentation
6. Write Feature Engineering Guide
7. Write Feature Selection Methodology
8. Write master README with navigation

### Phase 2: Analysis Scripts Development
1. Implement CorrelationAnalyzer
2. Implement FeatureImportanceAnalyzer
3. Implement MutualInformationAnalyzer
4. Implement DataLeakageValidator
5. Implement FeatureSelectionComparator

### Phase 3: Visualization and Reporting
1. Generate correlation heatmaps for all models
2. Generate feature importance charts
3. Generate MI plots
4. Generate comparison visualizations
5. Create summary reports

### Phase 4: Validation and Testing
1. Run data leakage validation
2. Verify feature selection results
3. Compare with existing model performance
4. Generate final comprehensive report

## Performance Considerations

### 1. Computational Efficiency

- **Large datasets**: Use sampling for exploratory analysis
- **Feature importance**: Cache results to avoid recomputation
- **Correlation matrix**: Use efficient numpy operations
- **Parallel processing**: Use joblib for independent analyses

### 2. Memory Management

- **Chunked processing**: Load large datasets in chunks
- **Feature selection**: Process features in batches
- **Visualization**: Generate plots one at a time, close figures

### 3. Scalability

- **Modular design**: Each analysis module independent
- **Configurable**: Parameters in config files
- **Extensible**: Easy to add new analysis methods
- **Reusable**: Analysis modules work for any model

## Dependencies

### Python Libraries

```
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
xgboost>=1.7.0
matplotlib>=3.6.0
seaborn>=0.12.0
scipy>=1.10.0
```

### Project Dependencies

- Access to REMEDIATION_PRODUCTION models
- Access to buildingModel.py/Dataset files
- Config.py for paths and parameters

## Configuration

### config.py Extensions

```python
# Documentation paths
DOCUMENTATION_PATH = BASE_DIR / 'Documentation'
TEST_EVALUATE_PATH = BASE_DIR / 'test_evaluate'
ANALYSIS_OUTPUT_PATH = TEST_EVALUATE_PATH / 'outputs'

# Analysis parameters
CORRELATION_THRESHOLD = 0.05
IMPORTANCE_THRESHOLD = 0.01
MI_THRESHOLD = 0.01
VARIANCE_THRESHOLD = 0.01

# Visualization parameters
FIGURE_DPI = 300
FIGURE_SIZE = (12, 8)
COLOR_PALETTE = 'viridis'
```

## Best Practices

### 1. Documentation

- Use clear, concise language
- Include code examples with comments
- Provide visual diagrams where helpful
- Link related sections
- Keep documentation up-to-date with code

### 2. Analysis

- Always validate assumptions
- Report confidence intervals
- Document limitations
- Compare multiple methods
- Provide reproducible results

### 3. Code Quality

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions
- Add inline comments for complex logic
- Use meaningful variable names

### 4. Version Control

- Commit documentation and code together
- Use descriptive commit messages
- Tag releases
- Maintain changelog

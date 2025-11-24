# Design Document

## Overview

ออกแบบระบบ retrain Model A (Crop Recommendation) ใหม่โดยเพิ่มจำนวน algorithms จาก 2 เป็น 3 algorithms และสร้างกราฟ bubble comparison chart สำหรับการเปรียบเทียบประสิทธิภาพ ระบบจะใช้ minimal dataset เพื่อความรวดเร็วในการทดสอบและ visualization

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Model A Retraining System                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │ Data Loader  │─────▶│   Trainer    │─────▶│ Evaluator │ │
│  │  (Minimal)   │      │ (3 Algos)    │      │ (Metrics) │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      │                     │       │
│         ▼                      ▼                     ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │ Time-Aware   │      │ Model Saver  │      │   Plot    │ │
│  │   Splitter   │      │   (.pkl)     │      │ Generator │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                                                       │       │
│                                                       ▼       │
│                                               ┌───────────┐  │
│                                               │  Bubble   │  │
│                                               │Comparison │  │
│                                               │   Chart   │  │
│                                               └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Flow

1. **Data Loader**: โหลดและ sample minimal dataset
2. **Time-Aware Splitter**: แบ่งข้อมูลตาม time-series
3. **Trainer**: Train 3 algorithms พร้อมกัน
4. **Evaluator**: ประเมินประสิทธิภาพแต่ละ algorithm
5. **Plot Generator**: สร้างกราฟ evaluation และ bubble comparison
6. **Model Saver**: บันทึก trained models

## Components and Interfaces

### 1. MinimalDataLoader

**Purpose**: โหลดและ sample ข้อมูลให้เหลือ minimal size

**Interface**:
```python
class MinimalDataLoader:
    def __init__(self, max_samples: int = 1000):
        """Initialize with maximum sample size"""
        
    def load_and_sample(self) -> pd.DataFrame:
        """Load full dataset and sample to minimal size"""
        
    def validate_sample(self, df: pd.DataFrame) -> bool:
        """Validate that sample maintains data distribution"""
```

**Key Methods**:
- `load_and_sample()`: โหลดข้อมูลเต็มและ sample ตาม stratified sampling
- `validate_sample()`: ตรวจสอบว่า sample มี distribution ใกล้เคียงกับข้อมูลเต็ม

### 2. ThreeAlgorithmTrainer

**Purpose**: Train Model A ด้วย 3 algorithms

**Interface**:
```python
class ThreeAlgorithmTrainer:
    def __init__(self):
        """Initialize 3 algorithms"""
        
    def train_all(self, X_train, y_train, X_val, y_val) -> Dict[str, Any]:
        """Train all 3 algorithms and return models"""
        
    def get_training_times(self) -> Dict[str, float]:
        """Get training time for each algorithm"""
```

**Algorithms**:
1. **XGBoost**: Gradient boosting with regularization
2. **Random Forest + ElasticNet**: Ensemble approach
3. **Gradient Boosting Regressor**: sklearn's GradientBoostingRegressor

**Key Features**:
- Track training time for each algorithm
- Use consistent hyperparameters for fair comparison
- Apply regularization to prevent overfitting

### 3. BubbleChartGenerator

**Purpose**: สร้าง bubble comparison chart

**Interface**:
```python
class BubbleChartGenerator:
    def __init__(self, results: Dict[str, Any]):
        """Initialize with evaluation results"""
        
    def generate_bubble_chart(self, output_path: Path) -> None:
        """Generate and save bubble comparison chart"""
        
    def _calculate_bubble_sizes(self) -> List[float]:
        """Calculate bubble sizes based on training time or complexity"""
```

**Chart Specifications**:
- **X-axis**: R² Score (0.0 to 1.0)
- **Y-axis**: RMSE (%)
- **Bubble Size**: Training time (seconds) หรือ model complexity
- **Colors**: แต่ละ algorithm ใช้สีต่างกัน
- **Labels**: แสดงชื่อ algorithm และ metrics หลัก

### 4. DetailedEvaluationPlotter

**Purpose**: สร้างกราฟ evaluation แบบละเอียดสำหรับแต่ละ algorithm

**Interface**:
```python
class DetailedEvaluationPlotter:
    def __init__(self, model_name: str, results: Dict[str, Any]):
        """Initialize with model results"""
        
    def generate_algorithm_plot(self, algo_key: str, output_path: Path) -> None:
        """Generate 2x2 subplot for one algorithm"""
        
    def generate_comparison_plot(self, output_path: Path) -> None:
        """Generate comparison plot for all algorithms"""
```

**Plot Types**:
1. **Actual vs Predicted**: Scatter plot with perfect prediction line
2. **Residual Plot**: Residuals vs predicted values
3. **R² Comparison**: Bar chart comparing train vs test R²
4. **Metrics Table**: Table showing all metrics

## Data Models

### TrainingResult

```python
@dataclass
class TrainingResult:
    algorithm_name: str
    model: Any
    train_metrics: Dict[str, float]
    val_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    training_time: float
    predictions: List[float]
```

### EvaluationMetrics

```python
@dataclass
class EvaluationMetrics:
    r2: float
    rmse: float
    mae: float
    mape: float  # Optional
```

### BubbleChartData

```python
@dataclass
class BubbleChartData:
    algorithm_name: str
    r2_score: float
    rmse: float
    bubble_size: float  # Training time or complexity
    color: str
```

## Error Handling

### Data Loading Errors

```python
try:
    df = loader.load_and_sample()
except FileNotFoundError:
    logger.error("Dataset files not found")
    raise
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
```

### Training Errors

```python
try:
    model.train(X_train, y_train, X_val, y_val)
except Exception as e:
    logger.error(f"Training failed for {algo_name}: {e}")
    # Continue with other algorithms
    continue
```

### Plotting Errors

```python
try:
    plotter.generate_bubble_chart(output_path)
except Exception as e:
    logger.error(f"Failed to generate bubble chart: {e}")
    # Continue with other plots
```

## Testing Strategy

### Unit Tests

1. **Test MinimalDataLoader**:
   - Test sampling maintains distribution
   - Test sample size is correct
   - Test validation logic

2. **Test ThreeAlgorithmTrainer**:
   - Test all 3 algorithms train successfully
   - Test training times are recorded
   - Test models can make predictions

3. **Test BubbleChartGenerator**:
   - Test chart is generated with correct axes
   - Test bubble sizes are calculated correctly
   - Test colors are distinct

### Integration Tests

1. **End-to-End Training**:
   - Load minimal data → Train → Evaluate → Plot
   - Verify all outputs are created
   - Verify metrics are reasonable

2. **Plot Generation**:
   - Generate all plots
   - Verify files exist
   - Verify file sizes are reasonable

### Performance Tests

1. **Training Time**:
   - Measure total training time
   - Verify it's under 5 minutes for minimal dataset

2. **Memory Usage**:
   - Monitor memory during training
   - Verify no memory leaks

## Implementation Notes

### Minimal Dataset Strategy

- Use stratified sampling by crop_id to maintain crop distribution
- Sample maximum 1000 records
- Maintain time-aware split ratios (70/20/10)
- Log original vs sampled dataset statistics

### Algorithm Selection

**Why these 3 algorithms?**

1. **XGBoost**: Industry standard, excellent performance
2. **Random Forest + ElasticNet**: Ensemble approach, good baseline
3. **Gradient Boosting Regressor**: sklearn's implementation, different from XGBoost

### Bubble Chart Design

**Bubble Size Calculation**:
```python
# Normalize training times to bubble sizes (100-1000)
min_time = min(training_times)
max_time = max(training_times)
bubble_size = 100 + 900 * (time - min_time) / (max_time - min_time)
```

**Color Scheme**:
- XGBoost: Blue (#3498db)
- Random Forest + ElasticNet: Green (#2ecc71)
- Gradient Boosting: Orange (#e67e22)

### File Structure

```
REMEDIATION_PRODUCTION/
├── Model_A_Retrain/
│   ├── train_model_a_minimal.py       # Main training script
│   ├── minimal_data_loader.py         # Data loading with sampling
│   ├── three_algorithm_trainer.py     # 3 algorithms trainer
│   ├── bubble_chart_generator.py      # Bubble chart generator
│   └── detailed_plotter.py            # Detailed evaluation plots
├── trained_models/
│   ├── model_a_xgboost_minimal.pkl
│   ├── model_a_rf_ensemble_minimal.pkl
│   └── model_a_gradboost_minimal.pkl
└── outputs/
    └── model_a_minimal_evaluation/
        ├── bubble_comparison.png
        ├── model_a_xgboost_evaluation.png
        ├── model_a_rf_ensemble_evaluation.png
        ├── model_a_gradboost_evaluation.png
        └── metadata.json
```

## Configuration

### New Config Parameters

```python
# Add to config.py
MODEL_A_MINIMAL_SAMPLES = 1000
MODEL_A_ALGORITHMS = ['xgboost', 'rf_ensemble', 'gradboost']
BUBBLE_CHART_DPI = 300
BUBBLE_SIZE_MIN = 100
BUBBLE_SIZE_MAX = 1000
```

## Dependencies

- pandas
- numpy
- scikit-learn
- xgboost
- matplotlib
- seaborn
- pickle
- logging

All dependencies are already available in the existing environment.

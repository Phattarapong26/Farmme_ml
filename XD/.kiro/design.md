# Design Document

## Overview

ระบบ ML Farming Pipeline ประกอบด้วย 4 โมเดล ML ที่ทำงานต่อเนื่องกันตลอดฤดูกาลเพาะปลูก โดยแต่ละโมเดลออกแบบมาเพื่อตอบโจทย์เฉพาะในแต่ละขั้นตอนของการตัดสินใจของเกษตรกร ระบบมีการป้องกัน data leakage อย่างเข้มงวดและใช้เฉพาะข้อมูลที่สามารถสังเกตได้ในขณะตัดสินใจเท่านั้น

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ML Farming Pipeline                          │
│                                                                 │
│  Stage 1          Stage 2          Stage 3          Stage 4    │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│  │Model A  │───▶│Model B  │───▶│Model C  │───▶│Model D  │    │
│  │Crop Rec │    │Planting │    │Price    │    │Harvest  │    │
│  │         │    │Window   │    │Forecast │    │Decision │    │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         Data Validation & Leakage Prevention         │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **No Data Leakage**: ใช้เฉพาะ pre-decision observable data
2. **Time-Aware Processing**: แบ่งข้อมูลตามลำดับเวลา
3. **Modular Design**: แต่ละโมเดลทำงานอิสระและสามารถ test แยกได้
4. **Explainable AI**: ทุกคำแนะนำมีเหตุผลและ confidence score
5. **Production Ready**: มี error handling, logging, และ monitoring

## Architecture

### High-Level Architecture


ระบบแบ่งออกเป็น 6 components หลัก:

1. **Data Loaders**: โหลดและทำความสะอาดข้อมูล ป้องกัน data leakage
2. **Model A - Crop Recommendation**: Multi-objective optimization สำหรับแนะนำพืช
3. **Model B - Planting Window**: Binary classification สำหรับช่วงเวลาปลูก
4. **Model C - Price Forecast**: Time series forecasting สำหรับราคา
5. **Model D - Harvest Decision**: Contextual bandit สำหรับตัดสินใจเก็บเกี่ยว
6. **Pipeline Integration**: เชื่อมโยงทั้ง 4 โมเดลและจัดการ state

### Component Interaction Flow

```
User Input (Farm Profile)
    │
    ▼
┌─────────────────────────┐
│  Data Loader Clean      │
│  - Validate inputs      │
│  - Remove leakage       │
│  - Feature engineering  │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Model A: Crop Rec      │
│  Input: Farm profile    │
│  Output: Top 3 crops    │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Model B: Planting      │
│  Input: Soil + Weather  │
│  Output: Good/Bad       │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Model C: Price         │
│  Input: Crop + Days     │
│  Output: Price forecast │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Model D: Harvest       │
│  Input: Price + Health  │
│  Output: Action + Profit│
└─────────────────────────┘
    │
    ▼
Final Recommendation
```

## Components and Interfaces

### 1. Data Loader Component


**Purpose**: โหลดข้อมูลที่สะอาดและป้องกัน data leakage

**Class**: `DataLoaderClean`

**Methods**:
```python
class DataLoaderClean:
    def __init__(self, data_path: str)
    
    def load_cultivation_clean(self) -> pd.DataFrame
        """Load cultivation data without post-outcome features"""
        # Returns: DataFrame with only pre-decision features
        
    def load_planting_window_clean(self) -> pd.DataFrame
        """Load planting data without future information"""
        # Returns: DataFrame with temporal features
        
    def validate_no_leakage(self, df: pd.DataFrame, 
                           forbidden_features: List[str]) -> bool
        """Check if DataFrame contains forbidden features"""
        # Returns: True if clean, raises error if leakage found
        
    def get_feature_correlations(self, df: pd.DataFrame, 
                                target: str) -> pd.DataFrame
        """Calculate feature correlations with target"""
        # Returns: Correlation matrix sorted by absolute value
```

**Forbidden Features by Model**:
- Model A: `actual_yield_kg`, `success_rate`, `harvest_timing_adjustment`, `yield_efficiency`
- Model B: `harvest_date`, `actual_yield_kg`, `success_rate`
- Model D: `actual_harvest_date`, `future_price`, `days_since_planting` (if calculated from harvest_date)

**Data Validation Rules**:
1. ตรวจสอบ missing values (< 5% allowed)
2. ตรวจสอบ outliers (IQR method)
3. ตรวจสอบ data types
4. ตรวจสอบ temporal ordering (for time-series data)

### 2. Model A - Crop Recommendation System

**Purpose**: แนะนำพืช 3 อันดับแรกที่เหมาะสมกับฟาร์ม

**Algorithm**: NSGA-II (primary), XGBoost, Random Forest

**Input Features**:
```python
{
    'farm_size_rai': float,           # 1-100 rai
    'soil_type': str,                 # categorical
    'soil_ph': float,                 # 4.0-8.5
    'soil_nitrogen': float,           # mg/kg
    'soil_phosphorus': float,         # mg/kg
    'soil_potassium': float,          # mg/kg
    'avg_temperature': float,         # 20-40°C
    'avg_rainfall': float,            # mm/month
    'humidity': float,                # 40-100%
    'budget_baht': float,             # 10,000-1,000,000
    'farmer_experience_years': int,   # 0-50
    'water_availability': str,        # Low/Medium/High
}
```

**Output Format**:
```python
{
    'recommendations': [
        {
            'crop_name': str,
            'roi_percent': float,
            'risk_score': float,        # 0-100
            'stability_score': float,   # 0-100
            'total_profit_baht': float,
            'investment_required': float,
            'days_to_maturity': int,
            'confidence': float,        # 0-1
            'reasons': List[str]
        }
    ]
}
```


**Class Design**:
```python
class ModelA_NSGA2:
    def __init__(self, population_size=100, generations=50)
    
    def train(self, X_train, y_train_roi, y_train_risk)
        """Train multi-objective optimization"""
        
    def predict(self, X) -> List[Dict]
        """Return top 3 crops with Pareto optimal solutions"""
        
    def evaluate(self, y_true, y_pred) -> Dict
        """Calculate R², MAE, RMSE"""

class ModelA_XGBoost:
    def __init__(self, **params)
    
    def train(self, X_train, y_train)
        """Train XGBoost regressor"""
        
    def predict(self, X) -> np.ndarray
        """Predict ROI"""
        
    def get_feature_importance(self) -> pd.DataFrame
        """Return feature importance scores"""
```

**Multi-Objective Optimization**:
- Objective 1: Maximize ROI
- Objective 2: Minimize Risk
- Objective 3: Maximize Stability

**Expected Performance**:
- R² Score: 0.45-0.55
- MAE: ±8-12% ROI
- Training Time: < 5 minutes

### 3. Model B - Planting Window Classifier

**Purpose**: จำแนกว่าช่วงเวลาปัจจุบันเหมาะสมในการปลูกหรือไม่

**Algorithm**: XGBoost Classifier, Temporal Gradient Boosting, Logistic Regression

**Input Features**:
```python
{
    'soil_moisture_percent': float,    # 0-100%
    'recent_rainfall_mm': float,       # last 7 days
    'temperature_c': float,            # current
    'humidity_percent': float,         # current
    'soil_temperature_c': float,       # current
    'wind_speed_kmh': float,          # current
    'month': int,                      # 1-12
    'day_of_year': int,               # 1-365
    'month_sin': float,               # cyclic encoding
    'month_cos': float,               # cyclic encoding
    'day_sin': float,                 # cyclic encoding
    'day_cos': float,                 # cyclic encoding
    'crop_type': str,                 # from Model A
}
```

**Output Format**:
```python
{
    'classification': str,              # 'Good' or 'Bad'
    'confidence': float,                # 0-1
    'optimal_time_range': str,          # e.g., '06:00-14:00'
    'expected_germination_rate': float, # 0-1
    'risk_level': str,                  # Low/Medium/High
    'reasons': List[str],
    'weather_warnings': List[str]
}
```

**Class Design**:
```python
class ModelB_XGBoost:
    def __init__(self, **params)
    
    def train(self, X_train, y_train)
        """Train with time-aware split"""
        
    def predict(self, X) -> np.ndarray
        """Predict Good/Bad classification"""
        
    def predict_proba(self, X) -> np.ndarray
        """Return probability scores"""
        
    def evaluate(self, y_true, y_pred) -> Dict
        """Calculate F1, Precision, Recall, AUC"""
```


**Time-Aware Data Split**:
```python
# Split by date, not random
train_data = data[data['date'] < '2023-01-01']
val_data = data[(data['date'] >= '2023-01-01') & 
                (data['date'] < '2024-01-01')]
test_data = data[data['date'] >= '2024-01-01']

# Embargo period: 7 days gap between sets
```

**Expected Performance**:
- F1 Score: 0.70-0.75
- Precision: ~0.75 (minimize false positives)
- Recall: ~0.68 (minimize missed good windows)
- AUC: 0.80-0.85

### 4. Model C - Price Forecast System

**Purpose**: คาดการณ์ราคาพืชผลในอนาคต

**Algorithm**: Time Series Forecasting (ARIMA, Prophet, LSTM)

**Input Features**:
```python
{
    'crop_type': str,
    'current_price': float,           # baht/kg
    'historical_prices': List[float], # last 90 days
    'days_to_harvest': int,           # remaining days
    'season': str,                    # Dry/Wet
    'market_demand_index': float,     # 0-100
    'supply_forecast': float,         # tons
    'export_volume': float,           # tons
    'competitor_prices': List[float]
}
```

**Output Format**:
```python
{
    'forecast_price_median': float,    # baht/kg
    'forecast_price_q10': float,       # 10th percentile
    'forecast_price_q90': float,       # 90th percentile
    'confidence': float,               # 0-1
    'price_trend': str,                # Up/Down/Stable
    'expected_change_percent': float,
    'expected_revenue': float,
    'risk_assessment': str
}
```

**Class Design**:
```python
class ModelC_PriceForecast:
    def __init__(self, model_type='prophet')
    
    def train(self, historical_data: pd.DataFrame)
        """Train on historical price data"""
        
    def predict(self, days_ahead: int, 
               current_price: float) -> Dict
        """Forecast price with confidence intervals"""
        
    def evaluate(self, y_true, y_pred) -> Dict
        """Calculate R², RMSE, MAPE"""
        
    def update_daily(self, new_data: pd.DataFrame)
        """Incremental update with new price data"""
```

**Expected Performance**:
- R² Score: > 0.99
- RMSE: < 0.30 baht/kg
- MAPE: < 0.5%

### 5. Model D - Harvest Decision Engine

**Purpose**: แนะนำว่าควรเก็บเกี่ยวเลยหรือรอ

**Algorithm**: Thompson Sampling (Contextual Bandit)


**Actions**:
1. Harvest Now
2. Wait 3 Days
3. Wait 7 Days

**Input Features (Context)**:
```python
{
    'current_price': float,            # baht/kg
    'forecast_price_median': float,    # from Model C
    'forecast_price_std': float,       # uncertainty
    'plant_health_score': float,       # 0-100
    'plant_age_days': int,            # days since planting
    'storage_cost_per_day': float,    # baht
    'yield_kg': float,                # expected yield
    'weather_risk_7d': float,         # 0-1
    'market_volatility': float        # 0-1
}
```

**Output Format**:
```python
{
    'recommended_action': str,         # 'Harvest Now', 'Wait 3 Days', 'Wait 7 Days'
    'action_confidence': float,        # 0-1
    'profit_projections': {
        'harvest_now': float,
        'wait_3_days': float,
        'wait_7_days': float
    },
    'profit_difference': float,        # vs harvest now
    'risk_assessment': str,
    'reasons': List[str]
}
```

**Class Design**:
```python
class HarvestDecisionEngine:
    def __init__(self, n_actions=3, alpha=1.0, beta=1.0)
        """Initialize Thompson Sampling with Beta priors"""
        self.actions = ['Harvest Now', 'Wait 3 Days', 'Wait 7 Days']
        self.alpha = np.ones(n_actions) * alpha  # successes
        self.beta = np.ones(n_actions) * beta    # failures
        
    def decide(self, context: Dict) -> Dict
        """Sample from Beta distributions and select action"""
        # Sample theta from Beta(alpha, beta) for each action
        # Select action with highest sampled value
        # Calculate profit projections
        # Return recommendation
        
    def update_beliefs(self, action_idx: int, reward: float)
        """Update Beta parameters based on outcome"""
        # If reward > threshold: alpha[action_idx] += 1
        # Else: beta[action_idx] += 1
        
    def get_action_probabilities(self) -> np.ndarray
        """Return current probability of selecting each action"""
        
    def calculate_profit(self, action: str, context: Dict) -> float
        """Calculate expected profit for given action"""
        # profit = (price * yield) - (storage_cost * days) - (risk_penalty)
```

**Thompson Sampling Algorithm**:
```
For each decision:
1. For each action a in {Now, Wait3, Wait7}:
   - Sample θ_a ~ Beta(α_a, β_a)
2. Select action a* = argmax(θ_a)
3. Calculate profit projections for all actions
4. Return recommendation with confidence

After outcome observed:
5. Calculate actual reward
6. Update beliefs: α or β += 1 based on success/failure
```

**Expected Performance**:
- Decision Accuracy: ~68%
- Profit Estimate Error: ±20%
- Regret Rate: ~15%


### 6. Pipeline Integration Component

**Purpose**: เชื่อมโยงทั้ง 4 โมเดลและจัดการ state ของเกษตรกร

**Class Design**:
```python
class FarmingPipeline:
    def __init__(self, farmer_id: str, farm_size_rai: float, 
                 budget_baht: float):
        self.farmer_id = farmer_id
        self.farm_size_rai = farm_size_rai
        self.budget_baht = budget_baht
        self.state = {
            'stage': 'initial',
            'selected_crop': None,
            'planting_date': None,
            'expected_harvest_date': None,
            'price_forecast': None,
            'decisions': []
        }
        
    def stage_1_crop_selection(self, farm_profile: Dict) -> Dict
        """Execute Model A and update state"""
        
    def stage_2_planting_window(self, current_conditions: Dict) -> Dict
        """Execute Model B and update state"""
        
    def stage_3_price_forecast(self, days_to_harvest: int) -> Dict
        """Execute Model C and update state"""
        
    def stage_4_harvest_decision(self, current_context: Dict) -> Dict
        """Execute Model D and update state"""
        
    def get_current_stage(self) -> str
        """Return current stage in pipeline"""
        
    def get_state_summary(self) -> Dict
        """Return complete state information"""
        
    def print_summary(self)
        """Print human-readable summary"""
        
    def save_state(self, filepath: str)
        """Save pipeline state to file"""
        
    def load_state(self, filepath: str)
        """Load pipeline state from file"""
```

**State Management**:
```python
state = {
    'farmer_id': str,
    'stage': str,  # 'crop_selection', 'planting', 'growing', 'harvest'
    'selected_crop': str,
    'planting_date': datetime,
    'expected_harvest_date': datetime,
    'crop_recommendations': List[Dict],
    'planting_window_result': Dict,
    'price_forecast': Dict,
    'harvest_decisions': List[Dict],
    'actual_outcomes': List[Dict],
    'total_profit': float,
    'created_at': datetime,
    'updated_at': datetime
}
```

## Data Models

### Cultivation Data Model

```python
@dataclass
class CultivationRecord:
    record_id: str
    farmer_id: str
    crop_type: str
    farm_size_rai: float
    planting_date: datetime
    
    # Pre-planting features (ALLOWED)
    soil_type: str
    soil_ph: float
    soil_nitrogen: float
    soil_phosphorus: float
    soil_potassium: float
    avg_temperature: float
    avg_rainfall: float
    humidity: float
    budget_baht: float
    farmer_experience_years: int
    
    # Post-harvest features (FORBIDDEN in training)
    actual_yield_kg: Optional[float] = None
    harvest_date: Optional[datetime] = None
    success_rate: Optional[float] = None
```


### Planting Window Data Model

```python
@dataclass
class PlantingWindowRecord:
    record_id: str
    farmer_id: str
    crop_type: str
    observation_date: datetime
    
    # Observable features (ALLOWED)
    soil_moisture_percent: float
    recent_rainfall_mm: float
    temperature_c: float
    humidity_percent: float
    soil_temperature_c: float
    wind_speed_kmh: float
    
    # Temporal features (ALLOWED)
    month: int
    day_of_year: int
    month_sin: float
    month_cos: float
    
    # Target (measured after planting)
    planting_success: bool  # Good/Bad window
```

### Price Forecast Data Model

```python
@dataclass
class PriceRecord:
    record_id: str
    crop_type: str
    date: datetime
    price_baht_per_kg: float
    volume_tons: float
    market_demand_index: float
    season: str
    export_volume: float
```

### Harvest Decision Data Model

```python
@dataclass
class HarvestDecisionRecord:
    record_id: str
    farmer_id: str
    decision_date: datetime
    
    # Context features (ALLOWED - observable at decision time)
    current_price: float
    forecast_price_median: float
    forecast_price_std: float
    plant_health_score: float
    plant_age_days: int
    storage_cost_per_day: float
    yield_kg: float
    
    # Decision and outcome
    action_taken: str
    actual_price_at_harvest: Optional[float] = None
    actual_profit: Optional[float] = None
```

## Error Handling

### Data Validation Errors

```python
class DataLeakageError(Exception):
    """Raised when forbidden features detected"""
    pass

class FeatureCorrelationError(Exception):
    """Raised when feature correlation is too low"""
    pass

class OverfittingDetectedError(Warning):
    """Warning when overfitting detected"""
    pass
```

**Error Handling Strategy**:
1. **Input Validation**: ตรวจสอบ input ก่อน process
2. **Feature Validation**: ตรวจสอบ data leakage ก่อน training
3. **Model Validation**: ตรวจสอบ overfitting หลัง training
4. **Graceful Degradation**: ถ้าโมเดลหนึ่งล้ม ให้ใช้ fallback model
5. **Logging**: บันทึกทุก error พร้อม context


### Error Recovery Mechanisms

```python
class ModelPipeline:
    def execute_with_fallback(self, model_primary, model_fallback, X):
        try:
            return model_primary.predict(X)
        except Exception as e:
            logger.error(f"Primary model failed: {e}")
            logger.info("Using fallback model")
            return model_fallback.predict(X)
```

## Testing Strategy

### Unit Testing

**Model A Tests**:
```python
def test_model_a_no_leakage():
    """Verify no post-outcome features used"""
    forbidden = ['actual_yield_kg', 'success_rate', 
                'harvest_timing_adjustment', 'yield_efficiency']
    features = model_a.get_feature_names()
    assert not any(f in features for f in forbidden)

def test_model_a_output_format():
    """Verify output contains required fields"""
    result = model_a.predict(sample_input)
    assert 'recommendations' in result
    assert len(result['recommendations']) == 3
    assert all('roi_percent' in r for r in result['recommendations'])

def test_model_a_performance():
    """Verify R² in expected range"""
    r2 = model_a.evaluate(X_test, y_test)['r2']
    assert 0.45 <= r2 <= 0.55
```

**Model B Tests**:
```python
def test_model_b_time_aware_split():
    """Verify temporal ordering in splits"""
    assert train_dates.max() < val_dates.min()
    assert val_dates.max() < test_dates.min()

def test_model_b_no_future_data():
    """Verify no future information used"""
    forbidden = ['harvest_date', 'actual_yield_kg', 'success_rate']
    features = model_b.get_feature_names()
    assert not any(f in features for f in forbidden)

def test_model_b_performance():
    """Verify F1 score in expected range"""
    f1 = model_b.evaluate(X_test, y_test)['f1']
    assert 0.70 <= f1 <= 0.75
```

**Model D Tests**:
```python
def test_model_d_thompson_sampling():
    """Verify Thompson Sampling implementation"""
    engine = HarvestDecisionEngine()
    decision = engine.decide(sample_context)
    assert decision['recommended_action'] in ['Harvest Now', 
                                              'Wait 3 Days', 
                                              'Wait 7 Days']

def test_model_d_belief_update():
    """Verify belief update mechanism"""
    engine = HarvestDecisionEngine()
    initial_alpha = engine.alpha.copy()
    engine.update_beliefs(action_idx=0, reward=1.0)
    assert engine.alpha[0] > initial_alpha[0]
```

### Integration Testing

```python
def test_pipeline_end_to_end():
    """Test complete pipeline flow"""
    pipeline = FarmingPipeline('F001', 25, 150000)
    
    # Stage 1
    crop_result = pipeline.stage_1_crop_selection(farm_profile)
    assert crop_result['recommendations'][0]['crop_name'] is not None
    
    # Stage 2
    planting_result = pipeline.stage_2_planting_window(conditions)
    assert planting_result['classification'] in ['Good', 'Bad']
    
    # Stage 3
    price_result = pipeline.stage_3_price_forecast(75)
    assert price_result['forecast_price_median'] > 0
    
    # Stage 4
    harvest_result = pipeline.stage_4_harvest_decision(context)
    assert 'profit_projections' in harvest_result
```


### Data Leakage Testing

```python
def test_no_data_leakage_model_a():
    """Comprehensive data leakage check for Model A"""
    loader = DataLoaderClean('data/')
    df = loader.load_cultivation_clean()
    
    forbidden = ['actual_yield_kg', 'success_rate', 
                'harvest_timing_adjustment', 'yield_efficiency']
    
    # Check columns
    assert not any(f in df.columns for f in forbidden)
    
    # Check feature importance
    model = ModelA_XGBoost()
    model.train(X_train, y_train)
    importance = model.get_feature_importance()
    assert not any(f in importance.index for f in forbidden)

def test_feature_correlation_makes_sense():
    """Verify features correlate logically with target"""
    correlations = loader.get_feature_correlations(df, 'roi')
    
    # Positive correlations expected
    assert correlations.loc['soil_nitrogen'] > 0
    assert correlations.loc['farmer_experience_years'] > 0
    
    # Check minimum correlation threshold
    assert all(abs(correlations) > 0.05)  # Not too weak
```

### Overfitting Detection Testing

```python
def test_overfitting_detection():
    """Verify overfitting detection mechanism"""
    model = ModelA_XGBoost()
    model.train(X_train, y_train)
    
    train_r2 = model.evaluate(X_train, y_train)['r2']
    val_r2 = model.evaluate(X_val, y_val)['r2']
    
    gap = train_r2 - val_r2
    
    if gap > 0.15:
        warnings.warn(f"Overfitting detected: gap={gap:.3f}")
    
    assert gap < 0.20  # Hard limit
```

### Visualization Testing

```python
def test_plot_generation():
    """Verify all required plots are generated"""
    output_dir = 'outputs/model_a_evaluation/'
    
    model = ModelA_XGBoost()
    model.train(X_train, y_train)
    model.generate_evaluation_plots(X_test, y_test, output_dir)
    
    # Check required plots exist
    required_plots = [
        'confusion_matrix.png',
        'feature_importance.png',
        'learning_curves.png',
        'residual_plot.png'
    ]
    
    for plot in required_plots:
        assert os.path.exists(os.path.join(output_dir, plot))
        
    # Check metadata file
    metadata_file = os.path.join(output_dir, 'metadata.json')
    assert os.path.exists(metadata_file)
    
    with open(metadata_file) as f:
        metadata = json.load(f)
        assert 'model_name' in metadata
        assert 'evaluation_type' in metadata
        assert 'timestamp' in metadata
```

## Monitoring and Logging

### Logging Strategy

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('FarmingPipeline')

# Log critical events
logger.info(f"Stage 1: Crop selection started for farmer {farmer_id}")
logger.warning(f"Model A: Low confidence ({confidence:.2f}) for recommendation")
logger.error(f"Model B: Prediction failed - {error}")
```


### Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'model_a': {'predictions': 0, 'avg_time': 0, 'errors': 0},
            'model_b': {'predictions': 0, 'avg_time': 0, 'errors': 0},
            'model_c': {'predictions': 0, 'avg_time': 0, 'errors': 0},
            'model_d': {'predictions': 0, 'avg_time': 0, 'errors': 0}
        }
    
    def log_prediction(self, model_name: str, duration: float, 
                      success: bool):
        """Log prediction performance"""
        self.metrics[model_name]['predictions'] += 1
        if not success:
            self.metrics[model_name]['errors'] += 1
        
        # Update average time
        n = self.metrics[model_name]['predictions']
        old_avg = self.metrics[model_name]['avg_time']
        new_avg = (old_avg * (n-1) + duration) / n
        self.metrics[model_name]['avg_time'] = new_avg
    
    def get_summary(self) -> Dict:
        """Return performance summary"""
        return self.metrics
```

### Model Drift Detection

```python
class DriftDetector:
    def __init__(self, baseline_metrics: Dict):
        self.baseline = baseline_metrics
        self.threshold = 0.10  # 10% degradation threshold
    
    def check_drift(self, current_metrics: Dict) -> bool:
        """Check if model performance has degraded"""
        for metric_name, baseline_value in self.baseline.items():
            current_value = current_metrics.get(metric_name, 0)
            degradation = (baseline_value - current_value) / baseline_value
            
            if degradation > self.threshold:
                logger.warning(
                    f"Model drift detected: {metric_name} "
                    f"degraded by {degradation*100:.1f}%"
                )
                return True
        return False
```

## Deployment Architecture

### Directory Structure

```
REMEDIATION_PRODUCTION/
│
├── Model_A_Fixed/
│   ├── data_loader_clean.py
│   ├── model_algorithms_clean.py
│   └── trained_models/
│       ├── nsga2_model.pkl
│       ├── xgboost_model.pkl
│       └── rf_model.pkl
│
├── Model_B_Fixed/
│   ├── data_loader_clean.py
│   ├── model_algorithms_clean.py
│   └── trained_models/
│       ├── xgboost_classifier.pkl
│       └── logistic_model.pkl
│
├── Model_C_PriceForecast/
│   ├── price_forecast.py
│   └── trained_models/
│       └── prophet_model.pkl
│
├── Model_D_L4_Bandit/
│   ├── thompson_sampling.py
│   └── belief_states/
│       └── bandit_beliefs.pkl
│
├── Pipeline_Integration/
│   ├── pipeline.py
│   └── state_storage/
│       └── farmer_states/
│
├── Real_World_Tests/
│   └── test_real_world_scenario.py
│
├── outputs/
│   ├── model_a_evaluation/
│   ├── model_b_evaluation/
│   ├── model_c_evaluation/
│   └── model_d_evaluation/
│
├── logs/
│   ├── pipeline.log
│   ├── model_a.log
│   ├── model_b.log
│   ├── model_c.log
│   └── model_d.log
│
└── Documentation/
    ├── README.md
    ├── QUICK_START.md
    ├── TECHNICAL_GUIDE.md
    ├── ALGORITHM_COMPARISON.md
    └── LEAKAGE_PREVENTION.md
```


### Deployment Configuration

```python
# config.py
class Config:
    # Paths
    DATA_PATH = 'Dataset/'  # All datasets located here
    MODEL_PATH = 'trained_models/'
    OUTPUT_PATH = 'outputs/'
    LOG_PATH = 'logs/'
    
    # Model A Config
    MODEL_A_ALGORITHM = 'nsga2'  # or 'xgboost', 'rf'
    MODEL_A_POPULATION_SIZE = 100
    MODEL_A_GENERATIONS = 50
    
    # Model B Config
    MODEL_B_ALGORITHM = 'xgboost'  # or 'logistic'
    MODEL_B_THRESHOLD = 0.5
    
    # Model C Config
    MODEL_C_UPDATE_FREQUENCY = 'daily'
    MODEL_C_FORECAST_HORIZON = 120  # days
    
    # Model D Config
    MODEL_D_ALPHA_INIT = 1.0
    MODEL_D_BETA_INIT = 1.0
    MODEL_D_REWARD_THRESHOLD = 0.8
    
    # Pipeline Config
    PIPELINE_TIMEOUT = 10  # seconds
    ENABLE_FALLBACK = True
    
    # Monitoring Config
    DRIFT_THRESHOLD = 0.10
    PERFORMANCE_LOG_INTERVAL = 100  # predictions
```

### API Design (Future Extension)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class CropRecommendationRequest(BaseModel):
    farmer_id: str
    farm_size_rai: float
    soil_type: str
    soil_ph: float
    budget_baht: float
    # ... other fields

@app.post("/api/v1/crop-recommendation")
async def get_crop_recommendation(request: CropRecommendationRequest):
    try:
        pipeline = FarmingPipeline(
            request.farmer_id, 
            request.farm_size_rai, 
            request.budget_baht
        )
        result = pipeline.stage_1_crop_selection(request.dict())
        return result
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/planting-window")
async def check_planting_window(request: PlantingWindowRequest):
    # Similar implementation
    pass

@app.post("/api/v1/price-forecast")
async def get_price_forecast(request: PriceForecastRequest):
    # Similar implementation
    pass

@app.post("/api/v1/harvest-decision")
async def get_harvest_decision(request: HarvestDecisionRequest):
    # Similar implementation
    pass
```

## Security Considerations

### Data Privacy

1. **Farmer Data Protection**:
   - Encrypt farmer_id in storage
   - Anonymize data for model training
   - Implement access controls

2. **Model Protection**:
   - Store trained models securely
   - Version control for models
   - Audit trail for model updates

### Input Validation

```python
def validate_farm_profile(profile: Dict) -> bool:
    """Validate farm profile inputs"""
    validations = [
        ('farm_size_rai', lambda x: 1 <= x <= 100),
        ('soil_ph', lambda x: 4.0 <= x <= 8.5),
        ('budget_baht', lambda x: 10000 <= x <= 1000000),
        ('farmer_experience_years', lambda x: 0 <= x <= 50)
    ]
    
    for field, validator in validations:
        if field not in profile:
            raise ValueError(f"Missing required field: {field}")
        if not validator(profile[field]):
            raise ValueError(f"Invalid value for {field}: {profile[field]}")
    
    return True
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache

class ModelCache:
    @lru_cache(maxsize=100)
    def get_crop_characteristics(self, crop_name: str) -> Dict:
        """Cache crop characteristics"""
        return load_crop_data(crop_name)
    
    @lru_cache(maxsize=1000)
    def get_historical_prices(self, crop_name: str, 
                             days: int) -> List[float]:
        """Cache historical price data"""
        return load_price_history(crop_name, days)
```

### Batch Processing

```python
class BatchProcessor:
    def process_batch_predictions(self, 
                                 requests: List[Dict]) -> List[Dict]:
        """Process multiple predictions efficiently"""
        # Vectorize inputs
        X = np.array([self.prepare_features(r) for r in requests])
        
        # Batch predict
        predictions = self.model.predict(X)
        
        # Format outputs
        return [self.format_output(p, r) 
                for p, r in zip(predictions, requests)]
```

## Scalability Considerations

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use message queue for async processing
- Implement distributed caching (Redis)

### Database Design

```python
# Use time-series database for price data
# Use document store for farmer states
# Use relational DB for structured data

class DatabaseManager:
    def __init__(self):
        self.timeseries_db = InfluxDBClient()  # Price data
        self.document_db = MongoClient()       # Farmer states
        self.relational_db = PostgreSQLClient() # Structured data
```

## Future Enhancements

1. **Mobile App Integration**: REST API for mobile apps
2. **Real-time Weather Integration**: Connect to weather APIs
3. **Market Data Integration**: Live price feeds
4. **Multi-language Support**: Thai, English, Lao
5. **Offline Mode**: Basic recommendations without internet
6. **Farmer Community**: Share experiences and outcomes
7. **Government Integration**: Report to agricultural agencies
8. **Insurance Integration**: Crop insurance recommendations
9. **Supply Chain Integration**: Connect farmers to buyers
10. **Advanced Analytics**: Dashboard for agricultural insights

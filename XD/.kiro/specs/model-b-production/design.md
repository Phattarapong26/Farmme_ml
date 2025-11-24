# Design Document - Model B Production Wrapper

## Overview

ออกแบบ Model B Wrapper ใหม่ให้เป็น production-ready โดยเน้น:
- **Clean Architecture**: แยก concerns ชัดเจน (data loading, validation, prediction, formatting)
- **Performance**: Caching และ lazy loading
- **Reliability**: Error handling และ fallback mechanisms
- **Maintainability**: โค้ดสะอาด มี tests ครบถ้วน
- **LLM-Friendly**: Response format ที่ LLM parse ได้ง่าย

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI /chat Endpoint                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   ModelBWrapper (Facade)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Public API:                                          │  │
│  │  - predict_planting_window()                          │  │
│  │  - get_planting_calendar()                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Validator  │  │  Predictor  │  │  Formatter  │
│             │  │             │  │             │
│ - validate  │  │ - ml_pred   │  │ - format    │
│   _input    │  │ - weather   │  │   _response │
│             │  │   _pred     │  │             │
│             │  │ - rule_pred │  │             │
└─────────────┘  └──────┬──────┘  └─────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ ModelLoader │  │WeatherCache │  │FallbackMgr  │
│             │  │             │  │             │
│ - load_ml   │  │ - get_data  │  │ - track     │
│ - load_pkl  │  │ - cache     │  │ - should    │
│             │  │             │  │   _fallback │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Component Responsibilities

1. **ModelBWrapper (Facade)**
   - Public API สำหรับ external callers
   - Orchestrate การทำงานของ components อื่นๆ
   - Handle high-level error และ logging

2. **InputValidator**
   - Validate ทุก input parameters
   - Normalize province names
   - Return clear error messages

3. **PredictionEngine**
   - ML model prediction
   - Weather-based prediction
   - Rule-based fallback
   - Feature engineering

4. **WeatherDataCache**
   - Load และ cache weather data
   - Province name normalization
   - Historical average calculation

5. **ResponseFormatter**
   - Format predictions เป็น standard response
   - Add metadata (model_version, timing)
   - Generate Thai explanations

6. **FallbackManager**
   - Track fallback usage
   - Rate limiting
   - Prevent infinite loops

## Components and Interfaces

### 1. InputValidator

```python
class InputValidator:
    """Validate and normalize all inputs"""
    
    PROVINCE_ALIASES = {
        'กรุงเทพ': 'กรุงเทพมหานคร',
        'กทม': 'กรุงเทพมหานคร',
        'Bangkok': 'กรุงเทพมหานคร',
        'นครปฐม': 'Nakhon Pathom',
        # ... more aliases
    }
    
    def validate_prediction_input(
        self,
        planting_date: str,
        province: str,
        soil_type: Optional[str] = None,
        soil_ph: Optional[float] = None,
        soil_nutrients: Optional[float] = None,
        days_to_maturity: Optional[int] = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Validate all inputs for prediction
        
        Returns:
            (is_valid, normalized_params, error_message)
        """
        pass
    
    def normalize_province(self, province: str) -> str:
        """Normalize province name using alias mapping"""
        pass
    
    def validate_date(self, date_str: str) -> Tuple[bool, Optional[pd.Timestamp], Optional[str]]:
        """Validate date format and parse"""
        pass
    
    def validate_soil_params(
        self, 
        soil_ph: Optional[float],
        soil_nutrients: Optional[float]
    ) -> Tuple[bool, Optional[str]]:
        """Validate soil parameters"""
        pass
```

### 2. PredictionEngine

```python
class PredictionEngine:
    """Core prediction logic with multiple strategies"""
    
    def __init__(self, model_loader: ModelLoader, weather_cache: WeatherDataCache):
        self.model_loader = model_loader
        self.weather_cache = weather_cache
        self.scaler = None
        self.model = None
    
    def predict(
        self,
        date: pd.Timestamp,
        province: str,
        soil_type: Optional[str] = None,
        soil_ph: Optional[float] = None,
        soil_nutrients: Optional[float] = None,
        days_to_maturity: Optional[int] = None
    ) -> PredictionResult:
        """
        Main prediction method with fallback chain:
        1. Try ML model
        2. Fall back to weather-based
        3. Fall back to rule-based
        """
        pass
    
    def _ml_prediction(self, features: pd.DataFrame) -> Optional[PredictionResult]:
        """ML model prediction"""
        pass
    
    def _weather_based_prediction(
        self,
        date: pd.Timestamp,
        province: str,
        weather_data: Dict,
        soil_params: Dict
    ) -> PredictionResult:
        """Weather-based prediction using real data"""
        pass
    
    def _rule_based_prediction(
        self,
        date: pd.Timestamp,
        soil_params: Dict
    ) -> PredictionResult:
        """Simple rule-based fallback"""
        pass
    
    def _engineer_features(self, params: Dict) -> pd.DataFrame:
        """Engineer features for ML model (temporal + encoded)"""
        pass
```

### 3. WeatherDataCache

```python
class WeatherDataCache:
    """Cache weather data for fast access"""
    
    def __init__(self, weather_csv_path: Path):
        self.weather_csv_path = weather_csv_path
        self._cache: Dict[str, pd.DataFrame] = {}
        self._monthly_cache: Dict[Tuple[str, int], Dict] = {}
        self._loaded = False
        self._df: Optional[pd.DataFrame] = None
    
    def load(self) -> bool:
        """Load weather data from CSV"""
        pass
    
    def get_weather(
        self,
        province: str,
        date: pd.Timestamp,
        use_historical: bool = False
    ) -> Optional[Dict[str, float]]:
        """
        Get weather data for province and date
        
        Args:
            province: Normalized province name
            date: Target date
            use_historical: Use monthly average if True
        
        Returns:
            Dict with temperature, rainfall, humidity, drought_index
        """
        pass
    
    def _get_monthly_average(self, province: str, month: int) -> Optional[Dict]:
        """Get cached monthly average"""
        pass
    
    def _calculate_monthly_average(self, province: str, month: int) -> Dict:
        """Calculate and cache monthly average"""
        pass
```

### 4. ModelLoader

```python
class ModelLoader:
    """Load ML models with fallback"""
    
    MODEL_PRIORITY = [
        ("model_b_logistic.pkl", "gradboost"),  # Deployed model
        ("model_b_gradboost_full.pkl", "gradboost"),
        ("model_b_xgboost_full.pkl", "xgboost"),
    ]
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.model_type = None
        self.model_path = None
    
    def load(self) -> bool:
        """
        Load model with priority order
        
        Returns:
            True if model loaded successfully
        """
        pass
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        pass
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        pass
```

### 5. ResponseFormatter

```python
class ResponseFormatter:
    """Format predictions into standard responses"""
    
    MODEL_VERSION = "2.0.0"
    
    def format_success(
        self,
        prediction_result: PredictionResult,
        weather_data: Optional[Dict],
        metadata: Dict
    ) -> Dict[str, Any]:
        """
        Format successful prediction
        
        Returns:
            {
                "success": True,
                "data": {
                    "is_good_window": bool,
                    "confidence": float,
                    "recommendation": str,
                    "reason": str,
                    "weather": dict,
                    "province": str,
                    "planting_date": str
                },
                "metadata": {
                    "model_version": str,
                    "model_used": str,
                    "prediction_time_ms": float,
                    "timestamp": str
                }
            }
        """
        pass
    
    def format_error(
        self,
        error_message: str,
        error_type: str = "ValidationError"
    ) -> Dict[str, Any]:
        """
        Format error response
        
        Returns:
            {
                "success": False,
                "error": str,
                "error_type": str,
                "metadata": {
                    "model_version": str,
                    "timestamp": str
                }
            }
        """
        pass
    
    def _generate_thai_explanation(
        self,
        is_good: bool,
        weather_data: Dict,
        soil_params: Dict,
        prediction_method: str
    ) -> str:
        """Generate Thai language explanation"""
        pass
    
    def _generate_recommendation(
        self,
        is_good: bool,
        confidence: float,
        alternative_months: Optional[List[str]] = None
    ) -> str:
        """Generate actionable recommendation"""
        pass
```

### 6. FallbackManager

```python
class FallbackManager:
    """Manage fallback usage and rate limiting"""
    
    MAX_FALLBACKS_PER_MINUTE = 3
    
    def __init__(self):
        self._fallback_history: List[datetime] = []
    
    def should_allow_fallback(self) -> bool:
        """Check if fallback is allowed (rate limit)"""
        pass
    
    def record_fallback(self, method: str):
        """Record fallback usage"""
        pass
    
    def get_stats(self) -> Dict:
        """Get fallback statistics"""
        pass
    
    def _cleanup_old_records(self):
        """Remove records older than 1 minute"""
        pass
```

### 7. PredictionResult (Data Class)

```python
@dataclass
class PredictionResult:
    """Result from prediction engine"""
    is_good_window: bool
    confidence: float
    probability_good: float
    probability_bad: float
    method_used: str  # "ml_model", "weather_based", "rule_based"
    reasons: List[str]
    raw_prediction: Optional[int] = None
    raw_probability: Optional[np.ndarray] = None
```

## Data Models

### Input Models

```python
class PlantingWindowRequest:
    planting_date: str  # YYYY-MM-DD
    province: str
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None  # 0-14
    soil_nutrients: Optional[float] = None  # 0-100
    days_to_maturity: Optional[int] = None  # 30-365

class PlantingCalendarRequest:
    province: str
    crop_type: str = "พริก"
    months_ahead: int = 12  # 1-24
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    soil_nutrients: Optional[float] = None
```

### Response Models

```python
class PlantingWindowResponse:
    success: bool
    data: Optional[PlantingWindowData]
    error: Optional[str]
    error_type: Optional[str]
    metadata: ResponseMetadata

class PlantingWindowData:
    is_good_window: bool
    confidence: float
    recommendation: str
    reason: str
    weather: WeatherData
    province: str
    planting_date: str
    probability: ProbabilityData

class WeatherData:
    temperature: float
    rainfall: float
    humidity: float
    drought_index: float
    data_type: str  # "actual", "historical_average", "recent_average"

class ProbabilityData:
    good: float
    bad: float

class ResponseMetadata:
    model_version: str
    model_used: str
    prediction_time_ms: float
    timestamp: str
```

## Error Handling

### Error Hierarchy

```
ModelBError (Base)
├── ValidationError
│   ├── InvalidDateError
│   ├── InvalidProvinceError
│   ├── InvalidSoilParamsError
│   └── MissingParameterError
├── ModelError
│   ├── ModelLoadError
│   ├── ModelPredictionError
│   └── FeatureEngineeringError
├── DataError
│   ├── WeatherDataNotFoundError
│   └── WeatherDataLoadError
└── FallbackError
    └── FallbackRateLimitError
```

### Error Handling Strategy

1. **Validation Errors**: Return immediately with clear message
2. **Model Errors**: Fall back to weather-based prediction
3. **Weather Data Errors**: Fall back to rule-based prediction
4. **Fallback Rate Limit**: Return error with retry-after suggestion

### Example Error Responses

```python
# Validation Error
{
    "success": False,
    "error": "Invalid date format. Expected YYYY-MM-DD, got '2024-13-01'",
    "error_type": "InvalidDateError",
    "metadata": {
        "model_version": "2.0.0",
        "timestamp": "2025-11-19T10:30:00Z"
    }
}

# Model Error with Fallback
{
    "success": True,
    "data": {
        "is_good_window": True,
        "confidence": 0.75,
        "recommendation": "ดี - แนะนำให้ปลูกในช่วงนี้",
        "reason": "อุณหภูมิเหมาะสม (28.5°C) | ปริมาณฝนเหมาะสม (45.2 mm)",
        "weather": {...},
        "province": "กรุงเทพมหานคร",
        "planting_date": "2024-11-15"
    },
    "metadata": {
        "model_version": "2.0.0",
        "model_used": "weather_based_fallback",
        "prediction_time_ms": 45.2,
        "timestamp": "2025-11-19T10:30:00Z",
        "warning": "ML model unavailable, using weather-based prediction"
    }
}
```

## Testing Strategy

### Unit Tests

1. **InputValidator Tests**
   - Valid inputs
   - Invalid date formats
   - Invalid soil parameters
   - Province normalization
   - Missing required parameters

2. **PredictionEngine Tests**
   - ML prediction with valid features
   - Weather-based prediction
   - Rule-based fallback
   - Feature engineering

3. **WeatherDataCache Tests**
   - Load weather data
   - Get exact date weather
   - Get monthly average
   - Handle missing data
   - Cache performance

4. **ModelLoader Tests**
   - Load valid model
   - Handle missing model files
   - Model priority order

5. **ResponseFormatter Tests**
   - Format success response
   - Format error response
   - Thai explanation generation
   - Metadata inclusion

6. **FallbackManager Tests**
   - Rate limiting
   - Fallback tracking
   - Statistics

### Integration Tests

1. **End-to-End Prediction**
   - Valid request → ML prediction
   - Valid request → Weather fallback
   - Valid request → Rule fallback

2. **Error Scenarios**
   - Invalid input → Validation error
   - Missing weather data → Fallback
   - Model load failure → Fallback

3. **Performance Tests**
   - Prediction time < 200ms
   - Cache hit rate > 80%
   - Memory usage stable

### Test Data

```python
# test_data.py
VALID_INPUTS = [
    {
        "planting_date": "2024-11-15",
        "province": "กรุงเทพมหานคร",
        "soil_ph": 6.5,
        "soil_nutrients": 70.0
    },
    {
        "planting_date": "2024-03-20",
        "province": "นครปฐม",
        "soil_type": "ดินร่วน"
    }
]

INVALID_INPUTS = [
    {
        "planting_date": "2024-13-01",  # Invalid month
        "province": "กรุงเทพมหานคร"
    },
    {
        "planting_date": "2024-11-15",
        "province": "กรุงเทพมหานคร",
        "soil_ph": 15.0  # Out of range
    }
]

EXPECTED_RESPONSES = {
    "ml_success": {
        "success": True,
        "data": {
            "is_good_window": True,
            "confidence": 0.85
        }
    },
    "validation_error": {
        "success": False,
        "error_type": "InvalidDateError"
    }
}
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**
   - Load ML model only on first prediction
   - Load weather data only when needed

2. **Caching**
   - Cache weather data in memory (by province)
   - Cache monthly averages
   - Cache province normalization results

3. **Batch Processing**
   - Support batch predictions for calendar feature
   - Reuse weather data across multiple predictions

4. **Memory Management**
   - Limit cache size (max 100 provinces)
   - Clear old cache entries (LRU)
   - Use generators for large datasets

### Performance Targets

- Single prediction: < 200ms (average)
- Calendar generation (12 months): < 2 seconds
- Memory usage: < 500MB
- Cache hit rate: > 80%

## Deployment Considerations

### Configuration

```python
# config.py
class ModelBConfig:
    MODEL_VERSION = "2.0.0"
    MODELS_DIR = Path("REMEDIATION_PRODUCTION/trained_models")
    WEATHER_CSV = Path("buildingModel.py/Dataset/weather.csv")
    
    # Performance
    CACHE_SIZE = 100
    PREDICTION_TIMEOUT = 5.0  # seconds
    
    # Fallback
    MAX_FALLBACKS_PER_MINUTE = 3
    FALLBACK_CONFIDENCE_PENALTY = 0.10
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Monitoring Metrics

1. **Performance Metrics**
   - Prediction latency (p50, p95, p99)
   - Cache hit rate
   - Memory usage

2. **Business Metrics**
   - Predictions per minute
   - Fallback rate
   - Error rate by type

3. **Model Metrics**
   - Confidence distribution
   - Positive/negative prediction ratio
   - Province coverage

### Logging Strategy

```python
# Log levels
DEBUG: Feature engineering details, cache operations
INFO: Prediction requests, model loading, performance metrics
WARNING: Fallback usage, missing data, low confidence
ERROR: Model failures, validation errors, exceptions
```

## Migration Plan

### Phase 1: Refactor Core Components
1. Create new component classes
2. Implement InputValidator
3. Implement WeatherDataCache
4. Implement ModelLoader

### Phase 2: Refactor Prediction Logic
1. Create PredictionEngine
2. Migrate ML prediction logic
3. Migrate weather-based logic
4. Migrate rule-based logic

### Phase 3: Response Formatting
1. Create ResponseFormatter
2. Standardize response format
3. Add metadata

### Phase 4: Error Handling & Fallback
1. Create FallbackManager
2. Implement error hierarchy
3. Add rate limiting

### Phase 5: Testing & Validation
1. Write unit tests
2. Write integration tests
3. Performance testing
4. Load testing

### Phase 6: Deployment
1. Update wrapper in backend/
2. Update tests
3. Monitor metrics
4. Gradual rollout

## Security Considerations

1. **Input Sanitization**
   - Validate all string inputs
   - Prevent SQL injection (if database added)
   - Limit input sizes

2. **Resource Limits**
   - Timeout on predictions (5 seconds)
   - Memory limits on cache
   - Rate limiting on API

3. **Data Privacy**
   - No PII in logs
   - Anonymize province data in metrics
   - Secure model files

## Future Enhancements

1. **Advanced Features**
   - Multi-crop recommendations
   - Seasonal trend analysis
   - Climate change projections

2. **Performance**
   - Model quantization for faster inference
   - Async predictions
   - Distributed caching (Redis)

3. **Monitoring**
   - Real-time dashboards
   - Alerting on high error rates
   - A/B testing framework

4. **Data**
   - Real-time weather API integration
   - Soil sensor data integration
   - Satellite imagery analysis

# Design Document: Model B Weather Context Enhancement

## Overview

This design enhances Model B (Planting Calendar Predictor) by integrating weather forecasts and anomaly detection. The current model relies solely on temporal features (month, season), making it blind to weather conditions. The enhanced model will incorporate real-time weather data, forecasted conditions, and anomaly flags to provide weather-aware planting recommendations.

**Key Improvements:**
- Weather feature integration (rainfall, temperature, humidity, drought index)
- Anomaly detection system (drought, floods, extreme conditions)
- Enhanced feature engineering (rolling averages, variability metrics)
- Weather-aware predictions with explanations
- Robust fallback mechanisms

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Model B Enhanced                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Weather    │      │   Temporal   │                     │
│  │   Features   │──┐   │   Features   │──┐                  │
│  └──────────────┘  │   └──────────────┘  │                  │
│                    │                     │                  │
│  ┌──────────────┐  │   ┌──────────────┐  │                  │
│  │   Anomaly    │──┤   │  Historical  │──┤                  │
│  │   Detector   │  │   │    Norms     │  │                  │
│  └──────────────┘  │   └──────────────┘  │                  │
│                    │                     │                  │
│                    ▼                     ▼                  │
│              ┌─────────────────────────────┐                │
│              │   Feature Engineering       │                │
│              │  - Rolling averages         │                │
│              │  - Variability metrics      │                │
│              │  - Interaction features     │                │
│              └─────────────────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│              ┌─────────────────────────────┐                │
│              │   XGBoost Classifier        │                │
│              │  (Weather + Temporal)       │                │
│              └─────────────────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│              ┌─────────────────────────────┐                │
│              │   Prediction Output         │                │
│              │  - Classification           │                │
│              │  - Confidence score         │                │
│              │  - Weather context          │                │
│              │  - Anomaly flags            │                │
│              │  - Explanation              │                │
│              └─────────────────────────────┘                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Weather    │  │  Cultivation │  │  Historical  │      │
│  │   Database   │  │   Database   │  │   Weather    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Feature Layer                               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WeatherFeatureEngine                                 │   │
│  │  - fetch_weather_forecast()                          │   │
│  │  - calculate_rolling_averages()                      │   │
│  │  - calculate_variability()                           │   │
│  │  - create_interaction_features()                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WeatherAnomalyDetector                               │   │
│  │  - detect_drought()                                   │   │
│  │  - detect_excessive_rainfall()                       │   │
│  │  - detect_extreme_temperature()                      │   │
│  │  - detect_unusual_humidity()                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Model Layer                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ModelBWeatherAware                                   │   │
│  │  - model: XGBClassifier                              │   │
│  │  - feature_cols: List[str]                           │   │
│  │  - weather_feature_engine: WeatherFeatureEngine      │   │
│  │  - anomaly_detector: WeatherAnomalyDetector          │   │
│  │                                                        │   │
│  │  Methods:                                             │   │
│  │  - predict(crop, province, planting_date)            │   │
│  │  - predict_with_weather(crop, province, date, weather)│   │
│  │  - explain_prediction(features, prediction)           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer                               │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PlantingCalendarService                              │   │
│  │  - get_planting_recommendation()                      │   │
│  │  - get_weather_aware_calendar()                       │   │
│  │  - check_planting_window()                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Components and Interfaces

### 1. WeatherFeatureEngine

**Purpose:** Generate weather-based features for model input

**Interface:**
```python
class WeatherFeatureEngine:
    def __init__(self, weather_db_path: str, cache_ttl: int = 21600):
        """
        Initialize weather feature engine
        
        Args:
            weather_db_path: Path to weather database
            cache_ttl: Cache time-to-live in seconds (default 6 hours)
        """
        
    def fetch_weather_forecast(
        self, 
        province: str, 
        start_date: datetime, 
        days_ahead: int = 30
    ) -> pd.DataFrame:
        """
        Fetch weather forecast for specified period
        
        Returns:
            DataFrame with columns: date, rainfall_mm, temperature_celsius, 
            humidity_percent, drought_index
        """
        
    def calculate_rolling_averages(
        self, 
        weather_df: pd.DataFrame, 
        windows: List[int] = [7, 14, 30]
    ) -> pd.DataFrame:
        """
        Calculate rolling averages for weather variables
        
        Returns:
            DataFrame with additional columns: rainfall_7d_avg, rainfall_14d_avg,
            rainfall_30d_avg, temperature_7d_avg, etc.
        """
        
    def calculate_variability(
        self, 
        weather_df: pd.DataFrame, 
        window: int = 30
    ) -> pd.DataFrame:
        """
        Calculate weather variability metrics
        
        Returns:
            DataFrame with columns: rainfall_std_30d, temperature_std_30d, etc.
        """
        
    def create_interaction_features(
        self, 
        weather_df: pd.DataFrame, 
        temporal_features: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create interaction features between weather and temporal variables
        
        Returns:
            DataFrame with interaction features like: 
            rainfall_x_month, temperature_x_season, etc.
        """
        
    def get_historical_norms(
        self, 
        province: str, 
        month: int, 
        day_of_year: int
    ) -> Dict[str, float]:
        """
        Get historical weather norms for comparison
        
        Returns:
            Dict with keys: rainfall_mean, rainfall_std, temperature_mean, etc.
        """
```

### 2. WeatherAnomalyDetector

**Purpose:** Detect unusual weather patterns

**Interface:**
```python
class WeatherAnomalyDetector:
    def __init__(self, historical_weather_path: str, threshold_std: float = 2.0):
        """
        Initialize anomaly detector
        
        Args:
            historical_weather_path: Path to historical weather data
            threshold_std: Number of standard deviations for anomaly threshold
        """
        
    def detect_anomalies(
        self, 
        current_weather: Dict[str, float], 
        historical_norms: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Detect all types of weather anomalies
        
        Returns:
            {
                'has_anomaly': bool,
                'anomaly_types': List[str],
                'anomaly_details': Dict[str, Any]
            }
        """
        
    def detect_drought(
        self, 
        rainfall_30d: float, 
        historical_mean: float, 
        historical_std: float
    ) -> Tuple[bool, float]:
        """
        Detect drought conditions
        
        Returns:
            (is_drought, severity_score)
        """
        
    def detect_excessive_rainfall(
        self, 
        rainfall_7d: float, 
        historical_mean: float, 
        historical_std: float
    ) -> Tuple[bool, float]:
        """
        Detect excessive rainfall
        
        Returns:
            (is_excessive, severity_score)
        """
        
    def detect_extreme_temperature(
        self, 
        temperature: float, 
        historical_mean: float, 
        historical_std: float
    ) -> Tuple[bool, str, float]:
        """
        Detect extreme temperatures
        
        Returns:
            (is_extreme, type ('hot'|'cold'), severity_score)
        """
        
    def detect_unusual_humidity(
        self, 
        humidity: float, 
        historical_mean: float, 
        historical_std: float
    ) -> Tuple[bool, str, float]:
        """
        Detect unusual humidity
        
        Returns:
            (is_unusual, type ('high'|'low'), severity_score)
        """
```

### 3. ModelBWeatherAware

**Purpose:** Enhanced Model B with weather awareness

**Interface:**
```python
class ModelBWeatherAware:
    def __init__(self, model_path: str):
        """
        Initialize weather-aware Model B
        
        Args:
            model_path: Path to trained model file
        """
        
    def predict(
        self, 
        crop_type: str, 
        province: str, 
        planting_date: datetime,
        use_weather: bool = True
    ) -> Dict[str, Any]:
        """
        Predict planting window quality
        
        Returns:
            {
                'classification': str ('good'|'bad'),
                'confidence': float,
                'weather_context': Dict,
                'anomaly_flags': List[str],
                'explanation': str,
                'factors': List[Dict]
            }
        """
        
    def predict_batch(
        self, 
        requests: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple planting windows
        
        Args:
            requests: List of dicts with keys: crop_type, province, planting_date
            
        Returns:
            List of prediction results
        """
        
    def explain_prediction(
        self, 
        features: pd.DataFrame, 
        prediction: int, 
        confidence: float
    ) -> Dict[str, Any]:
        """
        Generate human-readable explanation
        
        Returns:
            {
                'top_factors': List[Dict],
                'weather_impact': str,
                'recommendation': str
            }
        """
        
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from trained model
        
        Returns:
            DataFrame with columns: feature, importance, category
        """
```

### 4. PlantingCalendarService

**Purpose:** High-level service for planting recommendations

**Interface:**
```python
class PlantingCalendarService:
    def __init__(self, model_path: str, weather_db_path: str):
        """
        Initialize planting calendar service
        """
        
    def get_planting_recommendation(
        self, 
        crop_type: str, 
        province: str, 
        target_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Get planting recommendation for a specific date
        
        Returns:
            {
                'recommended': bool,
                'classification': str,
                'confidence': float,
                'weather_forecast': Dict,
                'anomalies': List[str],
                'explanation': str,
                'alternative_dates': List[datetime]
            }
        """
        
    def get_weather_aware_calendar(
        self, 
        crop_type: str, 
        province: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get weather-aware planting calendar for date range
        
        Returns:
            List of daily recommendations with weather context
        """
        
    def check_planting_window(
        self, 
        crop_type: str, 
        province: str, 
        planting_date: datetime,
        harvest_date: datetime
    ) -> Dict[str, Any]:
        """
        Check if entire planting-to-harvest window is favorable
        
        Returns:
            {
                'window_quality': str ('excellent'|'good'|'fair'|'poor'),
                'risk_factors': List[str],
                'weather_risks': List[Dict],
                'recommendation': str
            }
        """
```

---

## Data Models

### Weather Feature Schema

```python
weather_features = {
    # Raw weather data
    'rainfall_mm': float,
    'temperature_celsius': float,
    'humidity_percent': float,
    'drought_index': float,
    
    # Rolling averages
    'rainfall_7d_avg': float,
    'rainfall_14d_avg': float,
    'rainfall_30d_avg': float,
    'temperature_7d_avg': float,
    'temperature_14d_avg': float,
    'temperature_30d_avg': float,
    'humidity_7d_avg': float,
    
    # Variability metrics
    'rainfall_std_30d': float,
    'temperature_std_30d': float,
    'humidity_std_30d': float,
    
    # Interaction features
    'rainfall_x_month': float,
    'temperature_x_season': float,
    'humidity_x_day_of_year': float
}
```

### Anomaly Detection Schema

```python
anomaly_result = {
    'has_anomaly': bool,
    'anomaly_types': List[str],  # ['drought', 'excessive_rainfall', 'extreme_heat', etc.]
    'anomaly_details': {
        'drought': {
            'detected': bool,
            'severity': float,  # 0-1 scale
            'description': str
        },
        'excessive_rainfall': {
            'detected': bool,
            'severity': float,
            'description': str
        },
        'extreme_temperature': {
            'detected': bool,
            'type': str,  # 'hot' or 'cold'
            'severity': float,
            'description': str
        },
        'unusual_humidity': {
            'detected': bool,
            'type': str,  # 'high' or 'low'
            'severity': float,
            'description': str
        }
    }
}
```

### Prediction Output Schema

```python
prediction_output = {
    'classification': str,  # 'good' or 'bad'
    'confidence': float,  # 0-1
    'weather_context': {
        'current': {
            'rainfall_mm': float,
            'temperature_celsius': float,
            'humidity_percent': float,
            'drought_index': float
        },
        'forecast_7d': {
            'rainfall_avg': float,
            'temperature_avg': float,
            'humidity_avg': float
        },
        'forecast_30d': {
            'rainfall_avg': float,
            'temperature_avg': float,
            'humidity_avg': float
        }
    },
    'anomaly_flags': List[str],
    'anomaly_details': Dict,  # From anomaly detection
    'explanation': str,
    'top_factors': List[{
        'factor': str,
        'importance': float,
        'value': float,
        'impact': str  # 'positive' or 'negative'
    }],
    'recommendation': str,
    'confidence_level': str,  # 'high', 'medium', 'low'
    'data_quality': {
        'weather_data_available': bool,
        'using_fallback': bool,
        'fallback_type': str  # 'historical_avg', 'regional_avg', 'none'
    }
}
```

---

## Error Handling

### Fallback Strategy

```
Weather Data Unavailable
    ↓
Try Historical Average (same date, same province)
    ↓
Try Regional Average (same date, nearby provinces)
    ↓
Try Temporal-Only Prediction (no weather features)
    ↓
Return with Warning Flag + Reduced Confidence
```

### Error Scenarios

1. **Weather API Timeout**
   - Fallback to cached data (if < 6 hours old)
   - Otherwise use historical averages
   - Log event for monitoring

2. **Missing Historical Data**
   - Use regional averages
   - Interpolate from nearby dates
   - Flag as low-confidence prediction

3. **Invalid Weather Values**
   - Validate ranges (rainfall >= 0, temp -50 to 60°C, etc.)
   - Replace invalid values with historical mean
   - Log data quality issue

4. **Model Loading Failure**
   - Attempt to reload from backup
   - If fails, use rule-based fallback
   - Alert system administrators

---

## Testing Strategy

### Unit Tests

1. **WeatherFeatureEngine Tests**
   - Test rolling average calculations
   - Test variability metrics
   - Test interaction feature creation
   - Test caching mechanism

2. **WeatherAnomalyDetector Tests**
   - Test drought detection with known cases
   - Test excessive rainfall detection
   - Test extreme temperature detection
   - Test threshold sensitivity

3. **ModelBWeatherAware Tests**
   - Test prediction with complete weather data
   - Test prediction with missing weather data
   - Test fallback mechanisms
   - Test explanation generation

### Integration Tests

1. **End-to-End Prediction Flow**
   - Request → Weather Fetch → Feature Engineering → Prediction → Output
   - Test with real weather data
   - Test with synthetic data
   - Test with missing data

2. **Batch Prediction**
   - Test 1000 predictions in < 10 seconds
   - Test concurrent requests
   - Test memory usage

3. **API Integration**
   - Test weather API calls
   - Test database queries
   - Test caching behavior

### Performance Tests

1. **Latency Tests**
   - Single prediction < 500ms
   - Batch 1000 predictions < 10s
   - Weather fetch < 200ms (cached)

2. **Load Tests**
   - 100 concurrent users
   - 1000 requests/minute
   - Memory usage < 500MB

3. **Accuracy Tests**
   - F1-score >= 0.70
   - Precision >= baseline
   - Weather features contribute >= 20%

---

## Deployment Plan

### Phase 1: Development (Week 1-2)
1. Implement WeatherFeatureEngine
2. Implement WeatherAnomalyDetector
3. Create enhanced training dataset
4. Train initial model with weather features

### Phase 2: Testing (Week 3)
1. Unit tests for all components
2. Integration tests
3. Performance benchmarking
4. Accuracy evaluation

### Phase 3: Staging (Week 4)
1. Deploy to staging environment
2. A/B testing vs baseline model
3. Collect feedback from test users
4. Fine-tune thresholds and parameters

### Phase 4: Production (Week 5)
1. Gradual rollout (10% → 50% → 100%)
2. Monitor performance metrics
3. Set up alerts and dashboards
4. Document API changes

---

## Monitoring and Metrics

### Key Metrics to Track

1. **Model Performance**
   - Daily F1-score
   - Precision and recall
   - Confidence distribution
   - Weather feature importance

2. **Weather Data Quality**
   - API availability (%)
   - Fallback usage frequency
   - Data freshness (hours)
   - Anomaly detection rate

3. **System Performance**
   - Prediction latency (p50, p95, p99)
   - Cache hit rate
   - Memory usage
   - Error rate

4. **Business Metrics**
   - User satisfaction
   - Prediction accuracy (vs actual outcomes)
   - Weather-aware vs temporal-only comparison
   - Anomaly flag accuracy

### Alerts

- F1-score drops below 0.65
- Weather API unavailable > 1 hour
- Prediction latency > 1 second
- Error rate > 5%
- Weather feature importance < 15%

---

## Security Considerations

1. **Data Privacy**
   - No personal farmer data in weather features
   - Aggregate weather data only
   - Comply with data retention policies

2. **API Security**
   - Authenticate weather API calls
   - Rate limiting on prediction endpoints
   - Input validation and sanitization

3. **Model Security**
   - Encrypt model files at rest
   - Version control for model updates
   - Audit trail for predictions

---

## Future Enhancements

1. **Advanced Weather Features**
   - Soil moisture predictions
   - Pest outbreak risk (weather-based)
   - Disease risk (humidity + temperature)

2. **Climate Change Adaptation**
   - Long-term climate trend analysis
   - Seasonal pattern shifts
   - Adaptive thresholds

3. **Multi-Model Ensemble**
   - Combine weather-aware + temporal-only
   - Dynamic model selection based on confidence
   - Weighted voting system

4. **Real-Time Updates**
   - Streaming weather data
   - Continuous model updates
   - Live anomaly alerts

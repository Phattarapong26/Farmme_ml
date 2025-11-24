# Design Document

## Overview

Model C Wrapper จะเป็น Python class ที่ห่อหุ้ม Price Prediction Model (Model C) เพื่อให้มี interface ที่สอดคล้องกับ Model A, B และ D Wrappers โดยจะใช้ `price_forecast_service` ที่มีอยู่แล้วเป็น core engine และเพิ่ม wrapper layer เพื่อให้ API ที่เป็นมาตรฐาน

## Architecture

```
┌─────────────────────────────────────────┐
│         model_c_wrapper.py              │
│  ┌───────────────────────────────────┐  │
│  │     ModelCWrapper Class           │  │
│  │  - __init__()                     │  │
│  │  - _load_model()                  │  │
│  │  - predict_price()                │  │
│  │  - _analyze_price_trend()         │  │
│  │  - _generate_market_insights()    │  │
│  │  - _recommend_selling_period()    │  │
│  │  - _fallback_prediction()         │  │
│  │  - get_model_info()               │  │
│  └───────────────────────────────────┘  │
│              ↓ uses                     │
│  ┌───────────────────────────────────┐  │
│  │   price_forecast_service          │  │
│  │   (from app.services)             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                ↓ loads
┌─────────────────────────────────────────┐
│  REMEDIATION_PRODUCTION/                │
│    trained_models/                      │
│      model_c_ultimate.pkl               │
│      model_c_price_forecast.pkl         │
└─────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ModelCWrapper Class

**Purpose**: Main wrapper class that provides standardized interface for Model C

**Attributes**:
- `model`: Reference to the loaded ML model (from price_forecast_service)
- `forecast_service`: Instance of PriceForecastService
- `model_loaded`: Boolean flag indicating if model is loaded
- `model_path`: Path to the loaded model file

**Methods**:

#### `__init__(self)`
- Initialize the wrapper
- Import and instantiate price_forecast_service
- Set model_loaded flag based on service status
- Log initialization status

#### `predict_price(crop_type: str, province: str, days_ahead: int = 30, planting_area_rai: float = None, expected_yield_kg: float = None) -> Dict[str, Any]`
- Main prediction method
- **Parameters**:
  - `crop_type`: Type of crop (Thai name, e.g., 'พริก', 'มะเขือเทศ')
  - `province`: Thai province name
  - `days_ahead`: Number of days to predict (7, 30, 90, or 180)
  - `planting_area_rai`: Optional planting area
  - `expected_yield_kg`: Optional expected yield
- **Returns**: Dictionary with:
  - `success`: Boolean
  - `crop_type`: Input crop type
  - `province`: Input province
  - `predictions`: List of predictions for different timeframes
  - `historical_data`: Historical price data for charts
  - `daily_forecasts`: Daily predictions for the forecast period
  - `current_price`: Current market price
  - `price_trend`: Trend analysis (increasing/decreasing/stable)
  - `trend_percentage`: Percentage change
  - `market_insights`: List of insight strings
  - `best_selling_period`: Recommended selling timeframe
  - `model_used`: Model identifier
  - `confidence`: Overall confidence score

#### `_analyze_price_trend(current_price: float, predictions: List[Dict]) -> Dict`
- Analyze price trend from predictions
- Compare current price with future predictions
- Classify as increasing (>5%), decreasing (<-5%), or stable
- Return trend type and percentage change

#### `_generate_market_insights(crop_type: str, predictions: List[Dict], trend_analysis: Dict) -> List[str]`
- Generate actionable market insights
- Based on price trends and confidence levels
- Return list of Thai language insight strings

#### `_recommend_selling_period(predictions: List[Dict]) -> str`
- Find the best selling period based on highest predicted price
- Return Thai language recommendation (e.g., "ภายใน 7 วัน", "ภายใน 1 เดือน")

#### `_fallback_prediction(crop_type: str, province: str, days_ahead: int) -> Dict[str, Any]`
- Provide rule-based predictions when ML model fails
- Use seasonal patterns and historical averages
- Return same structure as predict_price()

#### `get_model_info() -> Dict[str, Any]`
- Return model metadata and status
- Include model_loaded, model_path, version, status

### 2. Integration with PriceForecastService

The wrapper will delegate actual ML predictions to `price_forecast_service`:

```python
# In predict_price()
if self.model_loaded and self.forecast_service:
    result = self.forecast_service.forecast_price(
        province=province,
        crop_type=crop_type,
        days_ahead=days_ahead,
        current_price=current_price,
        db_session=db
    )
```

### 3. Global Instance

Create a global singleton instance for easy import:

```python
# At module level
model_c_wrapper = ModelCWrapper()
logger.info("📦 Model C Wrapper loaded")
```

## Data Models

### Prediction Response Format

```python
{
    "success": True,
    "crop_type": "พริก",
    "province": "นครปฐม",
    "predictions": [
        {
            "days_ahead": 7,
            "predicted_price": 45.50,
            "confidence": 0.90,
            "price_range": {
                "min": 40.95,
                "max": 50.05
            }
        },
        {
            "days_ahead": 30,
            "predicted_price": 48.20,
            "confidence": 0.85,
            "price_range": {
                "min": 43.38,
                "max": 53.02
            }
        },
        # ... more timeframes
    ],
    "historical_data": [
        {"date": "2025-10-17", "price": 42.00},
        {"date": "2025-10-18", "price": 43.50},
        # ... more historical points
    ],
    "daily_forecasts": [
        {"date": "2025-11-17", "predicted_price": 44.20},
        {"date": "2025-11-18", "predicted_price": 44.50},
        # ... daily predictions
    ],
    "current_price": 42.50,
    "price_trend": "increasing",
    "trend_percentage": 13.4,
    "market_insights": [
        "ราคาพริกมีแนวโน้มเพิ่มขึ้น 13.4%",
        "แนะนำให้รอขายในช่วงที่ราคาสูงขึ้น",
        "ความแม่นยำของการทำนายอยู่ในระดับสูง"
    ],
    "best_selling_period": "ภายใน 1 เดือน",
    "model_used": "model_c_xgboost_hash_encoding",
    "confidence": 0.87
}
```

### Fallback Response Format

Same structure as above, but with:
- `model_used`: "fallback_rule_based"
- Lower confidence scores (0.50-0.65)
- Simpler predictions based on seasonal patterns

## Error Handling

### Model Loading Errors
- Catch exceptions during model file loading
- Log detailed error messages with stack traces
- Set `model_loaded = False`
- Continue with fallback mode

### Prediction Errors
- Wrap prediction calls in try-except blocks
- Log errors with context (crop_type, province, days_ahead)
- Automatically fall back to rule-based predictions
- Return error information in response

### Database Connection Errors
- Handle cases where database is unavailable
- Use default values for historical data
- Provide predictions based on model alone

## Testing Strategy

### Unit Tests
1. Test ModelCWrapper initialization
2. Test predict_price() with valid inputs
3. Test fallback prediction logic
4. Test trend analysis calculations
5. Test market insights generation
6. Test selling period recommendations

### Integration Tests
1. Test integration with price_forecast_service
2. Test database queries for historical data
3. Test end-to-end prediction flow
4. Test error handling with invalid inputs

### Manual Testing
1. Test with different crop types and provinces
2. Test with different timeframes (7, 30, 90, 180 days)
3. Verify predictions match expected patterns
4. Verify fallback mode works when model unavailable

## Design Decisions and Rationales

### 1. Wrapper Pattern
**Decision**: Create a wrapper around existing price_forecast_service instead of rewriting
**Rationale**: 
- Reuse existing, tested Model C v4 implementation
- Maintain consistency with other model wrappers
- Easier to maintain and update

### 2. Standardized Interface
**Decision**: Match the interface pattern of Model A, B, D wrappers
**Rationale**:
- Consistency across all model wrappers
- Easier for developers to use
- Simplifies integration with unified_model_service

### 3. Multiple Timeframe Predictions
**Decision**: Provide predictions for 7, 30, 90, 180 days
**Rationale**:
- Users need different planning horizons
- Confidence decreases with longer timeframes
- Matches existing price_prediction_service behavior

### 4. Thai Language Insights
**Decision**: Generate insights in Thai language
**Rationale**:
- Target users are Thai farmers
- Consistent with other parts of the system
- More actionable for end users

### 5. Fallback Mechanism
**Decision**: Implement rule-based fallback when ML model fails
**Rationale**:
- System remains functional even if model unavailable
- Better user experience than error messages
- Consistent with other model wrappers

### 6. Global Singleton Instance
**Decision**: Create `model_c_wrapper` as global instance
**Rationale**:
- Matches pattern of other wrappers
- Easy to import and use
- Model loaded once at startup

## Dependencies

- Python 3.8+
- numpy
- pandas
- pickle (standard library)
- logging (standard library)
- datetime (standard library)
- typing (standard library)
- app.services.price_forecast_service (existing)
- database module (for SessionLocal, CropPrice)

## File Structure

```
backend/
├── model_c_wrapper.py          # New wrapper file
├── app/
│   └── services/
│       └── price_forecast_service.py  # Existing service
├── REMEDIATION_PRODUCTION/
│   └── trained_models/
│       ├── model_c_ultimate.pkl
│       └── model_c_price_forecast.pkl
└── models/                     # Alternative model location
    └── model_c_price_forecast.pkl
```

## Performance Considerations

- Model loaded once at initialization (not per request)
- Database queries optimized with proper indexes
- Caching can be added later if needed
- Predictions are fast (<100ms for single request)

## Security Considerations

- Input validation for crop_type and province
- SQL injection prevention (using parameterized queries)
- No sensitive data in logs
- Error messages don't expose internal details

## Future Enhancements

1. Add caching layer for frequently requested predictions
2. Support batch predictions for multiple crops
3. Add confidence interval calculations
4. Integrate weather forecast data for better predictions
5. Add A/B testing framework for model improvements

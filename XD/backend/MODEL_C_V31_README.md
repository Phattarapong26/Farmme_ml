# Model C v3.1 - Seasonal-Aware Price Forecasting

## Overview

Model C v3.1 is a retrained XGBoost model for agricultural price forecasting with improved seasonal awareness and accuracy.

**Version**: 3.1_seasonal_aware_retrained  
**Model File**: `model_c_v3_seasonal_retrained.pkl`  
**Location**: `REMEDIATION_PRODUCTION/models_production/`

---

## Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **RMSE** | 0.4254 baht/kg | Root Mean Square Error |
| **MAE** | 0.2855 baht/kg | Mean Absolute Error |
| **MAPE** | 0.87% | Mean Absolute Percentage Error |
| **Features** | 31 | Seasonal-aware features |
| **Patterns** | 3,132 | Crop/province combinations |

---

## Key Improvements over v2.0

1. **Better Accuracy**: MAPE < 1% (vs unknown for v2.0)
2. **Seasonal Awareness**: 3,132 seasonal patterns for different crop/province combinations
3. **Fewer Features**: 31 features (vs 94 in v2.0) - faster predictions
4. **Smaller Model**: ~50MB (vs ~80MB in v2.0) - lower memory footprint
5. **Better Training**: 2.19M records with proper validation

---

## Features (31 Total)

### Lag Features (3)
- `price_per_kg_lag7`: Price 7 days ago
- `price_per_kg_lag14`: Price 14 days ago
- `price_per_kg_lag30`: Price 30 days ago

### Momentum Features (3)
- `price_per_kg_momentum_7d`: 7-day price momentum
- `price_per_kg_momentum_14d`: 14-day price momentum
- `price_per_kg_momentum_30d`: 30-day price momentum

### Trend Features (3)
- `price_per_kg_trend_7d`: 7-day trend
- `price_per_kg_trend_14d`: 14-day trend
- `price_per_kg_trend_30d`: 30-day trend

### Volatility Features (4)
- `price_per_kg_volatility_7d`: 7-day volatility
- `price_per_kg_volatility_14d`: 14-day volatility
- `price_per_kg_cv_7d`: 7-day coefficient of variation
- `price_per_kg_cv_14d`: 14-day coefficient of variation

### Market Features (3)
- `price_per_kg_historical_mean`: Historical average price
- `price_per_kg_distance_from_mean`: Distance from mean
- `price_per_kg_percentile`: Price percentile

### Time Features (5)
- `month`: Month (1-12)
- `quarter`: Quarter (1-4)
- `day_of_week`: Day of week (0-6)
- `day_of_month`: Day of month (1-31)
- `week_of_year`: Week of year (1-52)

### Cyclical Features (4)
- `month_sin`: Sine of month
- `month_cos`: Cosine of month
- `week_sin`: Sine of week
- `week_cos`: Cosine of week

### Seasonal Features (3)
- `seasonal_index`: Seasonal multiplier for month
- `seasonal_expected_price`: Expected price based on season
- `seasonal_deviation`: Deviation from seasonal expectation

### Seasonal Interactions (3)
- `month_momentum_7d`: Month × momentum interaction
- `quarter_trend_7d`: Quarter × trend interaction
- `seasonal_lag7`: Seasonal index × lag7 interaction

---

## Usage

### 1. Using model_c_v31_service (Direct)

```python
from model_c_v31_service import model_c_v31_service

result = model_c_v31_service.predict_price(
    crop_type="มะเขือเทศ",
    province="เชียงใหม่",
    current_price=42.0,
    days_ahead=[7, 30, 90, 180]
)

print(f"Predictions: {result['predictions']}")
print(f"Trend: {result['price_trend']}")
```

### 2. Using price_forecast_service (Production)

```python
from app.services.price_forecast_service import price_forecast_service
from database import SessionLocal

db = SessionLocal()

result = price_forecast_service.forecast_price(
    province="เชียงใหม่",
    crop_type="มะเขือเทศ",
    days_ahead=90,
    current_price=42.0,
    db_session=db
)

print(f"Daily forecasts: {len(result['daily_forecasts'])}")
print(f"Trend: {result['price_trend']}")
```

### 3. Using API Endpoint

```bash
curl -X POST http://localhost:8000/api/v2/model/predict-price-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "เชียงใหม่",
    "crop_type": "มะเขือเทศ",
    "days_ahead": 30
  }'
```

**Response:**
```json
{
  "success": true,
  "forecast": [
    {
      "date": "2025-11-21",
      "predicted_price": 43.49,
      "confidence_low": 39.14,
      "confidence_high": 47.84
    }
  ],
  "model_used": "model_c",
  "confidence_score": 0.85,
  "model_version": "3.1_seasonal_aware_retrained",
  "seasonal_patterns_used": 3132
}
```

---

## API Endpoints

### GET /api/v2/model/model-status

Get model status and metrics.

**Response:**
```json
{
  "model_available": true,
  "model_file": "model_c_v3_seasonal_retrained.pkl",
  "version": "3.1_seasonal_aware_retrained",
  "feature_count": 31,
  "seasonal_patterns": 3132,
  "status": "active",
  "metrics": {
    "rmse": 0.4254,
    "mae": 0.2855,
    "mape": 0.8711
  }
}
```

### POST /api/v2/model/predict-price-forecast

Generate price forecast.

**Request:**
```json
{
  "province": "เชียงใหม่",
  "crop_type": "มะเขือเทศ",
  "days_ahead": 30
}
```

**Response:** See example above.

---

## Seasonal Patterns

The model includes 3,132 seasonal patterns for different crop/province combinations:

- **Seasonal Index**: Monthly multiplier (e.g., 1.05 = 5% above average)
- **Overall Average**: Historical average price for the crop/province
- **Pattern Learning**: Learned from 2.19M historical records

Example seasonal pattern:
```python
{
    'overall_avg': 35.0,
    'seasonal_index': {
        1: 1.05,  # January: 5% above average
        2: 1.03,  # February: 3% above average
        3: 1.00,  # March: average
        4: 0.98,  # April: 2% below average
        5: 0.95,  # May: 5% below average
        ...
    }
}
```

---

## Confidence Scores

Confidence decreases with forecast horizon:

| Days Ahead | Confidence |
|------------|------------|
| 7 days | 0.89 |
| 30 days | 0.88 |
| 90 days | 0.83 |
| 180 days | 0.75 |

---

## Fallback Mechanism

If Model C v3.1 is unavailable, the system falls back to:

1. **simple_price_forecast**: Statistical forecasting using historical data
2. **Historical trend**: Basic trend-based prediction
3. **Default values**: Safe fallback with lower confidence

---

## Testing

Run comprehensive tests:

```bash
# Test services
python backend/test_model_c_service.py

# Test with database
python REMEDIATION_PRODUCTION/test_production_with_database.py

# Test API endpoints
python backend/test_api_endpoints_e2e.py

# Test model status
python backend/test_model_status_endpoint.py
```

---

## Troubleshooting

### Model not loading

**Error**: `FileNotFoundError: model_c_v3_seasonal_retrained.pkl`

**Solution**:
```bash
# Check file exists
ls REMEDIATION_PRODUCTION/models_production/model_c_v3_seasonal_retrained.pkl

# Check permissions
chmod 644 REMEDIATION_PRODUCTION/models_production/*.pkl
```

### Import errors

**Error**: `ModuleNotFoundError: No module named 'seasonal_feature_engineer_production'`

**Solution**:
```python
import sys
sys.path.append('REMEDIATION_PRODUCTION/Model_C_Fix')
```

### Predictions seem unrealistic

**Check**:
1. Database has recent data
2. Seasonal patterns loaded correctly
3. Feature engineer initialized

```bash
python REMEDIATION_PRODUCTION/test_production_with_database.py
```

---

## Migration from v2.0

If you need to rollback to v2.0:

```bash
# Restore v2.0 model
cp REMEDIATION_PRODUCTION/models_production/archive/model_c_v2_price_forecast_archived.pkl \
   REMEDIATION_PRODUCTION/models_production/model_c_price_forecast.pkl

# Update service paths
# Edit backend/app/services/price_forecast_service.py
# Change model path back to model_c_price_forecast.pkl

# Restart services
docker-compose restart backend
```

---

## Performance Benchmarks

| Operation | Time | Memory |
|-----------|------|--------|
| Model loading | ~1s | ~50MB |
| Single prediction | <50ms | - |
| 30-day forecast | <200ms | - |
| 90-day forecast | <500ms | - |
| 180-day forecast | <1s | - |

---

## References

- **Training Script**: `REMEDIATION_PRODUCTION/Model_C_Fix/retrain_model_v31.py`
- **Feature Engineer**: `REMEDIATION_PRODUCTION/Model_C_Fix/seasonal_feature_engineer_production.py`
- **Deployment Guide**: `REMEDIATION_PRODUCTION/DEPLOYMENT_GUIDE.md`
- **Update Summary**: `REMEDIATION_PRODUCTION/PRODUCTION_UPDATE_SUMMARY.md`

---

**Last Updated**: November 20, 2025  
**Model Version**: 3.1_seasonal_aware_retrained  
**Status**: ✅ Production Ready

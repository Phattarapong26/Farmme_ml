# API Documentation - Model C v3.1 Endpoints

## Base URL

```
http://localhost:8000/api/v2/model
```

---

## Endpoints

### 1. Get Model Status

Get current model status, version, and performance metrics.

**Endpoint**: `GET /model-status`

**Response**:
```json
{
  "model_available": true,
  "model_path": "/path/to/model_c_v3_seasonal_retrained.pkl",
  "model_type": "XGBRegressor",
  "model_file": "model_c_v3_seasonal_retrained.pkl",
  "version": "3.1_seasonal_aware_retrained",
  "status": "active",
  "feature_count": 31,
  "seasonal_patterns": 3132,
  "note": "Model C v3.1 - Seasonal-Aware Price Forecast",
  "metrics": {
    "rmse": 0.4254,
    "mae": 0.2855,
    "mape": 0.8711,
    "r2": null
  }
}
```

**Status Codes**:
- `200 OK`: Model status retrieved successfully
- `500 Internal Server Error`: Error retrieving model status

**Example**:
```bash
curl http://localhost:8000/api/v2/model/model-status
```

---

### 2. Predict Price Forecast

Generate price forecast for a specific crop and province.

**Endpoint**: `POST /predict-price-forecast`

**Request Body**:
```json
{
  "province": "เชียงใหม่",
  "crop_type": "มะเขือเทศ",
  "crop_category": "ผัก",  // Optional
  "days_ahead": 30
}
```

**Parameters**:
- `province` (string, required): Province name in Thai
- `crop_type` (string, required): Crop type in Thai
- `crop_category` (string, optional): Crop category
- `days_ahead` (integer, required): Number of days to forecast (1-180)

**Response**:
```json
{
  "success": true,
  "forecast": [
    {
      "date": "2025-11-21",
      "predicted_price": 43.49,
      "confidence_low": 39.14,
      "confidence_high": 47.84
    },
    {
      "date": "2025-11-22",
      "predicted_price": 43.90,
      "confidence_low": 39.51,
      "confidence_high": 48.29
    }
    // ... more forecasts
  ],
  "model_used": "model_c",
  "confidence_score": 0.85,
  "note": "ML Model C prediction for มะเขือเทศ in เชียงใหม่",
  "model_version": "3.1_seasonal_aware_retrained",
  "seasonal_patterns_used": 3132
}
```

**Response Fields**:
- `success` (boolean): Whether prediction succeeded
- `forecast` (array): Array of daily forecasts
  - `date` (string): Forecast date (YYYY-MM-DD)
  - `predicted_price` (number): Predicted price in baht/kg
  - `confidence_low` (number): Lower confidence bound
  - `confidence_high` (number): Upper confidence bound
- `model_used` (string): Model identifier ("model_c" or "fallback")
- `confidence_score` (number): Overall confidence (0.5-0.9)
- `note` (string): Additional information
- `model_version` (string, optional): Model version used
- `seasonal_patterns_used` (integer, optional): Number of seasonal patterns

**Status Codes**:
- `200 OK`: Forecast generated successfully
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Prediction failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/v2/model/predict-price-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "เชียงใหม่",
    "crop_type": "มะเขือเทศ",
    "days_ahead": 30
  }'
```

---

## Error Responses

### Model Not Available

When Model C v3.1 is not loaded, the API falls back to statistical forecasting:

```json
{
  "success": true,
  "forecast": [...],
  "model_used": "fallback_trend",
  "confidence_score": 0.60,
  "note": "Using trend-based forecast from historical data (ML model not available)"
}
```

### Invalid Request

```json
{
  "detail": [
    {
      "loc": ["body", "days_ahead"],
      "msg": "ensure this value is less than or equal to 180",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Recommended limits for production:

- **Per IP**: 100 requests/minute
- **Per User**: 1000 requests/hour

---

## Authentication

Currently no authentication required. For production, consider:

- API keys
- JWT tokens
- OAuth 2.0

---

## Versioning

API version is included in the URL path: `/api/v2/model/`

Future versions will use: `/api/v3/model/`, etc.

---

## Best Practices

### 1. Caching

Cache forecast results for the same crop/province/days_ahead combination:

```python
cache_key = f"{province}:{crop_type}:{days_ahead}"
cache_ttl = 3600  # 1 hour
```

### 2. Error Handling

Always check the `success` field:

```javascript
const response = await fetch('/api/v2/model/predict-price-forecast', {
  method: 'POST',
  body: JSON.stringify(request)
});

const data = await response.json();

if (!data.success) {
  console.error('Prediction failed:', data.note);
  // Handle fallback
}
```

### 3. Confidence Intervals

Use confidence intervals for visualization:

```javascript
// Chart.js example
{
  datasets: [
    {
      label: 'Predicted Price',
      data: forecast.map(f => f.predicted_price)
    },
    {
      label: 'Confidence Range',
      data: forecast.map(f => [f.confidence_low, f.confidence_high]),
      type: 'area'
    }
  ]
}
```

### 4. Model Version Tracking

Track which model version generated predictions:

```javascript
if (data.model_version) {
  console.log(`Prediction from: ${data.model_version}`);
  // Store in analytics
}
```

---

## Integration Examples

### React/TypeScript

```typescript
interface PriceForecastRequest {
  province: string;
  crop_type: string;
  days_ahead: number;
}

interface PriceForecastResponse {
  success: boolean;
  forecast: Array<{
    date: string;
    predicted_price: number;
    confidence_low?: number;
    confidence_high?: number;
  }>;
  model_used: string;
  confidence_score: number;
  model_version?: string;
}

async function fetchPriceForecast(
  request: PriceForecastRequest
): Promise<PriceForecastResponse> {
  const response = await fetch('/api/v2/model/predict-price-forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  return response.json();
}
```

### Python

```python
import requests

def get_price_forecast(province: str, crop_type: str, days_ahead: int):
    url = "http://localhost:8000/api/v2/model/predict-price-forecast"
    
    response = requests.post(url, json={
        "province": province,
        "crop_type": crop_type,
        "days_ahead": days_ahead
    })
    
    response.raise_for_status()
    return response.json()

# Usage
result = get_price_forecast("เชียงใหม่", "มะเขือเทศ", 30)
print(f"Forecast: {len(result['forecast'])} days")
```

---

## Monitoring

### Metrics to Track

1. **Request Rate**: Requests per minute
2. **Response Time**: p50, p95, p99 latencies
3. **Error Rate**: Failed predictions / total requests
4. **Model Usage**: ML model vs fallback ratio
5. **Confidence Distribution**: Average confidence scores

### Health Check

```bash
# Check if model is loaded
curl http://localhost:8000/api/v2/model/model-status | jq '.model_available'

# Expected: true
```

---

## Changelog

### v3.1 (November 20, 2025)
- ✅ Added Model C v3.1 (Seasonal-Aware)
- ✅ Added `model_version` field to responses
- ✅ Added `seasonal_patterns_used` field
- ✅ Added performance metrics to status endpoint
- ✅ Improved confidence intervals
- ✅ Better fallback mechanism

### v2.0 (Previous)
- Model C v2.0 with 94 features
- Basic forecasting without seasonal awareness

---

**Last Updated**: November 20, 2025  
**API Version**: v2  
**Model Version**: 3.1_seasonal_aware_retrained

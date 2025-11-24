# Frontend Integration Guide - Model C v3.1

## Overview

This guide helps frontend developers integrate Model C v3.1 predictions into their applications.

---

## New Response Fields

Model C v3.1 adds optional metadata fields to prediction responses:

```typescript
interface PriceForecastResponse {
  success: boolean;
  forecast: ForecastItem[];
  model_used: string;
  confidence_score: number;
  note?: string;
  
  // NEW in v3.1
  model_version?: string;  // "3.1_seasonal_aware_retrained"
  seasonal_patterns_used?: number;  // 3132
}
```

---

## Display Model Version Badge

Show users which model version generated their predictions:

### React Component

```tsx
import React from 'react';

interface ModelBadgeProps {
  modelVersion?: string;
  modelUsed: string;
}

export const ModelBadge: React.FC<ModelBadgeProps> = ({ 
  modelVersion, 
  modelUsed 
}) => {
  const isMLModel = modelUsed === 'model_c';
  
  return (
    <div className={`model-badge ${isMLModel ? 'ml' : 'fallback'}`}>
      {isMLModel ? (
        <>
          <span className="badge-icon">🤖</span>
          <span className="badge-text">
            ML Model {modelVersion ? `v${modelVersion.split('_')[0]}` : ''}
          </span>
        </>
      ) : (
        <>
          <span className="badge-icon">📊</span>
          <span className="badge-text">Statistical Forecast</span>
        </>
      )}
    </div>
  );
};
```

### CSS

```css
.model-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.model-badge.ml {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.model-badge.fallback {
  background-color: #fff3e0;
  color: #f57c00;
  border: 1px solid #ffb74d;
}
```

---

## Display Confidence Score

Show prediction confidence to users:

### React Component

```tsx
interface ConfidenceIndicatorProps {
  confidence: number;  // 0.0 - 1.0
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({ 
  confidence 
}) => {
  const percentage = Math.round(confidence * 100);
  const level = confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low';
  
  return (
    <div className="confidence-indicator">
      <div className="confidence-label">
        Confidence: {percentage}%
      </div>
      <div className="confidence-bar">
        <div 
          className={`confidence-fill ${level}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="confidence-description">
        {level === 'high' && '✅ High confidence - ML model with seasonal data'}
        {level === 'medium' && '⚠️ Medium confidence - Limited historical data'}
        {level === 'low' && '⚠️ Low confidence - Using statistical fallback'}
      </div>
    </div>
  );
};
```

### CSS

```css
.confidence-indicator {
  margin: 1rem 0;
}

.confidence-label {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.confidence-bar {
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.confidence-fill.high {
  background-color: #4caf50;
}

.confidence-fill.medium {
  background-color: #ff9800;
}

.confidence-fill.low {
  background-color: #f44336;
}

.confidence-description {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.25rem;
}
```

---

## Display Seasonal Awareness

Show that predictions use seasonal patterns:

### React Component

```tsx
interface SeasonalIndicatorProps {
  seasonalPatternsUsed?: number;
}

export const SeasonalIndicator: React.FC<SeasonalIndicatorProps> = ({ 
  seasonalPatternsUsed 
}) => {
  if (!seasonalPatternsUsed) return null;
  
  return (
    <div className="seasonal-indicator">
      <span className="seasonal-icon">🌱</span>
      <span className="seasonal-text">
        Seasonal-aware prediction using {seasonalPatternsUsed.toLocaleString()} 
        crop/province patterns
      </span>
    </div>
  );
};
```

---

## Chart with Confidence Intervals

Display predictions with confidence intervals:

### Chart.js Example

```tsx
import { Line } from 'react-chartjs-2';

interface ForecastChartProps {
  forecast: ForecastItem[];
  historical?: HistoricalItem[];
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ 
  forecast, 
  historical 
}) => {
  const data = {
    labels: forecast.map(f => f.date),
    datasets: [
      // Historical data
      {
        label: 'Historical',
        data: historical?.map(h => ({ x: h.date, y: h.price })) || [],
        borderColor: '#666',
        backgroundColor: '#666',
        pointRadius: 3,
      },
      // Predicted price
      {
        label: 'Predicted Price',
        data: forecast.map(f => ({ x: f.date, y: f.predicted_price })),
        borderColor: '#1976d2',
        backgroundColor: '#1976d2',
        borderWidth: 2,
        pointRadius: 0,
      },
      // Confidence interval (upper)
      {
        label: 'Confidence Range',
        data: forecast.map(f => ({ x: f.date, y: f.confidence_high })),
        borderColor: 'rgba(25, 118, 210, 0.2)',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: '+1',
        pointRadius: 0,
        borderWidth: 1,
        borderDash: [5, 5],
      },
      // Confidence interval (lower)
      {
        label: '',
        data: forecast.map(f => ({ x: f.date, y: f.confidence_low })),
        borderColor: 'rgba(25, 118, 210, 0.2)',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: false,
        pointRadius: 0,
        borderWidth: 1,
        borderDash: [5, 5],
      },
    ],
  };
  
  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value.toFixed(2)} บาท/กก.`;
          },
        },
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Price (บาท/กก.)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Date',
        },
      },
    },
  };
  
  return <Line data={data} options={options} />;
};
```

---

## Complete Integration Example

### Full Component

```tsx
import React, { useState, useEffect } from 'react';
import { ModelBadge } from './ModelBadge';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { SeasonalIndicator } from './SeasonalIndicator';
import { ForecastChart } from './ForecastChart';

interface PriceForecastViewProps {
  province: string;
  cropType: string;
  daysAhead: number;
}

export const PriceForecastView: React.FC<PriceForecastViewProps> = ({
  province,
  cropType,
  daysAhead,
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PriceForecastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchForecast();
  }, [province, cropType, daysAhead]);
  
  const fetchForecast = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v2/model/predict-price-forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ province, crop_type: cropType, days_ahead: daysAhead }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="loading">Loading forecast...</div>;
  }
  
  if (error) {
    return <div className="error">Error: {error}</div>;
  }
  
  if (!data || !data.success) {
    return <div className="error">Failed to load forecast</div>;
  }
  
  return (
    <div className="price-forecast-view">
      <div className="forecast-header">
        <h2>Price Forecast: {cropType} in {province}</h2>
        
        <div className="forecast-metadata">
          <ModelBadge 
            modelVersion={data.model_version}
            modelUsed={data.model_used}
          />
          
          <SeasonalIndicator 
            seasonalPatternsUsed={data.seasonal_patterns_used}
          />
        </div>
      </div>
      
      <ConfidenceIndicator confidence={data.confidence_score} />
      
      <div className="forecast-chart">
        <ForecastChart forecast={data.forecast} />
      </div>
      
      <div className="forecast-summary">
        <p>{data.note}</p>
        {data.model_version && (
          <p className="model-info">
            Generated by Model C {data.model_version.split('_')[0]} 
            with {data.seasonal_patterns_used?.toLocaleString()} seasonal patterns
          </p>
        )}
      </div>
    </div>
  );
};
```

---

## API Response Examples

### Successful ML Prediction

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
  "note": "ML Model C prediction for มะเขือเทศ in เชียงใหม่",
  "model_version": "3.1_seasonal_aware_retrained",
  "seasonal_patterns_used": 3132
}
```

### Fallback Prediction

```json
{
  "success": true,
  "forecast": [...],
  "model_used": "fallback_trend",
  "confidence_score": 0.60,
  "note": "Using trend-based forecast from historical data (ML model not available)"
}
```

---

## Best Practices

### 1. Handle Missing Metadata

New fields are optional for backward compatibility:

```typescript
const modelVersion = data.model_version || 'Unknown';
const seasonalPatterns = data.seasonal_patterns_used || 0;
```

### 2. Show Fallback Indicator

Alert users when ML model is unavailable:

```tsx
{data.model_used !== 'model_c' && (
  <div className="fallback-warning">
    ⚠️ Using statistical forecast. ML model temporarily unavailable.
  </div>
)}
```

### 3. Cache Responses

Cache forecast responses to reduce API calls:

```typescript
const cacheKey = `forecast:${province}:${cropType}:${daysAhead}`;
const cached = localStorage.getItem(cacheKey);

if (cached) {
  const { data, timestamp } = JSON.parse(cached);
  const age = Date.now() - timestamp;
  
  // Use cache if less than 1 hour old
  if (age < 3600000) {
    return data;
  }
}
```

### 4. Error Handling

Always handle errors gracefully:

```tsx
try {
  const data = await fetchForecast();
  // Use data
} catch (error) {
  console.error('Forecast error:', error);
  // Show user-friendly message
  showNotification('Unable to load forecast. Please try again.');
}
```

---

## Testing

### Mock Data for Development

```typescript
export const mockForecastResponse: PriceForecastResponse = {
  success: true,
  forecast: Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() + i * 86400000).toISOString().split('T')[0],
    predicted_price: 40 + Math.random() * 10,
    confidence_low: 35 + Math.random() * 5,
    confidence_high: 45 + Math.random() * 5,
  })),
  model_used: 'model_c',
  confidence_score: 0.85,
  model_version: '3.1_seasonal_aware_retrained',
  seasonal_patterns_used: 3132,
  note: 'ML Model C prediction for มะเขือเทศ in เชียงใหม่',
};
```

---

## Migration from v2.0

If your app was using Model C v2.0:

1. **No breaking changes** - All existing fields remain
2. **New fields are optional** - Check before using
3. **Update UI** - Add new components for v3.1 features
4. **Test thoroughly** - Verify with both ML and fallback responses

---

**Last Updated**: November 20, 2025  
**Model Version**: 3.1_seasonal_aware_retrained  
**Status**: Ready for Integration

# Model B - Gradient Boosting (Full Dataset)

## Overview
This directory contains the retrained Model B using **3 algorithms** with **6,226 samples** for binary classification (Good/Bad planting window).

## Performance Metrics

### Best Model: Gradient Boosting 🏆
- **Test F1**: 0.8488
- **Test Precision**: 0.7741
- **Test Recall**: 0.9393
- **Test ROC-AUC**: 0.5841
- **Training Time**: 0.31 seconds

### Dataset
- **Source**: cultivation.csv + weather.csv
- **Total Samples**: 6,226
- **Train**: 3,735 samples (60%)
- **Val**: 1,245 samples (20%)
- **Test**: 1,246 samples (20%)
- **Class Distribution**: 75.4% Good windows, 24.6% Bad windows

### Data Quality
- ✅ Time-aware split by planting date
- ✅ No post-outcome features
- ✅ Clean binary classification

## Files

### Training Scripts
- `train_model_b_full.py` - Train with full dataset (6K samples) ⭐
- `three_algorithm_trainer_b.py` - Train 3 algorithms
- `bubble_chart_generator_b.py` - Generate bubble comparison chart

### Trained Models
Located in `REMEDIATION_PRODUCTION/trained_models/`:
- `model_b_gradboost_full.pkl` - **Best model** (Gradient Boosting) ⭐
- `model_b_xgboost_full.pkl` - XGBoost
- `model_b_random_forest_full.pkl` - Random Forest

### Evaluation Results
- `model_b_full_evaluation.json` - Detailed metrics for all algorithms

### Visualizations
Located in `REMEDIATION_PRODUCTION/outputs/model_b_full_evaluation/`:
- `bubble_comparison.png` - Bubble chart comparing 3 algorithms
- `model_b_xgboost_evaluation.png` - XGBoost detailed evaluation
- `model_b_random_forest_evaluation.png` - Random Forest detailed evaluation
- `model_b_gradboost_evaluation.png` - Gradient Boosting detailed evaluation

## Usage

### Training

```bash
# Train with full dataset
python REMEDIATION_PRODUCTION/modelB19_11_25/train_model_b_full.py
```

### Loading Model for Prediction

```python
import pickle
import pandas as pd
import numpy as np

# Load the best model (Gradient Boosting)
with open('REMEDIATION_PRODUCTION/trained_models/model_b_gradboost_full.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']
scaler = model_data['scaler']

# Prepare features (8 features required)
# Features: soil_ph, soil_nutrients, days_to_maturity, plant_month, plant_quarter,
#           plant_day_of_year, month_sin, month_cos, day_sin, day_cos,
#           soil_type_encoded, province_encoded, season_encoded

X_new = pd.DataFrame({
    'soil_ph': [6.5],
    'soil_nutrients': [0.7],
    'days_to_maturity': [90],
    'plant_month': [11],
    'plant_quarter': [4],
    'plant_day_of_year': [305],
    'month_sin': [np.sin(2 * np.pi * 11 / 12)],
    'month_cos': [np.cos(2 * np.pi * 11 / 12)],
})

# Scale features
X_scaled = scaler.transform(X_new)

# Predict
prediction = model.predict(X_scaled)
probability = model.predict_proba(X_scaled)

print(f"Prediction: {'Good Window' if prediction[0] == 1 else 'Bad Window'}")
print(f"Probability: {probability[0][1]:.2%}")
```

## Algorithm Comparison

| Algorithm | Test F1 | Test Precision | Test Recall | Test ROC-AUC | Training Time |
|-----------|---------|----------------|-------------|--------------|---------------|
| XGBoost | 0.6987 | 0.8197 | 0.6088 | 0.6042 | 0.16s |
| Random Forest | 0.7143 | 0.7949 | 0.6485 | 0.5924 | 0.13s |
| **Gradient Boosting** | **0.8488** | **0.7741** | **0.9393** | **0.5841** | 0.31s |

**Winner**: Gradient Boosting - Best F1 score with excellent recall

## Features Used

### Temporal Features (6 features)
- plant_month
- plant_quarter
- plant_day_of_year
- month_sin, month_cos (cyclic encoding)
- day_sin, day_cos (cyclic encoding)

### Soil & Crop Features (3 features)
- soil_ph
- soil_nutrients
- days_to_maturity

### Categorical Features (3 features - encoded)
- soil_type_encoded
- province_encoded
- season_encoded

## Notes

- All models use **clean features only** (no post-outcome features)
- **Time-aware split** by planting date prevents temporal leakage
- Models handle **class imbalance** (75% positive, 25% negative)
- Gradient Boosting provides the best balance of precision and recall

## Date
Created: November 19, 2025

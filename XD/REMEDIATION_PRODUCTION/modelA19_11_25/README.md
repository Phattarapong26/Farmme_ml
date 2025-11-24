# Model A - Gradient Boosting (Large Dataset)

## Overview
This directory contains the retrained Model A using **Gradient Boosting Regressor** with **1.4M+ samples** from FARMME_GPU_DATASET.

## Performance Metrics

### Best Model: Gradient Boosting
- **Test R²**: 0.8549
- **Test RMSE**: 47.10%
- **Test MAE**: 33.96%
- **Training Time**: 250.21 seconds
- **No Overfitting**: Gap = 0.0470

### Dataset
- **Source**: FARMME_GPU_DATASET.csv (2.2M+ rows)
- **Total Samples**: 1,420,412 (after filtering)
- **Train**: 1,089,905 samples (74.9%)
- **Val**: 200,367 samples (13.8%)
- **Test**: 130,140 samples (8.9%)
- **Date Range**: 2023-11-01 to 2025-10-30

### Data Leakage Prevention
- ✅ Strict time-aware split
- ✅ 7-day embargo period between splits
- ✅ No temporal overlap
- ✅ No forbidden features (price_next_day, actual_yield_kg, etc.)

## Files

### Training Scripts
- `train_model_a_minimal.py` - Train with 1K samples (quick testing)
- `train_model_a_full.py` - Train with 6K samples (standard)
- `train_model_a_large.py` - Train with 1.4M+ samples (production) ⭐

### Data Loaders
- `minimal_data_loader.py` - Load and sample minimal dataset
- `large_data_loader.py` - Load FARMME_GPU_DATASET

### Trainers & Plotters
- `three_algorithm_trainer.py` - Train 3 algorithms (XGBoost, RF+ElasticNet, GradBoost)
- `bubble_chart_generator.py` - Generate bubble comparison chart
- `detailed_plotter.py` - Generate detailed evaluation plots

### Trained Models
Located in `REMEDIATION_PRODUCTION/trained_models/`:
- `model_a_gradboost_large.pkl` - **Best model** (1.4M samples) ⭐
- `model_a_xgboost_large.pkl` - XGBoost (1.4M samples)
- `model_a_rf_ensemble_large.pkl` - Random Forest + ElasticNet (1.4M samples)

### Evaluation Results
- `model_a_large_evaluation.json` - Detailed metrics for all algorithms

### Visualizations
Located in `REMEDIATION_PRODUCTION/outputs/model_a_large_evaluation/`:
- `bubble_comparison.png` - Bubble chart comparing 3 algorithms
- `model_a_xgboost_evaluation.png` - XGBoost detailed evaluation
- `model_a_rf_ensemble_evaluation.png` - RF+ElasticNet detailed evaluation
- `model_a_gradboost_evaluation.png` - Gradient Boosting detailed evaluation

## Usage

### Training

#### Quick Test (1K samples)
```bash
python REMEDIATION_PRODUCTION/modelA19_11_25/train_model_a_minimal.py
```

#### Standard (6K samples)
```bash
python REMEDIATION_PRODUCTION/modelA19_11_25/train_model_a_full.py
```

#### Production (1.4M+ samples) - Recommended
```bash
# Use all data (takes ~5 minutes)
python REMEDIATION_PRODUCTION/modelA19_11_25/train_model_a_large.py

# Or sample specific size
python REMEDIATION_PRODUCTION/modelA19_11_25/train_model_a_large.py --sample 100000
```

### Loading Model for Prediction

```python
import pickle
import pandas as pd
import numpy as np

# Load the best model (Gradient Boosting)
with open('REMEDIATION_PRODUCTION/trained_models/model_a_gradboost_large.pkl', 'rb') as f:
    model = pickle.load(f)

# Prepare features (19 features required)
features = [
    'planting_area_rai',
    'expected_yield_kg',
    'growth_days',
    'water_requirement',
    'investment_cost',
    'risk_level',
    'base_price',
    'inventory_level',
    'supply_level',
    'demand_elasticity',
    'temperature_celsius',
    'rainfall_mm',
    'humidity_percent',
    'drought_index',
    'fuel_price',
    'fertilizer_price',
    'inflation_rate',
    'gdp_growth',
    'unemployment_rate',
]

# Example prediction
X_new = pd.DataFrame({
    'planting_area_rai': [25.0],
    'expected_yield_kg': [30000.0],
    'growth_days': [90],
    'water_requirement': [0.6],
    'investment_cost': [250000.0],
    'risk_level': [0.4],
    'base_price': [45.0],
    'inventory_level': [0.5],
    'supply_level': [0.7],
    'demand_elasticity': [-0.5],
    'temperature_celsius': [28.0],
    'rainfall_mm': [100.0],
    'humidity_percent': [75.0],
    'drought_index': [50.0],
    'fuel_price': [40.0],
    'fertilizer_price': [900.0],
    'inflation_rate': [2.0],
    'gdp_growth': [3.0],
    'unemployment_rate': [1.5],
})

# Predict ROI
predicted_roi = model.predict(X_new)
print(f"Predicted ROI: {predicted_roi[0]:.2f}%")
```

## Algorithm Comparison

| Algorithm | Test R² | Test RMSE | Training Time | Overfitting Gap |
|-----------|---------|-----------|---------------|-----------------|
| XGBoost | 0.8318 | 50.71% | 1.07s | 0.0593 |
| RF + ElasticNet | 0.8370 | 49.93% | 30.35s | 0.0468 |
| **Gradient Boosting** | **0.8549** | **47.10%** | 250.21s | 0.0470 |

**Winner**: Gradient Boosting - Best performance with acceptable training time

## Model Deployment

The best model (`model_a_gradboost_large.pkl`) has been deployed as the default Model A:
- Replaced: `REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl`
- Backup: `REMEDIATION_PRODUCTION/trained_models/model_a_xgboost_backup.pkl`

## Features Used

### Planting Characteristics (6 features)
- planting_area_rai
- expected_yield_kg
- growth_days
- water_requirement
- investment_cost
- risk_level

### Market Conditions (4 features)
- base_price
- inventory_level
- supply_level
- demand_elasticity

### Weather (4 features)
- temperature_celsius
- rainfall_mm
- humidity_percent
- drought_index

### Economic Factors (5 features)
- fuel_price
- fertilizer_price
- inflation_rate
- gdp_growth
- unemployment_rate

## Notes

- All models use **clean features only** (no post-outcome features)
- Strict **time-aware split** prevents data leakage
- **7-day embargo** between train/val/test sets
- Models are production-ready and validated
- Gradient Boosting provides the best balance of accuracy and reliability

## Date
Created: November 19, 2025

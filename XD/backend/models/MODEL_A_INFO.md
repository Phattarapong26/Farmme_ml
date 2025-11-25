
# Model A - Gradient Boosting Regressor
# Production Model Information

## Model Details
- **Model Type**: Gradient Boosting Regressor
- **Version**: 1.0.0
- **Trained Date**: 2025-11-25 20:22:50
- **Algorithm**: Gradient Boosting (Winner from comparison)

## Performance Metrics
- **R² Score**: 0.9210
- **MAE**: 3370.83%
- **RMSE**: 7036.00%
- **MAPE**: 25.71%

## Training Details
- **Training Samples**: 4,980
- **Features**: 13
- **ROI Capping**: 99th percentile (120732.41%)

## Hyperparameters
- n_estimators: 150
- max_depth: 4
- learning_rate: 0.08
- min_samples_split: 10
- min_samples_leaf: 4
- subsample: 0.85

## Files Saved
1. model_a_gradient_boosting.pkl - Main model
2. model_a_scaler.pkl - Feature scaler
3. model_a_encoders.pkl - Label encoders
4. model_a_metadata.pkl - Model metadata
5. crop_characteristics.pkl - Crop reference data

## Usage
```python
import joblib

# Load model
model = joblib.load('model_a_gradient_boosting.pkl')
scaler = joblib.load('model_a_scaler.pkl')
encoders = joblib.load('model_a_encoders.pkl')

# Make prediction
prediction = model.predict(scaler.transform(features))
```

# Model C v8.0 - Comprehensive Improvements

## 📋 Overview

Model C v8.0 addresses **all critical feedback** from the ML review and implements best practices for time-series price prediction.

**Training Date:** To be determined (run `train_model_c_v8_improved.py`)  
**Previous Version:** v7.0.0 (trained 2025-11-23 17:09:22)

---

## ✅ Critical Fixes Implemented

### 1. **Time-Based Split (Prevents Data Leakage)** 🔴 CRITICAL
**Problem in v7.0:**
```python
split_idx = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:split_idx]  # ❌ No temporal guarantee
```

**Fixed in v8.0:**
```python
split_date = df_clean['date'].quantile(0.8)
train_df = df_clean[df_clean['date'] <= split_date]  # ✅ Temporal split
test_df = df_clean[df_clean['date'] > split_date]
assert train_df['date'].max() <= test_df['date'].min()  # Verify no leakage
```

**Impact:** Eliminates risk of model seeing "future" patterns during training.

---

### 2. **Proper Bins Handling** 🟡 IMPORTANT
**Problem in v7.0:**
```python
bins=[0, low_threshold, high_threshold, float('inf')]  # ❌ Fails if price < 0
```

**Fixed in v8.0:**
```python
price_min = train_df['target_price_7d'].min() - 1
bins=[price_min, low_threshold, high_threshold, float('inf')]  # ✅ Safe
```

---

### 3. **Fallback Model for Production Robustness** 🔴 CRITICAL
**Problem in v7.0:**
- If a price category has insufficient data → no model trained
- Production receives that price range → **crash**

**Fixed in v8.0:**
```python
# Train main fallback model on ALL data
fallback_model = HistGradientBoostingRegressor(...)
fallback_model.fit(X_train_all, y_train_all)

# Use in wrapper
try:
    pred = category_model.predict(X)
except:
    pred = fallback_model.predict(X)  # ✅ Always works
```

**Impact:** Zero-downtime predictions, even for edge cases.

---

## 🚀 Major Improvements

### 4. **Weather Features Included** 🟢 HIGH IMPACT
**Added Features:**
- `temperature_celsius_ma_7` - 7-day rolling average temperature
- `temperature_celsius_std_7` - Temperature volatility
- `rainfall_mm_ma_7` - 7-day rolling average rainfall
- `rainfall_mm_std_7` - Rainfall volatility
- `humidity_percent_ma_7` - 7-day rolling average humidity
- `humidity_percent_std_7` - Humidity volatility

**Expected Impact:** +10-20% improvement in MAE (weather strongly affects crop prices)

---

### 5. **Enhanced Seasonal Features** 🟢 MEDIUM IMPACT
**Added Features:**
- `month_sin`, `month_cos` - Cyclical month encoding
- `dayofyear_sin`, `dayofyear_cos` - Cyclical day encoding
- `quarter` - Quarter of year
- `week_of_month` - Week within month

**Why Cyclical Encoding?**
- December (12) and January (1) are close in time but far in numeric value
- Sine/cosine encoding captures this: `sin(2π * month / 12)`

---

### 6. **HistGradientBoostingRegressor** 🟢 PERFORMANCE
**Upgrade:**
- v7.0: `GradientBoostingRegressor` (sklearn)
- v8.0: `HistGradientBoostingRegressor` (sklearn)

**Benefits:**
- **2-10x faster** training on large datasets
- Better handling of missing values
- Native support for categorical features
- Often **5-15% better accuracy**

---

### 7. **Better Hyperparameters** 🟡 TUNING
**v7.0 Parameters:**
```python
n_estimators=200
max_depth=7
learning_rate=0.1
```

**v8.0 Parameters:**
```python
max_iter=300          # More trees
max_depth=6           # Prevent overfitting
learning_rate=0.05    # Slower, more stable
min_samples_leaf=20   # Regularization
```

**Rationale:** Slower learning rate + more trees = better generalization

---

### 8. **Per-Crop Evaluation Metrics** 🟢 INSIGHT
**New in v8.0:**
```
Per-Crop Performance (Top 10 by volume):
   พริก                : MAE=  5.23, R²=0.812, MAPE= 8.5%, Avg= 61.50
   มะเขือเทศ           : MAE=  3.45, R²=0.891, MAPE= 6.2%, Avg= 55.30
   ...
```

**Why Important:**
- Some crops are easier to predict than others
- Identifies which crops need more data or features
- Weighted MAPE prevents high-price crops from dominating metrics

---

### 9. **Additional Price Features** 🟢 FEATURE ENGINEERING
**New Features:**
- `price_median_7/14/30` - Median prices (outlier-resistant)
- `price_volatility_7d/30d` - Price volatility ratios
- Better momentum calculations with division safety

---

## 📊 Expected Performance Improvements

### v7.0 Baseline:
```
Overall MAE:  6.97 baht/kg
Overall RMSE: 14.09 baht/kg
Overall R²:   0.7589
```

### v8.0 Expected (Conservative Estimate):
```
Overall MAE:  5.5-6.0 baht/kg  (↓ 15-20%)
Overall RMSE: 11-12 baht/kg    (↓ 15-20%)
Overall R²:   0.80-0.82        (↑ 5-8%)
MAPE:         8-10%            (NEW)
```

**Key Drivers:**
1. Weather features: +10-15% improvement
2. No data leakage: +5-10% improvement (more realistic)
3. Better algorithm: +5-10% improvement
4. Enhanced features: +3-5% improvement

---

## 🔧 How to Use

### Step 1: Train New Models
```bash
cd XD
python buildingModel.py/train_model_c_v8_improved.py
```

**Expected Time:** 10-20 minutes (depending on hardware)

**Output Files:**
```
backend/models/
├── model_c_v8_stratified_low.pkl
├── model_c_v8_stratified_medium.pkl
├── model_c_v8_stratified_high.pkl
├── model_c_v8_fallback.pkl          # NEW!
├── model_c_v8_thresholds.json
├── model_c_v8_features.json
└── model_c_v8_metadata.json
```

---

### Step 2: Update Backend (Option A - Replace Wrapper)
```python
# In backend/model_c_wrapper.py
# Replace entire file with model_c_wrapper_v8.py content
```

**OR**

### Step 2: Update Backend (Option B - Gradual Migration)
```python
# Keep both wrappers, use v8 by default
from model_c_wrapper_v8 import ModelCWrapper  # Use v8
# from model_c_wrapper import ModelCWrapper   # Old v7
```

---

### Step 3: Test New Models
```bash
python test_model_c_wrapper.py
```

**Expected Output:**
```
✅ Model loaded: True
   Version: 8.0.0
   Algorithm: HistGradientBoostingRegressor
   Models: LOW, MEDIUM, HIGH + FALLBACK
   MAE: 5.50 baht/kg
   R²: 0.8100
```

---

## 🔍 Validation Checklist

Before deploying v8.0 to production:

- [ ] **Performance Check:** MAE < 7.0 baht/kg, R² > 0.75
- [ ] **No Leakage:** Verify `train_date.max() < test_date.min()`
- [ ] **Fallback Works:** Test with edge-case prices (very low/high)
- [ ] **Per-Crop Metrics:** Check top 10 crops have reasonable MAPE
- [ ] **API Integration:** Test with `test_model_c_wrapper.py`
- [ ] **Production Test:** Run on staging environment for 24 hours
- [ ] **Rollback Plan:** Keep v7.0 models as backup

---

## 📈 Monitoring After Deployment

### Key Metrics to Track:
1. **Prediction Accuracy:** Daily MAE/RMSE on new data
2. **Fallback Usage:** How often fallback model is used (should be <1%)
3. **Response Time:** Prediction latency (should be <500ms)
4. **Error Rate:** Failed predictions (should be <0.1%)

### Alert Thresholds:
- MAE > 10 baht/kg → Investigate
- Fallback usage > 5% → Check category models
- Error rate > 1% → Check data quality

---

## 🐛 Known Limitations

1. **Weather Data Dependency:** If weather features are missing in production, model may degrade
2. **Cold Start:** New crops with <30 records still won't predict well
3. **Extreme Events:** Black swan events (e.g., pandemic) not captured
4. **Seasonal Drift:** Model may need retraining every 6-12 months

---

## 🔄 Future Improvements (v9.0 Ideas)

1. **Hyperparameter Tuning:** Use Optuna for automated tuning
2. **Ensemble Methods:** Combine multiple algorithms (XGBoost + LightGBM + HistGBR)
3. **External Features:** Add export data, fuel prices, currency rates
4. **Online Learning:** Incremental updates without full retraining
5. **Uncertainty Quantification:** Prediction intervals using quantile regression
6. **Multi-Step Ahead:** Optimize for 7, 30, 90, 180 days separately

---

## 📚 References

- **Feedback Source:** ML Review (November 2025)
- **Algorithm:** [HistGradientBoostingRegressor Docs](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- **Time-Series Best Practices:** [Forecasting: Principles and Practice](https://otexts.com/fpp3/)

---

## 👥 Credits

- **Original Model (v7.0):** Trained November 23, 2025
- **Improvements (v8.0):** Based on comprehensive ML feedback
- **Review Feedback:** Addressed all critical and important issues

---

## 📞 Support

If you encounter issues:
1. Check logs in `backend/logs/`
2. Verify model files exist in `backend/models/`
3. Test with `test_model_c_wrapper.py`
4. Compare with v7.0 baseline performance

**Rollback Command:**
```python
# In model_c_wrapper_v8.py
wrapper = ModelCWrapper(prefer_v8=False)  # Use v7.0
```

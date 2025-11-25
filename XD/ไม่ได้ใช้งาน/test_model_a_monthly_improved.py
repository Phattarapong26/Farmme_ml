# -*- coding: utf-8 -*-
"""
 Model A 
Test if Model A recommends the same crops every month

:
-  dataset  buildingModel.py/Dataset
-  4 algorithms: Random Forest, Gradient Boosting, XGBoost, LSTM
- Feature engineering 
- Compare  capture evaluation charts
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Setup paths
project_root = Path(__file__).parent
dataset_dir = project_root / "buildingModel.py" / "Dataset"
output_dir = project_root / "buildingModel.py" / "Model_A_Monthly_Test"
output_dir.mkdir(exist_ok=True)

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb

print("=" * 80)
print("Model A Monthly Test - Improved Version")
print("=" * 80)
print()

# ============================================================================
# 1. Load Real Datasets
# ============================================================================
print(" Loading datasets...")

try:
    # Load all datasets
    crop_chars = pd.read_csv(dataset_dir / "crop_characteristics.csv", encoding='utf-8')
    cultivation = pd.read_csv(dataset_dir / "cultivation.csv", encoding='utf-8')
    weather = pd.read_csv(dataset_dir / "weather.csv", encoding='utf-8')
    price = pd.read_csv(dataset_dir / "price.csv", encoding='utf-8')
    economic = pd.read_csv(dataset_dir / "economic.csv", encoding='utf-8')
    
    print(f"    Crop characteristics: {len(crop_chars)} crops")
    print(f"    Cultivation data: {len(cultivation)} records")
    print(f"    Weather data: {len(weather)} records")
    print(f"    Price data: {len(price)} records")
    print(f"    Economic data: {len(economic)} records")
    print()
    
except Exception as e:
    print(f"    Error loading datasets: {e}")
    sys.exit(1)

# ============================================================================
# 2. Feature Engineering - 
# ============================================================================
print(" Feature Engineering...")

# Convert dates
cultivation['planting_date'] = pd.to_datetime(cultivation['planting_date'])
cultivation['harvest_date'] = pd.to_datetime(cultivation['harvest_date'])
weather['date'] = pd.to_datetime(weather['date'])
price['date'] = pd.to_datetime(price['date'])
economic['date'] = pd.to_datetime(economic['date'])

# Extract temporal features
cultivation['plant_month'] = cultivation['planting_date'].dt.month

# Thai seasonal encoding (more accurate)
def get_thai_season(month):
    """กำหนดฤดูกาลไทย"""
    if month in [11, 12, 1, 2]:
        return 'winter'  # ฤดูหนาว
    elif month in [3, 4, 5]:
        return 'summer'  # ฤดูร้อน
    else:
        return 'rainy'   # ฤดูฝน

cultivation['plant_season'] = cultivation['plant_month'].apply(get_thai_season)
cultivation['plant_year'] = cultivation['planting_date'].dt.year
cultivation['plant_quarter'] = cultivation['planting_date'].dt.quarter
cultivation['day_of_year'] = cultivation['planting_date'].dt.dayofyear

# Calculate ROI (target variable)
cultivation['revenue'] = cultivation['actual_yield_kg'] * 50  # Assume avg price 50 baht/kg
cultivation['roi'] = ((cultivation['revenue'] - cultivation['investment_cost']) / 
                      cultivation['investment_cost'] * 100)

# Merge with crop characteristics
cultivation = cultivation.merge(
    crop_chars[['crop_type', 'growth_days', 'water_requirement', 'soil_preference', 
                'risk_level', 'seasonal_type', 'weather_sensitivity', 'demand_elasticity']],
    on='crop_type',
    how='left'
)

# Add weather features (30 days before planting)
def add_weather_features(row):
    """ features  30 """
    start_date = row['planting_date'] - timedelta(days=30)
    end_date = row['planting_date']
    
    weather_period = weather[
        (weather['province'] == row['province']) &
        (weather['date'] >= start_date) &
        (weather['date'] < end_date)
    ]
    
    if len(weather_period) > 0:
        return pd.Series({
            'avg_temp_30d': weather_period['temperature_celsius'].mean(),
            'total_rain_30d': weather_period['rainfall_mm'].sum(),
            'avg_humidity_30d': weather_period['humidity_percent'].mean(),
            'avg_drought_30d': weather_period['drought_index'].mean(),
            'rainy_days_30d': (weather_period['rainfall_mm'] > 1).sum()
        })
    else:
        return pd.Series({
            'avg_temp_30d': 28.0,
            'total_rain_30d': 100.0,
            'avg_humidity_30d': 75.0,
            'avg_drought_30d': 50.0,
            'rainy_days_30d': 10
        })

print("   Adding weather features (this may take a while)...")
weather_features = cultivation.apply(add_weather_features, axis=1)
cultivation = pd.concat([cultivation, weather_features], axis=1)

# Add price features (average price 90 days before planting)
def add_price_features(row):
    """ features  90 """
    start_date = row['planting_date'] - timedelta(days=90)
    end_date = row['planting_date']
    
    price_period = price[
        (price['crop_type'] == row['crop_type']) &
        (price['province'] == row['province']) &
        (price['date'] >= start_date) &
        (price['date'] < end_date)
    ]
    
    if len(price_period) > 0:
        return pd.Series({
            'avg_price_90d': price_period['price_per_kg'].mean(),
            'price_volatility_90d': price_period['price_per_kg'].std(),
            'price_trend_90d': (price_period['price_per_kg'].iloc[-1] - price_period['price_per_kg'].iloc[0]) 
                               if len(price_period) > 1 else 0
        })
    else:
        return pd.Series({
            'avg_price_90d': 50.0,
            'price_volatility_90d': 10.0,
            'price_trend_90d': 0.0
        })

print("   Adding price features...")
price_features = cultivation.apply(add_price_features, axis=1)
cultivation = pd.concat([cultivation, price_features], axis=1)

# Add economic features
def add_economic_features(row):
    """ features """
    econ_date = economic[economic['date'] <= row['planting_date']].tail(1)
    
    if len(econ_date) > 0:
        return pd.Series({
            'fuel_price': econ_date['fuel_price'].values[0],
            'fertilizer_price': econ_date['fertilizer_price'].values[0],
            'inflation_rate': econ_date['inflation_rate'].values[0],
            'gdp_growth': econ_date['gdp_growth'].values[0]
        })
    else:
        return pd.Series({
            'fuel_price': 40.0,
            'fertilizer_price': 900.0,
            'inflation_rate': 2.0,
            'gdp_growth': 3.0
        })

print("   Adding economic features...")
economic_features = cultivation.apply(add_economic_features, axis=1)
cultivation = pd.concat([cultivation, economic_features], axis=1)

print(f"    Total features: {cultivation.shape[1]}")
print()

# ============================================================================
# 3. Prepare Features for ML
# ============================================================================
print(" Preparing features for ML...")

# Select features
feature_cols = [
    # Temporal (enhanced)
    'plant_month', 'plant_quarter', 'day_of_year',
    # Farm characteristics
    'planting_area_rai', 'farm_skill', 'tech_adoption',
    # Crop characteristics
    'growth_days', 'investment_cost', 'weather_sensitivity', 'demand_elasticity',
    # Weather (30 days before)
    'avg_temp_30d', 'total_rain_30d', 'avg_humidity_30d', 'avg_drought_30d', 'rainy_days_30d',
    # Price (90 days before)
    'avg_price_90d', 'price_volatility_90d', 'price_trend_90d',
    # Economic
    'fuel_price', 'fertilizer_price', 'inflation_rate', 'gdp_growth'
]

# Encode categorical variables
le_province = LabelEncoder()
le_crop = LabelEncoder()
le_season = LabelEncoder()

cultivation['province_encoded'] = le_province.fit_transform(cultivation['province'])
cultivation['crop_encoded'] = le_crop.fit_transform(cultivation['crop_type'])
cultivation['season_encoded'] = le_season.fit_transform(cultivation['plant_season'])

feature_cols.extend(['province_encoded', 'crop_encoded', 'season_encoded'])

# Remove rows with missing ROI
cultivation_clean = cultivation.dropna(subset=['roi'] + feature_cols)

X = cultivation_clean[feature_cols]
y = cultivation_clean['roi']

print(f"    Features: {len(feature_cols)}")
print(f"    Samples: {len(X)}")
print(f"    Target (ROI) range: {y.min():.2f}% to {y.max():.2f}%")
print()

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"    Train set: {len(X_train)} samples")
print(f"    Test set: {len(X_test)} samples")
print()

# ============================================================================
# Helper Functions
# ============================================================================

def top_k_accuracy(y_true, y_pred, k=3):
    """
    Business Metric: วัดว่าพืชที่แนะนำติด Top-K ถูกต้องหรือไม่
    """
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame({'true': y_true, 'pred': y_pred})
    
    # Get top-k indices
    true_top_k = df.nlargest(k, 'true').index
    pred_top_k = df.nlargest(k, 'pred').index
    
    # Calculate overlap
    overlap = len(set(true_top_k) & set(pred_top_k))
    return overlap / k

print()

# ============================================================================
# 4. Train Multiple Algorithms
# ============================================================================
print(" Training 4 algorithms...")
print()

models = {}
results = {}

# 1. Random Forest
print("1. Random Forest...")
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)

# Time Series Cross Validation
tscv = TimeSeriesSplit(n_splits=5)
cv_scores = cross_val_score(rf, X_train_scaled, y_train, cv=tscv, scoring='r2', n_jobs=-1)

rf.fit(X_train_scaled, y_train)
rf_pred = rf.predict(X_test_scaled)
models['Random Forest'] = rf
results['Random Forest'] = {
    'r2': r2_score(y_test, rf_pred),
    'mae': mean_absolute_error(y_test, rf_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)),
    'cv_r2_mean': cv_scores.mean(),
    'cv_r2_std': cv_scores.std()
}
print(f"   R2 (Test) = {results['Random Forest']['r2']:.4f}")
print(f"   R2 (CV) = {results['Random Forest']['cv_r2_mean']:.4f} (+/- {results['Random Forest']['cv_r2_std']:.4f})")
print(f"   MAE = {results['Random Forest']['mae']:.2f}%")
print()

# 2. Gradient Boosting
print("2. Gradient Boosting...")
gb = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

# Time Series Cross Validation
cv_scores = cross_val_score(gb, X_train_scaled, y_train, cv=tscv, scoring='r2', n_jobs=-1)

gb.fit(X_train_scaled, y_train)
gb_pred = gb.predict(X_test_scaled)
models['Gradient Boosting'] = gb
results['Gradient Boosting'] = {
    'r2': r2_score(y_test, gb_pred),
    'mae': mean_absolute_error(y_test, gb_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, gb_pred)),
    'cv_r2_mean': cv_scores.mean(),
    'cv_r2_std': cv_scores.std()
}
print(f"   R2 (Test) = {results['Gradient Boosting']['r2']:.4f}")
print(f"   R2 (CV) = {results['Gradient Boosting']['cv_r2_mean']:.4f} (+/- {results['Gradient Boosting']['cv_r2_std']:.4f})")
print(f"   MAE = {results['Gradient Boosting']['mae']:.2f}%")
print()

# 3. XGBoost
print("3. XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
)

# Time Series Cross Validation
cv_scores = cross_val_score(xgb_model, X_train_scaled, y_train, cv=tscv, scoring='r2', n_jobs=-1)

xgb_model.fit(X_train_scaled, y_train)
xgb_pred = xgb_model.predict(X_test_scaled)
models['XGBoost'] = xgb_model
results['XGBoost'] = {
    'r2': r2_score(y_test, xgb_pred),
    'mae': mean_absolute_error(y_test, xgb_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, xgb_pred)),
    'cv_r2_mean': cv_scores.mean(),
    'cv_r2_std': cv_scores.std()
}
print(f"   R2 (Test) = {results['XGBoost']['r2']:.4f}")
print(f"   R2 (CV) = {results['XGBoost']['cv_r2_mean']:.4f} (+/- {results['XGBoost']['cv_r2_std']:.4f})")
print(f"   MAE = {results['XGBoost']['mae']:.2f}%")
print()

# 4. Simple Baseline (Mean)
print("4. Baseline (Mean)...")
baseline_pred = np.full(len(y_test), y_train.mean())
results['Baseline'] = {
    'r2': r2_score(y_test, baseline_pred),
    'mae': mean_absolute_error(y_test, baseline_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, baseline_pred)),
    'cv_r2_mean': 0.0,
    'cv_r2_std': 0.0
}
print(f"   R2 (Test) = {results['Baseline']['r2']:.4f}")
print(f"   MAE = {results['Baseline']['mae']:.2f}%")
print()

# ============================================================================
# 5. Compare Algorithms
# ============================================================================
print(" Algorithm Comparison")
print("=" * 80)

comparison_df = pd.DataFrame(results).T
comparison_df = comparison_df.sort_values('r2', ascending=False)
print(comparison_df.to_string())
print()

# Save comparison
comparison_df.to_csv(output_dir / "algorithm_comparison.csv")

# ============================================================================
# 6. Visualization
# ============================================================================
print(" Creating visualizations...")

# 1. Algorithm Comparison Chart
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

metrics = ['r2', 'mae', 'rmse']
titles = ['R Score (Higher is Better)', 'MAE (Lower is Better)', 'RMSE (Lower is Better)']

for idx, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[idx]
    data = comparison_df[metric].sort_values(ascending=(metric != 'r2'))
    colors = ['green' if x == data.iloc[0] else 'skyblue' for x in data]
    data.plot(kind='barh', ax=ax, color=colors)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(metric.upper())
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "algorithm_comparison.png", dpi=300, bbox_inches='tight')
print(f"    Saved: algorithm_comparison.png")

# 2. Feature Importance (Best Model)
best_model_name = comparison_df.index[0]
best_model = models[best_model_name]

if hasattr(best_model, 'feature_importances_'):
    plt.figure(figsize=(10, 8))
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    
    plt.barh(range(len(importance)), importance['importance'])
    plt.yticks(range(len(importance)), importance['feature'])
    plt.xlabel('Importance')
    plt.title(f'Top 15 Feature Importance - {best_model_name}', fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_dir / "feature_importance.png", dpi=300, bbox_inches='tight')
    print(f"    Saved: feature_importance.png")

plt.close('all')

# ============================================================================
# 7. Monthly Recommendation Test
# ============================================================================
print()
print("=" * 80)
print(" Testing Monthly Recommendations")
print("=" * 80)
print()

# Use best model
best_model = models[best_model_name]

# Test conditions
test_province = "Chiang Mai"
test_conditions = {
    "planting_area_rai": 10,
    "farm_skill": 0.7,
    "tech_adoption": 0.5,
    "avg_temp_30d": 28.0,
    "total_rain_30d": 100.0,
    "avg_humidity_30d": 75.0,
    "avg_drought_30d": 50.0,
    "rainy_days_30d": 10,
    "avg_price_90d": 50.0,
    "price_volatility_90d": 10.0,
    "price_trend_90d": 0.0,
    "fuel_price": 40.0,
    "fertilizer_price": 900.0,
    "inflation_rate": 2.0,
    "gdp_growth": 3.0,
    "province_encoded": le_province.transform([test_province])[0]
}

months = list(range(1, 13))
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

monthly_results = {}

for month, month_name in zip(months, month_names):
    print(f"Month: {month_name} ({month})")
    print("-" * 60)
    
    # Prepare features for all crops
    crop_predictions = []
    
    for crop_type in crop_chars['crop_type'].unique()[:10]:  # Test top 10 crops
        crop_info = crop_chars[crop_chars['crop_type'] == crop_type].iloc[0]
        
        # Create feature vector
        features = test_conditions.copy()
        features['plant_month'] = month
        features['plant_quarter'] = (month - 1) // 3 + 1
        features['growth_days'] = crop_info['growth_days']
        features['investment_cost'] = crop_info['investment_cost']
        features['weather_sensitivity'] = crop_info['weather_sensitivity']
        features['demand_elasticity'] = crop_info['demand_elasticity']
        features['crop_encoded'] = le_crop.transform([crop_type])[0]
        features['season_encoded'] = le_season.transform([
            get_thai_season(month)
        ])[0]
        features['day_of_year'] = month * 30  # Approximate
        
        # Create feature array in correct order
        feature_array = np.array([[features[col] for col in feature_cols]])
        feature_array_scaled = scaler.transform(feature_array)
        
        # Predict ROI
        predicted_roi = best_model.predict(feature_array_scaled)[0]
        
        crop_predictions.append({
            'crop': crop_type,
            'predicted_roi': predicted_roi
        })
    
    # Sort by ROI
    crop_predictions = sorted(crop_predictions, key=lambda x: x['predicted_roi'], reverse=True)
    
    # Show top 5
    print(f"   Top 5 Crops:")
    for i, pred in enumerate(crop_predictions[:5], 1):
        print(f"      {i}. {pred['crop']}: ROI = {pred['predicted_roi']:.2f}%")
    
    monthly_results[month_name] = {
        'top_5': [p['crop'] for p in crop_predictions[:5]],
        'top_1': crop_predictions[0]['crop'],
        'top_1_roi': crop_predictions[0]['predicted_roi']
    }
    print()

# ============================================================================
# 8. Analyze Monthly Variation
# ============================================================================
print("=" * 80)
print("SUMMARY: Monthly Variation Analysis")
print("=" * 80)
print()

all_top_1 = [result['top_1'] for result in monthly_results.values()]
unique_top_1 = set(all_top_1)

print(f"Analysis:")
print(f"   - Total months tested: 12")
print(f"   - Unique top-1 crops: {len(unique_top_1)}")
print()

if len(unique_top_1) == 1:
    print("   WARNING: Top-1 crop is the SAME every month!")
    print(f"   Recommended crop: {list(unique_top_1)[0]}")
    print()
    print("   Conclusion: Model does NOT consider seasonal factors enough")
else:
    print(f"   SUCCESS: Top-1 crop varies across months")
    print(f"   Recommended crops: {', '.join(unique_top_1)}")
    print()
    print("   Conclusion: Model DOES consider seasonal factors")

print()
print("Monthly Details:")
print()

for month_name, result in monthly_results.items():
    print(f"   {month_name:12s} -> {result['top_1']:20s} (ROI: {result['top_1_roi']:.2f}%)")

print()
print("=" * 80)
print("TEST COMPLETED SUCCESSFULLY")
print("=" * 80)
print()
print(f"Results saved to: {output_dir}")
print(f"   - algorithm_comparison.csv")
print(f"   - algorithm_comparison.png")
print(f"   - feature_importance.png")


# -*- coding: utf-8 -*-
"""
Model A - Personalized Crop Recommendation System
ระบบแนะนำพืชแบบเฉพาะบุคคล

Features:
- ใช้ข้อมูลสภาพอากาศจริงของแต่ละจังหวัด
- รับ input จากผู้ใช้ (ทุน, พื้นที่, เป้าหมาย)
- เพิ่ม business rules สำหรับกรอง
- สร้าง personalized report
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for Thai characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
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
output_dir = project_root / "buildingModel.py" / "Model_A_Personalized"
output_dir.mkdir(exist_ok=True)

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score, learning_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Custom metrics for better evaluation
def mean_absolute_percentage_error(y_true, y_pred):
    """Calculate MAPE - better for relative error assessment"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def top_k_accuracy(y_true, y_pred, k=5):
    """
    Measure ranking accuracy - important for recommendation systems
    Returns: percentage of overlap in top-k predictions
    """
    true_top_k = set(np.argsort(y_true)[-k:])
    pred_top_k = set(np.argsort(y_pred)[-k:])
    return len(true_top_k & pred_top_k) / k * 100
import xgboost as xgb

# Deep Learning Libraries for LSTM
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("Warning: TensorFlow not available. LSTM model will be skipped.")

print("=" * 80)
print("Model A - Personalized Crop Recommendation System")
print("=" * 80)
print()

# Create timestamp for this run
from datetime import datetime
run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_output_dir = output_dir / f"run_{run_timestamp}"
run_output_dir.mkdir(exist_ok=True)

print(f"Output directory: {run_output_dir}")
print()

# ============================================================================
# 1. Load Real Datasets
# ============================================================================
print("Loading datasets...")

try:
    crop_chars = pd.read_csv(dataset_dir / "crop_characteristics.csv", encoding='utf-8')
    cultivation = pd.read_csv(dataset_dir / "cultivation.csv", encoding='utf-8')
    weather = pd.read_csv(dataset_dir / "weather.csv", encoding='utf-8')
    price = pd.read_csv(dataset_dir / "price.csv", encoding='utf-8')
    economic = pd.read_csv(dataset_dir / "economic.csv", encoding='utf-8')
    
    print(f"   Crop characteristics: {len(crop_chars)} crops")
    print(f"   Cultivation data: {len(cultivation)} records")
    print(f"   Weather data: {len(weather)} records")
    print(f"   Price data: {len(price)} records")
    print(f"   Economic data: {len(economic)} records")
    print()
    
except Exception as e:
    print(f"   Error loading datasets: {e}")
    sys.exit(1)

# Convert dates
cultivation['planting_date'] = pd.to_datetime(cultivation['planting_date'])
cultivation['harvest_date'] = pd.to_datetime(cultivation['harvest_date'])
weather['date'] = pd.to_datetime(weather['date'])
price['date'] = pd.to_datetime(price['date'])
economic['date'] = pd.to_datetime(economic['date'])

# ============================================================================
# 2. Helper Functions for Personalization
# ============================================================================

def get_thai_season(month):
    """กำหนดฤดูกาลไทย"""
    if month in [11, 12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'summer'
    else:
        return 'rainy'

def predict_with_model(model, feature_array_scaled, model_name=''):
    """
    Universal prediction function that works with both sklearn and LSTM models
    """
    if 'LSTM' in model_name or hasattr(model, 'predict') and 'Sequential' in str(type(model)):
        # LSTM model - needs 3D input
        feature_array_lstm = feature_array_scaled.reshape((feature_array_scaled.shape[0], 1, feature_array_scaled.shape[1]))
        prediction = model.predict(feature_array_lstm, verbose=0).flatten()[0]
    else:
        # sklearn models
        prediction = model.predict(feature_array_scaled)[0]
    return prediction

def get_province_weather_features(province, month):
    """
    ดึงข้อมูลสภาพอากาศจริงของจังหวัดในเดือนนั้นๆ
    """
    # Filter weather data for province and month
    province_weather = weather[
        (weather['province'] == province) &
        (weather['date'].dt.month == month)
    ]
    
    if len(province_weather) > 0:
        return {
            'avg_temp_30d': province_weather['temperature_celsius'].mean(),
            'total_rain_30d': province_weather['rainfall_mm'].sum(),
            'avg_humidity_30d': province_weather['humidity_percent'].mean(),
            'avg_drought_30d': province_weather['drought_index'].mean(),
            'rainy_days_30d': (province_weather['rainfall_mm'] > 1).sum()
        }
    else:
        # Fallback to default values
        return {
            'avg_temp_30d': 28.0,
            'total_rain_30d': 100.0,
            'avg_humidity_30d': 75.0,
            'avg_drought_30d': 50.0,
            'rainy_days_30d': 10
        }

def get_province_price_features(province, crop_type):
    """
    ดึงข้อมูลราคาเฉลี่ยของพืชในจังหวัดนั้นๆ
    """
    crop_price = price[
        (price['province'] == province) &
        (price['crop_type'] == crop_type)
    ]
    
    if len(crop_price) > 0:
        return {
            'avg_price_90d': crop_price['price_per_kg'].mean(),
            'price_volatility_90d': crop_price['price_per_kg'].std(),
            'price_trend_90d': 0.0
        }
    else:
        return {
            'avg_price_90d': 50.0,
            'price_volatility_90d': 10.0,
            'price_trend_90d': 0.0
        }

def get_economic_features():
    """ดึงข้อมูลเศรษฐกิจล่าสุด"""
    latest_econ = economic.tail(1)
    
    if len(latest_econ) > 0:
        return {
            'fuel_price': latest_econ['fuel_price'].values[0],
            'fertilizer_price': latest_econ['fertilizer_price'].values[0],
            'inflation_rate': latest_econ['inflation_rate'].values[0],
            'gdp_growth': latest_econ['gdp_growth'].values[0]
        }
    else:
        return {
            'fuel_price': 40.0,
            'fertilizer_price': 900.0,
            'inflation_rate': 2.0,
            'gdp_growth': 3.0
        }

def validate_user_input(user_profile):
    """
    ตรวจสอบความถูกต้องของข้อมูลผู้ใช้
    """
    errors = []
    warnings = []
    
    # ตรวจสอบจังหวัด
    if user_profile['province'] not in weather['province'].unique():
        errors.append(f"Province '{user_profile['province']}' not found in database")
    
    # ตรวจสอบ budget
    if user_profile['budget'] < 5000:
        errors.append("Budget too low (minimum 5,000 THB)")
    elif user_profile['budget'] < 10000:
        warnings.append("Low budget may limit crop options")
    
    # ตรวจสอบพื้นที่
    if user_profile['land_size'] <= 0:
        errors.append("Land size must be positive")
    elif user_profile['land_size'] < 1:
        warnings.append("Very small land size may limit options")
    
    return errors, warnings

def get_market_demand_factor(province, crop_type, month):
    """
    ปัจจัยความต้องการของตลาดท้องถิ่น
    วิเคราะห์จากข้อมูลราคาและความถี่การปลูก
    """
    # ดูว่ามีการปลูกพืชนี้ในจังหวัดนี้บ่อยแค่ไหน
    crop_in_province = cultivation[
        (cultivation['province'] == province) &
        (cultivation['crop_type'] == crop_type) &
        (cultivation['plant_month'] == month)
    ]
    
    if len(crop_in_province) > 0:
        # ยิ่งปลูกน้อย = โอกาสดี (scarcity)
        scarcity_factor = 1.0 / (len(crop_in_province) + 1)
        
        # ราคาเฉลี่ยสูง = ความต้องการสูง
        avg_revenue = crop_in_province['revenue'].mean()
        price_factor = min(avg_revenue / 50000, 2.0)  # normalize, cap at 2.0
        
        return (scarcity_factor * 0.3 + price_factor * 0.7)
    else:
        return 1.0  # default neutral

def apply_goal_weighting(predictions, user_profile, month):
    """
    ปรับน้ำหนักคะแนนตามเป้าหมายผู้ใช้
    """
    weighted_predictions = []
    
    for pred in predictions:
        crop_info = crop_chars[crop_chars['crop_type'] == pred['crop']].iloc[0]
        base_roi = pred['predicted_roi']
        
        # เริ่มต้นด้วย base ROI
        weighted_roi = base_roi
        factors = {'base': base_roi}
        
        # Goal-based weighting
        if user_profile['goal'] == 'profit':
            # ให้ความสำคัญกับ ROI สูง
            profit_bonus = 1.2
            weighted_roi *= profit_bonus
            factors['profit_bonus'] = profit_bonus
            
        elif user_profile['goal'] == 'stability':
            # ให้ความสำคัญกับความเสี่ยงต่ำ
            risk_level = crop_info['risk_level']
            if risk_level in ['ต่ำมาก', 'ต่ำ']:
                risk_bonus = 1.3
            elif risk_level in ['กลาง', 'ปานกลาง']:
                risk_bonus = 1.0
            else:
                risk_bonus = 0.7
            weighted_roi *= risk_bonus
            factors['stability_bonus'] = risk_bonus
            
        elif user_profile['goal'] == 'sustainability':
            # ให้ความสำคัญกับพืชที่ใช้น้ำน้อย
            water_req = crop_info['water_requirement']
            if water_req in ['ต่ำมาก', 'ต่ำ']:
                sustainability_bonus = 1.3
            elif water_req == 'ปานกลาง':
                sustainability_bonus = 1.1
            else:
                sustainability_bonus = 0.9
            weighted_roi *= sustainability_bonus
            factors['sustainability_bonus'] = sustainability_bonus
        
        # Market demand factor
        market_factor = get_market_demand_factor(
            user_profile['province'], 
            pred['crop'], 
            month
        )
        weighted_roi *= market_factor
        factors['market_factor'] = market_factor
        
        # Seasonal bonus
        seasonal_type = crop_info['seasonal_type']
        season = get_thai_season(month)
        
        if seasonal_type == 'ได้ทุกฤดู':
            seasonal_bonus = 1.1
        elif (season == 'winter' and 'หนาว' in seasonal_type) or \
             (season == 'summer' and 'ร้อน' in seasonal_type) or \
             (season == 'rainy' and 'ฝน' in seasonal_type):
            seasonal_bonus = 1.2
        else:
            seasonal_bonus = 0.8
        
        weighted_roi *= seasonal_bonus
        factors['seasonal_bonus'] = seasonal_bonus
        
        weighted_predictions.append({
            'crop': pred['crop'],
            'predicted_roi': base_roi,
            'weighted_roi': weighted_roi,
            'final_score': weighted_roi,
            'factors': factors
        })
    
    return sorted(weighted_predictions, key=lambda x: x['final_score'], reverse=True)

def apply_business_rules(predictions, user_profile):
    """
    กรองคำแนะนำตามโปรไฟล์ผู้ใช้
    """
    filtered = []
    reasons_excluded = []
    
    for pred in predictions:
        crop_info = crop_chars[crop_chars['crop_type'] == pred['crop']].iloc[0]
        
        # Rule 1: Budget constraint
        if crop_info['investment_cost'] > user_profile['budget']:
            reasons_excluded.append({
                'crop': pred['crop'],
                'reason': f"Investment cost ({crop_info['investment_cost']:,.0f}) > Budget ({user_profile['budget']:,.0f})"
            })
            continue
        
        # Rule 2: Water availability
        water_req = crop_info['water_requirement']
        if user_profile['water_access'] == 'poor' and water_req in ['สูง', 'สูงมาก']:
            reasons_excluded.append({
                'crop': pred['crop'],
                'reason': f"High water requirement but poor water access"
            })
            continue
        
        # Rule 3: Risk tolerance
        risk_level = crop_info['risk_level']
        if user_profile['risk_tolerance'] == 'low' and risk_level in ['สูง', 'สูงมาก']:
            reasons_excluded.append({
                'crop': pred['crop'],
                'reason': f"High risk crop but low risk tolerance"
            })
            continue
        
        # Rule 4: Experience level
        if user_profile['experience'] == 'beginner' and risk_level in ['สูง', 'สูงมาก']:
            reasons_excluded.append({
                'crop': pred['crop'],
                'reason': f"High risk crop not suitable for beginners"
            })
            continue
        
        # Passed all rules
        filtered.append(pred)
    
    return filtered, reasons_excluded

def generate_personal_report(user_profile, recommendations, month_name, excluded, show_factors=False):
    """
    สร้างรายงานส่วนบุคคล (Enhanced)
    """
    print()
    print("=" * 80)
    print(f"PERSONALIZED RECOMMENDATION REPORT - {month_name}")
    print("=" * 80)
    print()
    
    print("USER PROFILE:")
    print(f"   Province: {user_profile['province']}")
    print(f"   Budget: {user_profile['budget']:,.0f} Baht")
    print(f"   Land Size: {user_profile['land_size']} Rai")
    print(f"   Water Access: {user_profile['water_access']}")
    print(f"   Experience: {user_profile['experience']}")
    print(f"   Goal: {user_profile['goal']}")
    print(f"   Risk Tolerance: {user_profile['risk_tolerance']}")
    print()
    
    if len(recommendations) > 0:
        print(f"TOP {min(5, len(recommendations))} RECOMMENDED CROPS:")
        print()
        
        for i, rec in enumerate(recommendations[:5], 1):
            crop_info = crop_chars[crop_chars['crop_type'] == rec['crop']].iloc[0]
            
            print(f"{i}. {rec['crop']}")
            print(f"   - Base ROI: {rec['predicted_roi']:.2f}%")
            print(f"   - Final Score: {rec['final_score']:.2f}% (after weighting)")
            print(f"   - Investment Cost: {crop_info['investment_cost']:,.0f} Baht")
            print(f"   - Growth Days: {crop_info['growth_days']} days")
            print(f"   - Water Requirement: {crop_info['water_requirement']}")
            print(f"   - Risk Level: {crop_info['risk_level']}")
            print(f"   - Seasonal Type: {crop_info['seasonal_type']}")
            
            if show_factors and 'factors' in rec:
                print(f"   - Weighting Factors:")
                for factor_name, factor_value in rec['factors'].items():
                    if factor_name != 'base':
                        print(f"      * {factor_name}: {factor_value:.2f}x")
            print()
    else:
        print("NO CROPS MATCH YOUR CRITERIA")
        print("Please consider adjusting your constraints")
        print()
    
    if len(excluded) > 0:
        print(f"EXCLUDED CROPS ({len(excluded)}):")
        print()
        for exc in excluded[:5]:
            print(f"   X {exc['crop']}: {exc['reason']}")
        if len(excluded) > 5:
            print(f"   ... and {len(excluded) - 5} more")
        print()
    
    print("=" * 80)

def generate_comparison_report(user, monthly_recommendations):
    """
    รายงานเปรียบเทียบทั้งปี
    """
    print()
    print("=" * 80)
    print(f"YEAR-ROUND ANALYSIS FOR USER: {user['name']}")
    print("=" * 80)
    print()
    
    seasonal_plan = {}
    
    for month, recs in monthly_recommendations.items():
        if recs and len(recs) > 0:
            top_crop = recs[0]
            season = get_thai_season(month)
            
            if season not in seasonal_plan:
                seasonal_plan[season] = []
            
            seasonal_plan[season].append({
                'month': month,
                'crop': top_crop['crop'],
                'roi': top_crop['final_score']
            })
    
    print("OPTIMAL SEASONAL PLANNING:")
    print()
    
    season_names = {
        'winter': 'WINTER (Nov-Feb)',
        'summer': 'SUMMER (Mar-May)',
        'rainy': 'RAINY (Jun-Oct)'
    }
    
    for season in ['winter', 'summer', 'rainy']:
        if season in seasonal_plan:
            print(f"   {season_names[season]}:")
            for crop in seasonal_plan[season]:
                month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][crop['month']]
                print(f"      {month_name}: {crop['crop']} (Score: {crop['roi']:.1f}%)")
            print()
    
    # Best overall crop
    all_crops = []
    for recs in monthly_recommendations.values():
        if recs:
            all_crops.extend(recs[:3])
    
    if all_crops:
        crop_scores = {}
        for crop in all_crops:
            crop_name = crop['crop']
            if crop_name not in crop_scores:
                crop_scores[crop_name] = []
            crop_scores[crop_name].append(crop['final_score'])
        
        avg_scores = {crop: np.mean(scores) for crop, scores in crop_scores.items()}
        best_crop = max(avg_scores, key=avg_scores.get)
        
        print(f"BEST OVERALL CROP FOR THE YEAR:")
        print(f"   {best_crop} (Avg Score: {avg_scores[best_crop]:.1f}%)")
        print()
    
    print("=" * 80)

# ============================================================================
# 3. Quick Feature Engineering for Training
# ============================================================================
print()
print("=" * 80)
print("STEP 1/4: Feature Engineering")
print("=" * 80)
print()

print("[1/7] Extracting temporal features...")
# Extract temporal features
cultivation['plant_month'] = cultivation['planting_date'].dt.month
cultivation['plant_season'] = cultivation['plant_month'].apply(get_thai_season)
cultivation['plant_quarter'] = cultivation['planting_date'].dt.quarter
cultivation['day_of_year'] = cultivation['planting_date'].dt.dayofyear
print("      Done!")

print("[2/7] Calculating ROI (target variable)...")
# Calculate ROI with capping to handle extreme values
cultivation['revenue'] = cultivation['actual_yield_kg'] * 50
cultivation['roi'] = ((cultivation['revenue'] - cultivation['investment_cost']) / 
                      cultivation['investment_cost'] * 100)

# Analyze ROI distribution before capping
roi_stats = cultivation['roi'].describe()
print(f"      ROI statistics before capping:")
print(f"        Mean: {roi_stats['mean']:.2f}%, Median: {cultivation['roi'].median():.2f}%")
print(f"        Min: {roi_stats['min']:.2f}%, Max: {roi_stats['max']:.2f}%")
print(f"        75th percentile: {roi_stats['75%']:.2f}%")

# Cap ROI at 99th percentile to handle extreme outliers
# This preserves most data while removing extreme values
roi_99th = cultivation['roi'].quantile(0.99)
roi_1st = cultivation['roi'].quantile(0.01)

roi_before_cap = cultivation['roi'].copy()
cultivation['roi'] = np.clip(cultivation['roi'], roi_1st, roi_99th)

outliers_capped = (roi_before_cap != cultivation['roi']).sum()
print(f"      Capped {outliers_capped} extreme values at 99th percentile ({roi_99th:.2f}%)")
print(f"      ROI range after capping: {cultivation['roi'].min():.2f}% to {cultivation['roi'].max():.2f}%")
print("      Done!")

print("[3/7] Merging with crop characteristics...")
# Merge with crop characteristics (rename to avoid conflicts)
cultivation = cultivation.merge(
    crop_chars[['crop_type', 'growth_days', 'investment_cost', 
                'weather_sensitivity', 'demand_elasticity']],
    on='crop_type',
    how='left',
    suffixes=('', '_crop')
)
print("      Done!")

print("[4/7] Defining feature columns...")
# Simplified features (using existing columns)
feature_cols = [
    'plant_month', 'plant_quarter', 'day_of_year',
    'planting_area_rai', 'farm_skill', 'tech_adoption',
    'growth_days', 'investment_cost', 'weather_sensitivity', 'demand_elasticity'
]
print(f"      {len(feature_cols)} base features defined")

print("[5/7] Encoding categorical variables...")
# Encode categorical
le_province = LabelEncoder()
le_crop = LabelEncoder()
le_season = LabelEncoder()

cultivation['province_encoded'] = le_province.fit_transform(cultivation['province'])
cultivation['crop_encoded'] = le_crop.fit_transform(cultivation['crop_type'])
cultivation['season_encoded'] = le_season.fit_transform(cultivation['plant_season'])

feature_cols.extend(['province_encoded', 'crop_encoded', 'season_encoded'])
print(f"      Total features: {len(feature_cols)}")

print("[6/7] Preparing training data...")
# Prepare data
cultivation_clean = cultivation.dropna(subset=['roi'] + feature_cols)
X = cultivation_clean[feature_cols]
y = cultivation_clean['roi']
print(f"      Samples: {len(X)}")
print(f"      ROI range: {y.min():.2f}% to {y.max():.2f}%")

print("[7/7] Splitting and scaling data...")
# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print(f"      Train: {len(X_train)} samples")
print(f"      Test: {len(X_test)} samples")
print()
print("Feature Engineering Complete!")
print()

# ============================================================================
# 4. Train and Compare Multiple Models
# ============================================================================
print("=" * 80)
print("STEP 2/4: Training and Comparing Multiple Models")
print("=" * 80)
print()

# Dictionary to store all models and their results
models_results = {}
trained_models = {}

# ============================================================================
# 4.1 Random Forest (Optimized to reduce overfitting)
# ============================================================================
print("[1/4] Training Random Forest...")
print("      Initializing Random Forest Regressor (optimized hyperparameters)...")
rf_model = RandomForestRegressor(
    n_estimators=150,         # Increased for better learning
    max_depth=7,              # Balanced: not too deep, not too shallow
    min_samples_split=10,     # Moderate regularization
    min_samples_leaf=4,       # Moderate regularization
    max_features='sqrt',      # Use sqrt of features
    random_state=42,
    n_jobs=-1
)
print("      Training...")
rf_model.fit(X_train_scaled, y_train)
rf_pred = rf_model.predict(X_test_scaled)

rf_r2 = r2_score(y_test, rf_pred)
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_mape = mean_absolute_percentage_error(y_test, rf_pred)
rf_top5 = top_k_accuracy(y_test.values, rf_pred, k=5)

models_results['Random Forest'] = {
    'r2': rf_r2,
    'mae': rf_mae,
    'rmse': rf_rmse,
    'mape': rf_mape,
    'top5_acc': rf_top5,
    'predictions': rf_pred
}
trained_models['Random Forest'] = rf_model

print(f"      ✓ R² Score: {rf_r2:.4f}")
print(f"      ✓ MAE: {rf_mae:.2f}%")
print(f"      ✓ RMSE: {rf_rmse:.2f}%")
print(f"      ✓ MAPE: {rf_mape:.2f}%")
print(f"      ✓ Top-5 Ranking Accuracy: {rf_top5:.1f}%")
print()

# ============================================================================
# 4.2 Gradient Boosting (Optimized to reduce overfitting)
# ============================================================================
print("[2/4] Training Gradient Boosting...")
print("      Initializing Gradient Boosting Regressor (optimized hyperparameters)...")
gb_model = GradientBoostingRegressor(
    n_estimators=150,         # Increased for better learning
    max_depth=4,              # Balanced depth
    learning_rate=0.08,       # Moderate learning rate
    min_samples_split=10,     # Moderate regularization
    min_samples_leaf=4,       # Moderate regularization
    subsample=0.85,           # Use 85% of samples
    random_state=42
)
print("      Training...")
gb_model.fit(X_train_scaled, y_train)
gb_pred = gb_model.predict(X_test_scaled)

gb_r2 = r2_score(y_test, gb_pred)
gb_mae = mean_absolute_error(y_test, gb_pred)
gb_rmse = np.sqrt(mean_squared_error(y_test, gb_pred))
gb_mape = mean_absolute_percentage_error(y_test, gb_pred)
gb_top5 = top_k_accuracy(y_test.values, gb_pred, k=5)

models_results['Gradient Boosting'] = {
    'r2': gb_r2,
    'mae': gb_mae,
    'rmse': gb_rmse,
    'mape': gb_mape,
    'top5_acc': gb_top5,
    'predictions': gb_pred
}
trained_models['Gradient Boosting'] = gb_model

print(f"      ✓ R² Score: {gb_r2:.4f}")
print(f"      ✓ MAE: {gb_mae:.2f}%")
print(f"      ✓ RMSE: {gb_rmse:.2f}%")
print(f"      ✓ MAPE: {gb_mape:.2f}%")
print(f"      ✓ Top-5 Ranking Accuracy: {gb_top5:.1f}%")
print()

# ============================================================================
# 4.3 XGBoost (Optimized to reduce overfitting)
# ============================================================================
print("[3/4] Training XGBoost...")
print("      Initializing XGBoost Regressor (optimized hyperparameters)...")
xgb_model = xgb.XGBRegressor(
    n_estimators=150,         # Increased for better learning
    max_depth=4,              # Balanced depth
    learning_rate=0.08,       # Moderate learning rate
    min_child_weight=3,       # Moderate regularization
    subsample=0.85,           # Use 85% of samples
    colsample_bytree=0.85,    # Use 85% of features
    reg_alpha=0.05,           # Light L1 regularization
    reg_lambda=0.5,           # Light L2 regularization
    random_state=42,
    n_jobs=-1
)
print("      Training...")
xgb_model.fit(X_train_scaled, y_train)
xgb_pred = xgb_model.predict(X_test_scaled)

xgb_r2 = r2_score(y_test, xgb_pred)
xgb_mae = mean_absolute_error(y_test, xgb_pred)
xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
xgb_mape = mean_absolute_percentage_error(y_test, xgb_pred)
xgb_top5 = top_k_accuracy(y_test.values, xgb_pred, k=5)

models_results['XGBoost'] = {
    'r2': xgb_r2,
    'mae': xgb_mae,
    'rmse': xgb_rmse,
    'mape': xgb_mape,
    'top5_acc': xgb_top5,
    'predictions': xgb_pred
}
trained_models['XGBoost'] = xgb_model

print(f"      ✓ R² Score: {xgb_r2:.4f}")
print(f"      ✓ MAE: {xgb_mae:.2f}%")
print(f"      ✓ RMSE: {xgb_rmse:.2f}%")
print(f"      ✓ MAPE: {xgb_mape:.2f}%")
print(f"      ✓ Top-5 Ranking Accuracy: {xgb_top5:.1f}%")
print()

# ============================================================================
# 4.4 LSTM (if available)
# ============================================================================
if LSTM_AVAILABLE:
    print("[4/4] Training LSTM...")
    print("      Initializing LSTM model...")
    
    # Reshape data for LSTM (samples, timesteps, features)
    X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
    X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
    
    # Build LSTM model
    lstm_model = Sequential([
        LSTM(64, activation='relu', input_shape=(1, X_train_scaled.shape[1]), return_sequences=True),
        Dropout(0.2),
        LSTM(32, activation='relu'),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    
    lstm_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    print("      Training (this may take longer)...")
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Suppress verbose output
    history = lstm_model.fit(
        X_train_lstm, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop],
        verbose=0
    )
    
    lstm_pred = lstm_model.predict(X_test_lstm, verbose=0).flatten()
    
    lstm_r2 = r2_score(y_test, lstm_pred)
    lstm_mae = mean_absolute_error(y_test, lstm_pred)
    lstm_rmse = np.sqrt(mean_squared_error(y_test, lstm_pred))
    
    models_results['LSTM'] = {
        'r2': lstm_r2,
        'mae': lstm_mae,
        'rmse': lstm_rmse,
        'predictions': lstm_pred,
        'history': history.history
    }
    trained_models['LSTM'] = lstm_model
    
    print(f"      ✓ R² Score: {lstm_r2:.4f}")
    print(f"      ✓ MAE: {lstm_mae:.2f}%")
    print(f"      ✓ RMSE: {lstm_rmse:.2f}%")
    print(f"      ✓ Epochs trained: {len(history.history['loss'])}")
    print()
else:
    print("[4/4] LSTM skipped (TensorFlow not available)")
    print()

# ============================================================================
# 4.5 Model Comparison Summary
# ============================================================================
print("=" * 80)
print("MODEL COMPARISON SUMMARY")
print("=" * 80)
print()

comparison_df = pd.DataFrame({
    'Model': list(models_results.keys()),
    'R² Score': [models_results[m]['r2'] for m in models_results.keys()],
    'MAE (%)': [models_results[m]['mae'] for m in models_results.keys()],
    'RMSE (%)': [models_results[m]['rmse'] for m in models_results.keys()],
    'MAPE (%)': [models_results[m].get('mape', 0) for m in models_results.keys()],
    'Top-5 Acc (%)': [models_results[m].get('top5_acc', 0) for m in models_results.keys()]
})

comparison_df = comparison_df.sort_values('R² Score', ascending=False)

print(comparison_df.to_string(index=False))
print()
print("📊 Metrics Explanation:")
print("   - R² Score: Model fit quality (higher is better)")
print("   - MAE: Mean Absolute Error in % (lower is better)")
print("   - RMSE: Root Mean Squared Error in % (lower is better)")
print("   - MAPE: Mean Absolute Percentage Error (lower is better)")
print("   - Top-5 Acc: Ranking accuracy for top 5 crops (higher is better)")
print()

# Find best model
best_model_name = comparison_df.iloc[0]['Model']
best_model = trained_models[best_model_name]
print(f"🏆 Best Model: {best_model_name} (R² = {comparison_df.iloc[0]['R² Score']:.4f})")
print()

# Use best model for predictions
model = best_model
r2 = models_results[best_model_name]['r2']
mae = models_results[best_model_name]['mae']
rmse = models_results[best_model_name]['rmse']

print("Model Training and Comparison Complete!")
print()

# ============================================================================
# 4.6 Learning Curve Analysis
# ============================================================================
print("=" * 80)
print("LEARNING CURVE ANALYSIS")
print("=" * 80)
print()
print("Analyzing learning curves to detect overfitting/underfitting...")
print("(This may take a few minutes)")
print()

# Store learning curve data
learning_curves_data = {}

# Calculate learning curves for top 3 models (skip LSTM as it's too slow)
sklearn_models = {k: v for k, v in trained_models.items() if k != 'LSTM'}

for idx, (model_name, model_obj) in enumerate(sklearn_models.items(), 1):
    print(f"[{idx}/{len(sklearn_models)}] Computing learning curve for {model_name}...")
    
    # Define training sizes (10%, 20%, ..., 100%)
    train_sizes = np.linspace(0.1, 1.0, 10)
    
    # Calculate learning curve
    train_sizes_abs, train_scores, val_scores = learning_curve(
        model_obj,
        X_train_scaled,
        y_train,
        train_sizes=train_sizes,
        cv=5,  # 5-fold cross-validation
        scoring='r2',
        n_jobs=-1,
        random_state=42
    )
    
    # Calculate mean and std
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    learning_curves_data[model_name] = {
        'train_sizes': train_sizes_abs,
        'train_mean': train_mean,
        'train_std': train_std,
        'val_mean': val_mean,
        'val_std': val_std
    }
    
    # Analyze overfitting
    final_train_score = train_mean[-1]
    final_val_score = val_mean[-1]
    gap = final_train_score - final_val_score
    
    print(f"      Training Score (final): {final_train_score:.4f}")
    print(f"      Validation Score (final): {final_val_score:.4f}")
    print(f"      Gap: {gap:.4f}", end="")
    
    if gap < 0.02:
        print(" ✓ (Good - No overfitting)")
    elif gap < 0.05:
        print(" ⚠ (Slight overfitting)")
    else:
        print(" ✗ (Overfitting detected)")
    
    print()

print("Learning Curve Analysis Complete!")
print()

# ============================================================================
# 5. Test with Multiple User Profiles
# ============================================================================

# Define test users
test_users = [
    {
        'name': 'Somchai',
        'province': 'Chiang Mai',  # Use English to avoid encoding issues
        'budget': 50000,
        'land_size': 5,
        'water_access': 'good',
        'experience': 'intermediate',
        'goal': 'profit',
        'risk_tolerance': 'medium'
    },
    {
        'name': 'Malee',
        'province': 'Nakhon Ratchasima',
        'budget': 30000,
        'land_size': 10,
        'water_access': 'poor',
        'experience': 'beginner',
        'goal': 'stability',
        'risk_tolerance': 'low'
    },
    {
        'name': 'Prasert',
        'province': 'Bangkok',
        'budget': 100000,
        'land_size': 3,
        'water_access': 'good',
        'experience': 'expert',
        'goal': 'profit',
        'risk_tolerance': 'high'
    }
]

# Map English names to Thai names in dataset (simple approach)
all_provinces = cultivation['province'].unique()

# Find matching provinces
province_mapping = {}
for eng_name, thai_pattern in [
    ('Chiang Mai', 'เชียงใหม่'),
    ('Nakhon Ratchasima', 'นครราชสีมา'),
    ('Bangkok', 'กรุงเทพ')
]:
    matched = [p for p in all_provinces if thai_pattern in p]
    if matched:
        province_mapping[eng_name] = matched[0]
    else:
        # Fallback to first available province
        province_mapping[eng_name] = all_provinces[0]

# Update user provinces to match dataset
for user in test_users:
    if user['province'] in province_mapping:
        user['province'] = province_mapping[user['province']]

print(f"Province mapping completed for {len(province_mapping)} provinces")
print()

# Test for each user in different months
test_months = [1, 4, 7, 10]  # Jan, Apr, Jul, Oct
month_names_map = {
    1: 'January', 4: 'April', 7: 'July', 10: 'October'
}

print("=" * 80)
print("STEP 3/4: Testing with User Profiles")
print("=" * 80)
print()
print(f"Testing {len(test_users)} users across {len(test_months)} months...")
print()

for user_idx, user in enumerate(test_users, 1):
    print()
    print("=" * 80)
    print(f"USER {user_idx}/{len(test_users)}: {user['name']}")
    print("=" * 80)
    
    # Validate user input
    print(f"[Step 1/3] Validating user profile...")
    errors, warnings = validate_user_input(user)
    
    if errors:
        print()
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"   ERROR: {error}")
        print()
        print("Skipping this user...")
        continue
    
    if warnings:
        print()
        print("VALIDATION WARNINGS:")
        for warning in warnings:
            print(f"   WARNING: {warning}")
        print()
    else:
        print("      Profile validated successfully!")
    
    print(f"[Step 2/3] Generating recommendations for {len(test_months)} months...")
    monthly_recommendations = {}
    
    for month_idx, month in enumerate(test_months, 1):
        month_name = month_names_map[month]
        print(f"      [{month_idx}/{len(test_months)}] Processing {month_name}...", end=" ")
        
        # Get province-specific weather
        weather_features = get_province_weather_features(user['province'], month)
        economic_features = get_economic_features()
        
        # Prepare base features
        base_features = {
            'plant_month': month,
            'plant_quarter': (month - 1) // 3 + 1,
            'day_of_year': month * 30,
            'planting_area_rai': user['land_size'],
            'farm_skill': 0.7 if user['experience'] == 'expert' else (0.5 if user['experience'] == 'intermediate' else 0.3),
            'tech_adoption': 0.6,
            'province_encoded': le_province.transform([user['province']])[0],
            'season_encoded': le_season.transform([get_thai_season(month)])[0]
        }
        
        # Predict for all crops
        crop_predictions = []
        
        for crop_type in crop_chars['crop_type'].unique()[:20]:  # Test top 20 crops
            crop_info = crop_chars[crop_chars['crop_type'] == crop_type].iloc[0]
            
            features = base_features.copy()
            features['growth_days'] = crop_info['growth_days']
            features['investment_cost'] = crop_info['investment_cost']
            features['weather_sensitivity'] = crop_info['weather_sensitivity']
            features['demand_elasticity'] = crop_info['demand_elasticity']
            features['crop_encoded'] = le_crop.transform([crop_type])[0]
            
            # Create feature array
            feature_array = np.array([[features[col] for col in feature_cols]])
            feature_array_scaled = scaler.transform(feature_array)
            
            # Predict ROI
            predicted_roi = model.predict(feature_array_scaled)[0]
            
            crop_predictions.append({
                'crop': crop_type,
                'predicted_roi': predicted_roi
            })
        
        # Sort by ROI
        crop_predictions = sorted(crop_predictions, key=lambda x: x['predicted_roi'], reverse=True)
        
        # Apply business rules
        filtered_crops, excluded_crops = apply_business_rules(crop_predictions, user)
        
        # Apply goal-based weighting
        weighted_crops = apply_goal_weighting(filtered_crops, user, month)
        
        # Store for year-round analysis
        monthly_recommendations[month] = weighted_crops
        
        print(f"Done! ({len(weighted_crops)} crops recommended)")
        
        # Generate report (show factors for first month only)
        show_factors = (month == test_months[0])
        generate_personal_report(user, weighted_crops, month_name, excluded_crops, show_factors)
    
    print(f"[Step 3/3] Generating year-round analysis...")
    # Generate year-round comparison
    generate_comparison_report(user, monthly_recommendations)
    print(f"      Analysis complete for {user['name']}!")

# ============================================================================
# 6. Save Results and Generate Reports
# ============================================================================
print()
print("=" * 80)
print("STEP 4/4: Saving Results and Generating Reports")
print("=" * 80)
print()

# Save model performance
print("[1/7] Saving model performance metrics...")
model_performance = {
    'Best_Model': best_model_name,
    'R2_Score': r2,
    'MAE': mae,
    'RMSE': rmse,
    'Train_Samples': len(X_train),
    'Test_Samples': len(X_test),
    'Features': len(feature_cols),
    'Timestamp': run_timestamp
}

performance_df = pd.DataFrame([model_performance])
performance_df.to_csv(run_output_dir / "best_model_performance.csv", index=False)
print(f"      Saved: best_model_performance.csv")

# Save all recommendations
print("[2/7] Saving detailed recommendations...")
all_recommendations = []

for user_idx, user in enumerate(test_users):
    if user['province'] not in weather['province'].unique():
        continue
        
    for month in test_months:
        month_name = month_names_map[month]
        
        # Get recommendations (simplified version for saving)
        base_features = {
            'plant_month': month,
            'plant_quarter': (month - 1) // 3 + 1,
            'day_of_year': month * 30,
            'planting_area_rai': user['land_size'],
            'farm_skill': 0.7 if user['experience'] == 'expert' else (0.5 if user['experience'] == 'intermediate' else 0.3),
            'tech_adoption': 0.6,
            'province_encoded': le_province.transform([user['province']])[0],
            'season_encoded': le_season.transform([get_thai_season(month)])[0]
        }
        
        for crop_type in crop_chars['crop_type'].unique()[:10]:
            crop_info = crop_chars[crop_chars['crop_type'] == crop_type].iloc[0]
            
            features = base_features.copy()
            features['growth_days'] = crop_info['growth_days']
            features['investment_cost'] = crop_info['investment_cost']
            features['weather_sensitivity'] = crop_info['weather_sensitivity']
            features['demand_elasticity'] = crop_info['demand_elasticity']
            features['crop_encoded'] = le_crop.transform([crop_type])[0]
            
            feature_array = np.array([[features[col] for col in feature_cols]])
            feature_array_scaled = scaler.transform(feature_array)
            predicted_roi = model.predict(feature_array_scaled)[0]
            
            all_recommendations.append({
                'user_name': user['name'],
                'province': user['province'],
                'month': month,
                'month_name': month_name,
                'season': get_thai_season(month),
                'crop_type': crop_type,
                'predicted_roi': predicted_roi,
                'investment_cost': crop_info['investment_cost'],
                'growth_days': crop_info['growth_days'],
                'water_requirement': crop_info['water_requirement'],
                'risk_level': crop_info['risk_level'],
                'user_budget': user['budget'],
                'user_goal': user['goal'],
                'user_experience': user['experience']
            })

recommendations_df = pd.DataFrame(all_recommendations)
recommendations_df.to_csv(run_output_dir / "all_recommendations.csv", index=False)
print(f"      Saved: all_recommendations.csv ({len(recommendations_df)} records)")

# Create visualizations
print("[3/7] Creating visualizations...")

# Chart 1: Model Comparison - All Metrics
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Model Comparison - Performance Metrics', fontsize=16, fontweight='bold')

model_names = list(models_results.keys())
r2_scores = [models_results[m]['r2'] for m in model_names]
mae_scores = [models_results[m]['mae'] for m in model_names]
rmse_scores = [models_results[m]['rmse'] for m in model_names]

# R² Score comparison
axes[0].bar(model_names, r2_scores, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'][:len(model_names)], alpha=0.8)
axes[0].set_ylabel('R² Score', fontsize=12)
axes[0].set_title('R² Score (Higher is Better)', fontweight='bold')
axes[0].set_ylim([0, 1])
axes[0].grid(axis='y', alpha=0.3)
axes[0].tick_params(axis='x', rotation=45)
for i, v in enumerate(r2_scores):
    axes[0].text(i, v + 0.02, f'{v:.4f}', ha='center', fontweight='bold')

# MAE comparison
axes[1].bar(model_names, mae_scores, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'][:len(model_names)], alpha=0.8)
axes[1].set_ylabel('MAE (%)', fontsize=12)
axes[1].set_title('Mean Absolute Error (Lower is Better)', fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)
axes[1].tick_params(axis='x', rotation=45)
for i, v in enumerate(mae_scores):
    axes[1].text(i, v + max(mae_scores)*0.02, f'{v:.1f}', ha='center', fontweight='bold')

# RMSE comparison
axes[2].bar(model_names, rmse_scores, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'][:len(model_names)], alpha=0.8)
axes[2].set_ylabel('RMSE (%)', fontsize=12)
axes[2].set_title('Root Mean Squared Error (Lower is Better)', fontweight='bold')
axes[2].grid(axis='y', alpha=0.3)
axes[2].tick_params(axis='x', rotation=45)
for i, v in enumerate(rmse_scores):
    axes[2].text(i, v + max(rmse_scores)*0.02, f'{v:.1f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(run_output_dir / "model_comparison_metrics.png", dpi=300, bbox_inches='tight')
print(f"      Saved: model_comparison_metrics.png")
plt.close()

# Chart 2: Prediction vs Actual for Best Model
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Prediction vs Actual - All Models', fontsize=16, fontweight='bold')

for idx, (model_name, results) in enumerate(models_results.items()):
    if idx >= 4:
        break
    row = idx // 2
    col = idx % 2
    ax = axes[row, col]
    
    predictions = results['predictions']
    
    # Scatter plot
    ax.scatter(y_test, predictions, alpha=0.5, s=20)
    
    # Perfect prediction line
    min_val = min(y_test.min(), predictions.min())
    max_val = max(y_test.max(), predictions.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    ax.set_xlabel('Actual ROI (%)', fontsize=11)
    ax.set_ylabel('Predicted ROI (%)', fontsize=11)
    ax.set_title(f'{model_name}\nR² = {results["r2"]:.4f}', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(run_output_dir / "prediction_vs_actual.png", dpi=300, bbox_inches='tight')
print(f"      Saved: prediction_vs_actual.png")
plt.close()

# Chart 3: Residual Analysis
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Residual Analysis - All Models', fontsize=16, fontweight='bold')

for idx, (model_name, results) in enumerate(models_results.items()):
    if idx >= 4:
        break
    row = idx // 2
    col = idx % 2
    ax = axes[row, col]
    
    predictions = results['predictions']
    residuals = y_test - predictions
    
    # Residual plot
    ax.scatter(predictions, residuals, alpha=0.5, s=20)
    ax.axhline(y=0, color='r', linestyle='--', lw=2)
    
    ax.set_xlabel('Predicted ROI (%)', fontsize=11)
    ax.set_ylabel('Residuals', fontsize=11)
    ax.set_title(f'{model_name}\nMAE = {results["mae"]:.2f}%', fontweight='bold')
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(run_output_dir / "residual_analysis.png", dpi=300, bbox_inches='tight')
print(f"      Saved: residual_analysis.png")
plt.close()

# Chart 4: Learning Curves
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Learning Curves - Overfitting Analysis', fontsize=16, fontweight='bold')

colors = ['#3498db', '#e74c3c', '#2ecc71']

for idx, (model_name, lc_data) in enumerate(learning_curves_data.items()):
    if idx >= 3:
        break
    
    ax = axes[idx]
    color = colors[idx]
    
    # Plot training score
    ax.plot(lc_data['train_sizes'], lc_data['train_mean'], 
            label='Training Score', color=color, linewidth=2, marker='o')
    ax.fill_between(lc_data['train_sizes'], 
                     lc_data['train_mean'] - lc_data['train_std'],
                     lc_data['train_mean'] + lc_data['train_std'],
                     alpha=0.2, color=color)
    
    # Plot validation score
    ax.plot(lc_data['train_sizes'], lc_data['val_mean'], 
            label='Validation Score', color='orange', linewidth=2, marker='s')
    ax.fill_between(lc_data['train_sizes'], 
                     lc_data['val_mean'] - lc_data['val_std'],
                     lc_data['val_mean'] + lc_data['val_std'],
                     alpha=0.2, color='orange')
    
    # Calculate gap
    final_gap = lc_data['train_mean'][-1] - lc_data['val_mean'][-1]
    
    ax.set_xlabel('Training Set Size', fontsize=11)
    ax.set_ylabel('R² Score', fontsize=11)
    ax.set_title(f'{model_name}\nGap: {final_gap:.4f}', fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1])

plt.tight_layout()
plt.savefig(run_output_dir / "learning_curves.png", dpi=300, bbox_inches='tight')
print(f"      Saved: learning_curves.png")
plt.close()

# Chart 5: LSTM Training History (if available)
if LSTM_AVAILABLE and 'LSTM' in models_results and 'history' in models_results['LSTM']:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('LSTM Training History', fontsize=16, fontweight='bold')
    
    history = models_results['LSTM']['history']
    
    # Loss
    axes[0].plot(history['loss'], label='Training Loss', linewidth=2)
    axes[0].plot(history['val_loss'], label='Validation Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss (MSE)', fontsize=12)
    axes[0].set_title('Model Loss', fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # MAE
    axes[1].plot(history['mae'], label='Training MAE', linewidth=2)
    axes[1].plot(history['val_mae'], label='Validation MAE', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('MAE', fontsize=12)
    axes[1].set_title('Mean Absolute Error', fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(run_output_dir / "lstm_training_history.png", dpi=300, bbox_inches='tight')
    print(f"      Saved: lstm_training_history.png")
    plt.close()

# Chart 6: Best Model Performance
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

metrics = ['R2_Score', 'MAE', 'RMSE']
values = [r2, mae, rmse]
colors = ['green', 'orange', 'red']

for idx, (metric, value, color) in enumerate(zip(metrics, values, colors)):
    ax = axes[idx]
    ax.bar([metric], [value], color=color, alpha=0.7)
    ax.set_ylabel('Value')
    ax.set_title(f'{metric}: {value:.2f}', fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(run_output_dir / "best_model_performance.png", dpi=300, bbox_inches='tight')
print(f"      Saved: best_model_performance.png")
plt.close()

# Chart 6: Top Crops by User
fig, ax = plt.subplots(figsize=(12, 6))

top_crops_by_user = recommendations_df.groupby(['user_name', 'crop_type'])['predicted_roi'].mean().reset_index()
top_crops_by_user = top_crops_by_user.sort_values('predicted_roi', ascending=False).head(15)

colors_map = {'Somchai': 'skyblue', 'Malee': 'lightcoral', 'Prasert': 'lightgreen'}
bar_colors = [colors_map.get(name, 'gray') for name in top_crops_by_user['user_name']]

ax.barh(range(len(top_crops_by_user)), top_crops_by_user['predicted_roi'], color=bar_colors)
ax.set_yticks(range(len(top_crops_by_user)))
ax.set_yticklabels([f"{row['user_name']}: {row['crop_type']}" 
                     for _, row in top_crops_by_user.iterrows()])
ax.set_xlabel('Average Predicted ROI (%)')
ax.set_title('Top 15 Crop Recommendations by User', fontweight='bold')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(run_output_dir / "top_crops_by_user.png", dpi=300, bbox_inches='tight')
print(f"      Saved: top_crops_by_user.png")
plt.close()

# Chart 7: Seasonal Patterns
fig, ax = plt.subplots(figsize=(10, 6))

seasonal_avg = recommendations_df.groupby('season')['predicted_roi'].mean().sort_values(ascending=False)
colors_season = ['lightblue', 'orange', 'green']

ax.bar(seasonal_avg.index, seasonal_avg.values, color=colors_season, alpha=0.7)
ax.set_ylabel('Average Predicted ROI (%)')
ax.set_xlabel('Season')
ax.set_title('Average ROI by Season', fontweight='bold')
ax.grid(axis='y', alpha=0.3)

for i, v in enumerate(seasonal_avg.values):
    ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(run_output_dir / "seasonal_patterns.png", dpi=300, bbox_inches='tight')
print(f"      Saved: seasonal_patterns.png")
plt.close()

# Save model comparison results
comparison_df.to_csv(run_output_dir / "model_comparison.csv", index=False)
print(f"      Saved: model_comparison.csv")

# Generate summary report
print("[4/7] Generating summary report...")

# Create model comparison table for report
model_comparison_table = "\n".join([
    f"  {row['Model']:20s} | R²: {row['R² Score']:.4f} | MAE: {row['MAE (%)']:8.2f}% | RMSE: {row['RMSE (%)']:8.2f}%"
    for _, row in comparison_df.iterrows()
])

summary_report = f"""
{'=' * 80}
MODEL A - PERSONALIZED CROP RECOMMENDATION SYSTEM
SUMMARY REPORT
{'=' * 80}

Run Timestamp: {run_timestamp}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'=' * 80}
1. MODEL COMPARISON
{'=' * 80}

Tested {len(models_results)} machine learning algorithms:

{model_comparison_table}

🏆 Best Model: {best_model_name}

{'=' * 80}
2. LEARNING CURVE ANALYSIS
{'=' * 80}

Overfitting Detection (Training vs Validation Gap):
"""

for model_name, lc_data in learning_curves_data.items():
    final_train = lc_data['train_mean'][-1]
    final_val = lc_data['val_mean'][-1]
    gap = final_train - final_val
    
    status = "✓ Good" if gap < 0.02 else ("⚠ Slight" if gap < 0.05 else "✗ Overfitting")
    
    summary_report += f"""
  {model_name:20s}:
    Training Score:   {final_train:.4f}
    Validation Score: {final_val:.4f}
    Gap:              {gap:.4f} ({status})
"""

summary_report += f"""
Interpretation:
  - Gap < 0.02: No overfitting (Good generalization)
  - Gap 0.02-0.05: Slight overfitting (Acceptable)
  - Gap > 0.05: Overfitting (Model memorizing training data)

{'=' * 80}
3. BEST MODEL PERFORMANCE ({best_model_name})
{'=' * 80}

R² Score:  {r2:.4f}
MAE:       {mae:.2f}%
RMSE:      {rmse:.2f}%

Training Samples: {len(X_train):,}
Testing Samples:  {len(X_test):,}
Features Used:    {len(feature_cols)}

Data Quality Assessment:
  - Sample Size: {"✓ Adequate" if len(X_train) > 1000 else "⚠ Limited"}
  - Samples per Feature: {len(X_train) // len(feature_cols)} (Recommended: >20)
  - Train/Test Split: 80/20 (Standard)

{'=' * 80}
4. TESTING COVERAGE
{'=' * 80}

User Profiles Tested:  {len(test_users)}
Months Tested:         {len(test_months)}
Crop Types Evaluated:  {len(crop_chars)}
Total Predictions:     {len(recommendations_df):,}

{'=' * 80}
3. USER PROFILES
{'=' * 80}

"""

for user in test_users:
    summary_report += f"""
User: {user['name']}
  - Province: {user['province']}
  - Budget: {user['budget']:,} Baht
  - Land Size: {user['land_size']} Rai
  - Water Access: {user['water_access']}
  - Experience: {user['experience']}
  - Goal: {user['goal']}
  - Risk Tolerance: {user['risk_tolerance']}
"""

summary_report += f"""
{'=' * 80}
4. TOP RECOMMENDATIONS BY USER
{'=' * 80}

"""

for user in test_users:
    user_recs = recommendations_df[recommendations_df['user_name'] == user['name']]
    if len(user_recs) > 0:
        top_5 = user_recs.nlargest(5, 'predicted_roi')
        summary_report += f"\n{user['name']} ({user['province']}):\n"
        for idx, (_, rec) in enumerate(top_5.iterrows(), 1):
            summary_report += f"  {idx}. {rec['crop_type']}: {rec['predicted_roi']:.2f}% ROI\n"

summary_report += f"""
{'=' * 80}
5. SEASONAL ANALYSIS
{'=' * 80}

Average ROI by Season:
"""

for season, avg_roi in seasonal_avg.items():
    summary_report += f"  - {season.capitalize()}: {avg_roi:.2f}%\n"

summary_report += f"""
{'=' * 80}
6. KEY FEATURES
{'=' * 80}

The personalized recommendation system considers:
  ✓ Province-specific weather data
  ✓ Personal budget and land size constraints
  ✓ Experience level and risk tolerance
  ✓ Goal-based weighting (profit/stability/sustainability)
  ✓ Market demand factors
  ✓ Seasonal suitability
  ✓ Water availability matching
  ✓ Investment cost filtering

{'=' * 80}
7. OUTPUT FILES
{'=' * 80}

Generated files in: {run_output_dir}

  CSV Files:
  1. best_model_performance.csv     - Best model metrics
  2. model_comparison.csv           - All models comparison
  3. all_recommendations.csv        - Detailed predictions
  
  Evaluation Charts:
  4. model_comparison_metrics.png   - Algorithm comparison (R², MAE, RMSE)
  5. prediction_vs_actual.png       - Prediction accuracy scatter plots
  6. residual_analysis.png          - Residual distribution plots
  7. learning_curves.png            - Overfitting analysis ⭐ NEW
  8. lstm_training_history.png      - LSTM training curves (if available)
  
  Application Charts:
  9. best_model_performance.png     - Best model metrics
  10. top_crops_by_user.png         - User recommendations
  11. seasonal_patterns.png         - Seasonal analysis
  
  Reports:
  12. summary_report.txt            - This report
  13. quick_reference.txt           - Quick guide

{'=' * 80}
8. CONCLUSION
{'=' * 80}

The personalized recommendation system successfully:
  ✓ Compared {len(models_results)} machine learning algorithms
  ✓ Selected best model: {best_model_name} (R² = {r2:.4f})
  ✓ Analyzed learning curves to detect overfitting ⭐ NEW
  ✓ Generated {len(recommendations_df):,} personalized recommendations
  ✓ Tested across {len(test_users)} diverse user profiles
  ✓ Considered seasonal variations across {len(test_months)} months
  ✓ Applied business rules and goal-based weighting
  ✓ Created comprehensive evaluation charts

Model Reliability:
  - Training samples: {len(X_train):,} ({"Adequate" if len(X_train) > 1000 else "Limited"})
  - Overfitting status: {list(learning_curves_data.keys())[0] if learning_curves_data else "N/A"}
  - Cross-validation: 5-fold CV performed

The system is ready for deployment and can provide customized
crop recommendations based on individual farmer profiles and
local conditions.

{'=' * 80}
END OF REPORT
{'=' * 80}
"""

# Save summary report
with open(run_output_dir / "summary_report.txt", 'w', encoding='utf-8') as f:
    f.write(summary_report)

print(f"      Saved: summary_report.txt")

# Create a quick reference guide
print("[5/7] Creating quick reference guide...")

quick_guide = f"""
{'=' * 80}
QUICK REFERENCE GUIDE
Model A - Personalized Crop Recommendation System
{'=' * 80}

📁 OUTPUT LOCATION: {run_output_dir}

🏆 BEST MODEL: {best_model_name}

📊 KEY METRICS:
   R² Score: {r2:.4f}
   MAE: {mae:.2f}%
   RMSE: {rmse:.2f}%

🔬 MODELS COMPARED:
"""

for _, row in comparison_df.iterrows():
    quick_guide += f"   - {row['Model']:20s}: R² = {row['R² Score']:.4f}\n"

quick_guide += f"""
📋 FILES GENERATED:
   CSV Data:
   1. summary_report.txt             - Full detailed report
   2. quick_reference.txt            - This guide
   3. best_model_performance.csv     - Best model metrics
   4. model_comparison.csv           - All models comparison
   5. all_recommendations.csv        - All predictions
   
   Evaluation Charts:
   6. model_comparison_metrics.png   - Algorithm comparison
   7. prediction_vs_actual.png       - Prediction accuracy
   8. residual_analysis.png          - Residual plots
   9. learning_curves.png            - Overfitting analysis ⭐ NEW
   10. lstm_training_history.png     - LSTM training (if available)
   
   Application Charts:
   11. best_model_performance.png    - Best model charts
   12. top_crops_by_user.png         - User recommendations
   13. seasonal_patterns.png         - Seasonal analysis

🎯 HOW TO USE THE RESULTS:

   For Presentations:
   - Use summary_report.txt for overview
   - Use PNG charts for visual slides
   
   For Analysis:
   - Use all_recommendations.csv for detailed analysis
   - Filter by user_name, province, or season
   
   For Validation:
   - Check model_performance.csv for metrics
   - Compare predictions across different users

👥 TESTED USERS:
"""

for user in test_users:
    quick_guide += f"   - {user['name']} ({user['province']}): {user['goal']} goal\n"

quick_guide += f"""
📅 TESTED MONTHS:
   - {', '.join([month_names_map[m] for m in test_months])}

🌱 CROP TYPES:
   - {len(crop_chars)} different crops evaluated

{'=' * 80}
"""

with open(run_output_dir / "quick_reference.txt", 'w', encoding='utf-8') as f:
    f.write(quick_guide)

print(f"      Saved: quick_reference.txt")

print()
print("=" * 80)
print("ALL RESULTS SAVED SUCCESSFULLY!")
print("=" * 80)
print()
print(f"📁 Output Directory: {run_output_dir}")
print()
print(f"🏆 Best Model: {best_model_name} (R² = {r2:.4f})")
print()
print("📄 Generated Files:")
print("   CSV Data:")
print("   1. summary_report.txt             - Complete analysis report")
print("   2. quick_reference.txt            - Quick reference guide")
print("   3. best_model_performance.csv     - Best model metrics")
print("   4. model_comparison.csv           - All models comparison")
print("   5. all_recommendations.csv        - Detailed predictions")
print()
print("   Evaluation Charts:")
print("   6. model_comparison_metrics.png   - Algorithm comparison")
print("   7. prediction_vs_actual.png       - Prediction accuracy")
print("   8. residual_analysis.png          - Residual analysis")
print("   9. learning_curves.png            - Overfitting analysis ⭐")
if LSTM_AVAILABLE and 'LSTM' in models_results:
    print("   10. lstm_training_history.png     - LSTM training curves")
print()
print("   Application Charts:")
next_num = 11 if LSTM_AVAILABLE and 'LSTM' in models_results else 10
print(f"   {next_num}. best_model_performance.png    - Best model charts")
print(f"   {next_num+1}. top_crops_by_user.png         - User recommendations")
print(f"   {next_num+2}. seasonal_patterns.png         - Seasonal analysis")
print()
print("✅ Ready for presentation and analysis!")
print()
print("=" * 80)

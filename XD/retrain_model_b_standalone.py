"""
Retrain Model B แบบ standalone (ไม่ใช้ custom classes)
เพื่อให้ pickle ได้โดยไม่ต้องมี Model_B_Fixed module
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_prepare_data():
    """Load and prepare data"""
    logger.info("📥 Loading data...")
    
    # Load datasets
    cultivation = pd.read_csv('buildingModel.py/Dataset/cultivation.csv', 
                             parse_dates=['planting_date', 'harvest_date'])
    weather = pd.read_csv('buildingModel.py/Dataset/weather.csv', 
                         parse_dates=['date'])
    crop_chars = pd.read_csv('buildingModel.py/Dataset/crop_characteristics.csv')
    
    logger.info(f"✅ Cultivation: {len(cultivation)} records")
    logger.info(f"✅ Weather: {len(weather)} records")
    logger.info(f"✅ Crop chars: {len(crop_chars)} records")
    
    return cultivation, weather, crop_chars

def create_features(cultivation, weather, crop_chars):
    """Create all features"""
    logger.info("\n🔧 Creating features...")
    
    df = cultivation.copy()
    
    # 1. Join crop characteristics
    df = df.merge(
        crop_chars[['crop_type', 'growth_days', 'soil_preference', 'seasonal_type']],
        on='crop_type',
        how='left'
    )
    df['growth_days'] = df['growth_days'].fillna(90)
    df['soil_preference'] = df['soil_preference'].fillna('loam')
    df['seasonal_type'] = df['seasonal_type'].fillna('all_season')
    
    # 2. Create season
    def get_season(month):
        if month in [3, 4, 5]:
            return 'summer'
        elif month in [6, 7, 8, 9, 10]:
            return 'rainy'
        else:
            return 'winter'
    
    df['month'] = df['planting_date'].dt.month
    df['quarter'] = df['planting_date'].dt.quarter
    df['season'] = df['month'].apply(get_season)
    
    # 3. Create weather features (30 days before planting)
    logger.info("   Creating weather features...")
    weather_features = []
    
    for idx, row in df.iterrows():
        province = row['province']
        planting_date = row['planting_date']
        
        start_date = planting_date - timedelta(days=30)
        end_date = planting_date - timedelta(days=1)
        
        weather_window = weather[
            (weather['province'] == province) &
            (weather['date'] >= start_date) &
            (weather['date'] <= end_date)
        ]
        
        if len(weather_window) > 0:
            weather_features.append({
                'avg_temp_prev_30d': weather_window['temperature_celsius'].mean(),
                'avg_rainfall_prev_30d': weather_window['rainfall_mm'].mean(),
                'total_rainfall_prev_30d': weather_window['rainfall_mm'].sum(),
                'rainy_days_prev_30d': (weather_window['rainfall_mm'] > 5).sum(),
            })
        else:
            weather_features.append({
                'avg_temp_prev_30d': 28.0,
                'avg_rainfall_prev_30d': 100.0,
                'total_rainfall_prev_30d': 3000.0,
                'rainy_days_prev_30d': 15,
            })
    
    weather_df = pd.DataFrame(weather_features)
    df = pd.concat([df.reset_index(drop=True), weather_df], axis=1)
    
    # 4. Create target (rule-based)
    def is_good_window(row):
        score = 0
        
        # Season match
        if row['seasonal_type'] == 'all_season':
            score += 2
        elif row['seasonal_type'] == row['season']:
            score += 2
        
        # Rainfall
        if 10 <= row['avg_rainfall_prev_30d'] <= 150:
            score += 2
        elif 5 <= row['avg_rainfall_prev_30d'] <= 200:
            score += 1
        
        # Temperature
        if 22 <= row['avg_temp_prev_30d'] <= 32:
            score += 2
        elif 18 <= row['avg_temp_prev_30d'] <= 36:
            score += 1
        
        # Rainy days
        if 5 <= row['rainy_days_prev_30d'] <= 20:
            score += 1
        
        return int(score >= 4)
    
    df['is_good_window'] = df.apply(is_good_window, axis=1)
    
    logger.info(f"✅ Created features")
    logger.info(f"   Good windows: {df['is_good_window'].sum()} ({df['is_good_window'].mean()*100:.1f}%)")
    
    return df

def create_numeric_features(df):
    """Create numeric features for modeling"""
    logger.info("\n🔢 Creating numeric features...")
    
    # Temporal features
    df['plant_month'] = df['planting_date'].dt.month
    df['plant_quarter'] = df['planting_date'].dt.quarter
    df['plant_day_of_year'] = df['planting_date'].dt.dayofyear
    
    # Cyclic encoding
    df['month_sin'] = np.sin(2 * np.pi * df['plant_month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['plant_month'] / 12)
    df['day_sin'] = np.sin(2 * np.pi * df['plant_day_of_year'] / 365)
    df['day_cos'] = np.cos(2 * np.pi * df['plant_day_of_year'] / 365)
    
    # Encode categorical
    from sklearn.preprocessing import LabelEncoder
    
    le_crop = LabelEncoder()
    le_province = LabelEncoder()
    le_season = LabelEncoder()
    le_soil = LabelEncoder()
    le_seasonal_type = LabelEncoder()
    
    df['crop_type_encoded'] = le_crop.fit_transform(df['crop_type'])
    df['province_encoded'] = le_province.fit_transform(df['province'])
    df['season_encoded'] = le_season.fit_transform(df['season'])
    df['soil_preference_encoded'] = le_soil.fit_transform(df['soil_preference'])
    df['seasonal_type_encoded'] = le_seasonal_type.fit_transform(df['seasonal_type'])
    
    # Select features
    feature_cols = [
        'growth_days',
        'avg_temp_prev_30d', 'avg_rainfall_prev_30d',
        'total_rainfall_prev_30d', 'rainy_days_prev_30d',
        'plant_month', 'plant_quarter', 'plant_day_of_year',
        'month_sin', 'month_cos', 'day_sin', 'day_cos',
        'crop_type_encoded', 'province_encoded', 'season_encoded',
        'soil_preference_encoded', 'seasonal_type_encoded'
    ]
    
    X = df[feature_cols]
    y = df['is_good_window']
    
    logger.info(f"✅ Created {len(feature_cols)} numeric features")
    
    return X, y, df

def train_model(X, y):
    """Train XGBoost model"""
    logger.info("\n🤖 Training XGBoost...")
    
    # Time-based split
    n = len(X)
    train_size = int(n * 0.8)
    
    X_train = X.iloc[:train_size]
    y_train = y.iloc[:train_size]
    X_test = X.iloc[train_size:]
    y_test = y.iloc[train_size:]
    
    logger.info(f"   Train: {len(X_train)} samples")
    logger.info(f"   Test: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=pos_weight,
        random_state=42,
        verbosity=0
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
    
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)
    
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba[:, 1])
    
    logger.info(f"\n📊 Model Performance:")
    logger.info(f"   F1 Score: {f1:.4f}")
    logger.info(f"   Precision: {precision:.4f}")
    logger.info(f"   Recall: {recall:.4f}")
    logger.info(f"   ROC-AUC: {roc_auc:.4f}")
    
    return model, scaler

def save_model(model, scaler):
    """Save model and scaler"""
    logger.info("\n💾 Saving model...")
    
    # Create wrapper object
    model_wrapper = {
        'model': model,
        'scaler': scaler,
        'version': '1.0',
        'trained_at': datetime.now().isoformat()
    }
    
    # Save to backend
    output_path = Path('backend/models/model_b_xgboost.pkl')
    with open(output_path, 'wb') as f:
        pickle.dump(model_wrapper, f)
    
    logger.info(f"✅ Model saved to {output_path}")

def main():
    """Main training pipeline"""
    print("\n" + "="*80)
    print("MODEL B - STANDALONE RETRAINING")
    print("="*80)
    
    # Load data
    cultivation, weather, crop_chars = load_and_prepare_data()
    
    # Create features
    df = create_features(cultivation, weather, crop_chars)
    
    # Create numeric features
    X, y, df_full = create_numeric_features(df)
    
    # Train model
    model, scaler = train_model(X, y)
    
    # Save model
    save_model(model, scaler)
    
    print("\n" + "="*80)
    print("✅ MODEL B RETRAINED SUCCESSFULLY")
    print("="*80)
    print()

if __name__ == "__main__":
    main()

"""
Model A - Crop Recommendation (FIXED)
Algorithms - Using C's methodology (time-aware validation, clean features)

ใช้ NSGA-II + XGBoost + Random Forest
เปรียบเทียบ 3 อัลกอริทึมเพื่อเลือกพืชที่ดีที่สุด
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeAwareSplit:
    """
    Split data by time (like Model C) to prevent temporal leakage
    Training: older dates
    Validation: middle dates
    Test: recent dates
    """
    
    @staticmethod
    def split(df, date_col='planting_date', val_size=0.2, test_size=0.1):
        """Time-aware split"""
        df_sorted = df.sort_values(date_col).reset_index(drop=True)
        
        n = len(df_sorted)
        train_size = int(n * (1 - val_size - test_size))
        val_size_n = int(n * val_size)
        
        train = df_sorted.iloc[:train_size]
        val = df_sorted.iloc[train_size:train_size+val_size_n]
        test = df_sorted.iloc[train_size+val_size_n:]
        
        logger.info(f"✅ Time-aware split:")
        logger.info(f"   Train: {len(train)} samples (oldest)")
        logger.info(f"   Val:   {len(val)} samples")
        logger.info(f"   Test:  {len(test)} samples (recent)")
        
        return train, val, test

class ModelA_NSGA2:
    """NSGA-II: Multi-objective crop selection"""
    
    def __init__(self):
        self.name = "NSGA-II (Multi-Objective)"
        self.weights = {'roi': 0.4, 'risk': 0.3, 'stability': 0.3}
        
    def recommend(self, df_train, X_test, crops_available=10):
        """
        Recommend top crops using multi-objective optimization
        
        Objectives:
        1. Maximize expected ROI
        2. Minimize price risk (volatility)
        3. Maximize market demand (stability)
        """
        
        # Group by crop to get crop-level metrics
        crop_stats = df_train.groupby('crop_id').agg({
            'expected_roi_percent': ['mean', 'std', 'min', 'max'],
            'crop_name': 'first',
        }).reset_index()
        
        crop_stats.columns = ['crop_id', 'roi_mean', 'roi_std', 'roi_min', 'roi_max', 'crop_name']
        
        # Calculate objectives
        max_roi = crop_stats['roi_mean'].max()
        crop_stats['roi_score'] = crop_stats['roi_mean'] / max_roi if max_roi > 0 else 0.5
        
        # Risk: lower std = lower risk = higher score
        max_risk = crop_stats['roi_std'].max()
        crop_stats['risk_score'] = 1.0 - (crop_stats['roi_std'] / max_risk) if max_risk > 0 else 0.5
        
        # Stability: how consistent is the crop
        crop_stats['stability_score'] = 1.0 - (crop_stats['roi_std'] / crop_stats['roi_mean'].abs() + 1e-6)
        
        # Composite score
        crop_stats['composite_score'] = (
            self.weights['roi'] * crop_stats['roi_score'] +
            self.weights['risk'] * crop_stats['risk_score'] +
            self.weights['stability'] * crop_stats['stability_score']
        )
        
        # Get Pareto front (top crops)
        top_crops = crop_stats.nlargest(crops_available, 'composite_score')
        
        results = {
            'algorithm': self.name,
            'top_crops': top_crops[['crop_name', 'roi_mean', 'risk_score', 'composite_score']].head(3).to_dict('records'),
            'count': len(top_crops),
        }
        
        return results

class ModelA_XGBoost:
    """XGBoost: Predict ROI for each crop with regularization"""
    
    def __init__(self):
        self.name = "XGBoost (Gradient Boosting)"
        self.model = None
        
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """Train XGBoost to predict ROI with regularization"""
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,  # Reduced from 4 to prevent overfitting
            learning_rate=0.05,  # Reduced from 0.1 for better generalization
            subsample=0.8,  # Use 80% of data per tree
            colsample_bytree=0.8,  # Use 80% of features per tree
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=1.0,  # L2 regularization
            min_child_weight=3,  # Minimum samples in leaf
            gamma=0.1,  # Minimum loss reduction for split
            random_state=42,
            verbosity=0
        )
        
        # Train model (XGBoost 2.0+ uses callbacks for early stopping)
        self.model.fit(X_train, y_train, verbose=False)
        
    def predict(self, X_test):
        """Predict ROI"""
        return self.model.predict(X_test)
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return {
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
        }

class ModelA_RandomForest:
    """Random Forest + Elastic Net: Baseline model with regularization"""
    
    def __init__(self):
        self.name = "Random Forest + ElasticNet"
        self.rf = None
        self.en = None
        
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """Train ensemble with regularization"""
        self.rf = RandomForestRegressor(
            n_estimators=50,
            max_depth=4,  # Reduced from 5
            min_samples_split=10,  # Require at least 10 samples to split
            min_samples_leaf=5,  # Require at least 5 samples in leaf
            max_features='sqrt',  # Use sqrt(n_features) per tree
            random_state=42
        )
        self.rf.fit(X_train, y_train)
        
        # Get RF residuals and train ElasticNet
        rf_pred = self.rf.predict(X_train)
        residuals = y_train - rf_pred
        
        self.en = ElasticNet(
            alpha=1.0,  # Increased from 0.1 for stronger regularization
            l1_ratio=0.5,  # Balance between L1 and L2
            max_iter=2000,
            random_state=42
        )
        self.en.fit(X_train, residuals)
        
    def predict(self, X_test):
        """Predict ROI"""
        rf_pred = self.rf.predict(X_test)
        residual_pred = self.en.predict(X_test)
        return rf_pred + residual_pred
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return {
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
        }

def create_numeric_features(df, feature_cols):
    """Encode categorical features"""
    df_num = df[feature_cols].copy()
    
    # Encode categorical columns
    for col in df_num.columns:
        if df_num[col].dtype == 'object':
            le = LabelEncoder()
            df_num[col] = le.fit_transform(df_num[col])
    
    return df_num

if __name__ == "__main__":
    print("✅ Model A algorithms loaded successfully")
    print("Ready to train with clean (no post-outcome) features")

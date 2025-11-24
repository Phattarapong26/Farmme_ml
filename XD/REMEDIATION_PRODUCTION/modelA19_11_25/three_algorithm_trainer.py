"""
Three Algorithm Trainer for Model A
Trains 3 different algorithms: XGBoost, Random Forest + ElasticNet, Gradient Boosting
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingResult:
    """Container for training results"""
    algorithm_name: str
    model: Any
    train_metrics: Dict[str, float]
    val_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    training_time: float
    predictions: list

class ThreeAlgorithmTrainer:
    """Train Model A with 3 different algorithms"""
    
    def __init__(self):
        """Initialize trainer"""
        self.training_times = {}
        self.models = {}
        
    def train_all(self, X_train, y_train, X_val, y_val, X_test, y_test) -> Dict[str, TrainingResult]:
        """
        Train all 3 algorithms and return results
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            X_test, y_test: Test data
            
        Returns:
            Dict[str, TrainingResult]: Results for each algorithm
        """
        results = {}
        
        logger.info("\n🤖 Training 3 algorithms...")
        logger.info("="*70)
        
        # Algorithm 1: XGBoost
        logger.info("\n[1/3] Training XGBoost...")
        results['xgboost'] = self._train_xgboost(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Algorithm 2: Random Forest + ElasticNet
        logger.info("\n[2/3] Training Random Forest + ElasticNet...")
        results['rf_ensemble'] = self._train_rf_ensemble(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Algorithm 3: Gradient Boosting
        logger.info("\n[3/3] Training Gradient Boosting...")
        results['gradboost'] = self._train_gradboost(X_train, y_train, X_val, y_val, X_test, y_test)
        
        logger.info("\n" + "="*70)
        logger.info("✅ All 3 algorithms trained successfully")
        logger.info("="*70)
        
        return results
    
    def _train_xgboost(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResult:
        """Train XGBoost with regularization"""
        start_time = time.time()
        
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            verbosity=0
        )
        
        model.fit(X_train, y_train, verbose=False)
        
        training_time = time.time() - start_time
        self.training_times['xgboost'] = training_time
        self.models['xgboost'] = model
        
        # Evaluate on all sets
        train_metrics = self._evaluate(model, X_train, y_train)
        val_metrics = self._evaluate(model, X_val, y_val)
        test_metrics = self._evaluate(model, X_test, y_test)
        
        # Get predictions
        y_test_pred = model.predict(X_test)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train R²: {train_metrics['r2']:.4f}, RMSE: {train_metrics['rmse']:.2f}%")
        logger.info(f"   Val   R²: {val_metrics['r2']:.4f}, RMSE: {val_metrics['rmse']:.2f}%")
        logger.info(f"   Test  R²: {test_metrics['r2']:.4f}, RMSE: {test_metrics['rmse']:.2f}%")
        
        return TrainingResult(
            algorithm_name='XGBoost',
            model=model,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5]
        )
    
    def _train_rf_ensemble(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResult:
        """Train Random Forest + ElasticNet ensemble"""
        start_time = time.time()
        
        # Train Random Forest
        rf = RandomForestRegressor(
            n_estimators=50,
            max_depth=4,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            random_state=42
        )
        rf.fit(X_train, y_train)
        
        # Train ElasticNet on residuals
        rf_pred = rf.predict(X_train)
        residuals = y_train - rf_pred
        
        en = ElasticNet(
            alpha=1.0,
            l1_ratio=0.5,
            max_iter=2000,
            random_state=42
        )
        en.fit(X_train, residuals)
        
        training_time = time.time() - start_time
        self.training_times['rf_ensemble'] = training_time
        
        # Store both models
        ensemble_model = {'rf': rf, 'en': en}
        self.models['rf_ensemble'] = ensemble_model
        
        # Evaluate on all sets
        train_metrics = self._evaluate_ensemble(ensemble_model, X_train, y_train)
        val_metrics = self._evaluate_ensemble(ensemble_model, X_val, y_val)
        test_metrics = self._evaluate_ensemble(ensemble_model, X_test, y_test)
        
        # Get predictions
        y_test_pred = self._predict_ensemble(ensemble_model, X_test)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train R²: {train_metrics['r2']:.4f}, RMSE: {train_metrics['rmse']:.2f}%")
        logger.info(f"   Val   R²: {val_metrics['r2']:.4f}, RMSE: {val_metrics['rmse']:.2f}%")
        logger.info(f"   Test  R²: {test_metrics['r2']:.4f}, RMSE: {test_metrics['rmse']:.2f}%")
        
        return TrainingResult(
            algorithm_name='Random Forest + ElasticNet',
            model=ensemble_model,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5]
        )
    
    def _train_gradboost(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResult:
        """Train Gradient Boosting Regressor"""
        start_time = time.time()
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        self.training_times['gradboost'] = training_time
        self.models['gradboost'] = model
        
        # Evaluate on all sets
        train_metrics = self._evaluate(model, X_train, y_train)
        val_metrics = self._evaluate(model, X_val, y_val)
        test_metrics = self._evaluate(model, X_test, y_test)
        
        # Get predictions
        y_test_pred = model.predict(X_test)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train R²: {train_metrics['r2']:.4f}, RMSE: {train_metrics['rmse']:.2f}%")
        logger.info(f"   Val   R²: {val_metrics['r2']:.4f}, RMSE: {val_metrics['rmse']:.2f}%")
        logger.info(f"   Test  R²: {test_metrics['r2']:.4f}, RMSE: {test_metrics['rmse']:.2f}%")
        
        return TrainingResult(
            algorithm_name='Gradient Boosting',
            model=model,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5]
        )
    
    def _evaluate(self, model, X, y) -> Dict[str, float]:
        """Evaluate a single model"""
        y_pred = model.predict(X)
        return {
            'r2': r2_score(y, y_pred),
            'rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'mae': mean_absolute_error(y, y_pred)
        }
    
    def _evaluate_ensemble(self, ensemble_model, X, y) -> Dict[str, float]:
        """Evaluate ensemble model"""
        y_pred = self._predict_ensemble(ensemble_model, X)
        return {
            'r2': r2_score(y, y_pred),
            'rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'mae': mean_absolute_error(y, y_pred)
        }
    
    def _predict_ensemble(self, ensemble_model, X):
        """Make predictions with ensemble model"""
        rf_pred = ensemble_model['rf'].predict(X)
        residual_pred = ensemble_model['en'].predict(X)
        return rf_pred + residual_pred
    
    def get_training_times(self) -> Dict[str, float]:
        """Get training time for each algorithm"""
        return self.training_times

if __name__ == "__main__":
    # Test with dummy data
    from sklearn.datasets import make_regression
    
    X, y = make_regression(n_samples=1000, n_features=6, noise=10, random_state=42)
    
    # Split data
    train_size = int(0.7 * len(X))
    val_size = int(0.2 * len(X))
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
    X_test, y_test = X[train_size+val_size:], y[train_size+val_size:]
    
    # Train
    trainer = ThreeAlgorithmTrainer()
    results = trainer.train_all(X_train, y_train, X_val, y_val, X_test, y_test)
    
    print("\n✅ Three Algorithm Trainer Test Passed")
    print(f"Trained {len(results)} algorithms")
    print(f"Training times: {trainer.get_training_times()}")

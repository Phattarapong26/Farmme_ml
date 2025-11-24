"""
Three Algorithm Trainer for Model B
Trains 3 different algorithms: XGBoost, Random Forest, Gradient Boosting
For binary classification (Good/Bad planting window)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
import xgboost as xgb
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingResultB:
    """Container for training results"""
    algorithm_name: str
    model: Any
    scaler: Any
    train_metrics: Dict[str, float]
    val_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    training_time: float
    predictions: list
    y_proba: Any

class ThreeAlgorithmTrainerB:
    """Train Model B with 3 different algorithms"""
    
    def __init__(self):
        """Initialize trainer"""
        self.training_times = {}
        self.models = {}
        
    def train_all(self, X_train, y_train, X_val, y_val, X_test, y_test) -> Dict[str, TrainingResultB]:
        """
        Train all 3 algorithms and return results
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            X_test, y_test: Test data
            
        Returns:
            Dict[str, TrainingResultB]: Results for each algorithm
        """
        results = {}
        
        logger.info("\n🤖 Training 3 algorithms...")
        logger.info("="*70)
        
        # Algorithm 1: XGBoost
        logger.info("\n[1/3] Training XGBoost Classifier...")
        results['xgboost'] = self._train_xgboost(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Algorithm 2: Random Forest
        logger.info("\n[2/3] Training Random Forest Classifier...")
        results['random_forest'] = self._train_random_forest(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Algorithm 3: Gradient Boosting
        logger.info("\n[3/3] Training Gradient Boosting Classifier...")
        results['gradboost'] = self._train_gradboost(X_train, y_train, X_val, y_val, X_test, y_test)
        
        logger.info("\n" + "="*70)
        logger.info("✅ All 3 algorithms trained successfully")
        logger.info("="*70)
        
        return results
    
    def _train_xgboost(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResultB:
        """Train XGBoost Classifier"""
        start_time = time.time()
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        # Calculate class weight
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
        
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            verbosity=0
        )
        
        model.fit(X_train_scaled, y_train)
        
        training_time = time.time() - start_time
        self.training_times['xgboost'] = training_time
        self.models['xgboost'] = {'model': model, 'scaler': scaler}
        
        # Evaluate on all sets
        train_metrics = self._evaluate(model, X_train_scaled, y_train)
        val_metrics = self._evaluate(model, X_val_scaled, y_val)
        test_metrics = self._evaluate(model, X_test_scaled, y_test)
        
        # Get predictions and probabilities
        y_test_pred = model.predict(X_test_scaled)
        y_test_proba = model.predict_proba(X_test_scaled)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train F1: {train_metrics['f1']:.4f}, Precision: {train_metrics['precision']:.4f}, Recall: {train_metrics['recall']:.4f}")
        logger.info(f"   Val   F1: {val_metrics['f1']:.4f}, Precision: {val_metrics['precision']:.4f}, Recall: {val_metrics['recall']:.4f}")
        logger.info(f"   Test  F1: {test_metrics['f1']:.4f}, Precision: {test_metrics['precision']:.4f}, Recall: {test_metrics['recall']:.4f}")
        logger.info(f"   Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
        
        return TrainingResultB(
            algorithm_name='XGBoost',
            model=model,
            scaler=scaler,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5],
            y_proba=y_test_proba
        )
    
    def _train_random_forest(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResultB:
        """Train Random Forest Classifier"""
        start_time = time.time()
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        # Calculate class weight
        n_samples = len(y_train)
        n_classes = 2
        class_weight = {
            0: n_samples / (n_classes * (y_train == 0).sum()),
            1: n_samples / (n_classes * (y_train == 1).sum())
        }
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            class_weight=class_weight,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        training_time = time.time() - start_time
        self.training_times['random_forest'] = training_time
        self.models['random_forest'] = {'model': model, 'scaler': scaler}
        
        # Evaluate on all sets
        train_metrics = self._evaluate(model, X_train_scaled, y_train)
        val_metrics = self._evaluate(model, X_val_scaled, y_val)
        test_metrics = self._evaluate(model, X_test_scaled, y_test)
        
        # Get predictions and probabilities
        y_test_pred = model.predict(X_test_scaled)
        y_test_proba = model.predict_proba(X_test_scaled)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train F1: {train_metrics['f1']:.4f}, Precision: {train_metrics['precision']:.4f}, Recall: {train_metrics['recall']:.4f}")
        logger.info(f"   Val   F1: {val_metrics['f1']:.4f}, Precision: {val_metrics['precision']:.4f}, Recall: {val_metrics['recall']:.4f}")
        logger.info(f"   Test  F1: {test_metrics['f1']:.4f}, Precision: {test_metrics['precision']:.4f}, Recall: {test_metrics['recall']:.4f}")
        logger.info(f"   Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
        
        return TrainingResultB(
            algorithm_name='Random Forest',
            model=model,
            scaler=scaler,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5],
            y_proba=y_test_proba
        )
    
    def _train_gradboost(self, X_train, y_train, X_val, y_val, X_test, y_test) -> TrainingResultB:
        """Train Gradient Boosting Classifier"""
        start_time = time.time()
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        training_time = time.time() - start_time
        self.training_times['gradboost'] = training_time
        self.models['gradboost'] = {'model': model, 'scaler': scaler}
        
        # Evaluate on all sets
        train_metrics = self._evaluate(model, X_train_scaled, y_train)
        val_metrics = self._evaluate(model, X_val_scaled, y_val)
        test_metrics = self._evaluate(model, X_test_scaled, y_test)
        
        # Get predictions and probabilities
        y_test_pred = model.predict(X_test_scaled)
        y_test_proba = model.predict_proba(X_test_scaled)
        
        logger.info(f"   Training time: {training_time:.2f}s")
        logger.info(f"   Train F1: {train_metrics['f1']:.4f}, Precision: {train_metrics['precision']:.4f}, Recall: {train_metrics['recall']:.4f}")
        logger.info(f"   Val   F1: {val_metrics['f1']:.4f}, Precision: {val_metrics['precision']:.4f}, Recall: {val_metrics['recall']:.4f}")
        logger.info(f"   Test  F1: {test_metrics['f1']:.4f}, Precision: {test_metrics['precision']:.4f}, Recall: {test_metrics['recall']:.4f}")
        logger.info(f"   Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
        
        return TrainingResultB(
            algorithm_name='Gradient Boosting',
            model=model,
            scaler=scaler,
            train_metrics=train_metrics,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            training_time=training_time,
            predictions=y_test_pred.tolist()[:5],
            y_proba=y_test_proba
        )
    
    def _evaluate(self, model, X, y) -> Dict[str, float]:
        """Evaluate a classifier"""
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)
        
        return {
            'f1': f1_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y, y_proba[:, 1])
        }
    
    def get_training_times(self) -> Dict[str, float]:
        """Get training time for each algorithm"""
        return self.training_times

if __name__ == "__main__":
    # Test with dummy data
    from sklearn.datasets import make_classification
    
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, 
                               weights=[0.7, 0.3], random_state=42)
    
    # Split data
    train_size = int(0.6 * len(X))
    val_size = int(0.2 * len(X))
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
    X_test, y_test = X[train_size+val_size:], y[train_size+val_size:]
    
    # Train
    trainer = ThreeAlgorithmTrainerB()
    results = trainer.train_all(X_train, y_train, X_val, y_val, X_test, y_test)
    
    print("\n✅ Three Algorithm Trainer B Test Passed")
    print(f"Trained {len(results)} algorithms")
    print(f"Training times: {trainer.get_training_times()}")

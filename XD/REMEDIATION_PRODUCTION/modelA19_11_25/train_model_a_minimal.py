"""
Train Model A - Minimal Version with 3 Algorithms
Uses minimal dataset and generates bubble comparison chart

ขั้นตอน:
1. Load minimal data (max 1000 samples)
2. Split time-aware (train/val/test)
3. Train 3 algorithms (XGBoost, RF+ElasticNet, GradBoost)
4. Evaluate metrics
5. Generate bubble comparison chart
6. Generate detailed evaluation plots
7. Save models and results
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modelA19_11_25.minimal_data_loader import MinimalDataLoader
from modelA19_11_25.three_algorithm_trainer import ThreeAlgorithmTrainer
from modelA19_11_25.bubble_chart_generator import BubbleChartGenerator
from modelA19_11_25.detailed_plotter import DetailedEvaluationPlotter
from Model_A_Fixed.model_algorithms_clean import TimeAwareSplit, create_numeric_features
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_a_minimal')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelAMinimalTrainer:
    """Train and evaluate Model A with minimal dataset"""
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize trainer
        
        Args:
            max_samples: Maximum number of samples to use
        """
        self.max_samples = max_samples
        self.results = {}
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.start_time = None
        
    def load_data(self):
        """Load and prepare minimal data"""
        logger.info("📥 Loading minimal data...")
        self.start_time = datetime.now()
        
        loader = MinimalDataLoader(max_samples=self.max_samples)
        df = loader.load_and_sample()
        
        logger.info(f"✅ Loaded {len(df)} records")
        logger.info(f"   Columns: {df.shape[1]}")
        logger.info(f"   Target mean: {df['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Target std: {df['expected_roi_percent'].std():.2f}%")
        
        return df
    
    def split_data(self, df):
        """Time-aware split"""
        logger.info("\n⏱️  Time-aware split...")
        
        train, val, test = TimeAwareSplit.split(df, date_col='planting_date')
        
        # Get feature columns
        feature_cols = [
            'planting_area_rai',
            'expected_yield_kg',
            'growth_days',
            'water_requirement',
            'investment_cost',
            'risk_level',
        ]
        
        # Filter to only available numeric columns
        available_cols = [c for c in feature_cols if c in train.columns]
        logger.info(f"   Using features: {available_cols}")
        
        # Create numeric features
        X_train = create_numeric_features(train, available_cols)
        y_train = train['expected_roi_percent'].fillna(train['expected_roi_percent'].median())
        
        X_val = create_numeric_features(val, available_cols)
        y_val = val['expected_roi_percent'].fillna(val['expected_roi_percent'].median())
        
        X_test = create_numeric_features(test, available_cols)
        y_test = test['expected_roi_percent'].fillna(test['expected_roi_percent'].median())
        
        logger.info(f"✅ Train: {len(X_train)} samples")
        logger.info(f"✅ Val: {len(X_val)} samples")
        logger.info(f"✅ Test: {len(X_test)} samples")
        
        # Store for later use
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train_models(self, X_train, y_train, X_val, y_val, X_test, y_test):
        """Train all 3 algorithms"""
        logger.info("\n🤖 Training 3 algorithms...")
        
        trainer = ThreeAlgorithmTrainer()
        self.results = trainer.train_all(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Log summary
        logger.info("\n📊 Training Summary:")
        for key, result in self.results.items():
            logger.info(f"\n  {result.algorithm_name}:")
            logger.info(f"    Training time: {result.training_time:.2f}s")
            logger.info(f"    Test R²: {result.test_metrics['r2']:.4f}")
            logger.info(f"    Test RMSE: {result.test_metrics['rmse']:.2f}%")
    
    def generate_plots(self):
        """Generate bubble chart and detailed evaluation plots"""
        output_dir = Config.get_output_path('model_a_minimal', 'evaluation')
        logger.info(f"\n📊 Generating plots to {output_dir}...")
        
        # 1. Generate bubble comparison chart
        logger.info("\n[1/2] Generating bubble comparison chart...")
        bubble_generator = BubbleChartGenerator(self.results)
        bubble_path = output_dir / 'bubble_comparison.png'
        bubble_generator.generate_bubble_chart(bubble_path)
        
        # 2. Generate detailed evaluation plots
        logger.info("\n[2/2] Generating detailed evaluation plots...")
        detailed_plotter = DetailedEvaluationPlotter(
            self.results,
            self.X_train,
            self.y_train,
            self.X_test,
            self.y_test
        )
        detailed_plotter.generate_all_plots(output_dir)
        
        logger.info(f"\n✅ All plots saved to: {output_dir}")
    
    def save_models(self):
        """Save all trained models as .pkl"""
        logger.info("\n💾 Saving models...")
        
        for key, result in self.results.items():
            filepath = Config.MODEL_PATH / f'model_a_{key}_minimal.pkl'
            
            with open(filepath, 'wb') as f:
                pickle.dump(result.model, f)
            
            logger.info(f"  ✅ {filepath.name}")
    
    def save_results(self):
        """Save evaluation results as JSON"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_a_minimal_evaluation.json'
        
        # Find best algorithm
        best_algo = None
        best_r2 = -999
        for key, result in self.results.items():
            if result.test_metrics['r2'] > best_r2:
                best_r2 = result.test_metrics['r2']
                best_algo = key
        
        # Calculate total training time
        total_time = sum(r.training_time for r in self.results.values())
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Prepare results
        results_data = {
            'model': 'Model A - Crop Recommendation (Minimal)',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'dataset_size': self.max_samples,
            'actual_samples': len(self.X_train) + len(self.X_val) + len(self.X_test),
            'algorithms': {
                key: {
                    'name': result.algorithm_name,
                    'train_metrics': result.train_metrics,
                    'val_metrics': result.val_metrics,
                    'test_metrics': result.test_metrics,
                    'training_time': result.training_time,
                    'predictions_sample': result.predictions
                }
                for key, result in self.results.items()
            },
            'summary': {
                'best_algorithm': best_algo,
                'best_r2': best_r2,
                'best_rmse': self.results[best_algo].test_metrics['rmse'],
                'total_training_time': total_time,
                'total_elapsed_time': elapsed_time,
                'note': 'Trained with minimal dataset using 3 algorithms'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file.name}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL A MINIMAL TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\n📊 Dataset:")
        logger.info(f"   Samples: {results_data['actual_samples']}")
        logger.info(f"   Train: {len(self.X_train)}, Val: {len(self.X_val)}, Test: {len(self.X_test)}")
        logger.info(f"\n🏆 Best Algorithm: {self.results[best_algo].algorithm_name}")
        logger.info(f"   R² = {best_r2:.4f}")
        logger.info(f"   RMSE = {self.results[best_algo].test_metrics['rmse']:.2f}%")
        logger.info(f"   MAE = {self.results[best_algo].test_metrics['mae']:.2f}%")
        logger.info(f"\n⏱️  Training Time:")
        logger.info(f"   Total: {total_time:.2f}s")
        logger.info(f"   Elapsed: {elapsed_time:.2f}s")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_a_minimal', 'evaluation')}")
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL A - MINIMAL TRAINING WITH 3 ALGORITHMS".center(80))
    print("="*80)
    
    trainer = ModelAMinimalTrainer(max_samples=1000)
    
    # Load data
    df = trainer.load_data()
    
    # Split data
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data(df)
    
    # Train models
    trainer.train_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Generate plots
    trainer.generate_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

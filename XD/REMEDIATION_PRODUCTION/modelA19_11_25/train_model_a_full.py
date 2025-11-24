"""
Train Model A - Full Dataset with 3 Algorithms
Uses FULL dataset with strict train/test separation to prevent data leakage

ขั้นตอน:
1. Load FULL data (all samples)
2. Split time-aware with STRICT separation (train/val/test)
3. Train 3 algorithms (XGBoost, RF+ElasticNet, GradBoost)
4. Evaluate metrics with leakage prevention
5. Generate bubble comparison chart
6. Generate detailed evaluation plots
7. Save models and results
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Model_A_Fixed.data_loader_clean import DataLoaderClean
from modelA19_11_25.three_algorithm_trainer import ThreeAlgorithmTrainer
from modelA19_11_25.bubble_chart_generator import BubbleChartGenerator
from modelA19_11_25.detailed_plotter import DetailedEvaluationPlotter
from Model_A_Fixed.model_algorithms_clean import create_numeric_features
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_a_full')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StrictTimeAwareSplit:
    """
    Strict time-aware split with embargo period to prevent data leakage
    Ensures NO overlap between train/val/test periods
    """
    
    @staticmethod
    def split(df, date_col='planting_date', embargo_days=7, val_ratio=0.2, test_ratio=0.1):
        """
        Split data by time with embargo periods
        
        Args:
            df: DataFrame with date column
            date_col: Name of date column
            embargo_days: Days gap between splits to prevent leakage
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            
        Returns:
            train, val, test DataFrames
        """
        df_sorted = df.sort_values(date_col).reset_index(drop=True)
        
        n = len(df_sorted)
        
        # Calculate split points with embargo
        test_size = int(n * test_ratio)
        val_size = int(n * val_ratio)
        train_size = n - test_size - val_size
        
        # Get date ranges
        train_end_idx = train_size
        val_start_idx = train_size
        val_end_idx = train_size + val_size
        test_start_idx = val_end_idx
        
        # Apply embargo by removing samples near boundaries
        train_end_date = df_sorted.iloc[train_end_idx][date_col]
        val_start_date = train_end_date + timedelta(days=embargo_days)
        
        val_end_date = df_sorted.iloc[val_end_idx][date_col]
        test_start_date = val_end_date + timedelta(days=embargo_days)
        
        # Filter with embargo
        train = df_sorted[df_sorted[date_col] < train_end_date].copy()
        val = df_sorted[
            (df_sorted[date_col] >= val_start_date) & 
            (df_sorted[date_col] < val_end_date)
        ].copy()
        test = df_sorted[df_sorted[date_col] >= test_start_date].copy()
        
        logger.info(f"✅ Strict time-aware split with {embargo_days}-day embargo:")
        logger.info(f"   Train: {len(train)} samples (oldest)")
        logger.info(f"   Train date range: {train[date_col].min()} to {train[date_col].max()}")
        logger.info(f"   --- EMBARGO: {embargo_days} days ---")
        logger.info(f"   Val:   {len(val)} samples")
        logger.info(f"   Val date range: {val[date_col].min()} to {val[date_col].max()}")
        logger.info(f"   --- EMBARGO: {embargo_days} days ---")
        logger.info(f"   Test:  {len(test)} samples (most recent)")
        logger.info(f"   Test date range: {test[date_col].min()} to {test[date_col].max()}")
        
        # Verify no overlap
        assert train[date_col].max() < val[date_col].min(), "Train/Val overlap detected!"
        assert val[date_col].max() < test[date_col].min(), "Val/Test overlap detected!"
        
        logger.info(f"✅ No temporal overlap verified")
        
        return train, val, test

class ModelAFullTrainer:
    """Train and evaluate Model A with FULL dataset"""
    
    def __init__(self, embargo_days: int = 7):
        """
        Initialize trainer
        
        Args:
            embargo_days: Days gap between train/val/test to prevent leakage
        """
        self.embargo_days = embargo_days
        self.results = {}
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.start_time = None
        
    def load_data(self):
        """Load and prepare FULL data"""
        logger.info("📥 Loading FULL dataset...")
        self.start_time = datetime.now()
        
        loader = DataLoaderClean()
        
        # Load all datasets
        cultivation = loader.load_cultivation_clean()
        farmers = loader.load_farmer_profiles()
        crops = loader.load_crop_characteristics()
        weather = loader.load_weather()
        price = loader.load_price_data()
        
        # Create training dataset
        df = loader.create_training_data(
            cultivation, farmers, crops, weather, price
        )
        
        # Validate no leakage
        try:
            loader.validate_no_leakage(df, Config.FORBIDDEN_FEATURES_MODEL_A)
        except ValueError as e:
            logger.error(f"Data leakage detected: {e}")
            raise
        
        logger.info(f"✅ Loaded {len(df)} records (FULL dataset)")
        logger.info(f"   Columns: {df.shape[1]}")
        logger.info(f"   Target mean: {df['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Target std: {df['expected_roi_percent'].std():.2f}%")
        
        return df
    
    def split_data(self, df):
        """Strict time-aware split with embargo"""
        logger.info(f"\n⏱️  Strict time-aware split (embargo: {self.embargo_days} days)...")
        
        train, val, test = StrictTimeAwareSplit.split(
            df, 
            date_col='planting_date',
            embargo_days=self.embargo_days
        )
        
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
        
        logger.info(f"\n✅ Final split sizes:")
        logger.info(f"   Train: {len(X_train)} samples ({len(X_train)/len(df)*100:.1f}%)")
        logger.info(f"   Val:   {len(X_val)} samples ({len(X_val)/len(df)*100:.1f}%)")
        logger.info(f"   Test:  {len(X_test)} samples ({len(X_test)/len(df)*100:.1f}%)")
        
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
        logger.info("\n🤖 Training 3 algorithms on FULL dataset...")
        
        trainer = ThreeAlgorithmTrainer()
        self.results = trainer.train_all(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Log summary
        logger.info("\n📊 Training Summary:")
        for key, result in self.results.items():
            logger.info(f"\n  {result.algorithm_name}:")
            logger.info(f"    Training time: {result.training_time:.2f}s")
            logger.info(f"    Test R²: {result.test_metrics['r2']:.4f}")
            logger.info(f"    Test RMSE: {result.test_metrics['rmse']:.2f}%")
            
            # Check overfitting
            gap = result.train_metrics['r2'] - result.test_metrics['r2']
            if gap > Config.OVERFITTING_THRESHOLD:
                logger.warning(f"    ⚠️ Overfitting detected (gap: {gap:.4f})")
            else:
                logger.info(f"    ✅ No overfitting (gap: {gap:.4f})")
    
    def generate_plots(self):
        """Generate bubble chart and detailed evaluation plots"""
        output_dir = Config.get_output_path('model_a_full', 'evaluation')
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
            filepath = Config.MODEL_PATH / f'model_a_{key}_full.pkl'
            
            with open(filepath, 'wb') as f:
                pickle.dump(result.model, f)
            
            logger.info(f"  ✅ {filepath.name}")
    
    def save_results(self):
        """Save evaluation results as JSON"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_a_full_evaluation.json'
        
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
            'model': 'Model A - Crop Recommendation (Full Dataset)',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'dataset_info': {
                'total_samples': len(self.X_train) + len(self.X_val) + len(self.X_test),
                'train_samples': len(self.X_train),
                'val_samples': len(self.X_val),
                'test_samples': len(self.X_test),
                'embargo_days': self.embargo_days
            },
            'algorithms': {
                key: {
                    'name': result.algorithm_name,
                    'train_metrics': result.train_metrics,
                    'val_metrics': result.val_metrics,
                    'test_metrics': result.test_metrics,
                    'training_time': result.training_time,
                    'overfitting_gap': result.train_metrics['r2'] - result.test_metrics['r2'],
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
                'note': 'Trained with FULL dataset using strict time-aware split with embargo'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file.name}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL A FULL TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\n📊 Dataset:")
        logger.info(f"   Total samples: {results_data['dataset_info']['total_samples']}")
        logger.info(f"   Train: {len(self.X_train)}, Val: {len(self.X_val)}, Test: {len(self.X_test)}")
        logger.info(f"   Embargo: {self.embargo_days} days (prevents data leakage)")
        logger.info(f"\n🏆 Best Algorithm: {self.results[best_algo].algorithm_name}")
        logger.info(f"   R² = {best_r2:.4f}")
        logger.info(f"   RMSE = {self.results[best_algo].test_metrics['rmse']:.2f}%")
        logger.info(f"   MAE = {self.results[best_algo].test_metrics['mae']:.2f}%")
        logger.info(f"\n⏱️  Training Time:")
        logger.info(f"   Total: {total_time:.2f}s")
        logger.info(f"   Elapsed: {elapsed_time:.2f}s")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_a_full', 'evaluation')}")
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL A - FULL DATASET TRAINING WITH 3 ALGORITHMS".center(80))
    print("="*80)
    
    trainer = ModelAFullTrainer(embargo_days=7)
    
    # Load data
    df = trainer.load_data()
    
    # Split data with strict separation
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data(df)
    
    # Train models
    trainer.train_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Generate plots
    trainer.generate_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

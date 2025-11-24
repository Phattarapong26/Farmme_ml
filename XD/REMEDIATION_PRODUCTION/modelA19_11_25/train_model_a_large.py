"""
Train Model A - Large Dataset (2.2M+ rows)
Uses FARMME_GPU_DATASET with 3 algorithms and strict train/test separation

ขั้นตอน:
1. Load LARGE dataset (2.2M+ rows or sample)
2. Split time-aware with STRICT separation
3. Train 3 algorithms
4. Evaluate metrics
5. Generate bubble comparison chart
6. Save models and results
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

from modelA19_11_25.large_data_loader import LargeDataLoader
from modelA19_11_25.three_algorithm_trainer import ThreeAlgorithmTrainer
from modelA19_11_25.bubble_chart_generator import BubbleChartGenerator
from modelA19_11_25.detailed_plotter import DetailedEvaluationPlotter
from Model_A_Fixed.model_algorithms_clean import create_numeric_features
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_a_large')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StrictTimeAwareSplit:
    """Strict time-aware split with embargo period"""
    
    @staticmethod
    def split(df, date_col='date', embargo_days=7, val_ratio=0.15, test_ratio=0.10):
        """Split data by time with embargo periods"""
        df_sorted = df.sort_values(date_col).reset_index(drop=True)
        
        n = len(df_sorted)
        
        # Calculate split points
        test_size = int(n * test_ratio)
        val_size = int(n * val_ratio)
        train_size = n - test_size - val_size
        
        # Get date ranges
        train_end_idx = train_size
        val_end_idx = train_size + val_size
        
        # Apply embargo
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
        logger.info(f"   Train: {len(train):,} samples ({len(train)/n*100:.1f}%)")
        logger.info(f"   Train date range: {train[date_col].min()} to {train[date_col].max()}")
        logger.info(f"   --- EMBARGO: {embargo_days} days ---")
        logger.info(f"   Val:   {len(val):,} samples ({len(val)/n*100:.1f}%)")
        logger.info(f"   Val date range: {val[date_col].min()} to {val[date_col].max()}")
        logger.info(f"   --- EMBARGO: {embargo_days} days ---")
        logger.info(f"   Test:  {len(test):,} samples ({len(test)/n*100:.1f}%)")
        logger.info(f"   Test date range: {test[date_col].min()} to {test[date_col].max()}")
        
        # Verify no overlap
        assert train[date_col].max() < val[date_col].min(), "Train/Val overlap!"
        assert val[date_col].max() < test[date_col].min(), "Val/Test overlap!"
        
        logger.info(f"✅ No temporal overlap verified")
        
        return train, val, test

class ModelALargeTrainer:
    """Train Model A with LARGE dataset"""
    
    def __init__(self, sample_size=None, embargo_days=7):
        """
        Initialize trainer
        
        Args:
            sample_size: Number of rows to sample (None = use all 2.2M+)
            embargo_days: Days gap between splits
        """
        self.sample_size = sample_size
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
        """Load and prepare large dataset"""
        logger.info("📥 Loading LARGE dataset...")
        self.start_time = datetime.now()
        
        loader = LargeDataLoader()
        df = loader.load_and_prepare(sample_size=self.sample_size)
        
        logger.info(f"✅ Loaded {len(df):,} records")
        logger.info(f"   Columns: {df.shape[1]}")
        logger.info(f"   Target mean: {df['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Target std: {df['expected_roi_percent'].std():.2f}%")
        
        return df
    
    def split_data(self, df):
        """Strict time-aware split"""
        logger.info(f"\n⏱️  Strict time-aware split (embargo: {self.embargo_days} days)...")
        
        train, val, test = StrictTimeAwareSplit.split(
            df,
            date_col='date',
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
            'base_price',
            'inventory_level',
            'supply_level',
            'demand_elasticity',
            'temperature_celsius',
            'rainfall_mm',
            'humidity_percent',
            'drought_index',
            'fuel_price',
            'fertilizer_price',
            'inflation_rate',
            'gdp_growth',
            'unemployment_rate',
        ]
        
        # Filter to available columns
        available_cols = [c for c in feature_cols if c in train.columns]
        logger.info(f"   Using {len(available_cols)} features")
        
        # Create numeric features
        X_train = create_numeric_features(train, available_cols)
        y_train = train['expected_roi_percent']
        
        X_val = create_numeric_features(val, available_cols)
        y_val = val['expected_roi_percent']
        
        X_test = create_numeric_features(test, available_cols)
        y_test = test['expected_roi_percent']
        
        logger.info(f"\n✅ Final split sizes:")
        logger.info(f"   Train: {len(X_train):,} samples")
        logger.info(f"   Val:   {len(X_val):,} samples")
        logger.info(f"   Test:  {len(X_test):,} samples")
        
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
        logger.info("\n🤖 Training 3 algorithms on LARGE dataset...")
        
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
                logger.warning(f"    ⚠️ Overfitting (gap: {gap:.4f})")
            else:
                logger.info(f"    ✅ No overfitting (gap: {gap:.4f})")
    
    def generate_plots(self):
        """Generate bubble chart and detailed plots"""
        output_dir = Config.get_output_path('model_a_large', 'evaluation')
        logger.info(f"\n📊 Generating plots to {output_dir}...")
        
        # 1. Bubble comparison chart
        logger.info("\n[1/2] Generating bubble comparison chart...")
        bubble_generator = BubbleChartGenerator(self.results)
        bubble_path = output_dir / 'bubble_comparison.png'
        bubble_generator.generate_bubble_chart(bubble_path)
        
        # 2. Detailed evaluation plots
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
        """Save all trained models"""
        logger.info("\n💾 Saving models...")
        
        for key, result in self.results.items():
            filepath = Config.MODEL_PATH / f'model_a_{key}_large.pkl'
            
            with open(filepath, 'wb') as f:
                pickle.dump(result.model, f)
            
            logger.info(f"  ✅ {filepath.name}")
    
    def save_results(self):
        """Save evaluation results"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_a_large_evaluation.json'
        
        # Find best algorithm
        best_algo = max(self.results.items(), key=lambda x: x[1].test_metrics['r2'])[0]
        best_r2 = self.results[best_algo].test_metrics['r2']
        
        # Calculate times
        total_time = sum(r.training_time for r in self.results.values())
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Prepare results
        results_data = {
            'model': 'Model A - Crop Recommendation (Large Dataset)',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'dataset_info': {
                'source': 'FARMME_GPU_DATASET.csv',
                'sample_size': self.sample_size if self.sample_size else 'ALL',
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
                'note': 'Trained with LARGE dataset (FARMME_GPU_DATASET)'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file.name}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL A LARGE TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\n📊 Dataset:")
        logger.info(f"   Source: FARMME_GPU_DATASET.csv")
        logger.info(f"   Total samples: {results_data['dataset_info']['total_samples']:,}")
        logger.info(f"   Train: {len(self.X_train):,}, Val: {len(self.X_val):,}, Test: {len(self.X_test):,}")
        logger.info(f"   Embargo: {self.embargo_days} days")
        logger.info(f"\n🏆 Best Algorithm: {self.results[best_algo].algorithm_name}")
        logger.info(f"   R² = {best_r2:.4f}")
        logger.info(f"   RMSE = {self.results[best_algo].test_metrics['rmse']:.2f}%")
        logger.info(f"   MAE = {self.results[best_algo].test_metrics['mae']:.2f}%")
        logger.info(f"\n⏱️  Training Time:")
        logger.info(f"   Total: {total_time:.2f}s")
        logger.info(f"   Elapsed: {elapsed_time:.2f}s")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_a_large', 'evaluation')}")
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Model A with Large Dataset')
    parser.add_argument('--sample', type=int, default=None, 
                       help='Sample size (default: use all 2.2M+ rows)')
    parser.add_argument('--embargo', type=int, default=7,
                       help='Embargo days between splits (default: 7)')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("MODEL A - LARGE DATASET TRAINING (FARMME_GPU_DATASET)".center(80))
    print("="*80)
    
    if args.sample:
        print(f"\nUsing sample size: {args.sample:,} rows")
    else:
        print(f"\nUsing ALL rows (2.2M+) - this will take longer!")
    
    trainer = ModelALargeTrainer(sample_size=args.sample, embargo_days=args.embargo)
    
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

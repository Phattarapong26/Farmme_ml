"""
Train Model A - Crop Recommendation (FIXED VERSION)
ใช้ clean data (no post-outcome features)
Save as .pkl + Evaluation metrics

ขั้นตอน:
1. Load clean cultivation data
2. Split time-aware (train/val/test)
3. Train 3 algorithms
4. Evaluate metrics
5. Save best model as .pkl
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from Model_A_Fixed.data_loader_clean import DataLoaderClean
from Model_A_Fixed.model_algorithms_clean import (
    ModelA_NSGA2, ModelA_XGBoost, ModelA_RandomForest,
    TimeAwareSplit, create_numeric_features
)
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_a')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelATrainer:
    """Train and evaluate Model A"""
    
    def __init__(self, dataset_dir=None):
        if dataset_dir is None:
            self.dataset_dir = Config.DATA_PATH
        else:
            self.dataset_dir = dataset_dir
        self.results = {}
        self.models = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self):
        """Load and prepare clean data"""
        logger.info("📥 Loading clean data...")
        
        loader = DataLoaderClean(self.dataset_dir)
        
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
        
        logger.info(f"✅ Loaded {len(df)} records")
        logger.info(f"   Columns: {df.shape[1]}")
        logger.info(f"   Target mean: {df['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Target std: {df['expected_roi_percent'].std():.2f}%")
        
        return df
    
    def split_data(self, df):
        """Time-aware split"""
        logger.info("\n⏱️  Time-aware split...")
        
        train, val, test = TimeAwareSplit.split(df, date_col='planting_date')
        
        # Get feature columns (use actual columns from dataset)
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
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train_models(self, X_train, y_train, X_val, y_val):
        """Train all 3 algorithms with regularization"""
        
        logger.info("\n🤖 Training algorithms with regularization...")
        
        # Algorithm 1: NSGA-II (Multi-Objective)
        logger.info("\n  [1/3] NSGA-II (Multi-Objective GA)...")
        model_nsga2 = ModelA_NSGA2()
        self.models['nsga2'] = {
            'name': 'NSGA-II (Multi-Objective)',
            'model': model_nsga2,
            'type': 'multi_objective'
        }
        logger.info("      ✅ NSGA-II ready (uses on-demand evaluation)")
        
        # Algorithm 2: XGBoost with regularization
        logger.info("  [2/3] XGBoost Regressor (with regularization)...")
        model_xgb = ModelA_XGBoost()
        model_xgb.train(X_train, y_train, X_val, y_val)
        self.models['xgboost'] = {
            'name': 'XGBoost Regressor',
            'model': model_xgb,
            'type': 'regression'
        }
        logger.info("      ✅ Trained with early stopping")
        
        # Algorithm 3: Random Forest + ElasticNet with regularization
        logger.info("  [3/3] Random Forest + ElasticNet (with regularization)...")
        model_rf = ModelA_RandomForest()
        model_rf.train(X_train, y_train, X_val, y_val)
        self.models['rf_ensemble'] = {
            'name': 'Random Forest + ElasticNet',
            'model': model_rf,
            'type': 'regression'
        }
        logger.info("      ✅ Trained with stronger regularization")
    
    def evaluate_models(self, X_train, y_train, X_val, y_val, X_test, y_test):
        """Evaluate all models and check for overfitting"""
        
        logger.info("\n📊 Evaluation on All Sets (checking for overfitting)...")
        
        for key, model_info in self.models.items():
            if model_info['type'] == 'regression':
                model = model_info['model']
                
                # Evaluate on all sets
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                train_metrics = model.evaluate(y_train, y_train_pred)
                val_metrics = model.evaluate(y_val, y_val_pred)
                test_metrics = model.evaluate(y_test, y_test_pred)
                
                self.results[key] = {
                    'name': model_info['name'],
                    'train_metrics': train_metrics,
                    'val_metrics': val_metrics,
                    'test_metrics': test_metrics,
                    'metrics': test_metrics,  # For backward compatibility
                    'predictions': y_test_pred.tolist()[:5]
                }
                
                logger.info(f"\n  {model_info['name']}:")
                logger.info(f"    Train R² = {train_metrics['r2']:.4f}, RMSE = {train_metrics['rmse']:.2f}%")
                logger.info(f"    Val   R² = {val_metrics['r2']:.4f}, RMSE = {val_metrics['rmse']:.2f}%")
                logger.info(f"    Test  R² = {test_metrics['r2']:.4f}, RMSE = {test_metrics['rmse']:.2f}%")
                
                # Check for overfitting
                train_val_gap = train_metrics['r2'] - val_metrics['r2']
                train_test_gap = train_metrics['r2'] - test_metrics['r2']
                
                logger.info(f"\n    Overfitting Check:")
                logger.info(f"    Train-Val gap: {train_val_gap:.4f}")
                logger.info(f"    Train-Test gap: {train_test_gap:.4f}")
                
                if train_val_gap > Config.OVERFITTING_THRESHOLD:
                    logger.warning(f"    ⚠️ OVERFITTING DETECTED (gap > {Config.OVERFITTING_THRESHOLD})")
                else:
                    logger.info(f"    ✅ No significant overfitting (gap <= {Config.OVERFITTING_THRESHOLD})")
                
                # Check against requirements
                if Config.MODEL_A_EXPECTED_R2_MIN <= test_metrics['r2'] <= Config.MODEL_A_EXPECTED_R2_MAX:
                    logger.info(f"    ✅ Test R² within expected range ({Config.MODEL_A_EXPECTED_R2_MIN}-{Config.MODEL_A_EXPECTED_R2_MAX})")
                else:
                    logger.warning(f"    ⚠️ Test R² outside expected range ({Config.MODEL_A_EXPECTED_R2_MIN}-{Config.MODEL_A_EXPECTED_R2_MAX})")
    
    def generate_evaluation_plots(self):
        """Generate comprehensive evaluation plots for each algorithm"""
        output_dir = Config.get_output_path('model_a', 'evaluation')
        logger.info(f"\n📊 Generating evaluation plots to {output_dir}...")
        
        # Generate plots for each regression model separately
        for key, model_info in self.models.items():
            if model_info['type'] == 'regression':
                self._generate_algorithm_plot(key, model_info, output_dir)
        
        # Generate comparison plot
        self._generate_comparison_plot(output_dir)
        
        logger.info(f"✅ All evaluation plots saved to {output_dir}")
    
    def _generate_algorithm_plot(self, key, model_info, output_dir):
        """Generate detailed plot for one algorithm"""
        model = model_info['model']
        name = model_info['name']
        
        # Get predictions for all sets
        y_train_pred = model.predict(self.X_train)
        y_test_pred = model.predict(self.X_test)
        
        # Get metrics
        result = self.results[key]
        train_metrics = result['train_metrics']
        test_metrics = result['test_metrics']
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Model A - {name}', fontsize=16, fontweight='bold')
        
        # 1. Scatter plot: Actual vs Predicted (Test set)
        ax = axes[0, 0]
        ax.scatter(self.y_test, y_test_pred, alpha=0.6, s=30, color='blue', edgecolors='black', linewidth=0.5)
        ax.plot([self.y_test.min(), self.y_test.max()], 
               [self.y_test.min(), self.y_test.max()], 'r--', lw=2, label='Perfect Prediction')
        ax.set_xlabel('Actual ROI (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Predicted ROI (%)', fontsize=11, fontweight='bold')
        ax.set_title('Predictions (Test Set)', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, f'R² = {test_metrics["r2"]:.4f}\nRMSE = {test_metrics["rmse"]:.2f}%', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 2. Residual plot (Test set)
        ax = axes[0, 1]
        residuals = self.y_test.values - y_test_pred
        ax.scatter(y_test_pred, residuals, alpha=0.6, s=30, color='green', edgecolors='black', linewidth=0.5)
        ax.axhline(y=0, color='r', linestyle='--', lw=2)
        ax.set_xlabel('Predicted ROI (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Residuals (%)', fontsize=11, fontweight='bold')
        ax.set_title('Residual Plot (Test Set)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 3. R² Comparison (Train vs Test) - Overfitting Check
        ax = axes[1, 0]
        r2_values = [train_metrics['r2'], test_metrics['r2']]
        colors = ['#3498db', '#e74c3c']
        bars = ax.bar(['Train', 'Test'], r2_values, color=colors, edgecolor='black', linewidth=2)
        ax.set_ylabel('R² Score', fontsize=11, fontweight='bold')
        ax.set_title('R² Comparison (Overfitting Check)', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add values on bars
        for bar, r2 in zip(bars, r2_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02, 
                   f'{r2:.4f}', ha='center', fontsize=10, fontweight='bold')
        
        # Add overfitting indicator
        gap = train_metrics['r2'] - test_metrics['r2']
        gap_text = f'Gap: {gap:.4f}'
        if gap > Config.OVERFITTING_THRESHOLD:
            gap_text += '\n⚠️ Overfitting!'
            gap_color = 'red'
        else:
            gap_text += '\n✅ No overfitting'
            gap_color = 'green'
        ax.text(0.5, 0.5, gap_text, transform=ax.transAxes, 
               fontsize=11, ha='center', fontweight='bold', color=gap_color,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 4. Metrics Table
        ax = axes[1, 1]
        ax.axis('off')
        
        table_data = [
            ['Metric', 'Train', 'Test'],
            ['R²', f"{train_metrics['r2']:.4f}", f"{test_metrics['r2']:.4f}"],
            ['RMSE (%)', f"{train_metrics['rmse']:.2f}", f"{test_metrics['rmse']:.2f}"],
            ['MAE (%)', f"{train_metrics['mae']:.2f}", f"{test_metrics['mae']:.2f}"],
            ['Gap', '', f"{gap:.4f}"],
        ]
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.3, 0.35, 0.35])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(3):
            cell = table[(0, i)]
            cell.set_facecolor('#34495e')
            cell.set_text_props(weight='bold', color='white')
        
        # Style data rows
        for i in range(1, len(table_data)):
            for j in range(3):
                cell = table[(i, j)]
                cell.set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
        
        plt.tight_layout()
        plot_path = output_dir / f'model_a_{key}_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
    
    def _generate_comparison_plot(self, output_dir):
        """Generate comparison plot for all algorithms"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Model A - Algorithm Comparison', fontsize=16, fontweight='bold')
        
        # Collect data
        algorithms = []
        train_r2 = []
        test_r2 = []
        test_rmse = []
        
        for key, result in self.results.items():
            algorithms.append(result['name'].replace(' + ', '+\n'))
            train_r2.append(result['train_metrics']['r2'])
            test_r2.append(result['test_metrics']['r2'])
            test_rmse.append(result['test_metrics']['rmse'])
        
        # 1. R² Comparison
        ax = axes[0]
        x = np.arange(len(algorithms))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, train_r2, width, label='Train', color='#3498db', edgecolor='black')
        bars2 = ax.bar(x + width/2, test_r2, width, label='Test', color='#e74c3c', edgecolor='black')
        
        ax.set_ylabel('R² Score', fontsize=11, fontweight='bold')
        ax.set_title('R² Score Comparison', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, fontsize=9)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1])
        
        # Add values on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.3f}', ha='center', fontsize=8, fontweight='bold')
        
        # 2. RMSE Comparison
        ax = axes[1]
        bars = ax.bar(algorithms, test_rmse, color='#2ecc71', edgecolor='black', linewidth=2)
        ax.set_ylabel('RMSE (%)', fontsize=11, fontweight='bold')
        ax.set_title('Test RMSE Comparison', fontsize=12, fontweight='bold')
        ax.set_xticklabels(algorithms, fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add values on bars
        for bar, rmse in zip(bars, test_rmse):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rmse:.2f}%', ha='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plot_path = output_dir / 'model_a_comparison.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
        
        # Save metadata
        metadata = {
            'model_name': 'Model A - Crop Recommendation',
            'evaluation_type': 'roi_prediction',
            'timestamp': datetime.now().isoformat(),
            'results': self.results
        }
        
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✅ Saved: {metadata_path}")
    
    def save_models(self):
        """Save best models as .pkl"""
        
        logger.info("\n💾 Saving models...")
        
        for key, model_info in self.models.items():
            filepath = Config.get_model_path(f'model_a_{key}')
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_info['model'], f)
            
            logger.info(f"  ✅ {filepath}")
    
    def save_results(self):
        """Save evaluation results as JSON"""
        
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_a_evaluation.json'
        
        # Find best algorithm
        best_algo = None
        best_r2 = -999
        for key, result in self.results.items():
            if result['metrics']['r2'] > best_r2:
                best_r2 = result['metrics']['r2']
                best_algo = key
        
        # Prepare results
        results_data = {
            'model': 'Model A - Crop Recommendation',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'algorithms': self.results,
            'summary': {
                'best_algorithm': best_algo,
                'best_r2': best_r2,
                'note': 'All algorithms use CLEAN data (no post-outcome features)'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL A TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\nBest Algorithm: {best_algo}")
        logger.info(f"  R² = {best_r2:.4f}")
        logger.info(f"  RMSE = {self.results[best_algo]['metrics']['rmse']:.4f}%")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_a', 'evaluation')}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL A - CROP RECOMMENDATION SYSTEM".center(80))
    print("="*80)
    
    trainer = ModelATrainer()
    
    # Load data
    df = trainer.load_data()
    
    # Split data
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data(df)
    
    # Train models
    trainer.train_models(X_train, y_train, X_val, y_val)
    
    # Evaluate models (check overfitting)
    trainer.evaluate_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Generate plots
    trainer.generate_evaluation_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

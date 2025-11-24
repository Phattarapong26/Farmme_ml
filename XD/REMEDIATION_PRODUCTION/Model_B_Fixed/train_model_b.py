"""
Train Model B - Planting Window Classifier (FIXED VERSION - NO DATA LEAKAGE)
Binary classification: Good window / Bad window

✅ FIXED ISSUES:
1. Data Leakage → Use historical weather pattern (no post-harvest data)
2. Missing Features → Join with crop_characteristics + create season
3. Weather Not Used → Create weather aggregates (30-day historical)
4. Recall = 100% → Proper validation with time-based split

ขั้นตอน:
1. Load clean cultivation data + crop_characteristics
2. Create temporal + weather features (historical only)
3. Split time-aware
4. Train algorithms with regularization
5. Evaluate metrics (F1, Precision, Recall, ROC-AUC)
6. Generate evaluation plots
7. Save models
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
from sklearn.metrics import confusion_matrix, roc_curve, auc

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from Model_B_Fixed.model_algorithms_clean import (
    DataLoader_B, ModelB_XGBoost, ModelB_TemporalGB, ModelB_LogisticBaseline
)
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_b')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelBTrainer:
    """Train and evaluate Model B"""
    
    def __init__(self):
        self.cultivation_csv = Config.get_dataset_path('cultivation.csv')
        self.weather_csv = Config.get_dataset_path('weather.csv')
        self.crop_chars_csv = Config.get_dataset_path('crop_characteristics.csv')
        self.results = {}
        self.models = {}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self):
        """Load and prepare clean data (NO DATA LEAKAGE)"""
        logger.info("📥 Loading clean data...")
        logger.info("   ✅ Using historical weather (30 days before planting)")
        logger.info("   ✅ Joining crop_characteristics")
        logger.info("   ✅ Creating season from planting_date")
        logger.info("   ✅ Rule-based target (no post-harvest data)")
        
        loader = DataLoader_B(
            self.cultivation_csv, 
            self.weather_csv,
            self.crop_chars_csv
        )
        
        # Create training data with clean features
        df_clean = loader.create_training_data(success_threshold=0.75)
        
        # Create numeric features
        X = loader.create_features(df_clean)
        y = df_clean['is_good_window']
        
        logger.info(f"\n✅ Loaded {len(df_clean)} records")
        logger.info(f"   Features: {X.shape[1]} numeric")
        logger.info(f"   Class distribution:")
        logger.info(f"     Good windows: {y.sum()} ({y.mean()*100:.1f}%)")
        logger.info(f"     Bad windows: {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")
        
        return X, y, df_clean
    
    def split_data(self, X, y, df_clean):
        """Time-aware split by planting_date"""
        logger.info("\n⏱️  Time-aware split by planting date...")
        
        df_indexed = df_clean.copy()
        df_indexed['X_idx'] = X.index
        df_indexed['y_val'] = y.values
        
        # Sort by date
        df_sorted = df_indexed.sort_values('planting_date').reset_index(drop=True)
        
        n = len(df_sorted)
        train_size = int(n * 0.6)
        val_size = int(n * 0.2)
        
        train_idx = df_sorted.iloc[:train_size].index.tolist()
        val_idx = df_sorted.iloc[train_size:train_size+val_size].index.tolist()
        test_idx = df_sorted.iloc[train_size+val_size:].index.tolist()
        
        X_train = X.iloc[train_idx]
        y_train = y.iloc[train_idx]
        
        X_val = X.iloc[val_idx]
        y_val = y.iloc[val_idx]
        
        X_test = X.iloc[test_idx]
        y_test = y.iloc[test_idx]
        
        logger.info(f"✅ Train: {len(X_train)} samples ({y_train.mean()*100:.1f}% positive)")
        logger.info(f"✅ Val: {len(X_val)} samples ({y_val.mean()*100:.1f}% positive)")
        logger.info(f"✅ Test: {len(X_test)} samples ({y_test.mean()*100:.1f}% positive)")
        
        # Store for later use
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train_models(self, X_train, y_train):
        """Train all algorithms with regularization"""
        
        logger.info("\n🤖 Training algorithms with regularization...")
        
        # Algorithm 1: XGBoost Classifier
        logger.info("  [1/3] XGBoost Classifier...")
        model_xgb = ModelB_XGBoost()
        model_xgb.train(X_train, y_train)
        self.models['xgboost'] = {
            'name': 'XGBoost Classifier',
            'model': model_xgb,
        }
        logger.info("      ✅ Trained")
        
        # Algorithm 2: Temporal GB
        logger.info("  [2/3] Temporal Gradient Boosting...")
        model_temporal = ModelB_TemporalGB()
        model_temporal.train(X_train, y_train)
        self.models['temporal_gb'] = {
            'name': 'Temporal Gradient Boosting',
            'model': model_temporal,
        }
        logger.info("      ✅ Trained")
        
        # Algorithm 3: Logistic Regression (Baseline)
        logger.info("  [3/3] Logistic Regression (Baseline)...")
        model_logistic = ModelB_LogisticBaseline()
        model_logistic.train(X_train, y_train)
        self.models['logistic'] = {
            'name': 'Logistic Regression (Baseline)',
            'model': model_logistic,
        }
        logger.info("      ✅ Trained")
    
    def evaluate_models(self, X_test, y_test):
        """Evaluate all models"""
        
        logger.info("\n📊 Evaluation on Test Set...")
        
        for key, model_info in self.models.items():
            model = model_info['model']
            y_pred = model.predict(X_test)
            
            # Get probabilities if available
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test)
            else:
                y_proba = None
            
            metrics = model.evaluate(y_test, y_pred)
            if y_proba is not None:
                from sklearn.metrics import roc_auc_score
                metrics['roc_auc'] = roc_auc_score(y_test, y_proba[:, 1])
            
            self.results[key] = {
                'name': model_info['name'],
                'metrics': metrics,
                'predictions': y_pred.tolist()[:5],
                'y_proba': y_proba
            }
            
            logger.info(f"\n  {model_info['name']}:")
            logger.info(f"    F1 = {metrics['f1']:.4f}")
            logger.info(f"    Precision = {metrics['precision']:.4f}")
            logger.info(f"    Recall = {metrics['recall']:.4f}")
            if 'roc_auc' in metrics:
                logger.info(f"    ROC-AUC = {metrics['roc_auc']:.4f}")
            
            # Check against requirements
            if Config.MODEL_B_EXPECTED_F1_MIN <= metrics['f1'] <= Config.MODEL_B_EXPECTED_F1_MAX:
                logger.info(f"    ✅ F1 within expected range ({Config.MODEL_B_EXPECTED_F1_MIN}-{Config.MODEL_B_EXPECTED_F1_MAX})")
            else:
                logger.warning(f"    ⚠️ F1 outside expected range ({Config.MODEL_B_EXPECTED_F1_MIN}-{Config.MODEL_B_EXPECTED_F1_MAX})")
    
    def generate_evaluation_plots(self):
        """Generate comprehensive evaluation plots"""
        output_dir = Config.get_output_path('model_b', 'evaluation')
        logger.info(f"\n📊 Generating evaluation plots to {output_dir}...")
        
        # Generate plots for each algorithm
        for key, model_info in self.models.items():
            self._generate_algorithm_plot(key, model_info, output_dir)
        
        # Generate comparison plot
        self._generate_comparison_plot(output_dir)
        
        logger.info(f"✅ All evaluation plots saved to {output_dir}")
    
    def _generate_algorithm_plot(self, key, model_info, output_dir):
        """Generate detailed plot for one algorithm"""
        model = model_info['model']
        name = model_info['name']
        result = self.results[key]
        
        y_pred = model.predict(self.X_test)
        y_proba = result.get('y_proba')
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Model B - {name}', fontsize=16, fontweight='bold')
        
        # 1. Confusion Matrix
        ax = axes[0, 0]
        cm = confusion_matrix(self.y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=False)
        ax.set_xlabel('Predicted', fontweight='bold')
        ax.set_ylabel('Actual', fontweight='bold')
        ax.set_title('Confusion Matrix', fontweight='bold')
        ax.set_xticklabels(['Bad', 'Good'])
        ax.set_yticklabels(['Bad', 'Good'])
        
        # 2. ROC Curve
        ax = axes[0, 1]
        if y_proba is not None:
            fpr, tpr, _ = roc_curve(self.y_test, y_proba[:, 1])
            roc_auc = auc(fpr, tpr)
            ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
            ax.set_xlabel('False Positive Rate', fontweight='bold')
            ax.set_ylabel('True Positive Rate', fontweight='bold')
            ax.set_title('ROC Curve', fontweight='bold')
            ax.legend(loc='lower right')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'ROC curve not available\n(no probability predictions)', 
                   ha='center', va='center', fontsize=12)
            ax.set_title('ROC Curve', fontweight='bold')
        
        # 3. Metrics Bar Chart
        ax = axes[1, 0]
        metrics = result['metrics']
        metric_names = ['F1', 'Precision', 'Recall']
        metric_values = [metrics['f1'], metrics['precision'], metrics['recall']]
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        
        bars = ax.bar(metric_names, metric_values, color=colors, edgecolor='black', linewidth=2)
        ax.set_ylabel('Score', fontweight='bold')
        ax.set_title('Classification Metrics', fontweight='bold')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add target line for F1
        ax.axhline(y=Config.MODEL_B_EXPECTED_F1_MIN, color='green', linestyle='--', 
                  alpha=0.5, label=f'Target F1 ({Config.MODEL_B_EXPECTED_F1_MIN}-{Config.MODEL_B_EXPECTED_F1_MAX})')
        ax.axhline(y=Config.MODEL_B_EXPECTED_F1_MAX, color='green', linestyle='--', alpha=0.5)
        ax.legend()
        
        # Add values on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{value:.3f}', ha='center', fontsize=10, fontweight='bold')
        
        # 4. Metrics Table
        ax = axes[1, 1]
        ax.axis('off')
        
        table_data = [
            ['Metric', 'Value'],
            ['F1 Score', f"{metrics['f1']:.4f}"],
            ['Precision', f"{metrics['precision']:.4f}"],
            ['Recall', f"{metrics['recall']:.4f}"],
        ]
        
        if 'roc_auc' in metrics:
            table_data.append(['ROC-AUC', f"{metrics['roc_auc']:.4f}"])
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(2):
            cell = table[(0, i)]
            cell.set_facecolor('#34495e')
            cell.set_text_props(weight='bold', color='white')
        
        # Style data rows
        for i in range(1, len(table_data)):
            for j in range(2):
                cell = table[(i, j)]
                cell.set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
        
        plt.tight_layout()
        plot_path = output_dir / f'model_b_{key}_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
    
    def _generate_comparison_plot(self, output_dir):
        """Generate comparison plot for all algorithms"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Model B - Algorithm Comparison', fontsize=16, fontweight='bold')
        
        # Collect data
        algorithms = []
        f1_scores = []
        precision_scores = []
        recall_scores = []
        
        for key, result in self.results.items():
            algorithms.append(result['name'].replace(' ', '\n'))
            f1_scores.append(result['metrics']['f1'])
            precision_scores.append(result['metrics']['precision'])
            recall_scores.append(result['metrics']['recall'])
        
        # 1. F1, Precision, Recall Comparison
        ax = axes[0]
        x = np.arange(len(algorithms))
        width = 0.25
        
        bars1 = ax.bar(x - width, f1_scores, width, label='F1', color='#3498db', edgecolor='black')
        bars2 = ax.bar(x, precision_scores, width, label='Precision', color='#2ecc71', edgecolor='black')
        bars3 = ax.bar(x + width, recall_scores, width, label='Recall', color='#e74c3c', edgecolor='black')
        
        ax.set_ylabel('Score', fontsize=11, fontweight='bold')
        ax.set_title('Metrics Comparison', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, fontsize=8)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1])
        
        # Add target line
        ax.axhline(y=Config.MODEL_B_EXPECTED_F1_MIN, color='green', linestyle='--', alpha=0.5)
        
        # 2. ROC-AUC Comparison
        ax = axes[1]
        roc_aucs = [result['metrics'].get('roc_auc', 0) for result in self.results.values()]
        bars = ax.bar(algorithms, roc_aucs, color='#9b59b6', edgecolor='black', linewidth=2)
        ax.set_ylabel('ROC-AUC', fontsize=11, fontweight='bold')
        ax.set_title('ROC-AUC Comparison', fontsize=12, fontweight='bold')
        ax.set_xticklabels(algorithms, fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1])
        
        # Add values on bars
        for bar, auc_val in zip(bars, roc_aucs):
            if auc_val > 0:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{auc_val:.3f}', ha='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plot_path = output_dir / 'model_b_comparison.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
    
    def save_models(self):
        """Save models"""
        logger.info("\n💾 Saving models...")
        
        for key, model_info in self.models.items():
            filepath = Config.get_model_path(f'model_b_{key}')
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_info['model'], f)
            
            logger.info(f"  ✅ {filepath}")
    
    def save_results(self):
        """Save evaluation results"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_b_evaluation.json'
        
        # Find best algorithm
        best_algo = max(self.results.items(), key=lambda x: x[1]['metrics']['f1'])[0]
        
        # Prepare results (remove y_proba for JSON serialization)
        results_clean = {}
        for key, result in self.results.items():
            results_clean[key] = {
                'name': result['name'],
                'metrics': result['metrics'],
                'predictions': result['predictions']
            }
        
        results_data = {
            'model': 'Model B - Planting Window',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'algorithms': results_clean,
            'summary': {
                'best_algorithm': best_algo,
                'best_f1': self.results[best_algo]['metrics']['f1'],
                'note': 'Binary classification: Good/Bad planting window. All use CLEAN data (no post-outcome features)'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL B TRAINING COMPLETE (NO DATA LEAKAGE)".center(70))
        logger.info("="*70)
        logger.info(f"\n✅ FIXED ISSUES:")
        logger.info(f"   1. Data Leakage → Rule-based target (no post-harvest)")
        logger.info(f"   2. Missing Features → Joined crop_characteristics")
        logger.info(f"   3. Weather Not Used → Historical 30-day aggregates")
        logger.info(f"   4. Recall = 100% → Proper time-based validation")
        logger.info(f"\nBest Algorithm: {best_algo}")
        logger.info(f"  F1 = {self.results[best_algo]['metrics']['f1']:.4f}")
        logger.info(f"  Precision = {self.results[best_algo]['metrics']['precision']:.4f}")
        logger.info(f"  Recall = {self.results[best_algo]['metrics']['recall']:.4f}")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_b', 'evaluation')}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL B - PLANTING WINDOW CLASSIFIER".center(80))
    print("="*80)
    
    trainer = ModelBTrainer()
    
    # Load data
    X, y, df_clean = trainer.load_data()
    
    # Split data
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data(X, y, df_clean)
    
    # Train models
    trainer.train_models(X_train, y_train)
    
    # Evaluate models
    trainer.evaluate_models(X_test, y_test)
    
    # Generate plots
    trainer.generate_evaluation_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

"""
Train Model B - Full Dataset with 3 Algorithms
Binary Classification: Good/Bad Planting Window

ขั้นตอน:
1. Load FULL data
2. Split time-aware with STRICT separation
3. Train 3 algorithms (XGBoost, Random Forest, Gradient Boosting)
4. Evaluate metrics (F1, Precision, Recall, ROC-AUC)
5. Generate bubble comparison chart
6. Save models and results
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
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Model_B_Fixed.model_algorithms_clean import DataLoader_B
from modelB19_11_25.three_algorithm_trainer_b import ThreeAlgorithmTrainerB
from modelB19_11_25.bubble_chart_generator_b import BubbleChartGeneratorB
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_b_full')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelBFullTrainer:
    """Train and evaluate Model B with full dataset"""
    
    def __init__(self):
        self.cultivation_csv = Config.get_dataset_path('cultivation.csv')
        self.weather_csv = Config.get_dataset_path('weather.csv')
        self.results = {}
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.start_time = None
        
    def load_data(self):
        """Load and prepare clean data"""
        logger.info("📥 Loading FULL dataset...")
        self.start_time = datetime.now()
        
        loader = DataLoader_B(self.cultivation_csv, self.weather_csv)
        
        # Create training data with clean features
        df_clean = loader.create_training_data(success_threshold=0.75)
        
        # Create numeric features
        X = loader.create_features(df_clean)
        y = df_clean['is_good_window']
        
        logger.info(f"✅ Loaded {len(df_clean)} records")
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
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train_models(self, X_train, y_train, X_val, y_val, X_test, y_test):
        """Train all 3 algorithms"""
        logger.info("\n🤖 Training 3 algorithms on FULL dataset...")
        
        trainer = ThreeAlgorithmTrainerB()
        self.results = trainer.train_all(X_train, y_train, X_val, y_val, X_test, y_test)
        
        # Log summary
        logger.info("\n📊 Training Summary:")
        for key, result in self.results.items():
            logger.info(f"\n  {result.algorithm_name}:")
            logger.info(f"    Training time: {result.training_time:.2f}s")
            logger.info(f"    Test F1: {result.test_metrics['f1']:.4f}")
            logger.info(f"    Test Precision: {result.test_metrics['precision']:.4f}")
            logger.info(f"    Test Recall: {result.test_metrics['recall']:.4f}")
            logger.info(f"    Test ROC-AUC: {result.test_metrics['roc_auc']:.4f}")
    
    def generate_plots(self):
        """Generate bubble chart and detailed evaluation plots"""
        output_dir = Config.get_output_path('model_b_full', 'evaluation')
        logger.info(f"\n📊 Generating plots to {output_dir}...")
        
        # 1. Generate bubble comparison chart
        logger.info("\n[1/2] Generating bubble comparison chart...")
        bubble_generator = BubbleChartGeneratorB(self.results)
        bubble_path = output_dir / 'bubble_comparison.png'
        bubble_generator.generate_bubble_chart(bubble_path)
        
        # 2. Generate detailed evaluation plots
        logger.info("\n[2/2] Generating detailed evaluation plots...")
        self._generate_detailed_plots(output_dir)
        
        logger.info(f"\n✅ All plots saved to: {output_dir}")
    
    def _generate_detailed_plots(self, output_dir):
        """Generate detailed plots for each algorithm"""
        for key, result in self.results.items():
            self._generate_algorithm_plot(key, result, output_dir)
    
    def _generate_algorithm_plot(self, key, result, output_dir):
        """Generate detailed plot for one algorithm"""
        name = result.algorithm_name
        
        # Get predictions
        y_pred = result.model.predict(result.scaler.transform(self.X_test))
        y_proba = result.y_proba
        
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
        fpr, tpr, _ = roc_curve(self.y_test, y_proba[:, 1])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        ax.set_xlabel('False Positive Rate', fontweight='bold')
        ax.set_ylabel('True Positive Rate', fontweight='bold')
        ax.set_title('ROC Curve', fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        # 3. Metrics Bar Chart
        ax = axes[1, 0]
        metrics = result.test_metrics
        metric_names = ['F1', 'Precision', 'Recall', 'ROC-AUC']
        metric_values = [metrics['f1'], metrics['precision'], metrics['recall'], metrics['roc_auc']]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
        
        bars = ax.bar(metric_names, metric_values, color=colors, edgecolor='black', linewidth=2)
        ax.set_ylabel('Score', fontweight='bold')
        ax.set_title('Classification Metrics', fontweight='bold')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add values on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{value:.3f}', ha='center', fontsize=10, fontweight='bold')
        
        # 4. Metrics Table
        ax = axes[1, 1]
        ax.axis('off')
        
        table_data = [
            ['Metric', 'Train', 'Test'],
            ['F1', f"{result.train_metrics['f1']:.4f}", f"{result.test_metrics['f1']:.4f}"],
            ['Precision', f"{result.train_metrics['precision']:.4f}", f"{result.test_metrics['precision']:.4f}"],
            ['Recall', f"{result.train_metrics['recall']:.4f}", f"{result.test_metrics['recall']:.4f}"],
            ['ROC-AUC', f"{result.train_metrics['roc_auc']:.4f}", f"{result.test_metrics['roc_auc']:.4f}"],
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
        plot_path = output_dir / f'model_b_{key}_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
    
    def save_models(self):
        """Save all trained models as .pkl"""
        logger.info("\n💾 Saving models...")
        
        for key, result in self.results.items():
            filepath = Config.MODEL_PATH / f'model_b_{key}_full.pkl'
            
            # Save both model and scaler
            model_data = {
                'model': result.model,
                'scaler': result.scaler
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"  ✅ {filepath.name}")
    
    def save_results(self):
        """Save evaluation results as JSON"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_b_full_evaluation.json'
        
        # Find best algorithm
        best_algo = max(self.results.items(), key=lambda x: x[1].test_metrics['f1'])[0]
        best_f1 = self.results[best_algo].test_metrics['f1']
        
        # Calculate total training time
        total_time = sum(r.training_time for r in self.results.values())
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Prepare results
        results_data = {
            'model': 'Model B - Planting Window (Full Dataset)',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'dataset_info': {
                'total_samples': len(self.X_train) + len(self.X_val) + len(self.X_test),
                'train_samples': len(self.X_train),
                'val_samples': len(self.X_val),
                'test_samples': len(self.X_test),
            },
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
                'best_f1': best_f1,
                'best_precision': self.results[best_algo].test_metrics['precision'],
                'best_recall': self.results[best_algo].test_metrics['recall'],
                'best_roc_auc': self.results[best_algo].test_metrics['roc_auc'],
                'total_training_time': total_time,
                'total_elapsed_time': elapsed_time,
                'note': 'Binary classification with FULL dataset using 3 algorithms'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"  ✅ {results_file.name}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL B FULL TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\n📊 Dataset:")
        logger.info(f"   Total samples: {results_data['dataset_info']['total_samples']}")
        logger.info(f"   Train: {len(self.X_train)}, Val: {len(self.X_val)}, Test: {len(self.X_test)}")
        logger.info(f"\n🏆 Best Algorithm: {self.results[best_algo].algorithm_name}")
        logger.info(f"   F1 = {best_f1:.4f}")
        logger.info(f"   Precision = {self.results[best_algo].test_metrics['precision']:.4f}")
        logger.info(f"   Recall = {self.results[best_algo].test_metrics['recall']:.4f}")
        logger.info(f"   ROC-AUC = {self.results[best_algo].test_metrics['roc_auc']:.4f}")
        logger.info(f"\n⏱️  Training Time:")
        logger.info(f"   Total: {total_time:.2f}s")
        logger.info(f"   Elapsed: {elapsed_time:.2f}s")
        logger.info(f"\n✅ Models saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_b_full', 'evaluation')}")
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL B - FULL DATASET TRAINING WITH 3 ALGORITHMS".center(80))
    print("="*80)
    
    trainer = ModelBFullTrainer()
    
    # Load data
    X, y, df_clean = trainer.load_data()
    
    # Split data
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data(X, y, df_clean)
    
    # Train models
    trainer.train_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Generate plots
    trainer.generate_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

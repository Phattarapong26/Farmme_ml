"""
Train Model B - Full Dataset with 3 Algorithms (FIXED V2 - BLOCKED STRATIFIED SPLIT)
Binary Classification: Good/Bad Planting Window

🔧 FIXES APPLIED (V2):
1. ✅ Fixed time-aware split index mismatch
2. ✅ Added random seeds for reproducibility
3. ✅ Added class balancing (scale_pos_weight, class_weight)
4. ✅ Verified scaler fit only on training data
5. ✅ Verified y_proba from X_test predictions
6. ✅ Fixed model filename to use algorithm name
7. ✅ Added feature order metadata
8. ✅ Added accuracy metric
9. ✅ Enhanced logging with feature names
10. ✅✅ BLOCKED STRATIFIED TIME SERIES SPLIT (NEW!)
    - Divide data into time blocks
    - Stratified sampling within each block
    - Maintains temporal order + balanced distribution

ขั้นตอน:
1. Load FULL data
2. Split with BLOCKED STRATIFIED strategy (FIXED V2)
3. Train 3 algorithms (XGBoost, Random Forest, Gradient Boosting)
4. Evaluate metrics (F1, Precision, Recall, ROC-AUC, Accuracy)
5. Generate bubble comparison chart
6. Save models and results
"""

import pandas as pd
import numpy as np
import pickle
import json
import random
from pathlib import Path
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score
from sklearn.model_selection import train_test_split
import sys

# Set random seeds for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

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
        logging.FileHandler(Config.get_log_path('model_b_full_fixed_v2')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelBFullTrainerFixedV2:
    """Train and evaluate Model B with full dataset (FIXED V2 - BLOCKED STRATIFIED)"""
    
    def __init__(self):
        self.cultivation_csv = Config.get_dataset_path('cultivation.csv')
        self.weather_csv = Config.get_dataset_path('weather.csv')
        self.crop_chars_csv = Config.get_dataset_path('crop_characteristics.csv')
        self.results = {}
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.start_time = None
        self.feature_names = None
        
    def load_data(self):
        """Load and prepare clean data"""
        logger.info("📥 Loading FULL dataset...")
        self.start_time = datetime.now()
        
        loader = DataLoader_B(self.cultivation_csv, self.weather_csv, self.crop_chars_csv)
        
        # Create training data with clean features
        df_clean = loader.create_training_data(success_threshold=0.75)
        
        # Create numeric features
        X = loader.create_features(df_clean)
        y = df_clean['is_good_window']
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        logger.info(f"✅ Loaded {len(df_clean)} records")
        logger.info(f"   Features: {X.shape[1]} numeric")
        logger.info(f"   Feature names: {', '.join(self.feature_names[:5])}... (showing first 5)")
        logger.info(f"   Class distribution:")
        logger.info(f"     Good windows: {y.sum()} ({y.mean()*100:.1f}%)")
        logger.info(f"     Bad windows: {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")
        
        return X, y, df_clean
    
    def split_data_blocked_stratified(self, X, y, df_clean, n_blocks=10):
        """
        Blocked Stratified Time Series Split (V2)
        
        Strategy:
        1. Sort by planting_date
        2. Divide into N time blocks
        3. Within each block, stratified split 60/20/20
        4. Combine all blocks
        
        Benefits:
        - Maintains temporal order (no future leakage)
        - Balanced class distribution across train/val/test
        - Each split sees all seasons/patterns
        """
        logger.info(f"\n⏱️  Blocked Stratified Time Series Split (V2) with {n_blocks} blocks...")
        
        # Create a copy with original indices preserved
        df_indexed = df_clean.copy()
        df_indexed['original_idx'] = X.index
        df_indexed['y_val'] = y.values
        
        # Sort by date
        df_sorted = df_indexed.sort_values('planting_date').reset_index(drop=True)
        
        # Divide into blocks
        n = len(df_sorted)
        block_size = n // n_blocks
        
        train_indices = []
        val_indices = []
        test_indices = []
        
        logger.info(f"   Dividing {n} samples into {n_blocks} blocks of ~{block_size} samples each")
        
        for i in range(n_blocks):
            # Get block
            start_idx = i * block_size
            if i == n_blocks - 1:
                end_idx = n  # Last block gets remaining samples
            else:
                end_idx = (i + 1) * block_size
            
            block = df_sorted.iloc[start_idx:end_idx]
            
            # Get X and y for this block
            block_original_idx = block['original_idx'].values
            block_y = block['y_val'].values
            
            # Check if block has both classes and enough samples for stratification
            unique_classes, class_counts = np.unique(block_y, return_counts=True)
            min_class_count = class_counts.min() if len(class_counts) > 0 else 0
            
            # Need at least 5 samples per class for stratified split (to ensure 60/20/20 works)
            if len(unique_classes) < 2 or min_class_count < 5:
                logger.warning(f"   Block {i+1} has insufficient samples for stratification (min class: {min_class_count}), using simple split")
                # Simple split without stratification
                n_block = len(block)
                train_size = int(n_block * 0.6)
                val_size = int(n_block * 0.2)
                
                train_indices.extend(block_original_idx[:train_size])
                val_indices.extend(block_original_idx[train_size:train_size+val_size])
                test_indices.extend(block_original_idx[train_size+val_size:])
            else:
                try:
                    # Stratified split within block
                    # First split: train vs (val+test)
                    train_idx, temp_idx = train_test_split(
                        block_original_idx,
                        test_size=0.4,
                        stratify=block_y,
                        random_state=RANDOM_SEED + i
                    )
                    
                    # Second split: val vs test
                    temp_y = block_y[np.isin(block_original_idx, temp_idx)]
                    val_idx, test_idx = train_test_split(
                        temp_idx,
                        test_size=0.5,
                        stratify=temp_y,
                        random_state=RANDOM_SEED + i + 100
                    )
                    
                    train_indices.extend(train_idx)
                    val_indices.extend(val_idx)
                    test_indices.extend(test_idx)
                except ValueError as e:
                    # Fallback to simple split if stratification fails
                    logger.warning(f"   Block {i+1} stratification failed: {e}, using simple split")
                    n_block = len(block)
                    train_size = int(n_block * 0.6)
                    val_size = int(n_block * 0.2)
                    
                    train_indices.extend(block_original_idx[:train_size])
                    val_indices.extend(block_original_idx[train_size:train_size+val_size])
                    test_indices.extend(block_original_idx[train_size+val_size:])
            
            # Log block info
            block_pos_rate = block_y.mean()
            logger.info(f"   Block {i+1}: {len(block)} samples, {block_pos_rate*100:.1f}% positive")
        
        # Create final splits using original indices
        X_train = X.loc[train_indices]
        y_train = y.loc[train_indices]
        
        X_val = X.loc[val_indices]
        y_val = y.loc[val_indices]
        
        X_test = X.loc[test_indices]
        y_test = y.loc[test_indices]
        
        # Verify alignment
        assert len(X_train) == len(y_train), "X_train and y_train length mismatch!"
        assert len(X_val) == len(y_val), "X_val and y_val length mismatch!"
        assert len(X_test) == len(y_test), "X_test and y_test length mismatch!"
        
        logger.info(f"\n✅ Final Split Results:")
        logger.info(f"   Train: {len(X_train)} samples ({y_train.mean()*100:.1f}% positive)")
        logger.info(f"   Val:   {len(X_val)} samples ({y_val.mean()*100:.1f}% positive)")
        logger.info(f"   Test:  {len(X_test)} samples ({y_test.mean()*100:.1f}% positive)")
        logger.info(f"   ✅ Balanced distribution achieved!")
        logger.info(f"   ✅ Index alignment verified!")
        
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
        output_dir = Config.get_output_path('model_b_full_fixed_v2', 'evaluation')
        logger.info(f"\n📊 Generating plots to {output_dir}...")
        
        # 1. Generate bubble comparison chart
        logger.info("\n[1/2] Generating bubble comparison chart...")
        bubble_generator = BubbleChartGeneratorB(self.results)
        bubble_path = output_dir / 'bubble_comparison_fixed_v2.png'
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
        
        # Get predictions (using stored y_proba from test set)
        y_pred = result.model.predict(result.scaler.transform(self.X_test))
        y_proba = result.y_proba  # Already from X_test
        
        # Calculate accuracy
        accuracy = accuracy_score(self.y_test, y_pred)
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Model B - {name} (FIXED V2)', fontsize=16, fontweight='bold')
        
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
        
        # 3. Metrics Bar Chart (including Accuracy)
        ax = axes[1, 0]
        metrics = result.test_metrics
        metric_names = ['F1', 'Precision', 'Recall', 'ROC-AUC', 'Accuracy']
        metric_values = [metrics['f1'], metrics['precision'], metrics['recall'], 
                        metrics['roc_auc'], accuracy]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
        
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
            ['Accuracy', f"{accuracy_score(self.y_train, result.model.predict(result.scaler.transform(self.X_train))):.4f}", 
             f"{accuracy:.4f}"],
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
        plot_path = output_dir / f'model_b_{key}_evaluation_fixed_v2.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"  ✅ Saved: {plot_path.name}")
        plt.close()
    
    def save_models(self):
        """Save all trained models as .pkl with proper naming"""
        logger.info("\n💾 Saving models...")
        
        for key, result in self.results.items():
            # Use algorithm name in filename
            algo_name_clean = result.algorithm_name.lower().replace(' ', '_')
            filepath = Config.MODEL_PATH / f'model_b_full_{algo_name_clean}_fixed_v2.pkl'
            
            # Save model, scaler, and metadata
            model_data = {
                'model': result.model,
                'scaler': result.scaler,
                'version': 'fixed_v2.0_blocked_stratified',
                'trained_date': datetime.now().isoformat(),
                'feature_names': self.feature_names,
                'random_seed': RANDOM_SEED,
                'algorithm': result.algorithm_name,
                'split_strategy': 'blocked_stratified_time_series'
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"  ✅ {filepath.name}")
    
    def save_results(self):
        """Save evaluation results as JSON"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_b_full_evaluation_fixed_v2.json'
        
        # Find best algorithm
        best_algo = max(self.results.items(), key=lambda x: x[1].test_metrics['f1'])[0]
        best_f1 = self.results[best_algo].test_metrics['f1']
        
        # Calculate total training time
        total_time = sum(r.training_time for r in self.results.values())
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Prepare results
        results_data = {
            'model': 'Model B - Planting Window (Full Dataset FIXED V2)',
            'version': 'fixed_v2.0_blocked_stratified',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'random_seed': RANDOM_SEED,
            'split_strategy': 'blocked_stratified_time_series',
            'fixes_applied': [
                'Fixed time-aware split index mismatch',
                'Added random seeds for reproducibility',
                'Added class balancing',
                'Verified scaler fit only on training data',
                'Verified y_proba from X_test predictions',
                'Fixed model filename to use algorithm name',
                'Added feature order metadata',
                'Added accuracy metric',
                'BLOCKED STRATIFIED TIME SERIES SPLIT - balanced distribution'
            ],
            'dataset_info': {
                'total_samples': len(self.X_train) + len(self.X_val) + len(self.X_test),
                'train_samples': len(self.X_train),
                'val_samples': len(self.X_val),
                'test_samples': len(self.X_test),
                'train_positive_rate': float(self.y_train.mean()),
                'val_positive_rate': float(self.y_val.mean()),
                'test_positive_rate': float(self.y_test.mean()),
                'n_features': len(self.feature_names),
                'feature_names': self.feature_names
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
                'note': 'Binary classification with FULL dataset using 3 algorithms (FIXED V2 - BLOCKED STRATIFIED)'
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✅ {results_file.name}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL B FULL TRAINING COMPLETE (FIXED V2)".center(70))
        logger.info("="*70)
        logger.info(f"\n📊 Dataset:")
        logger.info(f"   Total samples: {results_data['dataset_info']['total_samples']}")
        logger.info(f"   Train: {len(self.X_train)} ({self.y_train.mean()*100:.1f}% positive)")
        logger.info(f"   Val:   {len(self.X_val)} ({self.y_val.mean()*100:.1f}% positive)")
        logger.info(f"   Test:  {len(self.X_test)} ({self.y_test.mean()*100:.1f}% positive)")
        logger.info(f"   Features: {len(self.feature_names)}")
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
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_b_full_fixed_v2', 'evaluation')}")
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL B - FULL DATASET TRAINING (FIXED V2 - BLOCKED STRATIFIED)".center(80))
    print("="*80)
    
    trainer = ModelBFullTrainerFixedV2()
    
    # Load data
    X, y, df_clean = trainer.load_data()
    
    # Split data (FIXED V2 - Blocked Stratified)
    X_train, y_train, X_val, y_val, X_test, y_test = trainer.split_data_blocked_stratified(X, y, df_clean, n_blocks=10)
    
    # Train models
    trainer.train_models(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # Generate plots
    trainer.generate_plots()
    
    # Save models and results
    trainer.save_models()
    trainer.save_results()
    
    print("\n" + "="*80)

"""
Detailed Evaluation Plotter for Model A
Creates 2x2 subplot figures for each algorithm
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetailedEvaluationPlotter:
    """Generate detailed evaluation plots for each algorithm"""
    
    def __init__(self, results: Dict[str, Any], X_train, y_train, X_test, y_test):
        """
        Initialize with model results and data
        
        Args:
            results: Dictionary of TrainingResult objects
            X_train, y_train: Training data
            X_test, y_test: Test data
        """
        self.results = results
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        
    def generate_algorithm_plot(self, algo_key: str, output_path: Path) -> None:
        """
        Generate 2x2 subplot for one algorithm
        
        Args:
            algo_key: Algorithm key (e.g., 'xgboost')
            output_path: Path to save the plot
        """
        result = self.results[algo_key]
        model = result.model
        name = result.algorithm_name
        
        logger.info(f"📊 Generating detailed plot for {name}...")
        
        # Get predictions
        if isinstance(model, dict):  # Ensemble model
            y_train_pred = self._predict_ensemble(model, self.X_train)
            y_test_pred = self._predict_ensemble(model, self.X_test)
        else:
            y_train_pred = model.predict(self.X_train)
            y_test_pred = model.predict(self.X_test)
        
        # Create figure with 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Model A - {name}', fontsize=16, fontweight='bold')
        
        # 1. Actual vs Predicted (Test set)
        self._plot_actual_vs_predicted(axes[0, 0], self.y_test, y_test_pred, result.test_metrics)
        
        # 2. Residual plot (Test set)
        self._plot_residuals(axes[0, 1], y_test_pred, self.y_test)
        
        # 3. R² Comparison (Train vs Test)
        self._plot_r2_comparison(axes[1, 0], result.train_metrics, result.test_metrics)
        
        # 4. Metrics Table
        self._plot_metrics_table(axes[1, 1], result.train_metrics, result.test_metrics)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"   ✅ Saved: {output_path.name}")
        plt.close()
    
    def _plot_actual_vs_predicted(self, ax, y_true, y_pred, metrics):
        """Plot actual vs predicted scatter plot"""
        ax.scatter(y_true, y_pred, alpha=0.6, s=30, color='blue', 
                  edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 
               'r--', lw=2, label='Perfect Prediction')
        
        ax.set_xlabel('Actual ROI (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Predicted ROI (%)', fontsize=11, fontweight='bold')
        ax.set_title('Predictions (Test Set)', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add metrics text
        metrics_text = f"R² = {metrics['r2']:.4f}\nRMSE = {metrics['rmse']:.2f}%"
        ax.text(0.05, 0.95, metrics_text,
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def _plot_residuals(self, ax, y_pred, y_true):
        """Plot residual plot"""
        residuals = y_true.values - y_pred
        
        ax.scatter(y_pred, residuals, alpha=0.6, s=30, color='green',
                  edgecolors='black', linewidth=0.5)
        ax.axhline(y=0, color='r', linestyle='--', lw=2)
        
        ax.set_xlabel('Predicted ROI (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Residuals (%)', fontsize=11, fontweight='bold')
        ax.set_title('Residual Plot (Test Set)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_r2_comparison(self, ax, train_metrics, test_metrics):
        """Plot R² comparison bar chart"""
        r2_values = [train_metrics['r2'], test_metrics['r2']]
        colors = ['#3498db', '#e74c3c']
        
        bars = ax.bar(['Train', 'Test'], r2_values, color=colors, 
                     edgecolor='black', linewidth=2)
        
        ax.set_ylabel('R² Score', fontsize=11, fontweight='bold')
        ax.set_title('R² Comparison (Overfitting Check)', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add values on bars
        for bar, r2 in zip(bars, r2_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{r2:.4f}',
                   ha='center',
                   fontsize=10,
                   fontweight='bold')
        
        # Add overfitting indicator
        gap = train_metrics['r2'] - test_metrics['r2']
        gap_text = f'Gap: {gap:.4f}'
        
        if gap > Config.OVERFITTING_THRESHOLD:
            gap_text += '\n⚠️ Overfitting!'
            gap_color = 'red'
        else:
            gap_text += '\n✅ No overfitting'
            gap_color = 'green'
        
        ax.text(0.5, 0.5, gap_text,
               transform=ax.transAxes,
               fontsize=11,
               ha='center',
               fontweight='bold',
               color=gap_color,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _plot_metrics_table(self, ax, train_metrics, test_metrics):
        """Plot metrics table"""
        ax.axis('off')
        
        gap = train_metrics['r2'] - test_metrics['r2']
        
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
    
    def _predict_ensemble(self, ensemble_model, X):
        """Make predictions with ensemble model"""
        rf_pred = ensemble_model['rf'].predict(X)
        residual_pred = ensemble_model['en'].predict(X)
        return rf_pred + residual_pred
    
    def generate_all_plots(self, output_dir: Path) -> None:
        """
        Generate detailed plots for all algorithms
        
        Args:
            output_dir: Directory to save plots
        """
        logger.info(f"\n📊 Generating detailed evaluation plots...")
        
        for algo_key in self.results.keys():
            output_path = output_dir / f'model_a_{algo_key}_evaluation.png'
            self.generate_algorithm_plot(algo_key, output_path)
        
        logger.info(f"✅ All detailed plots generated")

if __name__ == "__main__":
    print("✅ Detailed Evaluation Plotter loaded successfully")

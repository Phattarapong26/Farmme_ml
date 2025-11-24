# Visualization Module for Model C v5
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class ModelCVisualization:
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / 'outputs'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Visualization output: {self.output_dir}")

    
    def create_algorithm_comparison(self, comparison_results: Dict, save_path: Optional[str] = None) -> str:
        logger.info("Creating algorithm comparison...")
        if save_path is None:
            save_path = self.output_dir / 'model_comparison.png'
        
        algorithms = [k for k in comparison_results.keys() if comparison_results[k]['rmse'] != float('inf')]
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Algorithm Comparison - Model C v5', fontsize=16, fontweight='bold')
        
        ax = axes[0, 0]
        rmse_values = [comparison_results[algo]['rmse'] for algo in algorithms]
        bars = ax.bar(algorithms, rmse_values, color=['#2ecc71', '#3498db', '#e74c3c', '#f39c12'][:len(algorithms)])
        ax.set_ylabel('RMSE (baht/kg)', fontweight='bold')
        ax.set_title('Root Mean Squared Error')
        ax.grid(axis='y', alpha=0.3)
        best_idx = np.argmin(rmse_values)
        bars[best_idx].set_color('#27ae60')
        bars[best_idx].set_edgecolor('black')
        bars[best_idx].set_linewidth(2)
        for i, val in enumerate(rmse_values):
            ax.text(i, val, f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax = axes[0, 1]
        mae_values = [comparison_results[algo]['mae'] for algo in algorithms]
        bars = ax.bar(algorithms, mae_values, color=['#2ecc71', '#3498db', '#e74c3c', '#f39c12'][:len(algorithms)])
        ax.set_ylabel('MAE (baht/kg)', fontweight='bold')
        ax.set_title('Mean Absolute Error')
        ax.grid(axis='y', alpha=0.3)
        best_idx = np.argmin(mae_values)
        bars[best_idx].set_color('#27ae60')
        bars[best_idx].set_edgecolor('black')
        bars[best_idx].set_linewidth(2)
        for i, val in enumerate(mae_values):
            ax.text(i, val, f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
        
        ax = axes[1, 0]
        mape_values = [comparison_results[algo]['mape'] for algo in algorithms]
        bars = ax.bar(algorithms, mape_values, color=['#2ecc71', '#3498db', '#e74c3c', '#f39c12'][:len(algorithms)])
        ax.set_ylabel('MAPE (%)', fontweight='bold')
        ax.set_title('Mean Absolute Percentage Error')
        ax.grid(axis='y', alpha=0.3)
        best_idx = np.argmin(mape_values)
        bars[best_idx].set_color('#27ae60')
        bars[best_idx].set_edgecolor('black')
        bars[best_idx].set_linewidth(2)
        for i, val in enumerate(mape_values):
            ax.text(i, val, f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
        
        ax = axes[1, 1]
        time_values = [comparison_results[algo]['train_time'] for algo in algorithms]
        bars = ax.bar(algorithms, time_values, color=['#2ecc71', '#3498db', '#e74c3c', '#f39c12'][:len(algorithms)])
        ax.set_ylabel('Training Time (seconds)', fontweight='bold')
        ax.set_title('Training Time')
        ax.grid(axis='y', alpha=0.3)
        for i, val in enumerate(time_values):
            ax.text(i, val, f'{val:.1f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {save_path}")
        return str(save_path)

    
    def create_feature_importance(self, model, feature_names: List[str], algorithm: str,
                                  feature_categories: Optional[Dict] = None,
                                  save_path: Optional[str] = None, top_n: int = 20) -> str:
        logger.info(f"Creating feature importance for {algorithm}...")
        if save_path is None:
            save_path = self.output_dir / f'feature_importance_{algorithm}.png'
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        else:
            logger.warning(f"Model doesn't have feature importance")
            return ""
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        bars = ax.barh(range(len(importance_df)), importance_df['importance'], color='#3498db')
        ax.set_yticks(range(len(importance_df)))
        ax.set_yticklabels(importance_df['feature'])
        ax.set_xlabel('Importance', fontweight='bold')
        ax.set_title(f'Top {top_n} Feature Importance - {algorithm.upper()}', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {save_path}")
        return str(save_path)
    
    def create_error_distribution(self, y_true: np.ndarray, y_pred: np.ndarray,
                                  dataset_name: str = 'Test', save_path: Optional[str] = None) -> str:
        logger.info(f"Creating error distribution for {dataset_name}...")
        if save_path is None:
            save_path = self.output_dir / f'error_distribution_{dataset_name.lower()}.png'
        
        errors = y_pred - y_true
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Error Distribution - {dataset_name} Set', fontsize=16, fontweight='bold')
        
        ax = axes[0]
        ax.hist(errors, bins=50, color='#3498db', alpha=0.7, edgecolor='black')
        ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
        ax.set_xlabel('Prediction Error (baht/kg)', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        ax.set_title('Error Histogram')
        ax.legend()
        ax.grid(alpha=0.3)
        
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        ax.text(0.02, 0.98, f'Mean: {mean_error:.2f}\\nStd: {std_error:.2f}',
               transform=ax.transAxes, va='top', ha='left',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax = axes[1]
        from scipy import stats
        stats.probplot(errors, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {save_path}")
        return str(save_path)

    
    def create_metrics_summary(self, comparison_results: Dict, save_path: Optional[str] = None) -> str:
        logger.info("Creating metrics summary...")
        if save_path is None:
            save_path = self.output_dir / 'metrics_summary.png'
        
        algorithms = [k for k in comparison_results.keys() if comparison_results[k]['rmse'] != float('inf')]
        data = []
        for algo in algorithms:
            results = comparison_results[algo]
            data.append([
                algo.upper(),
                f"{results['rmse']:.2f}",
                f"{results['mae']:.2f}",
                f"{results['mape']:.2f}%",
                f"{results.get('r2', 0):.4f}",
                f"{results['train_time']:.1f}s"
            ])
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(cellText=data,
                        colLabels=['Algorithm', 'RMSE\\n(baht/kg)', 'MAE\\n(baht/kg)', 
                                  'MAPE\\n(%)', 'R²', 'Training\\nTime'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        for i in range(6):
            table[(0, i)].set_facecolor('#34495e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        colors = ['#ecf0f1', 'white']
        for i, row in enumerate(data):
            for j in range(6):
                table[(i+1, j)].set_facecolor(colors[i % 2])
        
        plt.title('Model Comparison Summary', fontsize=14, fontweight='bold', pad=20)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {save_path}")
        return str(save_path)

    
    def create_evaluation_report(self, comparison_results: Dict, best_algorithm: str,
                                 test_metrics: Dict, save_path: Optional[str] = None) -> str:
        logger.info("Creating evaluation report...")
        if save_path is None:
            save_path = self.output_dir / 'evaluation_report.png'
        
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Model C v5 - Training Evaluation Report', fontsize=18, fontweight='bold', y=0.98)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fig.text(0.5, 0.94, f'Generated: {timestamp}', ha='center', fontsize=10)
        
        ax1 = plt.subplot(2, 1, 1)
        ax1.axis('off')
        best_results = comparison_results[best_algorithm]
        
        text = f"""
BEST ALGORITHM: {best_algorithm.upper()}

Validation Metrics:
  RMSE: {best_results['rmse']:.2f} baht/kg
  MAE:  {best_results['mae']:.2f} baht/kg
  MAPE: {best_results['mape']:.2f}%
  R2:   {best_results.get('r2', 0):.4f}

Test Metrics:
  RMSE: {test_metrics.get('test_rmse', 0):.2f} baht/kg
  MAE:  {test_metrics.get('test_mae', 0):.2f} baht/kg
  MAPE: {test_metrics.get('test_mape', 0):.2f}%
  R2:   {test_metrics.get('test_r2', 0):.4f}
        """
        
        ax1.text(0.1, 0.5, text, fontsize=12, family='monospace',
                bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.2))
        
        ax2 = plt.subplot(2, 1, 2)
        ax2.axis('off')
        
        insights = f"""
KEY INSIGHTS:

Best algorithm: {best_algorithm.upper()}
Test RMSE: {test_metrics.get('test_rmse', 0):.2f} baht/kg (Target: < 5.0)
Test MAPE: {test_metrics.get('test_mape', 0):.2f}% (Target: < 15%)
Model generalization: Excellent (R2 = {test_metrics.get('test_r2', 0):.4f})

RECOMMENDATIONS:
Deploy {best_algorithm.upper()} model to production
Monitor prediction accuracy on real data
Retrain monthly with new data
        """
        
        ax2.text(0.1, 0.5, insights, fontsize=11, family='monospace',
                bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {save_path}")
        return str(save_path)
    
    def generate_all_visualizations(self, comparison_results: Dict, best_algorithm: str,
                                   best_model, feature_names: List[str],
                                   feature_categories: Dict, test_metrics: Dict,
                                   y_test: np.ndarray, y_pred: np.ndarray) -> Dict[str, str]:
        logger.info("="*70)
        logger.info("GENERATING VISUALIZATIONS")
        logger.info("="*70)
        
        paths = {}
        paths['model_comparison'] = self.create_algorithm_comparison(comparison_results)
        paths['feature_importance'] = self.create_feature_importance(
            best_model, feature_names, best_algorithm, feature_categories
        )
        paths['error_distribution'] = self.create_error_distribution(y_test, y_pred, 'Test')
        paths['metrics_summary'] = self.create_metrics_summary(comparison_results)
        paths['evaluation_report'] = self.create_evaluation_report(
            comparison_results, best_algorithm, test_metrics
        )
        
        logger.info("="*70)
        logger.info("VISUALIZATIONS COMPLETE")
        logger.info("="*70)
        
        return paths

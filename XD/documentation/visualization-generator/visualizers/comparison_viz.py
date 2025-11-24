# -*- coding: utf-8 -*-
"""
Comparison Visualizer
Generates cross-model comparison visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List
import logging

from .base_visualizer import BaseVisualizer

logger = logging.getLogger(__name__)


class ComparisonVisualizer(BaseVisualizer):
    """Visualizer for cross-model comparisons"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        super().__init__(output_dir, dpi)
        self.model_name = "Comparison"
    
    def generate_all(self, all_models_data: Dict[str, Dict[str, Any]]) -> List[Path]:
        """
        Generate all comparison visualizations
        
        Args:
            all_models_data: Dictionary containing all models' data
            
        Returns:
            List of paths to generated visualizations
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating Cross-Model Comparison Visualizations")
        logger.info(f"{'='*60}")
        
        outputs = []
        
        try:
            outputs.append(self.model_overview(all_models_data))
        except Exception as e:
            logger.error(f"Failed to generate model overview: {e}")
        
        try:
            outputs.append(self.performance_summary(all_models_data))
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
        
        logger.info(f"✅ Generated {len(outputs)} comparison visualizations\n")
        return outputs
    
    def model_overview(self, all_models_data: Dict[str, Dict[str, Any]]) -> Path:
        """Generate model overview comparison"""
        
        # Prepare data
        models_info = []
        
        for model_key, model_data in all_models_data.items():
            eval_data = model_data.get('evaluation', {})
            
            model_name = eval_data.get('model', f'Model {model_key}')
            status = eval_data.get('status', 'Unknown')
            
            # Get primary metric based on model type
            if model_key == 'A':
                algorithms = eval_data.get('algorithms', {})
                best_algo = eval_data.get('summary', {}).get('best_algorithm', 'xgboost')
                metrics = algorithms.get(best_algo, {}).get('metrics', {})
                primary_metric = f"R² = {metrics.get('r2', 0):.4f}"
                metric_type = "Regression"
            elif model_key == 'B':
                algorithms = eval_data.get('algorithms', {})
                best_algo = eval_data.get('summary', {}).get('best_algorithm', 'logistic')
                metrics = algorithms.get(best_algo, {}).get('metrics', {})
                primary_metric = f"F1 = {metrics.get('f1', 0):.4f}"
                metric_type = "Classification"
            elif model_key == 'C':
                algorithms = eval_data.get('algorithms', {})
                algo_key = list(algorithms.keys())[0] if algorithms else 'xgboost_quantile'
                metrics = algorithms.get(algo_key, {}).get('metrics', {})
                primary_metric = f"R² = {metrics.get('r2', 0):.4f}"
                metric_type = "Regression"
            elif model_key == 'D':
                metrics = eval_data.get('metrics', {})
                primary_metric = f"Profit Eff. = {metrics.get('profit_efficiency', 0):.4f}"
                metric_type = "Bandit"
            else:
                primary_metric = "N/A"
                metric_type = "Unknown"
            
            models_info.append({
                'Model': model_name.split('-')[0].strip(),
                'Purpose': model_name.split('-')[1].strip() if '-' in model_name else 'Unknown',
                'Type': metric_type,
                'Primary Metric': primary_metric,
                'Status': status
            })
        
        df = pd.DataFrame(models_info)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='left',
            loc='center',
            colWidths=[0.12, 0.35, 0.15, 0.23, 0.15]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(len(df.columns)):
            cell = table[(0, i)]
            cell.set_facecolor(self.style['colors']['primary'])
            cell.set_text_props(weight='bold', color='white')
        
        # Style rows
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['secondary'],
                 self.style['colors']['success'],
                 self.style['colors']['warning']]
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell = table[(i+1, j)]
                cell.set_facecolor('white' if i % 2 == 0 else '#f0f0f0')
                
                # Highlight model column
                if j == 0:
                    cell.set_text_props(weight='bold', color=colors[i % len(colors)])
        
        ax.set_title('FarmMe ML Pipeline: Model Overview',
                    fontsize=14, fontweight='bold', pad=20)
        
        return self.save_figure(fig, 'comparison_model_overview.png')
    
    def performance_summary(self, all_models_data: Dict[str, Dict[str, Any]]) -> Path:
        """Generate performance summary comparison"""
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Model A - Regression metrics
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_model_a_summary(ax1, all_models_data.get('A', {}))
        
        # Model B - Classification metrics
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_model_b_summary(ax2, all_models_data.get('B', {}))
        
        # Model C - Price forecast metrics
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_model_c_summary(ax3, all_models_data.get('C', {}))
        
        # Model D - Decision metrics
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_model_d_summary(ax4, all_models_data.get('D', {}))
        
        fig.suptitle('FarmMe ML Pipeline: Performance Summary',
                    fontsize=16, fontweight='bold', y=0.98)
        
        return self.save_figure(fig, 'comparison_performance_summary.png')
    
    def _plot_model_a_summary(self, ax, model_data: Dict[str, Any]):
        """Plot Model A summary"""
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        best_algo = eval_data.get('summary', {}).get('best_algorithm', 'xgboost')
        metrics = algorithms.get(best_algo, {}).get('metrics', {})
        
        data = {
            'R²': metrics.get('r2', 0),
            'RMSE': min(metrics.get('rmse', 0) / 100, 1),  # Normalize
            'MAE': min(metrics.get('mae', 0) / 100, 1)     # Normalize
        }
        
        bars = ax.bar(data.keys(), data.values(), 
                     color=self.style['colors']['primary'], alpha=0.7)
        
        for bar, (key, val) in zip(bars, data.items()):
            height = bar.get_height()
            raw_val = metrics.get(key.lower().replace('²', '2'), val)
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{raw_val:.3f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title('Model A: Crop Recommendation', fontsize=11, fontweight='bold')
        ax.set_ylabel('Score', fontsize=10)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_model_b_summary(self, ax, model_data: Dict[str, Any]):
        """Plot Model B summary"""
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        best_algo = eval_data.get('summary', {}).get('best_algorithm', 'logistic')
        metrics = algorithms.get(best_algo, {}).get('metrics', {})
        
        data = {
            'F1': metrics.get('f1', 0),
            'Precision': metrics.get('precision', 0),
            'Recall': metrics.get('recall', 0)
        }
        
        bars = ax.bar(data.keys(), data.values(),
                     color=self.style['colors']['secondary'], alpha=0.7)
        
        for bar, val in zip(bars, data.values()):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title('Model B: Planting Window', fontsize=11, fontweight='bold')
        ax.set_ylabel('Score', fontsize=10)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_model_c_summary(self, ax, model_data: Dict[str, Any]):
        """Plot Model C summary"""
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        algo_key = list(algorithms.keys())[0] if algorithms else 'xgboost_quantile'
        metrics = algorithms.get(algo_key, {}).get('metrics', {})
        
        data = {
            'R²': metrics.get('r2', 0),
            'RMSE': 1 - min(metrics.get('rmse', 0) / 10, 1),
            'MAE': 1 - min(metrics.get('mae', 0) / 10, 1)
        }
        
        bars = ax.bar(data.keys(), data.values(),
                     color=self.style['colors']['success'], alpha=0.7)
        
        raw_values = [metrics.get('r2', 0), metrics.get('rmse', 0), metrics.get('mae', 0)]
        for bar, val in zip(bars, raw_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title('Model C: Price Forecast', fontsize=11, fontweight='bold')
        ax.set_ylabel('Score', fontsize=10)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _plot_model_d_summary(self, ax, model_data: Dict[str, Any]):
        """Plot Model D summary"""
        eval_data = model_data.get('evaluation', {})
        metrics = eval_data.get('metrics', {})
        
        data = {
            'Decision\nAccuracy': metrics.get('decision_accuracy', 0),
            'Profit\nEfficiency': metrics.get('profit_efficiency', 0)
        }
        
        bars = ax.bar(data.keys(), data.values(),
                     color=self.style['colors']['warning'], alpha=0.7)
        
        for bar, val in zip(bars, data.values()):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title('Model D: Harvest Decision', fontsize=11, fontweight='bold')
        ax.set_ylabel('Score', fontsize=10)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')

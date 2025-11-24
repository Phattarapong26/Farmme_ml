# -*- coding: utf-8 -*-
"""
Model C Visualizer
Generates visualizations for Price Forecast Model
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


class ModelCVisualizer(BaseVisualizer):
    """Visualizer for Model C - Price Forecast"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        super().__init__(output_dir, dpi)
        self.model_name = "Model C"
    
    def generate_all(self, model_data: Dict[str, Any]) -> List[Path]:
        """
        Generate all Model C visualizations
        
        Args:
            model_data: Dictionary containing model file path and evaluation data
            
        Returns:
            List of paths to generated visualizations
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating {self.model_name} Visualizations")
        logger.info(f"{'='*60}")
        
        outputs = []
        
        try:
            outputs.append(self.performance_metrics(model_data))
        except Exception as e:
            logger.error(f"Failed to generate performance metrics: {e}")
        
        try:
            outputs.append(self.metrics_comparison(model_data))
        except Exception as e:
            logger.error(f"Failed to generate metrics comparison: {e}")
        
        logger.info(f"✅ Generated {len(outputs)} visualizations for {self.model_name}\n")
        return outputs
    
    def performance_metrics(self, model_data: Dict[str, Any]) -> Path:
        """Generate performance metrics visualization"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Get the main algorithm (usually xgboost_quantile)
        algo_key = list(algorithms.keys())[0] if algorithms else 'xgboost_quantile'
        algo_info = algorithms.get(algo_key, {})
        metrics = algo_info.get('metrics', {})
        
        # Prepare data
        metric_names = ['R²', 'RMSE', 'MAE', 'MAPE']
        metric_values = [
            metrics.get('r2', 0),
            metrics.get('rmse', 0),
            metrics.get('mae', 0),
            metrics.get('mape', 0)
        ]
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['warning'],
                 self.style['colors']['success'],
                 self.style['colors']['secondary']]
        
        for idx, (name, value, color) in enumerate(zip(metric_names, metric_values, colors)):
            ax = axes[idx]
            
            # Create bar
            bar = ax.bar([name], [value], color=color, alpha=0.7, width=0.5)
            
            # Add value label
            ax.text(0, value, f'{value:.4f}', 
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            ax.set_title(f'{name} Score', fontsize=12, fontweight='bold')
            ax.set_ylabel('Value', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Set y-axis limits based on metric
            if name == 'R²':
                ax.set_ylim(0, 1.1)
            elif name == 'MAPE':
                ax.set_ylim(0, max(value * 1.5, 0.1))
            else:
                ax.set_ylim(0, value * 1.3)
        
        fig.suptitle(f'Model C: {algo_info.get("name", "Price Forecast")} Performance Metrics', 
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return self.save_figure(fig, 'model_c_performance_metrics.png')
    
    def metrics_comparison(self, model_data: Dict[str, Any]) -> Path:
        """Generate metrics comparison bar chart"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Get the main algorithm
        algo_key = list(algorithms.keys())[0] if algorithms else 'xgboost_quantile'
        algo_info = algorithms.get(algo_key, {})
        metrics = algo_info.get('metrics', {})
        
        # Prepare data - normalize metrics for comparison
        data = {
            'Metric': ['R²', 'RMSE\n(normalized)', 'MAE\n(normalized)', 'MAPE\n(normalized)'],
            'Score': [
                metrics.get('r2', 0),
                1 - min(metrics.get('rmse', 0) / 10, 1),  # Normalize RMSE
                1 - min(metrics.get('mae', 0) / 10, 1),   # Normalize MAE
                1 - min(metrics.get('mape', 0) * 100, 1)  # Normalize MAPE
            ],
            'Raw Value': [
                f"{metrics.get('r2', 0):.4f}",
                f"{metrics.get('rmse', 0):.2f}",
                f"{metrics.get('mae', 0):.2f}",
                f"{metrics.get('mape', 0):.4f}"
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['warning'],
                 self.style['colors']['success'],
                 self.style['colors']['secondary']]
        
        bars = ax.bar(df['Metric'], df['Score'], color=colors, alpha=0.7)
        
        # Add value labels with raw values
        for bar, raw_val in zip(bars, df['Raw Value']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{raw_val}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Normalized Score (0-1)', fontsize=12)
        ax.set_title(f'Model C: {algo_info.get("name", "Price Forecast")} - Metrics Overview\n(Higher is better for all metrics)',
                    fontsize=13, fontweight='bold', pad=20)
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add note
        note_text = "Note: RMSE, MAE, and MAPE are normalized (lower raw values = better performance)"
        ax.text(0.5, -0.15, note_text, 
               ha='center', va='top', transform=ax.transAxes,
               fontsize=9, style='italic', color='gray')
        
        return self.save_figure(fig, 'model_c_metrics_comparison.png')

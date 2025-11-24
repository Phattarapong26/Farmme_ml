# -*- coding: utf-8 -*-
"""
Model A Visualizer
Generates visualizations for Crop Recommendation Model
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List
import logging
import pickle

from .base_visualizer import BaseVisualizer

logger = logging.getLogger(__name__)


class ModelAVisualizer(BaseVisualizer):
    """Visualizer for Model A - Crop Recommendation"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        super().__init__(output_dir, dpi)
        self.model_name = "Model A"
    
    def generate_all(self, model_data: Dict[str, Any]) -> List[Path]:
        """
        Generate all Model A visualizations
        
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
            outputs.append(self.algorithm_comparison(model_data))
        except Exception as e:
            logger.error(f"Failed to generate algorithm comparison: {e}")
        
        try:
            outputs.append(self.metrics_breakdown(model_data))
        except Exception as e:
            logger.error(f"Failed to generate metrics breakdown: {e}")
        
        logger.info(f"✅ Generated {len(outputs)} visualizations for {self.model_name}\n")
        return outputs
    
    def performance_metrics(self, model_data: Dict[str, Any]) -> Path:
        """Generate performance metrics comparison chart"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Prepare data
        metrics_data = []
        for algo_key, algo_info in algorithms.items():
            metrics = algo_info.get('metrics', {})
            metrics_data.append({
                'Algorithm': algo_info.get('name', algo_key),
                'R²': metrics.get('r2', 0),
                'RMSE': metrics.get('rmse', 0),
                'MAE': metrics.get('mae', 0)
            })
        
        df = pd.DataFrame(metrics_data)
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        metrics = ['R²', 'RMSE', 'MAE']
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['warning'],
                 self.style['colors']['success']]
        
        for idx, (metric, color) in enumerate(zip(metrics, colors)):
            ax = axes[idx]
            bars = ax.bar(df['Algorithm'], df[metric], color=color, alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.4f}' if metric == 'R²' else f'{height:.2f}',
                       ha='center', va='bottom', fontsize=10)
            
            ax.set_title(f'{metric} Score', fontsize=12, fontweight='bold')
            ax.set_ylabel(metric, fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_xticklabels(df['Algorithm'], rotation=15, ha='right')
        
        fig.suptitle('Model A: Performance Metrics Comparison', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        return self.save_figure(fig, 'model_a_performance_metrics.png')
    
    def algorithm_comparison(self, model_data: Dict[str, Any]) -> Path:
        """Generate algorithm comparison heatmap"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Prepare data for heatmap
        data = []
        algo_names = []
        
        for algo_key, algo_info in algorithms.items():
            algo_names.append(algo_info.get('name', algo_key))
            metrics = algo_info.get('metrics', {})
            
            # Get train, val, test metrics if available
            train_metrics = algo_info.get('train_metrics', {})
            val_metrics = algo_info.get('val_metrics', {})
            test_metrics = algo_info.get('test_metrics', {})
            
            data.append([
                train_metrics.get('r2', metrics.get('r2', 0)),
                val_metrics.get('r2', metrics.get('r2', 0)),
                test_metrics.get('r2', metrics.get('r2', 0)),
                train_metrics.get('rmse', metrics.get('rmse', 0)),
                val_metrics.get('rmse', metrics.get('rmse', 0)),
                test_metrics.get('rmse', metrics.get('rmse', 0))
            ])
        
        df = pd.DataFrame(
            data,
            index=algo_names,
            columns=['R² Train', 'R² Val', 'R² Test', 'RMSE Train', 'RMSE Val', 'RMSE Test']
        )
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.heatmap(
            df,
            annot=True,
            fmt='.4f',
            cmap='RdYlGn',
            center=df.mean().mean(),
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Model A: Algorithm Performance Across Train/Val/Test Sets',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Algorithm', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        return self.save_figure(fig, 'model_a_algorithm_comparison.png')
    
    def metrics_breakdown(self, model_data: Dict[str, Any]) -> Path:
        """Generate detailed metrics breakdown"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Get best algorithm
        best_algo = eval_data.get('summary', {}).get('best_algorithm', 'xgboost')
        best_algo_data = algorithms.get(best_algo, {})
        
        # Prepare data
        train_metrics = best_algo_data.get('train_metrics', {})
        val_metrics = best_algo_data.get('val_metrics', {})
        test_metrics = best_algo_data.get('test_metrics', {})
        
        metrics_dict = {
            'Train': [train_metrics.get('r2', 0), 
                     train_metrics.get('rmse', 0), 
                     train_metrics.get('mae', 0)],
            'Validation': [val_metrics.get('r2', 0), 
                          val_metrics.get('rmse', 0), 
                          val_metrics.get('mae', 0)],
            'Test': [test_metrics.get('r2', 0), 
                    test_metrics.get('rmse', 0), 
                    test_metrics.get('mae', 0)]
        }
        
        df = pd.DataFrame(metrics_dict, index=['R²', 'RMSE', 'MAE'])
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(df.index))
        width = 0.25
        
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['secondary'],
                 self.style['colors']['success']]
        
        for idx, (col, color) in enumerate(zip(df.columns, colors)):
            offset = width * (idx - 1)
            bars = ax.bar(x + offset, df[col], width, label=col, color=color, alpha=0.8)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'Model A: Best Algorithm ({best_algo_data.get("name", best_algo)}) - Train/Val/Test Breakdown',
                    fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(df.index)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')
        
        return self.save_figure(fig, 'model_a_metrics_breakdown.png')

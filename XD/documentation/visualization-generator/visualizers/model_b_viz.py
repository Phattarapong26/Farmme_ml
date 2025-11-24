# -*- coding: utf-8 -*-
"""
Model B Visualizer
Generates visualizations for Planting Window Classification Model
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


class ModelBVisualizer(BaseVisualizer):
    """Visualizer for Model B - Planting Window Classification"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        super().__init__(output_dir, dpi)
        self.model_name = "Model B"
    
    def generate_all(self, model_data: Dict[str, Any]) -> List[Path]:
        """
        Generate all Model B visualizations
        
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
            outputs.append(self.classification_metrics(model_data))
        except Exception as e:
            logger.error(f"Failed to generate classification metrics: {e}")
        
        try:
            outputs.append(self.algorithm_comparison(model_data))
        except Exception as e:
            logger.error(f"Failed to generate algorithm comparison: {e}")
        
        try:
            outputs.append(self.precision_recall_comparison(model_data))
        except Exception as e:
            logger.error(f"Failed to generate precision-recall comparison: {e}")
        
        logger.info(f"✅ Generated {len(outputs)} visualizations for {self.model_name}\n")
        return outputs
    
    def classification_metrics(self, model_data: Dict[str, Any]) -> Path:
        """Generate classification metrics comparison chart"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Prepare data
        metrics_data = []
        for algo_key, algo_info in algorithms.items():
            metrics = algo_info.get('metrics', {})
            metrics_data.append({
                'Algorithm': algo_info.get('name', algo_key),
                'F1-Score': metrics.get('f1', 0),
                'Precision': metrics.get('precision', 0),
                'Recall': metrics.get('recall', 0),
                'ROC-AUC': metrics.get('roc_auc', 0)
            })
        
        df = pd.DataFrame(metrics_data)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        metrics = ['F1-Score', 'Precision', 'Recall', 'ROC-AUC']
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['success'],
                 self.style['colors']['warning'],
                 self.style['colors']['secondary']]
        
        for idx, (metric, color) in enumerate(zip(metrics, colors)):
            ax = axes[idx]
            
            # Filter out zero values for ROC-AUC (if not available)
            plot_df = df[df[metric] > 0] if metric == 'ROC-AUC' else df
            
            if len(plot_df) > 0:
                bars = ax.bar(plot_df['Algorithm'], plot_df[metric], 
                            color=color, alpha=0.7)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.4f}',
                           ha='center', va='bottom', fontsize=9)
                
                ax.set_title(f'{metric}', fontsize=12, fontweight='bold')
                ax.set_ylabel(metric, fontsize=11)
                ax.set_ylim(0, 1.1)
                ax.grid(True, alpha=0.3, axis='y')
                ax.set_xticklabels(plot_df['Algorithm'], rotation=15, ha='right', fontsize=9)
            else:
                ax.text(0.5, 0.5, f'No {metric} data available',
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'{metric}', fontsize=12, fontweight='bold')
        
        fig.suptitle('Model B: Classification Metrics Comparison', 
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return self.save_figure(fig, 'model_b_classification_metrics.png')
    
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
            
            data.append([
                metrics.get('f1', 0),
                metrics.get('precision', 0),
                metrics.get('recall', 0),
                metrics.get('roc_auc', 0)
            ])
        
        df = pd.DataFrame(
            data,
            index=algo_names,
            columns=['F1-Score', 'Precision', 'Recall', 'ROC-AUC']
        )
        
        # Replace 0 with NaN for ROC-AUC if not available
        df['ROC-AUC'] = df['ROC-AUC'].replace(0, np.nan)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.heatmap(
            df,
            annot=True,
            fmt='.4f',
            cmap='YlGnBu',
            vmin=0,
            vmax=1,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
            mask=df.isna()
        )
        
        ax.set_title('Model B: Algorithm Performance Heatmap',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Algorithm', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        return self.save_figure(fig, 'model_b_algorithm_heatmap.png')
    
    def precision_recall_comparison(self, model_data: Dict[str, Any]) -> Path:
        """Generate precision vs recall scatter plot"""
        
        eval_data = model_data.get('evaluation', {})
        algorithms = eval_data.get('algorithms', {})
        
        # Prepare data
        algo_names = []
        precisions = []
        recalls = []
        f1_scores = []
        
        for algo_key, algo_info in algorithms.items():
            metrics = algo_info.get('metrics', {})
            algo_names.append(algo_info.get('name', algo_key))
            precisions.append(metrics.get('precision', 0))
            recalls.append(metrics.get('recall', 0))
            f1_scores.append(metrics.get('f1', 0))
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create scatter with size based on F1-score
        sizes = [f1 * 500 for f1 in f1_scores]
        colors_list = [self.style['colors']['primary'], 
                      self.style['colors']['secondary'],
                      self.style['colors']['success']]
        
        for i, (name, prec, rec, size, color) in enumerate(zip(
            algo_names, precisions, recalls, sizes, colors_list[:len(algo_names)]
        )):
            ax.scatter(rec, prec, s=size, alpha=0.6, color=color, label=name)
            ax.annotate(name, (rec, prec), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold')
        
        # Add diagonal line (F1 = 0.5 contour)
        x = np.linspace(0, 1, 100)
        for f1_val in [0.5, 0.7, 0.9]:
            y = (f1_val * x) / (2 * x - f1_val)
            y = np.where((y >= 0) & (y <= 1), y, np.nan)
            ax.plot(x, y, '--', alpha=0.3, label=f'F1={f1_val}')
        
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title('Model B: Precision vs Recall Trade-off\n(Bubble size = F1-Score)',
                    fontsize=13, fontweight='bold', pad=20)
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower left', fontsize=9)
        
        return self.save_figure(fig, 'model_b_precision_recall.png')

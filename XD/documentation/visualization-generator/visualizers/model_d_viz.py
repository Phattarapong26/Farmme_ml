# -*- coding: utf-8 -*-
"""
Model D Visualizer
Generates visualizations for Harvest Decision Engine (Thompson Sampling)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List
import logging
from scipy import stats

from .base_visualizer import BaseVisualizer

logger = logging.getLogger(__name__)


class ModelDVisualizer(BaseVisualizer):
    """Visualizer for Model D - Harvest Decision Engine"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        super().__init__(output_dir, dpi)
        self.model_name = "Model D"
    
    def generate_all(self, model_data: Dict[str, Any]) -> List[Path]:
        """
        Generate all Model D visualizations
        
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
            outputs.append(self.decision_metrics(model_data))
        except Exception as e:
            logger.error(f"Failed to generate decision metrics: {e}")
        
        try:
            outputs.append(self.posterior_distributions(model_data))
        except Exception as e:
            logger.error(f"Failed to generate posterior distributions: {e}")
        
        try:
            outputs.append(self.arm_comparison(model_data))
        except Exception as e:
            logger.error(f"Failed to generate arm comparison: {e}")
        
        logger.info(f"✅ Generated {len(outputs)} visualizations for {self.model_name}\n")
        return outputs
    
    def decision_metrics(self, model_data: Dict[str, Any]) -> Path:
        """Generate decision metrics visualization"""
        
        eval_data = model_data.get('evaluation', {})
        metrics = eval_data.get('metrics', {})
        
        # Prepare data
        metric_names = ['Decision\nAccuracy', 'Profit\nEfficiency']
        metric_values = [
            metrics.get('decision_accuracy', 0),
            metrics.get('profit_efficiency', 0)
        ]
        
        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        colors = [self.style['colors']['primary'], self.style['colors']['success']]
        
        for idx, (ax, name, value, color) in enumerate(zip(axes, metric_names, metric_values, colors)):
            # Create bar
            bar = ax.bar([name], [value], color=color, alpha=0.7, width=0.5)
            
            # Add value label
            ax.text(0, value, f'{value:.4f}\n({value*100:.2f}%)', 
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.set_title(f'{name.replace(chr(10), " ")}', fontsize=12, fontweight='bold')
            ax.set_ylabel('Score', fontsize=11)
            ax.set_ylim(0, 1.1)
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_xticklabels([])
        
        # Add summary text
        total_scenarios = metrics.get('total_scenarios', 0)
        correct_decisions = metrics.get('correct_decisions', 0)
        
        fig.text(0.5, 0.02, 
                f'Total Scenarios: {total_scenarios:,} | Correct Decisions: {correct_decisions:,}',
                ha='center', fontsize=10, style='italic', color='gray')
        
        fig.suptitle('Model D: Thompson Sampling Performance Metrics', 
                    fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        return self.save_figure(fig, 'model_d_decision_metrics.png')
    
    def posterior_distributions(self, model_data: Dict[str, Any]) -> Path:
        """Generate posterior distributions for each arm"""
        
        eval_data = model_data.get('evaluation', {})
        posteriors = eval_data.get('posteriors', {})
        
        if not posteriors:
            logger.warning("No posterior data available for Model D")
            # Create placeholder
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No posterior distribution data available',
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return self.save_figure(fig, 'model_d_posterior_distributions.png')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = [self.style['colors']['primary'], 
                 self.style['colors']['success'],
                 self.style['colors']['warning']]
        
        x = np.linspace(0, 1, 1000)
        
        for idx, (arm_name, posterior) in enumerate(posteriors.items()):
            alpha = posterior.get('alpha', 1)
            beta = posterior.get('beta', 1)
            mean = posterior.get('mean', 0)
            
            # Generate Beta distribution
            y = stats.beta.pdf(x, alpha, beta)
            
            color = colors[idx % len(colors)]
            ax.plot(x, y, label=f'{arm_name} (α={alpha:.0f}, β={beta:.0f})',
                   linewidth=2.5, color=color)
            
            # Add vertical line for mean
            ax.axvline(mean, color=color, linestyle='--', alpha=0.5, linewidth=1.5)
            
            # Add text annotation for mean
            max_y = stats.beta.pdf(mean, alpha, beta)
            ax.text(mean, max_y * 1.05, f'μ={mean:.3f}',
                   ha='center', fontsize=9, color=color, fontweight='bold')
        
        ax.set_xlabel('Success Probability', fontsize=12)
        ax.set_ylabel('Probability Density', fontsize=12)
        ax.set_title('Model D: Thompson Sampling - Posterior Distributions (Beta)',
                    fontsize=13, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add note
        note_text = "Dashed lines indicate mean success probability for each action"
        ax.text(0.5, -0.12, note_text, 
               ha='center', va='top', transform=ax.transAxes,
               fontsize=9, style='italic', color='gray')
        
        return self.save_figure(fig, 'model_d_posterior_distributions.png')
    
    def arm_comparison(self, model_data: Dict[str, Any]) -> Path:
        """Generate arm comparison chart"""
        
        eval_data = model_data.get('evaluation', {})
        posteriors = eval_data.get('posteriors', {})
        
        if not posteriors:
            logger.warning("No posterior data available for arm comparison")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No posterior data available',
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return self.save_figure(fig, 'model_d_arm_comparison.png')
        
        # Prepare data
        arms = []
        means = []
        variances = []
        alphas = []
        betas = []
        
        for arm_name, posterior in posteriors.items():
            arms.append(arm_name)
            means.append(posterior.get('mean', 0))
            variances.append(posterior.get('variance', 0))
            alphas.append(posterior.get('alpha', 0))
            betas.append(posterior.get('beta', 0))
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Mean success probability
        ax1 = axes[0, 0]
        bars = ax1.bar(arms, means, color=self.style['colors']['primary'], alpha=0.7)
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax1.set_title('Mean Success Probability', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Probability', fontsize=11)
        ax1.set_ylim(0, 1.1)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.tick_params(axis='x', rotation=15)
        
        # 2. Variance (uncertainty)
        ax2 = axes[0, 1]
        bars = ax2.bar(arms, variances, color=self.style['colors']['warning'], alpha=0.7)
        for bar, var in zip(bars, variances):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{var:.6f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax2.set_title('Variance (Uncertainty)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Variance', fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.tick_params(axis='x', rotation=15)
        
        # 3. Alpha parameters
        ax3 = axes[1, 0]
        bars = ax3.bar(arms, alphas, color=self.style['colors']['success'], alpha=0.7)
        for bar, alpha in zip(bars, alphas):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{alpha:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax3.set_title('Alpha (Successes)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Count', fontsize=11)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.tick_params(axis='x', rotation=15)
        
        # 4. Beta parameters
        ax4 = axes[1, 1]
        bars = ax4.bar(arms, betas, color=self.style['colors']['danger'], alpha=0.7)
        for bar, beta in zip(bars, betas):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{beta:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax4.set_title('Beta (Failures)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Count', fontsize=11)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.tick_params(axis='x', rotation=15)
        
        fig.suptitle('Model D: Thompson Sampling - Arm Comparison', 
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        return self.save_figure(fig, 'model_d_arm_comparison.png')

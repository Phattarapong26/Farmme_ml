"""
Bubble Chart Generator for Model B Algorithm Comparison
Creates bubble chart with F1 Score (x-axis), Precision (y-axis), and bubble size (training time)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BubbleChartGeneratorB:
    """Generate bubble comparison chart for Model B algorithms"""
    
    def __init__(self, results: Dict[str, Any]):
        """
        Initialize with evaluation results
        
        Args:
            results: Dictionary of TrainingResultB objects keyed by algorithm name
        """
        self.results = results
        self.colors = {
            'xgboost': '#3498db',  # Blue
            'random_forest': '#2ecc71',  # Green
            'gradboost': '#e67e22'  # Orange
        }
        
    def generate_bubble_chart(self, output_path: Path) -> None:
        """
        Generate and save bubble comparison chart
        
        Args:
            output_path: Path to save the chart
        """
        logger.info("📊 Generating bubble comparison chart for Model B...")
        
        # Extract data
        algo_names = []
        f1_scores = []
        precision_values = []
        training_times = []
        colors = []
        recall_values = []
        roc_auc_values = []
        
        for key, result in self.results.items():
            algo_names.append(result.algorithm_name)
            f1_scores.append(result.test_metrics['f1'])
            precision_values.append(result.test_metrics['precision'])
            recall_values.append(result.test_metrics['recall'])
            roc_auc_values.append(result.test_metrics['roc_auc'])
            training_times.append(result.training_time)
            colors.append(self.colors.get(key, '#95a5a6'))
        
        # Calculate bubble sizes
        bubble_sizes = self._calculate_bubble_sizes(training_times)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot bubbles
        for i, (name, f1, precision, recall, roc_auc, size, color) in enumerate(zip(
            algo_names, f1_scores, precision_values, recall_values, roc_auc_values, bubble_sizes, colors
        )):
            # Plot bubble
            ax.scatter(f1, precision, s=size, c=color, alpha=0.6, 
                      edgecolors='black', linewidth=2, label=name)
            
            # Add label with metrics
            label_text = f"{name}\nF1={f1:.3f}\nPrec={precision:.3f}\nRecall={recall:.3f}\nAUC={roc_auc:.3f}\nTime={training_times[i]:.2f}s"
            
            # Position label slightly offset from bubble
            offset_x = 0.01 if i % 2 == 0 else -0.01
            offset_y = precision * 0.05 if i % 2 == 0 else -precision * 0.05
            
            ax.annotate(label_text, 
                       xy=(f1, precision),
                       xytext=(f1 + offset_x, precision + offset_y),
                       fontsize=9,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3),
                       ha='center')
        
        # Styling
        ax.set_xlabel('F1 Score', fontsize=14, fontweight='bold')
        ax.set_ylabel('Precision', fontsize=14, fontweight='bold')
        ax.set_title('Model B - Algorithm Comparison (Bubble Chart)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Set axis limits with padding
        f1_min, f1_max = min(f1_scores), max(f1_scores)
        prec_min, prec_max = min(precision_values), max(precision_values)
        
        f1_range = f1_max - f1_min if f1_max > f1_min else 0.1
        prec_range = prec_max - prec_min if prec_max > prec_min else 0.1
        
        ax.set_xlim(max(0, f1_min - f1_range * 0.15), min(1, f1_max + f1_range * 0.15))
        ax.set_ylim(max(0, prec_min - prec_range * 0.2), min(1, prec_max + prec_range * 0.2))
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend for bubble size
        legend_text = "Bubble size = Training time\n(Larger = Slower)"
        ax.text(0.02, 0.98, legend_text, 
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Add interpretation guide
        guide_text = "Better models:\n→ Higher F1 (right)\n→ Higher Precision (up)"
        ax.text(0.98, 0.02, guide_text,
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='bottom',
               horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Bubble chart saved: {output_path}")
        
        plt.close()
    
    def _calculate_bubble_sizes(self, training_times: List[float]) -> List[float]:
        """
        Calculate bubble sizes based on training times
        
        Args:
            training_times: List of training times in seconds
            
        Returns:
            List of bubble sizes (100-1000 range)
        """
        min_time = min(training_times)
        max_time = max(training_times)
        
        if max_time == min_time:
            # All same time, use medium size
            return [550] * len(training_times)
        
        # Normalize to 100-1000 range
        bubble_sizes = []
        for time in training_times:
            normalized = (time - min_time) / (max_time - min_time)
            size = 100 + 900 * normalized
            bubble_sizes.append(size)
        
        return bubble_sizes

if __name__ == "__main__":
    print("✅ Bubble Chart Generator B loaded successfully")

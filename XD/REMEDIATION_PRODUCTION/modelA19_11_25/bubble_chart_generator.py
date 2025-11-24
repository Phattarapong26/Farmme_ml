"""
Bubble Chart Generator for Model A Algorithm Comparison
Creates bubble chart with R² (x-axis), RMSE (y-axis), and bubble size (training time)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BubbleChartGenerator:
    """Generate bubble comparison chart for algorithms"""
    
    def __init__(self, results: Dict[str, Any]):
        """
        Initialize with evaluation results
        
        Args:
            results: Dictionary of TrainingResult objects keyed by algorithm name
        """
        self.results = results
        self.colors = {
            'xgboost': '#3498db',  # Blue
            'rf_ensemble': '#2ecc71',  # Green
            'gradboost': '#e67e22'  # Orange
        }
        
    def generate_bubble_chart(self, output_path: Path) -> None:
        """
        Generate and save bubble comparison chart
        
        Args:
            output_path: Path to save the chart
        """
        logger.info("📊 Generating bubble comparison chart...")
        
        # Extract data
        algo_names = []
        r2_scores = []
        rmse_values = []
        training_times = []
        colors = []
        
        for key, result in self.results.items():
            algo_names.append(result.algorithm_name)
            r2_scores.append(result.test_metrics['r2'])
            rmse_values.append(result.test_metrics['rmse'])
            training_times.append(result.training_time)
            colors.append(self.colors.get(key, '#95a5a6'))
        
        # Calculate bubble sizes
        bubble_sizes = self._calculate_bubble_sizes(training_times)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot bubbles
        for i, (name, r2, rmse, size, color) in enumerate(zip(
            algo_names, r2_scores, rmse_values, bubble_sizes, colors
        )):
            # Plot bubble
            ax.scatter(r2, rmse, s=size, c=color, alpha=0.6, 
                      edgecolors='black', linewidth=2, label=name)
            
            # Add label with metrics
            label_text = f"{name}\nR²={r2:.3f}\nRMSE={rmse:.2f}%\nTime={training_times[i]:.2f}s"
            
            # Position label slightly offset from bubble
            offset_x = 0.01 if i % 2 == 0 else -0.01
            offset_y = rmse * 0.05 if i % 2 == 0 else -rmse * 0.05
            
            ax.annotate(label_text, 
                       xy=(r2, rmse),
                       xytext=(r2 + offset_x, rmse + offset_y),
                       fontsize=9,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3),
                       ha='center')
        
        # Styling
        ax.set_xlabel('R² Score', fontsize=14, fontweight='bold')
        ax.set_ylabel('RMSE (%)', fontsize=14, fontweight='bold')
        ax.set_title('Model A - Algorithm Comparison (Bubble Chart)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Set axis limits with padding
        r2_min, r2_max = min(r2_scores), max(r2_scores)
        rmse_min, rmse_max = min(rmse_values), max(rmse_values)
        
        r2_range = r2_max - r2_min
        rmse_range = rmse_max - rmse_min
        
        ax.set_xlim(r2_min - r2_range * 0.15, r2_max + r2_range * 0.15)
        ax.set_ylim(rmse_min - rmse_range * 0.2, rmse_max + rmse_range * 0.2)
        
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
        guide_text = "Better models:\n→ Higher R² (right)\n→ Lower RMSE (down)"
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
    # Test with dummy data
    from dataclasses import dataclass
    from typing import Dict
    
    @dataclass
    class DummyResult:
        algorithm_name: str
        test_metrics: Dict[str, float]
        training_time: float
    
    # Create dummy results
    results = {
        'xgboost': DummyResult(
            algorithm_name='XGBoost',
            test_metrics={'r2': 0.85, 'rmse': 12.5},
            training_time=2.5
        ),
        'rf_ensemble': DummyResult(
            algorithm_name='Random Forest + ElasticNet',
            test_metrics={'r2': 0.82, 'rmse': 14.2},
            training_time=3.8
        ),
        'gradboost': DummyResult(
            algorithm_name='Gradient Boosting',
            test_metrics={'r2': 0.87, 'rmse': 11.8},
            training_time=4.2
        )
    }
    
    # Generate chart
    generator = BubbleChartGenerator(results)
    output_path = Path('test_bubble_chart.png')
    generator.generate_bubble_chart(output_path)
    
    print(f"\n✅ Bubble Chart Generator Test Passed")
    print(f"Chart saved to: {output_path}")

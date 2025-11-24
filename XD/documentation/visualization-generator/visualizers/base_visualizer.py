# -*- coding: utf-8 -*-
"""
Base Visualizer Class
Provides shared utilities and consistent styling for all visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseVisualizer:
    """Base class for all model visualizers"""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        """
        Initialize base visualizer
        
        Args:
            output_dir: Directory to save visualizations
            dpi: Resolution for saved figures (default: 300 for publication quality)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.style = self._setup_style()
        
        logger.info(f"Initialized visualizer with output dir: {self.output_dir}")
    
    def _setup_style(self) -> Dict[str, Any]:
        """Configure matplotlib style for publication quality"""
        
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.2)
        
        # Configure matplotlib
        plt.rcParams['figure.figsize'] = (10, 8)
        plt.rcParams['figure.dpi'] = self.dpi
        plt.rcParams['savefig.dpi'] = self.dpi
        plt.rcParams['savefig.bbox'] = 'tight'
        plt.rcParams['savefig.pad_inches'] = 0.1
        
        # Font settings
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        
        # Try to use Thai font if available
        try:
            # Try common Thai fonts
            thai_fonts = ['Sarabun', 'TH Sarabun New', 'Angsana New', 'Cordia New']
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font in thai_fonts:
                if font in available_fonts:
                    plt.rcParams['font.family'] = font
                    logger.info(f"Using Thai font: {font}")
                    break
            else:
                logger.warning("No Thai font found, using default")
        except Exception as e:
            logger.warning(f"Could not set Thai font: {e}")
        
        # Color palette
        colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'info': '#6C757D'
        }
        
        return {
            'colors': colors,
            'palette': sns.color_palette("husl", 8)
        }
    
    def save_figure(self, fig, filename: str, close: bool = True) -> Path:
        """
        Save figure with consistent settings
        
        Args:
            fig: Matplotlib figure object
            filename: Output filename (without path)
            close: Whether to close the figure after saving
            
        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename
        
        try:
            fig.savefig(
                filepath,
                dpi=self.dpi,
                bbox_inches='tight',
                pad_inches=0.1,
                facecolor='white',
                edgecolor='none'
            )
            logger.info(f"✅ Saved: {filename}")
            
            if close:
                plt.close(fig)
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save {filename}: {e}")
            if close:
                plt.close(fig)
            raise
    
    def create_heatmap(
        self,
        data: pd.DataFrame,
        title: str,
        filename: str,
        annot: bool = True,
        fmt: str = '.2f',
        cmap: str = 'coolwarm',
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        **kwargs
    ) -> Path:
        """
        Generate correlation heatmap
        
        Args:
            data: DataFrame with correlation data
            title: Chart title
            filename: Output filename
            annot: Whether to annotate cells
            fmt: Format string for annotations
            cmap: Colormap name
            vmin: Minimum value for colormap
            vmax: Maximum value for colormap
            
        Returns:
            Path to saved file
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap
        sns.heatmap(
            data,
            annot=annot,
            fmt=fmt,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            center=0 if vmin is None and vmax is None else None,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
            **kwargs
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        return self.save_figure(fig, filename)
    
    def create_bar_chart(
        self,
        data: pd.DataFrame,
        title: str,
        filename: str,
        xlabel: str = '',
        ylabel: str = '',
        horizontal: bool = False,
        **kwargs
    ) -> Path:
        """
        Generate bar chart
        
        Args:
            data: DataFrame with data to plot
            title: Chart title
            filename: Output filename
            xlabel: X-axis label
            ylabel: Y-axis label
            horizontal: Whether to create horizontal bars
            
        Returns:
            Path to saved file
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if horizontal:
            data.plot(kind='barh', ax=ax, **kwargs)
        else:
            data.plot(kind='bar', ax=ax, **kwargs)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        if not horizontal:
            plt.xticks(rotation=45, ha='right')
        
        return self.save_figure(fig, filename)
    
    def create_line_plot(
        self,
        data: pd.DataFrame,
        title: str,
        filename: str,
        xlabel: str = '',
        ylabel: str = '',
        **kwargs
    ) -> Path:
        """
        Generate line plot
        
        Args:
            data: DataFrame with data to plot
            title: Chart title
            filename: Output filename
            xlabel: X-axis label
            ylabel: Y-axis label
            
        Returns:
            Path to saved file
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data.plot(ax=ax, **kwargs)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        return self.save_figure(fig, filename)
    
    def create_scatter_plot(
        self,
        x: np.ndarray,
        y: np.ndarray,
        title: str,
        filename: str,
        xlabel: str = '',
        ylabel: str = '',
        add_diagonal: bool = True,
        **kwargs
    ) -> Path:
        """
        Generate scatter plot
        
        Args:
            x: X-axis data
            y: Y-axis data
            title: Chart title
            filename: Output filename
            xlabel: X-axis label
            ylabel: Y-axis label
            add_diagonal: Whether to add y=x diagonal line
            
        Returns:
            Path to saved file
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.scatter(x, y, alpha=0.6, **kwargs)
        
        if add_diagonal:
            min_val = min(x.min(), y.min())
            max_val = max(x.max(), y.max())
            ax.plot([min_val, max_val], [min_val, max_val], 
                   'r--', lw=2, label='Perfect Prediction')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        return self.save_figure(fig, filename)

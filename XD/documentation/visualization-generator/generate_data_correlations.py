# -*- coding: utf-8 -*-
"""
Data Correlation Analysis and Heatmap Generator
Generates correlation matrices and heatmaps for FarmMe datasets
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCorrelationAnalyzer:
    """Analyzer for dataset correlations"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.dataset_dir = self.base_dir / 'buildingModel.py' / 'Dataset'
        self.output_dir = Path(__file__).parent / 'outputs' / 'data_correlations'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup matplotlib style
        self._setup_style()
        
    def _setup_style(self):
        """Configure matplotlib style"""
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.2)
        
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['savefig.bbox'] = 'tight'
        plt.rcParams['font.size'] = 10
        
    def load_dataset(self, filename: str) -> pd.DataFrame:
        """Load dataset from CSV"""
        filepath = self.dataset_dir / filename
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return None
    
    def get_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract only numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        logger.info(f"Numeric columns: {len(numeric_df.columns)}")
        return numeric_df
    
    def create_correlation_heatmap(
        self, 
        df: pd.DataFrame, 
        title: str, 
        filename: str,
        figsize=(14, 12),
        annot=False,
        target_col=None
    ):
        """Create correlation heatmap"""
        
        # Get numeric data
        numeric_df = self.get_numeric_columns(df)
        
        if numeric_df.empty:
            logger.warning(f"No numeric columns in dataset for {filename}")
            return None
        
        # Calculate correlation
        if target_col and target_col in numeric_df.columns:
            # Correlation with target only
            corr = numeric_df.corr()[target_col].sort_values(ascending=False)
            
            # Create bar plot for target correlation
            fig, ax = plt.subplots(figsize=(10, max(8, len(corr) * 0.3)))
            
            colors = ['red' if x < 0 else 'green' for x in corr.values]
            bars = ax.barh(range(len(corr)), corr.values, color=colors, alpha=0.6)
            
            ax.set_yticks(range(len(corr)))
            ax.set_yticklabels(corr.index, fontsize=9)
            ax.set_xlabel('Correlation with Target', fontsize=12)
            ax.set_title(f'{title}\nCorrelation with {target_col}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, corr.values)):
                ax.text(val, i, f' {val:.3f}', 
                       va='center', fontsize=8,
                       ha='left' if val > 0 else 'right')
            
        else:
            # Full correlation matrix
            corr = numeric_df.corr()
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=figsize)
            
            # Determine if we should annotate
            should_annot = annot and len(corr) <= 20
            
            sns.heatmap(
                corr,
                annot=should_annot,
                fmt='.2f' if should_annot else '',
                cmap='coolwarm',
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={"shrink": 0.8},
                ax=ax,
                vmin=-1,
                vmax=1
            )
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.yticks(rotation=0, fontsize=8)
        
        # Save figure
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"Saved: {filename}")
        return filepath
    
    def analyze_full_datasets(self):
        """Analyze full datasets"""
        
        logger.info("\n" + "="*60)
        logger.info("FULL DATASET CORRELATION ANALYSIS")
        logger.info("="*60)
        
        outputs = []
        
        # 1. Cultivation dataset
        df = self.load_dataset('cultivation.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Full Cultivation Dataset - Correlation Matrix',
                'full_cultivation_correlation.png',
                figsize=(16, 14)
            ))
        
        # 2. Weather dataset
        df = self.load_dataset('weather.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Full Weather Dataset - Correlation Matrix',
                'full_weather_correlation.png',
                figsize=(12, 10)
            ))
        
        # 3. Price dataset
        df = self.load_dataset('price.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Full Price Dataset - Correlation Matrix',
                'full_price_correlation.png',
                figsize=(12, 10)
            ))
        
        # 4. Economic dataset
        df = self.load_dataset('economic.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Full Economic Dataset - Correlation Matrix',
                'full_economic_correlation.png',
                figsize=(12, 10)
            ))
        
        # 5. Merged Model AB dataset
        df = self.load_dataset('merged_model_ab.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Merged Model A+B Dataset - Correlation Matrix',
                'full_merged_ab_correlation.png',
                figsize=(18, 16)
            ))
        
        return [o for o in outputs if o is not None]
    
    def analyze_minimal_datasets(self):
        """Analyze minimal datasets"""
        
        logger.info("\n" + "="*60)
        logger.info("MINIMAL DATASET CORRELATION ANALYSIS")
        logger.info("="*60)
        
        outputs = []
        
        # 1. Minimal Cultivation
        df = self.load_dataset('minimal_cultivation.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Minimal Cultivation Dataset - Correlation Matrix',
                'minimal_cultivation_correlation.png',
                figsize=(12, 10),
                annot=True
            ))
        
        # 2. Minimal Weather
        df = self.load_dataset('minimal_weather.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Minimal Weather Dataset - Correlation Matrix',
                'minimal_weather_correlation.png',
                figsize=(10, 8),
                annot=True
            ))
        
        # 3. Minimal Price
        df = self.load_dataset('minimal_price.csv')
        if df is not None:
            outputs.append(self.create_correlation_heatmap(
                df,
                'Minimal Price Dataset - Correlation Matrix',
                'minimal_price_correlation.png',
                figsize=(10, 8),
                annot=True
            ))
        
        return [o for o in outputs if o is not None]
    
    def analyze_target_correlations(self):
        """Analyze correlations with target variables for each model"""
        
        logger.info("\n" + "="*60)
        logger.info("TARGET CORRELATION ANALYSIS")
        logger.info("="*60)
        
        outputs = []
        
        # Model A: Crop Recommendation (target: profit or yield)
        df = self.load_dataset('merged_model_ab.csv')
        if df is not None:
            # Try to find profit/yield column
            target_candidates = ['profit', 'Profit', 'yield', 'Yield', 
                               'expected_profit', 'total_profit']
            target_col = None
            for col in target_candidates:
                if col in df.columns:
                    target_col = col
                    break
            
            if target_col:
                outputs.append(self.create_correlation_heatmap(
                    df,
                    f'Model A: Features Correlation with {target_col}',
                    f'model_a_target_correlation_{target_col}.png',
                    target_col=target_col
                ))
        
        # Model B: Planting Window (target: success/good_window)
        if df is not None:
            target_candidates = ['success', 'good_window', 'is_good_window', 
                               'planting_success', 'window_quality']
            target_col = None
            for col in target_candidates:
                if col in df.columns:
                    target_col = col
                    break
            
            if target_col:
                outputs.append(self.create_correlation_heatmap(
                    df,
                    f'Model B: Features Correlation with {target_col}',
                    f'model_b_target_correlation_{target_col}.png',
                    target_col=target_col
                ))
        
        # Model C: Price Forecast (target: price)
        df_price = self.load_dataset('price.csv')
        if df_price is not None:
            target_candidates = ['price', 'Price', 'avg_price', 'market_price']
            target_col = None
            for col in target_candidates:
                if col in df_price.columns:
                    target_col = col
                    break
            
            if target_col:
                outputs.append(self.create_correlation_heatmap(
                    df_price,
                    f'Model C: Features Correlation with {target_col}',
                    f'model_c_target_correlation_{target_col}.png',
                    target_col=target_col
                ))
        
        return [o for o in outputs if o is not None]
    
    def create_summary_report(self, all_outputs):
        """Create summary report"""
        
        report_path = self.output_dir / 'README.md'
        
        content = f"""# Data Correlation Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

Total visualizations generated: {len(all_outputs)}

## Files Generated

### Full Dataset Correlations
"""
        
        full_files = [f for f in all_outputs if 'full_' in str(f)]
        for f in full_files:
            content += f"- `{f.name}`\n"
        
        content += "\n### Minimal Dataset Correlations\n"
        minimal_files = [f for f in all_outputs if 'minimal_' in str(f)]
        for f in minimal_files:
            content += f"- `{f.name}`\n"
        
        content += "\n### Target Correlations (by Model)\n"
        target_files = [f for f in all_outputs if 'model_' in str(f) and 'target' in str(f)]
        for f in target_files:
            content += f"- `{f.name}`\n"
        
        content += """
## Dataset Descriptions

### Full Datasets
- **cultivation.csv**: Complete cultivation data with all features
- **weather.csv**: Complete weather data (temperature, rainfall, humidity, etc.)
- **price.csv**: Complete price data for all crops
- **economic.csv**: Economic indicators and market data
- **merged_model_ab.csv**: Combined dataset for Models A and B

### Minimal Datasets
- **minimal_cultivation.csv**: Essential cultivation features only
- **minimal_weather.csv**: Essential weather features only
- **minimal_price.csv**: Essential price features only

### Target Variables
- **Model A (Crop Recommendation)**: Profit/Yield prediction
- **Model B (Planting Window)**: Success/Good window classification
- **Model C (Price Forecast)**: Price prediction

## Interpretation Guide

### Correlation Values
- **1.0**: Perfect positive correlation
- **0.7 to 1.0**: Strong positive correlation
- **0.3 to 0.7**: Moderate positive correlation
- **-0.3 to 0.3**: Weak or no correlation
- **-0.7 to -0.3**: Moderate negative correlation
- **-1.0 to -0.7**: Strong negative correlation
- **-1.0**: Perfect negative correlation

### Color Scheme
- **Red**: Negative correlation
- **White**: No correlation (0)
- **Blue**: Positive correlation

## Usage

These correlation matrices help identify:
1. **Feature relationships**: Which features are related to each other
2. **Multicollinearity**: Features that are highly correlated (may cause issues)
3. **Feature importance**: Which features correlate strongly with target variables
4. **Data quality**: Unexpected correlations may indicate data issues

---

**Generated by**: FarmMe Data Correlation Analyzer
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Summary report saved: {report_path}")


def main():
    """Main execution"""
    
    logger.info("\n" + "="*80)
    logger.info("FARMME DATA CORRELATION ANALYZER".center(80))
    logger.info("="*80 + "\n")
    
    analyzer = DataCorrelationAnalyzer()
    
    all_outputs = []
    
    # Analyze full datasets
    outputs = analyzer.analyze_full_datasets()
    all_outputs.extend(outputs)
    
    # Analyze minimal datasets
    outputs = analyzer.analyze_minimal_datasets()
    all_outputs.extend(outputs)
    
    # Analyze target correlations
    outputs = analyzer.analyze_target_correlations()
    all_outputs.extend(outputs)
    
    # Create summary report
    analyzer.create_summary_report(all_outputs)
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS COMPLETE".center(80))
    logger.info("="*80)
    logger.info(f"\nTotal visualizations: {len(all_outputs)}")
    logger.info(f"Output directory: {analyzer.output_dir}")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    main()

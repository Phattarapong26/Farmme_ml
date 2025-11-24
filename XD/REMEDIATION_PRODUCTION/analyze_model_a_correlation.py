"""
Analyze Model A Feature Correlations
Generate correlation heatmap to understand feature importance for ROI prediction
"""

import sys
sys.path.insert(0, 'REMEDIATION_PRODUCTION')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from Model_A_Fixed.data_loader_clean import DataLoaderClean
from config import Config

print("\n" + "="*80)
print("MODEL A - FEATURE CORRELATION ANALYSIS".center(80))
print("="*80)

# Load data
print("\n📊 Loading data...")
loader = DataLoaderClean()
cultivation = loader.load_cultivation_clean()
farmers = loader.load_farmer_profiles()
crops = loader.load_crop_characteristics()
weather = loader.load_weather()
price = loader.load_price_data()

df = loader.create_training_data(cultivation, farmers, crops, weather, price)

print(f"✅ Loaded {len(df)} samples")
print(f"✅ Features: {df.shape[1]} columns")

# Select numeric features for correlation analysis
print("\n🔍 Selecting numeric features...")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Core features we care about
core_features = [
    'planting_area_rai',
    'expected_yield_kg',
    'growth_days',
    'investment_cost',
    'expected_roi_percent'  # Target
]

# Add water_requirement and risk_level if they're numeric
# If not, we'll encode them
if 'water_requirement' not in numeric_cols:
    # Encode water_requirement
    water_map = {'ต่ำมาก': 1, 'ต่ำ': 2, 'ปานกลาง': 3, 'สูง': 4, 'สูงมาก': 5}
    df['water_requirement_num'] = df['water_requirement'].map(water_map)
    core_features.append('water_requirement_num')
else:
    core_features.append('water_requirement')

if 'risk_level' not in numeric_cols:
    # Encode risk_level
    risk_map = {'ต่ำมาก': 0.1, 'ต่ำ': 0.3, 'กลาง': 0.5, 'ปานกลาง': 0.5, 'สูง': 0.7, 'สูงมาก': 0.9}
    df['risk_level_num'] = df['risk_level'].map(risk_map)
    core_features.append('risk_level_num')
else:
    core_features.append('risk_level')

# Filter to only available features
available_features = [f for f in core_features if f in df.columns]
print(f"✅ Analyzing {len(available_features)} features:")
for feat in available_features:
    print(f"   - {feat}")

# Calculate correlation matrix
print("\n📈 Calculating correlation matrix...")
df_corr = df[available_features].copy()

# Remove any infinite or NaN values
df_corr = df_corr.replace([np.inf, -np.inf], np.nan)
df_corr = df_corr.dropna()

print(f"✅ Clean data: {len(df_corr)} samples")

# Correlation matrix
corr_matrix = df_corr.corr()

# Print correlation with target (expected_roi_percent)
print("\n" + "="*80)
print("CORRELATION WITH TARGET (expected_roi_percent)".center(80))
print("="*80)

target_corr = corr_matrix['expected_roi_percent'].drop('expected_roi_percent').sort_values(ascending=False, key=abs)

print("\n📊 Feature Correlations (sorted by absolute value):")
print("-" * 80)
for feat, corr in target_corr.items():
    bar_length = int(abs(corr) * 50)
    bar = "█" * bar_length
    sign = "+" if corr > 0 else "-"
    print(f"{feat:30s} {sign} {abs(corr):.4f} {bar}")

# Identify top features
print("\n" + "="*80)
print("TOP 3 MOST IMPORTANT FEATURES".center(80))
print("="*80)

top_3 = target_corr.head(3)
for i, (feat, corr) in enumerate(top_3.items(), 1):
    print(f"\n{i}. {feat}")
    print(f"   Correlation: {corr:.4f}")
    print(f"   Impact: {'Positive' if corr > 0 else 'Negative'}")
    if abs(corr) > 0.7:
        print(f"   Strength: 🔴 Very Strong")
    elif abs(corr) > 0.5:
        print(f"   Strength: 🟠 Strong")
    elif abs(corr) > 0.3:
        print(f"   Strength: 🟡 Moderate")
    else:
        print(f"   Strength: 🟢 Weak")

# Create visualizations
print("\n📊 Creating visualizations...")

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'

# Create figure with 2 subplots
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 1. Correlation Heatmap
ax1 = axes[0]
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='RdYlGn', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax1)
ax1.set_title('Model A - Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
ax1.set_xlabel('')
ax1.set_ylabel('')

# Rotate labels
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)

# 2. Bar chart of correlations with target
ax2 = axes[1]
target_corr_sorted = target_corr.sort_values()
colors = ['red' if x < 0 else 'green' for x in target_corr_sorted.values]
target_corr_sorted.plot(kind='barh', ax=ax2, color=colors, alpha=0.7)
ax2.set_title('Feature Correlation with ROI', fontsize=14, fontweight='bold', pad=20)
ax2.set_xlabel('Correlation Coefficient', fontsize=12)
ax2.set_ylabel('')
ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
ax2.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, (feat, val) in enumerate(target_corr_sorted.items()):
    ax2.text(val, i, f' {val:.3f}', va='center', fontsize=10)

plt.tight_layout()

# Save figure
output_dir = Path('REMEDIATION_PRODUCTION/evaluation_results')
output_dir.mkdir(exist_ok=True)
output_file = output_dir / 'model_a_correlation_heatmap.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Saved heatmap to: {output_file}")

# Create a second figure with detailed analysis
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))

# 1. Scatter plot: expected_yield_kg vs ROI
ax1 = axes2[0, 0]
ax1.scatter(df_corr['expected_yield_kg'], df_corr['expected_roi_percent'], 
           alpha=0.3, s=10, color='blue')
ax1.set_xlabel('Expected Yield (kg)', fontsize=11)
ax1.set_ylabel('Expected ROI (%)', fontsize=11)
ax1.set_title('Expected Yield vs ROI', fontsize=12, fontweight='bold')
ax1.grid(alpha=0.3)

# Add correlation text
corr_val = corr_matrix.loc['expected_yield_kg', 'expected_roi_percent']
ax1.text(0.05, 0.95, f'Correlation: {corr_val:.4f}', 
        transform=ax1.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 2. Scatter plot: investment_cost vs ROI
ax2 = axes2[0, 1]
ax2.scatter(df_corr['investment_cost'], df_corr['expected_roi_percent'], 
           alpha=0.3, s=10, color='orange')
ax2.set_xlabel('Investment Cost (Baht)', fontsize=11)
ax2.set_ylabel('Expected ROI (%)', fontsize=11)
ax2.set_title('Investment Cost vs ROI', fontsize=12, fontweight='bold')
ax2.grid(alpha=0.3)

corr_val = corr_matrix.loc['investment_cost', 'expected_roi_percent']
ax2.text(0.05, 0.95, f'Correlation: {corr_val:.4f}', 
        transform=ax2.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 3. Scatter plot: growth_days vs ROI
ax3 = axes2[1, 0]
ax3.scatter(df_corr['growth_days'], df_corr['expected_roi_percent'], 
           alpha=0.3, s=10, color='green')
ax3.set_xlabel('Growth Days', fontsize=11)
ax3.set_ylabel('Expected ROI (%)', fontsize=11)
ax3.set_title('Growth Days vs ROI', fontsize=12, fontweight='bold')
ax3.grid(alpha=0.3)

corr_val = corr_matrix.loc['growth_days', 'expected_roi_percent']
ax3.text(0.05, 0.95, f'Correlation: {corr_val:.4f}', 
        transform=ax3.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 4. Scatter plot: planting_area_rai vs ROI
ax4 = axes2[1, 1]
ax4.scatter(df_corr['planting_area_rai'], df_corr['expected_roi_percent'], 
           alpha=0.3, s=10, color='purple')
ax4.set_xlabel('Planting Area (Rai)', fontsize=11)
ax4.set_ylabel('Expected ROI (%)', fontsize=11)
ax4.set_title('Planting Area vs ROI', fontsize=12, fontweight='bold')
ax4.grid(alpha=0.3)

corr_val = corr_matrix.loc['planting_area_rai', 'expected_roi_percent']
ax4.text(0.05, 0.95, f'Correlation: {corr_val:.4f}', 
        transform=ax4.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save detailed analysis
output_file2 = output_dir / 'model_a_feature_analysis.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight')
print(f"✅ Saved detailed analysis to: {output_file2}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS".center(80))
print("="*80)

print("\n📊 Feature Statistics:")
print("-" * 80)
for feat in available_features:
    if feat != 'expected_roi_percent':
        print(f"\n{feat}:")
        print(f"  Mean: {df_corr[feat].mean():.2f}")
        print(f"  Std:  {df_corr[feat].std():.2f}")
        print(f"  Min:  {df_corr[feat].min():.2f}")
        print(f"  Max:  {df_corr[feat].max():.2f}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE".center(80))
print("="*80)
print(f"\n📁 Output files:")
print(f"   1. {output_file}")
print(f"   2. {output_file2}")
print("\n💡 Key Insights:")
print(f"   - Most important feature: {target_corr.index[0]} (r={target_corr.iloc[0]:.4f})")
print(f"   - Weakest feature: {target_corr.index[-1]} (r={target_corr.iloc[-1]:.4f})")
print(f"   - Features with |r| > 0.5: {sum(abs(target_corr) > 0.5)}")
print(f"   - Features with |r| > 0.3: {sum(abs(target_corr) > 0.3)}")

print("\n" + "="*80)

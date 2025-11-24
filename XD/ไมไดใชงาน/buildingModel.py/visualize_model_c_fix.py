"""
Visualize Model C Fix
=====================
สร้างกราฟเปรียบเทียบ Single Model vs Stratified Models
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from test results
models = ['Single Model', 'Stratified Models']
overall_r2 = [0.5906, 0.7486]
overall_mae = [12.67, 7.64]
expensive_r2 = [-0.0617, 0.0954]
expensive_mae = [26.58, 23.64]

# Create figure with 2x2 subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Model C: Single Model vs Stratified Models Comparison', fontsize=16, fontweight='bold')

# Colors
color_single = '#e74c3c'  # Red
color_stratified = '#27ae60'  # Green

# Plot 1: Overall R²
ax1 = axes[0, 0]
bars1 = ax1.bar(models, overall_r2, color=[color_single, color_stratified], alpha=0.7, edgecolor='black')
ax1.set_ylabel('R² Score', fontsize=12)
ax1.set_title('Overall R² Performance', fontsize=14, fontweight='bold')
ax1.set_ylim([0, 1.0])
ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Baseline')
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.4f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add improvement annotation
improvement_r2 = overall_r2[1] - overall_r2[0]
ax1.annotate(f'+{improvement_r2:.4f}\n(+26.7%)',
             xy=(1, overall_r2[1]), xytext=(1.3, overall_r2[1] + 0.05),
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             fontsize=11, color='green', fontweight='bold')

# Plot 2: Overall MAE
ax2 = axes[0, 1]
bars2 = ax2.bar(models, overall_mae, color=[color_single, color_stratified], alpha=0.7, edgecolor='black')
ax2.set_ylabel('MAE (baht/kg)', fontsize=12)
ax2.set_title('Overall MAE Performance', fontsize=14, fontweight='bold')
ax2.set_ylim([0, 15])
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add improvement annotation
improvement_mae = overall_mae[0] - overall_mae[1]
ax2.annotate(f'-{improvement_mae:.2f}\n(-40%)',
             xy=(1, overall_mae[1]), xytext=(1.3, overall_mae[1] - 1),
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             fontsize=11, color='green', fontweight='bold')

# Plot 3: Expensive Crops R²
ax3 = axes[1, 0]
bars3 = ax3.bar(models, expensive_r2, color=[color_single, color_stratified], alpha=0.7, edgecolor='black')
ax3.set_ylabel('R² Score', fontsize=12)
ax3.set_title('Expensive Crops (>54 baht) R²', fontsize=14, fontweight='bold')
ax3.set_ylim([-0.2, 0.2])
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
ax3.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars3:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.4f}',
             ha='center', va='bottom' if height > 0 else 'top',
             fontsize=11, fontweight='bold')

# Add improvement annotation
improvement_exp_r2 = expensive_r2[1] - expensive_r2[0]
ax3.annotate(f'+{improvement_exp_r2:.4f}\n(+157%)',
             xy=(1, expensive_r2[1]), xytext=(1.3, expensive_r2[1] + 0.05),
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             fontsize=11, color='green', fontweight='bold')

# Plot 4: Expensive Crops MAE
ax4 = axes[1, 1]
bars4 = ax4.bar(models, expensive_mae, color=[color_single, color_stratified], alpha=0.7, edgecolor='black')
ax4.set_ylabel('MAE (baht/kg)', fontsize=12)
ax4.set_title('Expensive Crops (>54 baht) MAE', fontsize=14, fontweight='bold')
ax4.set_ylim([0, 30])
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars4:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add improvement annotation
improvement_exp_mae = expensive_mae[0] - expensive_mae[1]
ax4.annotate(f'-{improvement_exp_mae:.2f}\n(-11%)',
             xy=(1, expensive_mae[1]), xytext=(1.3, expensive_mae[1] - 2),
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             fontsize=11, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('buildingModel.py/model_c_fix_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Saved: buildingModel.py/model_c_fix_comparison.png")

# Create second figure: Performance by Price Range
fig2, ax = plt.subplots(figsize=(12, 6))

price_ranges = ['Low\n(<30 baht)', 'Medium\n(30-54 baht)', 'High\n(>54 baht)', 'Overall']
r2_scores = [0.5782, 0.1059, 0.0954, 0.7486]
mae_scores = [3.04, 4.65, 23.64, 7.64]

x = np.arange(len(price_ranges))
width = 0.35

bars1 = ax.bar(x - width/2, r2_scores, width, label='R² Score', color='#3498db', alpha=0.7, edgecolor='black')
ax2 = ax.twinx()
bars2 = ax2.bar(x + width/2, mae_scores, width, label='MAE (baht/kg)', color='#e74c3c', alpha=0.7, edgecolor='black')

ax.set_xlabel('Price Range', fontsize=12, fontweight='bold')
ax.set_ylabel('R² Score', fontsize=12, fontweight='bold', color='#3498db')
ax2.set_ylabel('MAE (baht/kg)', fontsize=12, fontweight='bold', color='#e74c3c')
ax.set_title('Stratified Models: Performance by Price Range', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(price_ranges)
ax.tick_params(axis='y', labelcolor='#3498db')
ax2.tick_params(axis='y', labelcolor='#e74c3c')
ax.set_ylim([0, 1.0])
ax2.set_ylim([0, 30])
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}',
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#3498db')

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}',
             ha='center', va='bottom', fontsize=10, fontweight='bold', color='#e74c3c')

# Add legends
ax.legend(loc='upper left', fontsize=11)
ax2.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig('buildingModel.py/model_c_stratified_performance.png', dpi=300, bbox_inches='tight')
print("✅ Saved: buildingModel.py/model_c_stratified_performance.png")

print("\n" + "="*80)
print("✅ Visualizations created successfully!")
print("="*80)
print("\nFiles created:")
print("  1. model_c_fix_comparison.png - Comparison between Single and Stratified models")
print("  2. model_c_stratified_performance.png - Performance by price range")
print("\n" + "="*80)

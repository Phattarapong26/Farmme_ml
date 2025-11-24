"""
Visualize Model C Predictions
==============================
สร้างกราฟเปรียบเทียบ Actual vs Predicted Price
"""

import pickle
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("📊 Visualizing Model C Predictions")
print("="*80)

# ============================================================================
# Load Model and Prepare Data
# ============================================================================
print("\n🔄 Loading model and preparing data...")

# Load model
with open('backend/models/model_c_gradient_boosting.pkl', 'rb') as f:
    model = pickle.load(f)

# Load features
with open('backend/models/model_c_features.json', 'r') as f:
    features = json.load(f)

# Load dataset
df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Remove leaky features
LEAKY_FEATURES = ['future_price_7d', 'price_next_day', 'bid_price', 'ask_price', 'base_price', 'spread_pct']
existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
if existing_leaky:
    df = df.drop(columns=existing_leaky)

# Create target
df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)

# Create features
grouped = df.groupby(['province', 'crop_type'])

for lag in [7, 14, 21, 30]:
    df[f'price_lag_{lag}'] = grouped['price_per_kg'].shift(lag)

for window in [7, 14, 30]:
    df[f'price_ma_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).mean()
    )
    df[f'price_std_{window}'] = grouped['price_per_kg'].transform(
        lambda x: x.shift(7).rolling(window, min_periods=1).std()
    )

df['price_momentum_7d'] = (df['price_lag_7'] - df['price_lag_14']) / df['price_lag_14']
df['price_momentum_30d'] = (df['price_lag_7'] - df['price_lag_30']) / df['price_lag_30']

for feature in ['temperature_celsius', 'rainfall_mm', 'humidity_percent', 'drought_index']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

for feature in ['fuel_price', 'fertilizer_price', 'inflation_rate', 'gdp_growth']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

for feature in ['supply_level', 'inventory_level', 'demand_elasticity', 'income_elasticity']:
    if feature in df.columns:
        for lag in [7, 14]:
            df[f'{feature}_lag_{lag}'] = grouped[feature].shift(lag)

# Prepare data
available_features = [col for col in features if col in df.columns]
df_clean = df[['date', 'province', 'crop_type', 'price_per_kg', 'target_price_7d'] + available_features].copy()
df_clean = df_clean.dropna()

# Split
split_idx = int(len(df_clean) * 0.8)
test_df = df_clean.iloc[split_idx:].copy()

X_test = test_df[available_features]
y_test = test_df['target_price_7d']

# Make predictions
y_pred = model.predict(X_test)

# Calculate metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"✅ Data prepared: {len(y_test):,} test samples")
print(f"   MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.4f}")

# ============================================================================
# Create Visualizations
# ============================================================================
print("\n📊 Creating visualizations...")

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))

# ============================================================================
# Plot 1: Actual vs Predicted Scatter
# ============================================================================
ax1 = plt.subplot(2, 3, 1)
plt.scatter(y_test, y_pred, alpha=0.3, s=1)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual Price (บาท/กก.)', fontsize=12)
plt.ylabel('Predicted Price (บาท/กก.)', fontsize=12)
plt.title('Actual vs Predicted Price', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# Add metrics text
textstr = f'R² = {r2:.4f}\nMAE = {mae:.2f}\nRMSE = {rmse:.2f}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', bbox=props)

# ============================================================================
# Plot 2: Residual Plot
# ============================================================================
ax2 = plt.subplot(2, 3, 2)
residuals = y_pred - y_test
plt.scatter(y_pred, residuals, alpha=0.3, s=1)
plt.axhline(y=0, color='r', linestyle='--', lw=2)
plt.xlabel('Predicted Price (บาท/กก.)', fontsize=12)
plt.ylabel('Residuals (บาท)', fontsize=12)
plt.title('Residual Plot', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

# ============================================================================
# Plot 3: Error Distribution
# ============================================================================
ax3 = plt.subplot(2, 3, 3)
plt.hist(residuals, bins=100, edgecolor='black', alpha=0.7)
plt.xlabel('Prediction Error (บาท)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Error Distribution', fontsize=14, fontweight='bold')
plt.axvline(x=0, color='r', linestyle='--', lw=2)
plt.grid(True, alpha=0.3)

# ============================================================================
# Plot 4: Time Series Sample (First 500 points)
# ============================================================================
ax4 = plt.subplot(2, 3, 4)
sample_size = min(500, len(y_test))
x_range = range(sample_size)
plt.plot(x_range, y_test.values[:sample_size], label='Actual', alpha=0.7, linewidth=1)
plt.plot(x_range, y_pred[:sample_size], label='Predicted', alpha=0.7, linewidth=1)
plt.xlabel('Sample Index', fontsize=12)
plt.ylabel('Price (บาท/กก.)', fontsize=12)
plt.title(f'Time Series Comparison (First {sample_size} samples)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# ============================================================================
# Plot 5: Absolute Error Distribution
# ============================================================================
ax5 = plt.subplot(2, 3, 5)
abs_errors = np.abs(residuals)
plt.hist(abs_errors, bins=100, edgecolor='black', alpha=0.7, color='orange')
plt.xlabel('Absolute Error (บาท)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Absolute Error Distribution', fontsize=14, fontweight='bold')
plt.axvline(x=mae, color='r', linestyle='--', lw=2, label=f'MAE = {mae:.2f}')
plt.legend()
plt.grid(True, alpha=0.3)

# ============================================================================
# Plot 6: Error by Price Range
# ============================================================================
ax6 = plt.subplot(2, 3, 6)

# Bin prices
price_bins = pd.cut(y_test, bins=10)
error_by_bin = pd.DataFrame({
    'price_bin': price_bins,
    'abs_error': abs_errors
}).groupby('price_bin')['abs_error'].mean()

x_pos = range(len(error_by_bin))
plt.bar(x_pos, error_by_bin.values, alpha=0.7, color='skyblue', edgecolor='black')
plt.xlabel('Price Range (บาท/กก.)', fontsize=12)
plt.ylabel('Mean Absolute Error (บาท)', fontsize=12)
plt.title('Error by Price Range', fontsize=14, fontweight='bold')
plt.xticks(x_pos, [f'{int(interval.left)}-{int(interval.right)}' for interval in error_by_bin.index], 
           rotation=45, ha='right')
plt.grid(True, alpha=0.3, axis='y')

# ============================================================================
# Add overall title and adjust layout
# ============================================================================
fig.suptitle('Model C - Gradient Boosting Performance Analysis', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])

# Save figure
output_path = 'model_c_predictions_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Saved: {output_path}")

# ============================================================================
# Create detailed comparison plot
# ============================================================================
print("\n📊 Creating detailed comparison plot...")

fig2, axes = plt.subplots(2, 2, figsize=(16, 12))

# Sample random crops for detailed view
sample_indices = np.random.choice(len(y_test), size=min(1000, len(y_test)), replace=False)
sample_indices = sorted(sample_indices)

# Plot 1: Scatter with density
ax = axes[0, 0]
from scipy.stats import gaussian_kde
xy = np.vstack([y_test.values[sample_indices], y_pred[sample_indices]])
z = gaussian_kde(xy)(xy)
scatter = ax.scatter(y_test.values[sample_indices], y_pred[sample_indices], 
                     c=z, s=20, alpha=0.5, cmap='viridis')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
        'r--', lw=2, label='Perfect Prediction')
ax.set_xlabel('Actual Price (บาท/กก.)', fontsize=12)
ax.set_ylabel('Predicted Price (บาท/กก.)', fontsize=12)
ax.set_title('Actual vs Predicted (Density)', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Density')

# Plot 2: Box plot of errors by price quartile
ax = axes[0, 1]
quartiles = pd.qcut(y_test, q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
error_df = pd.DataFrame({
    'quartile': quartiles,
    'error': residuals
})
error_df.boxplot(column='error', by='quartile', ax=ax)
ax.set_xlabel('Price Quartile', fontsize=12)
ax.set_ylabel('Prediction Error (บาท)', fontsize=12)
ax.set_title('Error Distribution by Price Quartile', fontsize=14, fontweight='bold')
ax.axhline(y=0, color='r', linestyle='--', lw=2)
plt.suptitle('')  # Remove default title

# Plot 3: Cumulative error distribution
ax = axes[1, 0]
sorted_abs_errors = np.sort(abs_errors)
cumulative = np.arange(1, len(sorted_abs_errors) + 1) / len(sorted_abs_errors) * 100
ax.plot(sorted_abs_errors, cumulative, linewidth=2)
ax.axvline(x=5, color='g', linestyle='--', alpha=0.7, label='±5 บาท')
ax.axvline(x=10, color='orange', linestyle='--', alpha=0.7, label='±10 บาท')
ax.axvline(x=20, color='r', linestyle='--', alpha=0.7, label='±20 บาท')
ax.set_xlabel('Absolute Error (บาท)', fontsize=12)
ax.set_ylabel('Cumulative Percentage (%)', fontsize=12)
ax.set_title('Cumulative Error Distribution', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 50)

# Plot 4: Performance metrics summary
ax = axes[1, 1]
ax.axis('off')

metrics_text = f"""
Model Performance Summary
{'='*40}

Overall Metrics:
  • R² Score:        {r2:.4f}
  • MAE:             {mae:.2f} บาท/กก.
  • RMSE:            {rmse:.2f} บาท/กก.
  • MAPE:            {np.mean(np.abs((y_test - y_pred) / y_test)) * 100:.2f}%

Accuracy Distribution:
  • Within ±5 บาท:   {(abs_errors <= 5).mean()*100:.1f}%
  • Within ±10 บาท:  {(abs_errors <= 10).mean()*100:.1f}%
  • Within ±20 บาท:  {(abs_errors <= 20).mean()*100:.1f}%

Error Statistics:
  • Mean Error:      {np.mean(residuals):.2f} บาท
  • Std Error:       {np.std(residuals):.2f} บาท
  • Median Error:    {np.median(abs_errors):.2f} บาท

Test Set:
  • Total Samples:   {len(y_test):,}
  • Date Range:      {test_df['date'].min().strftime('%Y-%m-%d')}
                     to {test_df['date'].max().strftime('%Y-%m-%d')}

Model: Gradient Boosting (Clean Version)
Version: 6.0.0
No Data Leakage ✓
"""

ax.text(0.1, 0.9, metrics_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

fig2.suptitle('Model C - Detailed Performance Analysis', 
              fontsize=16, fontweight='bold')
plt.tight_layout()

# Save figure
output_path2 = 'model_c_detailed_analysis.png'
plt.savefig(output_path2, dpi=300, bbox_inches='tight')
print(f"✅ Saved: {output_path2}")

# ============================================================================
# Create crop-specific comparison
# ============================================================================
print("\n📊 Creating crop-specific analysis...")

# Get top 6 crops by sample count
top_crops = test_df['crop_type'].value_counts().head(6).index

fig3, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for idx, crop in enumerate(top_crops):
    crop_mask = test_df['crop_type'] == crop
    crop_actual = y_test[crop_mask]
    crop_pred = y_pred[crop_mask]
    
    ax = axes[idx]
    ax.scatter(crop_actual, crop_pred, alpha=0.5, s=10)
    ax.plot([crop_actual.min(), crop_actual.max()], 
            [crop_actual.min(), crop_actual.max()], 
            'r--', lw=2)
    
    crop_mae = mean_absolute_error(crop_actual, crop_pred)
    crop_r2 = r2_score(crop_actual, crop_pred)
    
    ax.set_xlabel('Actual Price (บาท/กก.)', fontsize=10)
    ax.set_ylabel('Predicted Price (บาท/กก.)', fontsize=10)
    ax.set_title(f'{crop}\nMAE: {crop_mae:.2f}, R²: {crop_r2:.3f}', 
                 fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)

fig3.suptitle('Model C - Performance by Crop Type (Top 6)', 
              fontsize=16, fontweight='bold')
plt.tight_layout()

# Save figure
output_path3 = 'model_c_by_crop.png'
plt.savefig(output_path3, dpi=300, bbox_inches='tight')
print(f"✅ Saved: {output_path3}")

print("\n" + "="*80)
print("✅ All visualizations created successfully!")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. {output_path}")
print(f"  2. {output_path2}")
print(f"  3. {output_path3}")
print("\n" + "="*80)

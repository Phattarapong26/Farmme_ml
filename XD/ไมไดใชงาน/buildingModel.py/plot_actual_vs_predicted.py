"""
Plot Actual vs Predicted Prices
================================
สร้างกราฟเปรียบเทียบราคาจริง vs ราคาที่ทำนาย
หลังจากปรับปรุง Model C ด้วย Stratified approach
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("📊 Plotting Actual vs Predicted Prices")
print("="*80)

# ============================================================================
# Load Data
# ============================================================================
print("\n📂 Loading data...")
df = pd.read_csv('buildingModel.py/Dataset/FARMME_GPU_DATASET.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
print(f"✅ Loaded {len(df):,} rows")

# Remove leaky features
LEAKY_FEATURES = ['future_price_7d', 'price_next_day', 'bid_price', 'ask_price', 'base_price', 'spread_pct']
existing_leaky = [col for col in LEAKY_FEATURES if col in df.columns]
if existing_leaky:
    df = df.drop(columns=existing_leaky)

# Create target
df['target_price_7d'] = df.groupby(['province', 'crop_type'])['price_per_kg'].shift(-7)

# Create features
print("🔄 Creating features...")
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

# ============================================================================
# Load Models
# ============================================================================
print("\n📦 Loading trained models...")

# Try to load final models first, fallback to test models
try:
    with open('backend/models/model_c_stratified_low_final.pkl', 'rb') as f:
        model_low = pickle.load(f)
    with open('backend/models/model_c_stratified_medium_final.pkl', 'rb') as f:
        model_medium = pickle.load(f)
    with open('backend/models/model_c_stratified_high_final.pkl', 'rb') as f:
        model_high = pickle.load(f)
    with open('backend/models/model_c_stratified_thresholds_final.json', 'r') as f:
        thresholds = json.load(f)
    with open('backend/models/model_c_stratified_features_final.json', 'r') as f:
        features = json.load(f)
    print("✅ Loaded FINAL models")
except:
    print("⚠️  Final models not found, loading test models...")
    with open('backend/models/model_c_stratified_low.pkl', 'rb') as f:
        model_low = pickle.load(f)
    with open('backend/models/model_c_stratified_medium.pkl', 'rb') as f:
        model_medium = pickle.load(f)
    with open('backend/models/model_c_stratified_high.pkl', 'rb') as f:
        model_high = pickle.load(f)
    with open('backend/models/model_c_stratified_thresholds.json', 'r') as f:
        thresholds = json.load(f)
    with open('backend/models/model_c_stratified_features.json', 'r') as f:
        features = json.load(f)
    print("✅ Loaded test models")

low_threshold = thresholds['low_threshold']
high_threshold = thresholds['high_threshold']

print(f"   Low threshold: {low_threshold:.2f} baht/kg")
print(f"   High threshold: {high_threshold:.2f} baht/kg")

# ============================================================================
# Prepare Test Data
# ============================================================================
print("\n🔄 Preparing test data...")
available_features = [col for col in features if col in df.columns]
df_clean = df[['crop_type', 'province', 'target_price_7d'] + available_features].dropna()

# Use last 20% as test set
split_idx = int(len(df_clean) * 0.8)
test_df = df_clean.iloc[split_idx:].copy()

print(f"✅ Test set: {len(test_df):,} samples")

# Categorize by price
test_df['price_category'] = pd.cut(
    test_df['target_price_7d'],
    bins=[0, low_threshold, high_threshold, float('inf')],
    labels=['low', 'medium', 'high']
)

# ============================================================================
# Make Predictions
# ============================================================================
print("\n🔮 Making predictions...")
test_df['predicted_price'] = np.nan

models = {'low': model_low, 'medium': model_medium, 'high': model_high}

for category in ['low', 'medium', 'high']:
    mask = test_df['price_category'] == category
    X_test_cat = test_df.loc[mask, available_features]
    test_df.loc[mask, 'predicted_price'] = models[category].predict(X_test_cat)

test_df = test_df.dropna(subset=['predicted_price'])

# Calculate metrics
y_true = test_df['target_price_7d']
y_pred = test_df['predicted_price']

overall_mae = mean_absolute_error(y_true, y_pred)
overall_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
overall_r2 = r2_score(y_true, y_pred)

print(f"\n📊 Overall Performance:")
print(f"   MAE:  {overall_mae:.2f} baht/kg")
print(f"   RMSE: {overall_rmse:.2f} baht/kg")
print(f"   R²:   {overall_r2:.4f}")

# ============================================================================
# Create Visualizations
# ============================================================================
print("\n📊 Creating visualizations...")

# Figure 1: Overall Actual vs Predicted
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Model C (Stratified): Actual vs Predicted Prices', fontsize=18, fontweight='bold')

# Plot 1: Scatter plot - Overall
ax1 = axes[0, 0]
ax1.scatter(y_true, y_pred, alpha=0.3, s=10, c='#3498db')
ax1.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 
         'r--', lw=2, label='Perfect Prediction')
ax1.set_xlabel('Actual Price (baht/kg)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Predicted Price (baht/kg)', fontsize=12, fontweight='bold')
ax1.set_title(f'Overall Performance\nR² = {overall_r2:.4f}, MAE = {overall_mae:.2f}', 
              fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Plot 2: Residual plot
ax2 = axes[0, 1]
residuals = y_true - y_pred
ax2.scatter(y_pred, residuals, alpha=0.3, s=10, c='#e74c3c')
ax2.axhline(y=0, color='black', linestyle='-', lw=2)
ax2.set_xlabel('Predicted Price (baht/kg)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Residuals (baht/kg)', fontsize=12, fontweight='bold')
ax2.set_title('Residual Plot', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Plot 3: Distribution of errors
ax3 = axes[1, 0]
errors = np.abs(residuals)
ax3.hist(errors, bins=50, color='#9b59b6', alpha=0.7, edgecolor='black')
ax3.axvline(x=overall_mae, color='red', linestyle='--', lw=2, label=f'MAE = {overall_mae:.2f}')
ax3.set_xlabel('Absolute Error (baht/kg)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax3.set_title('Distribution of Prediction Errors', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# Plot 4: Performance by price range
ax4 = axes[1, 1]
categories = ['Low\n(<30)', 'Medium\n(30-54)', 'High\n(>54)', 'Overall']
r2_scores = []
mae_scores = []

for cat in ['low', 'medium', 'high']:
    mask = test_df['price_category'] == cat
    if mask.sum() > 0:
        r2 = r2_score(test_df.loc[mask, 'target_price_7d'], 
                      test_df.loc[mask, 'predicted_price'])
        mae = mean_absolute_error(test_df.loc[mask, 'target_price_7d'], 
                                  test_df.loc[mask, 'predicted_price'])
        r2_scores.append(r2)
        mae_scores.append(mae)

r2_scores.append(overall_r2)
mae_scores.append(overall_mae)

x = np.arange(len(categories))
width = 0.35

bars1 = ax4.bar(x - width/2, r2_scores, width, label='R²', color='#3498db', alpha=0.7, edgecolor='black')
ax4_twin = ax4.twinx()
bars2 = ax4_twin.bar(x + width/2, mae_scores, width, label='MAE', color='#e74c3c', alpha=0.7, edgecolor='black')

ax4.set_xlabel('Price Range', fontsize=12, fontweight='bold')
ax4.set_ylabel('R² Score', fontsize=12, fontweight='bold', color='#3498db')
ax4_twin.set_ylabel('MAE (baht/kg)', fontsize=12, fontweight='bold', color='#e74c3c')
ax4.set_title('Performance by Price Range', fontsize=13, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(categories)
ax4.tick_params(axis='y', labelcolor='#3498db')
ax4_twin.tick_params(axis='y', labelcolor='#e74c3c')
ax4.set_ylim([0, 1.0])
ax4_twin.set_ylim([0, max(mae_scores) * 1.2])

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.3f}',
             ha='center', va='bottom', fontsize=9, fontweight='bold', color='#3498db')

for bar in bars2:
    height = bar.get_height()
    ax4_twin.text(bar.get_x() + bar.get_width()/2., height,
                  f'{height:.1f}',
                  ha='center', va='bottom', fontsize=9, fontweight='bold', color='#e74c3c')

ax4.legend(loc='upper left', fontsize=10)
ax4_twin.legend(loc='upper right', fontsize=10)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('buildingModel.py/actual_vs_predicted_overall.png', dpi=300, bbox_inches='tight')
print("✅ Saved: actual_vs_predicted_overall.png")

# ============================================================================
# Figure 2: Detailed view by price range
# ============================================================================
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
fig2.suptitle('Actual vs Predicted by Price Range', fontsize=16, fontweight='bold')

colors = {'low': '#27ae60', 'medium': '#f39c12', 'high': '#e74c3c'}
titles = {
    'low': f'Low Price (<{low_threshold:.0f} baht/kg)',
    'medium': f'Medium Price ({low_threshold:.0f}-{high_threshold:.0f} baht/kg)',
    'high': f'High Price (>{high_threshold:.0f} baht/kg)'
}

for idx, (cat, ax) in enumerate(zip(['low', 'medium', 'high'], axes2)):
    mask = test_df['price_category'] == cat
    if mask.sum() == 0:
        continue
    
    y_true_cat = test_df.loc[mask, 'target_price_7d']
    y_pred_cat = test_df.loc[mask, 'predicted_price']
    
    r2_cat = r2_score(y_true_cat, y_pred_cat)
    mae_cat = mean_absolute_error(y_true_cat, y_pred_cat)
    
    ax.scatter(y_true_cat, y_pred_cat, alpha=0.4, s=15, c=colors[cat])
    ax.plot([y_true_cat.min(), y_true_cat.max()], 
            [y_true_cat.min(), y_true_cat.max()], 
            'r--', lw=2, label='Perfect')
    ax.set_xlabel('Actual Price (baht/kg)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Predicted Price (baht/kg)', fontsize=11, fontweight='bold')
    ax.set_title(f'{titles[cat]}\nR² = {r2_cat:.4f}, MAE = {mae_cat:.2f}', 
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('buildingModel.py/actual_vs_predicted_by_range.png', dpi=300, bbox_inches='tight')
print("✅ Saved: actual_vs_predicted_by_range.png")

# ============================================================================
# Figure 3: Sample crops comparison
# ============================================================================
print("\n📊 Creating sample crops comparison...")

# Select some interesting crops
sample_crops = test_df.groupby('crop_type').size().nlargest(6).index.tolist()

fig3, axes3 = plt.subplots(2, 3, figsize=(18, 10))
fig3.suptitle('Actual vs Predicted: Sample Crops', fontsize=16, fontweight='bold')

for idx, crop in enumerate(sample_crops):
    ax = axes3[idx // 3, idx % 3]
    
    crop_data = test_df[test_df['crop_type'] == crop]
    if len(crop_data) < 10:
        continue
    
    y_true_crop = crop_data['target_price_7d']
    y_pred_crop = crop_data['predicted_price']
    
    r2_crop = r2_score(y_true_crop, y_pred_crop)
    mae_crop = mean_absolute_error(y_true_crop, y_pred_crop)
    
    ax.scatter(y_true_crop, y_pred_crop, alpha=0.5, s=20)
    ax.plot([y_true_crop.min(), y_true_crop.max()], 
            [y_true_crop.min(), y_true_crop.max()], 
            'r--', lw=2)
    ax.set_xlabel('Actual (baht/kg)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Predicted (baht/kg)', fontsize=10, fontweight='bold')
    ax.set_title(f'{crop}\nR² = {r2_crop:.3f}, MAE = {mae_crop:.1f}', 
                 fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('buildingModel.py/actual_vs_predicted_crops.png', dpi=300, bbox_inches='tight')
print("✅ Saved: actual_vs_predicted_crops.png")

# ============================================================================
# Print Summary Statistics
# ============================================================================
print("\n" + "="*80)
print("📊 SUMMARY STATISTICS")
print("="*80)

print(f"\n✅ Overall Performance:")
print(f"   Samples: {len(test_df):,}")
print(f"   R²:      {overall_r2:.4f}")
print(f"   MAE:     {overall_mae:.2f} baht/kg")
print(f"   RMSE:    {overall_rmse:.2f} baht/kg")

print(f"\n📊 Performance by Price Range:")
for cat in ['low', 'medium', 'high']:
    mask = test_df['price_category'] == cat
    if mask.sum() > 0:
        r2 = r2_score(test_df.loc[mask, 'target_price_7d'], 
                      test_df.loc[mask, 'predicted_price'])
        mae = mean_absolute_error(test_df.loc[mask, 'target_price_7d'], 
                                  test_df.loc[mask, 'predicted_price'])
        print(f"   {cat.upper()}: R² = {r2:.4f}, MAE = {mae:.2f} baht/kg ({mask.sum():,} samples)")

print(f"\n📊 Error Statistics:")
print(f"   Mean Absolute Error: {overall_mae:.2f} baht/kg")
print(f"   Median Absolute Error: {np.median(errors):.2f} baht/kg")
print(f"   90th Percentile Error: {np.percentile(errors, 90):.2f} baht/kg")
print(f"   95th Percentile Error: {np.percentile(errors, 95):.2f} baht/kg")
print(f"   Max Error: {errors.max():.2f} baht/kg")

print("\n" + "="*80)
print("✅ Visualizations Complete!")
print("="*80)
print("\nFiles created:")
print("  1. actual_vs_predicted_overall.png - Overall performance")
print("  2. actual_vs_predicted_by_range.png - By price range")
print("  3. actual_vs_predicted_crops.png - Sample crops")
print("\n" + "="*80)

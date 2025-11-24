"""
Visualize Model C Predictions Over Time
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from model_c_prediction_service import model_c_service

print("\n" + "="*80)
print("VISUALIZING MODEL C PREDICTIONS".center(80))
print("="*80)

# Test multiple crops
test_cases = [
    ("พริก", "เชียงใหม่"),
    ("มะเขือเทศ", "กรุงเทพมหานคร"),
    ("ผักบุ้ง", "นครปฐม")
]

fig, axes = plt.subplots(len(test_cases), 1, figsize=(15, 5 * len(test_cases)))

if len(test_cases) == 1:
    axes = [axes]

for idx, (crop, province) in enumerate(test_cases):
    print(f"\nTesting case {idx+1}...")
    
    # Get predictions
    result = model_c_service.predict_price(
        crop_type=crop,
        province=province,
        days_ahead=180
    )
    
    if not result['success']:
        print(f"   Failed!")
        continue
    
    # Extract data
    current_price = result['current_price']
    predictions = result['predictions']
    
    # Prepare plot data
    days = [0] + [p['days_ahead'] for p in predictions]
    prices = [current_price] + [p['predicted_price'] for p in predictions]
    price_mins = [current_price] + [p['price_range']['min'] for p in predictions]
    price_maxs = [current_price] + [p['price_range']['max'] for p in predictions]
    
    # Plot
    ax = axes[idx]
    
    ax.plot(days, prices, 'b-o', linewidth=2, markersize=8, label='Predicted Price')
    ax.fill_between(days, price_mins, price_maxs, alpha=0.2, label='Price Range')
    ax.axhline(y=current_price, color='r', linestyle='--', linewidth=1, label='Current Price')
    
    if 'historical_mean' in result:
        ax.axhline(y=result['historical_mean'], color='g', linestyle=':', linewidth=1, label='Historical Mean')
    
    ax.set_xlabel('Days Ahead')
    ax.set_ylabel('Price (baht/kg)')
    ax.set_title(f'{crop} - {province}\nCurrent: {current_price} baht/kg, Trend: {result["price_trend"]} ({result["trend_percentage"]}%)',
                fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    print(f"   Current: {current_price} baht/kg")
    print(f"   7 days: {predictions[0]['predicted_price']} baht/kg")
    print(f"   30 days: {predictions[1]['predicted_price']} baht/kg")
    print(f"   Trend: {result['price_trend']} ({result['trend_percentage']}%)")

plt.tight_layout()

output_path = Path('outputs/model_c_predictions_test.png')
output_path.parent.mkdir(exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight')

print(f"\nVisualization saved: {output_path}")
print("\n" + "="*80)

plt.close()

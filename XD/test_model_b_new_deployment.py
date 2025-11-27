"""
Test Model B New Deployment (V2 - Gradient Boosting)
Test the newly deployed model with the updated wrapper
"""

from backend.model_b_wrapper import ModelBWrapper
import logging

logging.basicConfig(level=logging.INFO)

print("\n" + "="*80)
print("MODEL B NEW DEPLOYMENT TEST (V2 - Gradient Boosting)")
print("="*80)

# Initialize wrapper
print("\n📦 Loading Model B...")
wrapper = ModelBWrapper()

print("\n" + "="*80)
print("TEST PREDICTIONS")
print("="*80)

# Test case 1: Good window (rainy season)
print("\n📝 Test 1: พริก - เชียงใหม่ - ฤดูฝน (มิถุนายน)")
result = wrapper.predict_planting_window(
    crop_type='พริก',
    province='เชียงใหม่',
    planting_date='2024-06-15'
)
print(f"  Is Good Window: {result['is_good_window']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Reason: {result['reason']}")

# Test case 2: Bad window (winter)
print("\n📝 Test 2: พริก - เชียงใหม่ - ฤดูหนาว (มกราคม)")
result = wrapper.predict_planting_window(
    crop_type='พริก',
    province='เชียงใหม่',
    planting_date='2024-01-15'
)
print(f"  Is Good Window: {result['is_good_window']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Reason: {result['reason']}")

# Test case 3: Different crop - มะเขือเทศ
print("\n📝 Test 3: มะเขือเทศ - กรุงเทพมหานคร - ฤดูฝน (กรกฎาคม)")
result = wrapper.predict_planting_window(
    crop_type='มะเขือเทศ',
    province='กรุงเทพมหานคร',
    planting_date='2024-07-15'
)
print(f"  Is Good Window: {result['is_good_window']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Reason: {result['reason']}")

# Test case 4: Different province - เชียงราย
print("\n📝 Test 4: พริก - เชียงราย - ฤดูร้อน (เมษายน)")
result = wrapper.predict_planting_window(
    crop_type='พริก',
    province='เชียงราย',
    planting_date='2024-04-15'
)
print(f"  Is Good Window: {result['is_good_window']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Reason: {result['reason']}")

# Test batch prediction
print("\n📝 Test 5: Batch Prediction (3 records)")
batch_data = [
    {'crop_type': 'พริก', 'province': 'เชียงใหม่', 'planting_date': '2024-06-15'},
    {'crop_type': 'มะเขือเทศ', 'province': 'กรุงเทพมหานคร', 'planting_date': '2024-07-15'},
    {'crop_type': 'พริก', 'province': 'เชียงราย', 'planting_date': '2024-01-15'},
]

results = wrapper.predict_batch(batch_data)
for i, result in enumerate(results, 1):
    if 'error' not in result:
        print(f"  Record {i}: {result['is_good_window']} (confidence: {result['confidence']:.2%})")
    else:
        print(f"  Record {i}: Error - {result['error']}")

print("\n" + "="*80)
print("✅ Model B New Deployment Test Complete")
print("="*80)
print("\nModel Details:")
print("  - Algorithm: Gradient Boosting")
print("  - Version: fixed_v2.0_blocked_stratified")
print("  - Trained: November 27, 2025")
print("  - File: backend/models/model_b_xgboost.pkl")
print("  - Old model backed up: backend/models/model_b_xgboost_OLD_Nov23.pkl")
print("="*80 + "\n")

# -*- coding: utf-8 -*-
"""
Test Model A Integration with Multiple User Profiles
ทดสอบ Model A กับผู้ใช้หลายจังหวัด
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("MODEL A INTEGRATION TEST")
print("Testing with Multiple User Profiles from Different Provinces")
print("=" * 80)
print()

# Test users from different provinces
test_users = [
    {
        "name": "สมชาย - เชียงใหม่",
        "province": "เชียงใหม่",
        "soil_type": "ดินร่วน",
        "water_availability": "น้ำชลประทาน",
        "budget_level": "ปานกลาง",
        "risk_tolerance": "ปานกลาง"
    },
    {
        "name": "สมหญิง - นครราชสีมา",
        "province": "นครราชสีมา",
        "soil_type": "ดินร่วนปนทราย",
        "water_availability": "น้ำฝน",
        "budget_level": "ต่ำ",
        "risk_tolerance": "ต่ำ"
    },
    {
        "name": "ประเสริฐ - กรุงเทพมหานคร",
        "province": "กรุงเทพมหานคร",
        "soil_type": "ดินเหนียว",
        "water_availability": "น้ำประปา",
        "budget_level": "สูง",
        "risk_tolerance": "สูง"
    },
    {
        "name": "มาลี - ขอนแก่น",
        "province": "ขอนแก่น",
        "soil_type": "ดินทราย",
        "water_availability": "น้ำบาดาล",
        "budget_level": "ปานกลาง",
        "risk_tolerance": "ต่ำ"
    },
    {
        "name": "สุดา - สุราษฎร์ธานี",
        "province": "สุราษฎร์ธานี",
        "soil_type": "ดินร่วน",
        "water_availability": "น้ำฝน",
        "budget_level": "สูง",
        "risk_tolerance": "ปานกลาง"
    }
]

# ============================================================================
# Test 1: Load Model A Wrapper
# ============================================================================
print("=" * 80)
print("TEST 1: Loading Model A Wrapper")
print("=" * 80)
print()

try:
    from model_a_wrapper import model_a_wrapper
    
    print(f"✅ Model A Wrapper loaded successfully!")
    print(f"   Model loaded: {model_a_wrapper.model_loaded}")
    print(f"   Model path: {model_a_wrapper.model_path}")
    print(f"   Model type: {type(model_a_wrapper.model).__name__}")
    print(f"   Has scaler: {model_a_wrapper.scaler is not None}")
    print(f"   Has encoders: {model_a_wrapper.encoders is not None}")
    
    if model_a_wrapper.metadata:
        print(f"   Model version: {model_a_wrapper.metadata.get('version', 'N/A')}")
        print(f"   R² Score: {model_a_wrapper.metadata.get('r2_score', 'N/A'):.4f}")
        print(f"   MAE: {model_a_wrapper.metadata.get('mae', 'N/A'):.2f}%")
        print(f"   MAPE: {model_a_wrapper.metadata.get('mape', 'N/A'):.2f}%")
    
    print()
    
except Exception as e:
    print(f"❌ Failed to load Model A Wrapper: {e}")
    sys.exit(1)

# ============================================================================
# Test 2: Test Recommendations for Each User
# ============================================================================
print("=" * 80)
print("TEST 2: Testing Recommendations for Multiple Users")
print("=" * 80)
print()

results_summary = []

for idx, user in enumerate(test_users, 1):
    print(f"[{idx}/{len(test_users)}] Testing: {user['name']}")
    print("-" * 80)
    print(f"   Province: {user['province']}")
    print(f"   Soil Type: {user['soil_type']}")
    print(f"   Water: {user['water_availability']}")
    print(f"   Budget: {user['budget_level']}")
    print(f"   Risk Tolerance: {user['risk_tolerance']}")
    print()
    
    try:
        # Get recommendations
        result = model_a_wrapper.get_recommendations(
            province=user['province'],
            soil_type=user['soil_type'],
            water_availability=user['water_availability'],
            budget_level=user['budget_level'],
            risk_tolerance=user['risk_tolerance']
        )
        
        if result.get('success'):
            recommendations = result.get('recommendations', [])
            
            print(f"   ✅ Success! Got {len(recommendations)} recommendations")
            print(f"   Model used: {result.get('model_used', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 0):.2%}")
            print()
            
            if recommendations:
                print(f"   Top 5 Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. {rec.get('crop_type', 'N/A')}")
                    print(f"      - Suitability Score: {rec.get('suitability_score', 0):.2f}")
                    print(f"      - Expected Yield: {rec.get('expected_yield_kg_per_rai', 0):,.0f} kg/rai")
                    print(f"      - Estimated Revenue: {rec.get('estimated_revenue_per_rai', 0):,.0f} บาท/ไร่")
                    print(f"      - Predicted ROI: {rec.get('predicted_roi', 0):.2f}%")
                    print(f"      - Water Requirement: {rec.get('water_requirement', 'N/A')}")
                    print(f"      - Risk Level: {rec.get('risk_level', 'N/A')}")
                
                # Store summary
                results_summary.append({
                    'user': user['name'],
                    'province': user['province'],
                    'success': True,
                    'recommendations': len(recommendations),
                    'top_crop': recommendations[0].get('crop_type', 'N/A'),
                    'top_score': recommendations[0].get('suitability_score', 0),
                    'top_roi': recommendations[0].get('predicted_roi', 0)
                })
            else:
                print(f"   ⚠️ No recommendations returned")
                results_summary.append({
                    'user': user['name'],
                    'province': user['province'],
                    'success': True,
                    'recommendations': 0,
                    'top_crop': 'N/A',
                    'top_score': 0,
                    'top_roi': 0
                })
        else:
            error = result.get('error', 'Unknown error')
            print(f"   ❌ Failed: {error}")
            results_summary.append({
                'user': user['name'],
                'province': user['province'],
                'success': False,
                'error': error
            })
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        results_summary.append({
            'user': user['name'],
            'province': user['province'],
            'success': False,
            'error': str(e)
        })
    
    print()

# ============================================================================
# Test 3: Summary Report
# ============================================================================
print("=" * 80)
print("TEST 3: Summary Report")
print("=" * 80)
print()

successful = [r for r in results_summary if r.get('success')]
failed = [r for r in results_summary if not r.get('success')]

print(f"Total Tests: {len(test_users)}")
print(f"Successful: {len(successful)} ({len(successful)/len(test_users)*100:.1f}%)")
print(f"Failed: {len(failed)} ({len(failed)/len(test_users)*100:.1f}%)")
print()

if successful:
    print("✅ Successful Tests:")
    print()
    for result in successful:
        print(f"   {result['user']} ({result['province']})")
        print(f"      Recommendations: {result['recommendations']}")
        if result['recommendations'] > 0:
            print(f"      Top Crop: {result['top_crop']}")
            print(f"      Score: {result['top_score']:.2f}")
            print(f"      ROI: {result['top_roi']:.2f}%")
        print()

if failed:
    print("❌ Failed Tests:")
    print()
    for result in failed:
        print(f"   {result['user']} ({result['province']})")
        print(f"      Error: {result.get('error', 'Unknown')}")
        print()

# ============================================================================
# Test 4: Model Performance Check
# ============================================================================
print("=" * 80)
print("TEST 4: Model Performance Check")
print("=" * 80)
print()

if successful:
    # Calculate average scores
    avg_recommendations = sum(r['recommendations'] for r in successful) / len(successful)
    avg_score = sum(r['top_score'] for r in successful if r['recommendations'] > 0) / len([r for r in successful if r['recommendations'] > 0])
    avg_roi = sum(r['top_roi'] for r in successful if r['recommendations'] > 0) / len([r for r in successful if r['recommendations'] > 0])
    
    print(f"Average Recommendations per User: {avg_recommendations:.1f}")
    print(f"Average Top Crop Score: {avg_score:.2f}")
    print(f"Average Top Crop ROI: {avg_roi:.2f}%")
    print()
    
    # Check diversity
    top_crops = [r['top_crop'] for r in successful if r['recommendations'] > 0]
    unique_crops = len(set(top_crops))
    
    print(f"Crop Diversity:")
    print(f"   Unique Top Crops: {unique_crops}/{len(top_crops)}")
    print(f"   Diversity Rate: {unique_crops/len(top_crops)*100:.1f}%")
    print()
    
    # Show crop distribution
    from collections import Counter
    crop_counts = Counter(top_crops)
    print(f"Top Crop Distribution:")
    for crop, count in crop_counts.most_common():
        print(f"   {crop}: {count} times ({count/len(top_crops)*100:.1f}%)")

print()
print("=" * 80)
print("✅ INTEGRATION TEST COMPLETE!")
print("=" * 80)
print()

if len(successful) == len(test_users):
    print("🎉 All tests passed! Model A is working correctly.")
elif len(successful) > 0:
    print(f"⚠️ Partial success: {len(successful)}/{len(test_users)} tests passed.")
else:
    print("❌ All tests failed. Please check the model configuration.")

print()

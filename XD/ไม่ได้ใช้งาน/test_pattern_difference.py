"""
Test Pattern Difference
========================
ทดสอบว่าแต่ละพืช/จังหวัด มี pattern ต่างกันหรือไม่
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("="*80)
print("Testing Pattern Difference")
print("="*80)

# Test different crops and provinces
test_cases = [
    {"crop": "พริก", "province": "เชียงใหม่"},
    {"crop": "มะเขือเทศ", "province": "เชียงใหม่"},
    {"crop": "พริก", "province": "กรุงเทพมหานคร"},
    {"crop": "ข้าว", "province": "สุพรรณบุรี"},
]

try:
    from price_prediction_service import price_prediction_service
    
    results = []
    
    for case in test_cases:
        print(f"\nTesting: {case['crop']} in {case['province']}")
        print("-" * 50)
        
        result = price_prediction_service.predict_price(
            crop_type=case['crop'],
            province=case['province'],
            days_ahead=7
        )
        
        if result.get('success'):
            daily_forecasts = result.get('daily_forecasts', [])
            
            if daily_forecasts:
                # Get first 3 prices
                prices = [f['predicted_price'] for f in daily_forecasts[:3]]
                
                print(f"  Model: {result.get('model_used')}")
                print(f"  Current price: {result.get('current_price')}")
                print(f"  First 3 forecasts: {prices}")
                
                # Calculate pattern (price changes)
                if len(prices) >= 2:
                    changes = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
                    print(f"  Price changes: {[round(c, 2) for c in changes]}")
                    
                    results.append({
                        'crop': case['crop'],
                        'province': case['province'],
                        'prices': prices,
                        'changes': changes,
                        'model': result.get('model_used')
                    })
        else:
            print(f"  FAILED: {result.get('error')}")
    
    # Compare patterns
    print("\n" + "="*80)
    print("PATTERN COMPARISON")
    print("="*80)
    
    if len(results) >= 2:
        print("\nComparing patterns:")
        
        for i, r1 in enumerate(results):
            for r2 in results[i+1:]:
                print(f"\n{r1['crop']} ({r1['province']}) vs {r2['crop']} ({r2['province']}):")
                
                # Compare price changes
                if r1['changes'] and r2['changes']:
                    # Check if patterns are similar
                    diff = sum(abs(c1 - c2) for c1, c2 in zip(r1['changes'], r2['changes']))
                    avg_change = (sum(abs(c) for c in r1['changes']) + sum(abs(c) for c in r2['changes'])) / 2
                    
                    similarity = 1 - (diff / (avg_change + 0.01))  # Avoid division by zero
                    
                    print(f"  Pattern similarity: {similarity:.2%}")
                    
                    if similarity > 0.9:
                        print(f"  WARNING: Patterns are TOO SIMILAR! (Using fallback?)")
                    elif similarity > 0.7:
                        print(f"  CAUTION: Patterns are quite similar")
                    else:
                        print(f"  OK: Patterns are different")
        
        # Check if all using same model
        models = [r['model'] for r in results]
        unique_models = set(models)
        
        print(f"\nModels used: {unique_models}")
        
        if 'fallback' in str(unique_models).lower():
            print("\nPROBLEM: Using FALLBACK model!")
            print("  - All patterns will be similar")
            print("  - Not using real Model C predictions")
            print("\nREASON: Database connection error")
            print("  Fix: Ensure DATABASE_URL is correct in config")
        elif len(unique_models) == 1:
            print(f"\nOK: All using same model: {list(unique_models)[0]}")
        
    else:
        print("\nNot enough results to compare")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Test Complete!")
print("="*80)

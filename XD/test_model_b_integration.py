"""
Test Model B Integration
ทดสอบ Model B ทั้งหมด:
1. Wrapper (standalone)
2. API endpoints
3. Integration with backend
"""

import sys
import requests
import json
from datetime import datetime

def test_wrapper_standalone():
    """Test 1: Wrapper standalone"""
    print("\n" + "="*80)
    print("TEST 1: MODEL B WRAPPER (STANDALONE)")
    print("="*80)
    
    try:
        from backend.model_b_wrapper import get_model_b
        
        model_b = get_model_b()
        
        # Test prediction
        result = model_b.predict_planting_window(
            crop_type='พริก',
            province='เชียงใหม่',
            planting_date='2024-06-15'
        )
        
        print(f"\n✅ Wrapper loaded successfully")
        print(f"   Is Good Window: {result['is_good_window']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Recommendation: {result['recommendation']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_health():
    """Test 2: API health check"""
    print("\n" + "="*80)
    print("TEST 2: API HEALTH CHECK")
    print("="*80)
    
    try:
        response = requests.get("http://localhost:8000/api/planting/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Model Loaded: {data.get('model_loaded')}")
            print(f"   Model Type: {data.get('model_type')}")
            return True
        else:
            print(f"\n❌ API health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Server not running")
        print(f"💡 Start server with: uvicorn backend.app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        return False

def test_api_window_prediction():
    """Test 3: API window prediction"""
    print("\n" + "="*80)
    print("TEST 3: API WINDOW PREDICTION")
    print("="*80)
    
    test_cases = [
        {
            "name": "พริก - เชียงใหม่ - ฤดูฝน",
            "data": {
                "planting_date": "2024-06-15",
                "province": "เชียงใหม่"
            }
        },
        {
            "name": "พริก - กรุงเทพมหานคร - ฤดูร้อน",
            "data": {
                "planting_date": "2024-04-15",
                "province": "กรุงเทพมหานคร"
            }
        }
    ]
    
    passed = 0
    
    for test in test_cases:
        print(f"\n📝 {test['name']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/planting/window",
                json=test['data'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success")
                print(f"   Is Good Window: {data.get('is_good_window')}")
                print(f"   Confidence: {data.get('confidence', 0):.2%}")
                print(f"   Recommendation: {data.get('recommendation')}")
                passed += 1
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print(f"Result: {passed}/{len(test_cases)} tests passed")
    
    return passed == len(test_cases)

def test_api_calendar():
    """Test 4: API calendar prediction"""
    print("\n" + "="*80)
    print("TEST 4: API CALENDAR PREDICTION")
    print("="*80)
    
    try:
        data = {
            "province": "เชียงใหม่",
            "crop_type": "พริก",
            "months_ahead": 6
        }
        
        print(f"\n📝 Request: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(
            "http://localhost:8000/api/planting/calendar",
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Calendar generated successfully")
            print(f"   Success: {result.get('success')}")
            print(f"   Months analyzed: {len(result.get('monthly_predictions', []))}")
            print(f"   Good windows: {len(result.get('good_windows', []))}")
            print(f"   Best windows: {len(result.get('best_windows', []))}")
            print(f"   Summary: {result.get('summary')}")
            
            # Show monthly predictions
            print(f"\n   Monthly Predictions:")
            for pred in result.get('monthly_predictions', [])[:3]:
                icon = "✅" if pred['is_good_window'] else "❌"
                print(f"      {icon} {pred['month']}: {pred['recommendation']}")
            
            return True
        else:
            print(f"\n❌ Calendar generation failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Calendar test failed: {e}")
        return False

def test_model_v2_endpoint():
    """Test 5: Model v2 endpoint"""
    print("\n" + "="*80)
    print("TEST 5: MODEL V2 ENDPOINT")
    print("="*80)
    
    try:
        params = {
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "planting_date": "2024-06-15"
        }
        
        print(f"\n📝 Request: {json.dumps(params, ensure_ascii=False)}")
        
        response = requests.post(
            "http://localhost:8000/api/v2/model/predict-planting-window",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Prediction successful")
            print(f"   Success: {data.get('success')}")
            print(f"   Is Good Window: {data.get('is_good_window')}")
            print(f"   Confidence: {data.get('confidence', 0):.2%}")
            print(f"   Recommendation: {data.get('recommendation')}")
            print(f"   Reason: {data.get('reason')}")
            return True
        else:
            print(f"\n❌ Prediction failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Model v2 test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("MODEL B - INTEGRATION TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: Wrapper standalone
    results.append(("Wrapper Standalone", test_wrapper_standalone()))
    
    # Test 2: API health
    results.append(("API Health", test_api_health()))
    
    # Test 3: API window prediction
    results.append(("API Window Prediction", test_api_window_prediction()))
    
    # Test 4: API calendar
    results.append(("API Calendar", test_api_calendar()))
    
    # Test 5: Model v2 endpoint
    results.append(("Model V2 Endpoint", test_model_v2_endpoint()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, passed in results:
        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {status:6s} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n{'='*80}")
    print(f"Result: {passed_count}/{total_count} tests passed")
    print(f"{'='*80}")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed")

if __name__ == "__main__":
    main()

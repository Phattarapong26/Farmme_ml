"""
Test Model B API Endpoint
ทดสอบ /api/v2/model/predict-planting-window
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_planting_window_prediction():
    """Test planting window prediction endpoint"""
    
    print("\n" + "="*80)
    print("MODEL B API - PLANTING WINDOW PREDICTION TEST")
    print("="*80)
    
    # Test cases
    test_cases = [
        {
            "name": "Test 1: พริก - เชียงใหม่ - ฤดูฝน (มิถุนายน)",
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "planting_date": "2024-06-15",
            "expected": True  # Should be good window
        },
        {
            "name": "Test 2: พริก - เชียงใหม่ - ฤดูหนาว (มกราคม)",
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "planting_date": "2024-01-15",
            "expected": None  # Unknown
        },
        {
            "name": "Test 3: ข้าว - นครราชสีมา - ฤดูฝน (กรกฎาคม)",
            "crop_type": "ข้าว",
            "province": "นครราชสีมา",
            "planting_date": "2024-07-01",
            "expected": True  # Should be good window
        },
        {
            "name": "Test 4: มะเขือเทศ - กรุงเทพมหานคร - ฤดูร้อน (เมษายน)",
            "crop_type": "มะเขือเทศ",
            "province": "กรุงเทพมหานคร",
            "planting_date": "2024-04-15",
            "expected": None  # Unknown
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📝 {test['name']}")
        print(f"{'='*80}")
        
        # Make request
        url = f"{BASE_URL}/api/v2/model/predict-planting-window"
        params = {
            "crop_type": test['crop_type'],
            "province": test['province'],
            "planting_date": test['planting_date']
        }
        
        print(f"\n📤 Request:")
        print(f"   URL: {url}")
        print(f"   Params: {json.dumps(params, ensure_ascii=False, indent=6)}")
        
        try:
            response = requests.post(url, params=params, timeout=10)
            
            print(f"\n📥 Response:")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Is Good Window: {data.get('is_good_window')}")
                print(f"   Confidence: {data.get('confidence', 0):.2%}")
                print(f"   Recommendation: {data.get('recommendation')}")
                print(f"   Reason: {data.get('reason')}")
                
                # Check result
                if test['expected'] is not None:
                    if data.get('is_good_window') == test['expected']:
                        print(f"\n   ✅ Result matches expected: {test['expected']}")
                        results.append(("PASS", test['name']))
                    else:
                        print(f"\n   ⚠️ Result differs from expected: {test['expected']}")
                        results.append(("WARN", test['name']))
                else:
                    print(f"\n   ℹ️ No expected result to compare")
                    results.append(("INFO", test['name']))
                
            else:
                print(f"   Error: {response.text}")
                results.append(("FAIL", test['name']))
                
        except requests.exceptions.ConnectionError:
            print(f"\n   ❌ Connection Error: Server not running?")
            print(f"   💡 Start server with: uvicorn backend.app.main:app --reload")
            results.append(("ERROR", test['name']))
            break
            
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            results.append(("ERROR", test['name']))
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for status, name in results:
        icon = {
            "PASS": "✅",
            "WARN": "⚠️",
            "INFO": "ℹ️",
            "FAIL": "❌",
            "ERROR": "❌"
        }.get(status, "❓")
        
        print(f"{icon} {status:6s} - {name}")
    
    passed = sum(1 for s, _ in results if s == "PASS")
    total = len(results)
    
    print(f"\n{'='*80}")
    print(f"Result: {passed}/{total} tests passed")
    print(f"{'='*80}")

def test_model_status():
    """Test model status endpoint"""
    
    print("\n" + "="*80)
    print("MODEL STATUS CHECK")
    print("="*80)
    
    url = f"{BASE_URL}/api/v2/model/model-status"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Model Status:")
            print(f"   Model Available: {data.get('model_available')}")
            print(f"   Model Type: {data.get('model_type')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Algorithm: {data.get('algorithm')}")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Server not running?")
        print(f"💡 Start server with: uvicorn backend.app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Test model status first
    test_model_status()
    
    # Test planting window predictions
    test_planting_window_prediction()
    
    print("\n" + "="*80)
    print("✅ Model B API Test Complete")
    print("="*80)
    print()

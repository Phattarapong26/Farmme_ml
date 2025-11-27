"""
Test Model B API Endpoints
"""

import requests
import json
from datetime import datetime
import sys
import io

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test Model B health check"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/planting/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_planting_window():
    """Test planting window prediction"""
    print("\n" + "="*80)
    print("TEST 2: Planting Window Prediction")
    print("="*80)
    
    # Test case 1: Good window (rainy season)
    print("\n📝 Test 2.1: พริก - เชียงใหม่ - ฤดูฝน (มิถุนายน)")
    payload = {
        "planting_date": "2024-06-15",
        "province": "เชียงใหม่"
    }
    
    response = requests.post(f"{BASE_URL}/api/planting/window", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Is Good Window: {result.get('is_good_window')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Recommendation: {result.get('recommendation')}")
        print(f"Reason: {result.get('reason')}")
    else:
        print(f"Error: {response.text}")
    
    # Test case 2: Bad window (winter)
    print("\n📝 Test 2.2: พริก - เชียงใหม่ - ฤดูหนาว (มกราคม)")
    payload = {
        "planting_date": "2024-01-15",
        "province": "เชียงใหม่"
    }
    
    response = requests.post(f"{BASE_URL}/api/planting/window", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Is Good Window: {result.get('is_good_window')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Recommendation: {result.get('recommendation')}")
        print(f"Reason: {result.get('reason')}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_planting_calendar():
    """Test planting calendar"""
    print("\n" + "="*80)
    print("TEST 3: Planting Calendar (6 months)")
    print("="*80)
    
    payload = {
        "province": "เชียงใหม่",
        "crop_type": "พริก",
        "months_ahead": 6
    }
    
    response = requests.post(f"{BASE_URL}/api/planting/calendar", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Summary: {result.get('summary')}")
        print(f"\nGood Windows: {len(result.get('good_windows', []))} months")
        
        print("\nMonthly Predictions:")
        for pred in result.get('monthly_predictions', []):
            status = "✅" if pred['is_good_window'] else "❌"
            print(f"  {status} {pred['month']}: {pred['recommendation']} ({pred['confidence']:.1%})")
        
        if result.get('best_windows'):
            print("\nBest Consecutive Windows:")
            for window in result['best_windows']:
                print(f"  📅 {window['start']} to {window['end']} ({window['duration_months']} months)")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("MODEL B API TESTING")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Health check
        health_ok = test_health_check()
        
        if not health_ok:
            print("\n❌ Health check failed. Make sure the API server is running.")
            print("   Run: python XD/backend/app/main.py")
            return
        
        # Test 2: Planting window
        test_planting_window()
        
        # Test 3: Planting calendar
        test_planting_calendar()
        
        print("\n" + "="*80)
        print("✅ All API tests completed")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Run: python XD/backend/app/main.py")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()

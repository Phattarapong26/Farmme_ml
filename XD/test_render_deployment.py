"""
ทดสอบ Backend หลัง Deploy บน Render
"""
import requests
import json
from datetime import datetime

# ใส่ URL ของ Render ที่ได้หลัง deploy
RENDER_URL = "https://farmme-backend.onrender.com"  # เปลี่ยนเป็น URL จริงของคุณ

def test_endpoint(name, url, method="GET", data=None):
    """ทดสอบ endpoint"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text[:500]}")
            
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT - Render อาจกำลัง wake up (รอ 30-60 วินาที แล้วลองใหม่)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*60)
    print("🚀 Render Backend Deployment Test")
    print(f"Target: {RENDER_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    # Test 1: Ping endpoint
    results.append(test_endpoint(
        "Ping (Health Check)",
        f"{RENDER_URL}/ping"
    ))
    
    # Test 2: Root endpoint
    results.append(test_endpoint(
        "Root Endpoint",
        f"{RENDER_URL}/"
    ))
    
    # Test 3: Health endpoint
    results.append(test_endpoint(
        "Health Check",
        f"{RENDER_URL}/health"
    ))
    
    # Test 4: API Docs (ถ้าเปิด DEBUG)
    results.append(test_endpoint(
        "API Documentation",
        f"{RENDER_URL}/docs"
    ))
    
    # Test 5: Planting recommendation (ตัวอย่าง)
    planting_data = {
        "crop_type": "ข้าว",
        "province": "เชียงใหม่",
        "growth_days": 120,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "top_n": 5
    }
    results.append(test_endpoint(
        "Planting Recommendation",
        f"{RENDER_URL}/recommend-planting-date",
        method="POST",
        data=planting_data
    ))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ All tests passed! Backend is working correctly.")
    elif passed > 0:
        print("\n⚠️ Some tests failed. Check the logs above.")
    else:
        print("\n❌ All tests failed. Check:")
        print("   1. Render service is running")
        print("   2. Environment variables are set correctly")
        print("   3. Database connection is working")
        print("   4. Render might be waking up (wait 60 seconds)")

if __name__ == "__main__":
    main()

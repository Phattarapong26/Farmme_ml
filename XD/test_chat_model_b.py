"""
Test Chat Integration with Model B
ทดสอบว่า chat สามารถใช้ Model B ได้ดีไหม
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_planting_window():
    """Test chat asking about planting window"""
    
    print("\n" + "="*80)
    print("TEST: CHAT - PLANTING WINDOW QUESTION")
    print("="*80)
    
    test_cases = [
        {
            "name": "ถามว่าวันนี้เหมาะปลูกพริกไหม",
            "query": "วันนี้เหมาะปลูกพริกในเชียงใหม่ไหม",
            "expected_function": "check_planting_window"
        },
        {
            "name": "ถามว่าเดือนหน้าเหมาะปลูกไหม",
            "query": "เดือนหน้าเหมาะปลูกมะเขือเทศในกรุงเทพไหม",
            "expected_function": "check_planting_window"
        },
        {
            "name": "ถามปฏิทินการปลูก",
            "query": "ช่วงไหนเหมาะปลูกพริกในเชียงใหม่ตลอดทั้งปี",
            "expected_function": "get_planting_calendar"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📝 {test['name']}")
        print(f"{'='*80}")
        
        # Prepare request
        data = {
            "query": test['query'],
            "crop_id": 1,  # พริก
            "price_history": [30, 32, 31, 33, 35],
            "weather": [100, 28],
            "crop_info": [1, 2, 1],
            "calendar": [0, 0, 1]
        }
        
        print(f"\n📤 Query: {test['query']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📥 Response:")
                print(f"   Status: {response.status_code}")
                print(f"   Success: {result.get('success')}")
                
                # Check if function was called
                if 'function_calls' in result:
                    print(f"\n   Function Calls:")
                    for call in result['function_calls']:
                        print(f"      - {call.get('name')}")
                        if call.get('name') == test['expected_function']:
                            print(f"        ✅ Expected function called!")
                
                # Show response
                response_text = result.get('response', '')
                print(f"\n   Response Text:")
                print(f"   {response_text[:200]}...")
                
                # Check for Model B indicators
                if any(keyword in response_text for keyword in ['เหมาะสม', 'ไม่เหมาะสม', 'แนะนำ', 'ช่วงเวลา']):
                    print(f"\n   ✅ Response contains planting advice")
                else:
                    print(f"\n   ⚠️ Response might not contain planting advice")
                
            else:
                print(f"\n   ❌ Error: {response.status_code}")
                print(f"   {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"\n   ❌ Connection Error: Server not running")
            print(f"   💡 Start server with: uvicorn backend.app.main:app --reload")
            break
            
        except Exception as e:
            print(f"\n   ❌ Error: {e}")

def test_direct_function_call():
    """Test direct function call to Model B"""
    
    print("\n" + "="*80)
    print("TEST: DIRECT FUNCTION CALL")
    print("="*80)
    
    try:
        from backend.gemini_functions import function_handler
        
        # Test check_planting_window
        print(f"\n📝 Test: check_planting_window")
        result = function_handler._handle_check_planting_window({
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "planting_date": "2024-06-15"
        })
        
        print(f"   Success: {result.get('success')}")
        print(f"   Is Good Window: {result.get('is_good_window')}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        print(f"   Recommendation: {result.get('recommendation')}")
        
        # Test get_planting_calendar
        print(f"\n📝 Test: get_planting_calendar")
        result = function_handler._handle_get_planting_calendar({
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "months_ahead": 6
        })
        
        print(f"   Success: {result.get('success')}")
        print(f"   Good Windows: {len(result.get('good_windows', []))}")
        print(f"   Summary: {result.get('summary')}")
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_function_definitions():
    """Test that Gemini functions are properly defined"""
    
    print("\n" + "="*80)
    print("TEST: GEMINI FUNCTION DEFINITIONS")
    print("="*80)
    
    try:
        from backend.gemini_functions import GEMINI_FUNCTIONS
        
        # Check for planting functions
        planting_functions = [
            "check_planting_window",
            "get_planting_calendar",
            "get_planting_window_advice"
        ]
        
        found_functions = []
        
        for func in GEMINI_FUNCTIONS:
            func_name = func.get('name')
            if func_name in planting_functions:
                found_functions.append(func_name)
                print(f"\n✅ Found: {func_name}")
                print(f"   Description: {func.get('description')[:100]}...")
        
        missing = set(planting_functions) - set(found_functions)
        if missing:
            print(f"\n⚠️ Missing functions: {missing}")
        else:
            print(f"\n✅ All planting functions defined")
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("CHAT + MODEL B INTEGRATION TEST")
    print("="*80)
    
    results = []
    
    # Test 1: Function definitions
    results.append(("Function Definitions", test_gemini_function_definitions()))
    
    # Test 2: Direct function calls
    results.append(("Direct Function Calls", test_direct_function_call()))
    
    # Test 3: Chat integration
    print(f"\n{'='*80}")
    print("Starting chat integration tests...")
    print(f"{'='*80}")
    test_chat_planting_window()
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for name, passed in results:
        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {status:6s} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n{'='*80}")
    print(f"Result: {passed_count}/{total_count} tests passed")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

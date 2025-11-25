"""
Test Chat with Model B - Final Test
ทดสอบหลังปรับปรุง function descriptions
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_queries():
    """Test various chat queries"""
    
    print("\n" + "="*80)
    print("TEST: CHAT WITH MODEL B (IMPROVED DESCRIPTIONS)")
    print("="*80)
    
    test_cases = [
        {
            "name": "Test 1: วันนี้เหมาะปลูกไหม",
            "query": "วันนี้เหมาะปลูกพริกในเชียงใหม่ไหม",
            "expected_function": "check_planting_window"
        },
        {
            "name": "Test 2: ช่วงไหนเหมาะปลูก",
            "query": "ช่วงไหนเหมาะปลูกพริกในเชียงใหม่",
            "expected_function": "get_planting_calendar"
        },
        {
            "name": "Test 3: ปฏิทินการปลูก",
            "query": "ขอดูปฏิทินการปลูกพริกในเชียงใหม่",
            "expected_function": "get_planting_calendar"
        },
        {
            "name": "Test 4: เดือนหน้าเหมาะปลูกไหม",
            "query": "เดือนหน้าเหมาะปลูกมะเขือเทศในกรุงเทพไหม",
            "expected_function": "check_planting_window"
        },
        {
            "name": "Test 5: ควรปลูกเมื่อไหร่",
            "query": "ควรปลูกข้าวในนครราชสีมาเมื่อไหร่",
            "expected_function": "check_planting_window"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📝 {test['name']}")
        print(f"{'='*80}")
        print(f"Query: {test['query']}")
        print(f"Expected Function: {test['expected_function']}")
        
        # Prepare request
        data = {
            "query": test['query'],
            "crop_id": 1,
            "price_history": [30, 32, 31, 33, 35],
            "weather": [100, 28],
            "crop_info": [1, 2, 1],
            "calendar": [0, 0, 1]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if function was called
                function_called = result.get('function_called')
                function_result = result.get('function_result')
                
                if function_called:
                    print(f"\n✅ Function Called: {function_called}")
                    
                    # Show function result summary
                    if function_result and isinstance(function_result, dict):
                        if function_result.get('is_good_window') is not None:
                            print(f"   📊 Is Good Window: {function_result.get('is_good_window')}")
                            print(f"   🎯 Confidence: {function_result.get('confidence', 0):.1%}")
                        elif function_result.get('summary'):
                            print(f"   📅 Summary: {function_result.get('summary')}")
                    
                    if function_called == test['expected_function']:
                        print(f"   ✅ Correct function!")
                        results.append(("PASS", test['name']))
                    else:
                        print(f"   ⚠️ Different function (expected: {test['expected_function']})")
                        # Still count as partial success since function was called
                        results.append(("WARN", test['name']))
                else:
                    print(f"\n❌ No function called")
                    results.append(("FAIL", test['name']))
                
                # Show response
                response_text = result.get('gemini_answer', '')
                if response_text:
                    print(f"\n💬 Response:")
                    print(f"   {response_text[:150]}...")
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                results.append(("ERROR", test['name']))
                
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection Error: Server not running")
            print(f"💡 Start server with: uvicorn backend.app.main:app --reload")
            break
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            results.append(("ERROR", test['name']))
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for status, name in results:
        icon = {
            "PASS": "✅",
            "WARN": "⚠️",
            "FAIL": "❌",
            "ERROR": "❌"
        }.get(status, "❓")
        
        print(f"{icon} {status:6s} - {name}")
    
    passed = sum(1 for s, _ in results if s == "PASS")
    total = len(results)
    
    print(f"\n{'='*80}")
    print(f"Result: {passed}/{total} tests passed")
    print(f"{'='*80}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Model B chat integration works!")
    elif passed > 0:
        print(f"\n✅ {passed} tests passed - Model B is working but needs improvement")
    else:
        print(f"\n⚠️ No tests passed - Check function descriptions or Gemini model")

if __name__ == "__main__":
    test_chat_queries()

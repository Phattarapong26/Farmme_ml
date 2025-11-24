"""
Test Chat with Model B - Real Test
ทดสอบจริงว่า chat เรียก Model B ได้ไหม
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_simple():
    """Test simple chat query"""
    
    print("\n" + "="*80)
    print("TEST: CHAT WITH MODEL B")
    print("="*80)
    
    # Test query
    query = "วันนี้เหมาะปลูกพริกในเชียงใหม่ไหม"
    
    print(f"\n📝 Query: {query}")
    
    # Prepare request
    data = {
        "query": query,
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
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Print full response for debugging
            print(f"\n📄 Full Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check response text
            response_text = result.get('response', '')
            print(f"\n💬 Gemini Response:")
            print(response_text)
            
            # Check if Model B was mentioned
            model_b_keywords = ['เหมาะสม', 'ไม่เหมาะสม', 'ปลูก', 'อุณหภูมิ', 'ฝน', 'ฤดู']
            found_keywords = [kw for kw in model_b_keywords if kw in response_text]
            
            if found_keywords:
                print(f"\n✅ Found keywords: {', '.join(found_keywords)}")
            else:
                print(f"\n⚠️ No Model B keywords found")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Server not running")
        print(f"💡 Start server with: uvicorn backend.app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_direct_gemini_function():
    """Test calling Gemini function directly"""
    
    print("\n" + "="*80)
    print("TEST: DIRECT GEMINI FUNCTION CALL")
    print("="*80)
    
    try:
        import sys
        sys.path.insert(0, 'backend')
        
        from gemini_functions import function_handler
        
        # Test check_planting_window
        print(f"\n📝 Calling check_planting_window...")
        
        result = function_handler.handle_function_call(
            'check_planting_window',
            {
                'crop_type': 'พริก',
                'province': 'เชียงใหม่',
                'planting_date': '2024-11-23'
            }
        )
        
        print(f"\n✅ Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('success'):
            print(f"\n🎯 Is Good Window: {result.get('is_good_window')}")
            print(f"🎯 Confidence: {result.get('confidence', 0):.2%}")
            print(f"💡 Recommendation: {result.get('recommendation')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_with_function_calling():
    """Test Gemini with function calling enabled"""
    
    print("\n" + "="*80)
    print("TEST: GEMINI WITH FUNCTION CALLING")
    print("="*80)
    
    try:
        import google.generativeai as genai
        from backend.config import GEMINI_API_KEY
        from backend.gemini_functions import GEMINI_FUNCTIONS
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create model with function calling
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            tools=GEMINI_FUNCTIONS
        )
        
        # Test query
        query = "วันนี้เหมาะปลูกพริกในเชียงใหม่ไหม"
        
        print(f"\n📝 Query: {query}")
        print(f"\n🔧 Functions available: {len(GEMINI_FUNCTIONS)}")
        
        # Check if planting functions exist
        planting_funcs = [f['name'] for f in GEMINI_FUNCTIONS if 'planting' in f['name'].lower()]
        print(f"🌱 Planting functions: {planting_funcs}")
        
        # Send query
        print(f"\n📤 Sending to Gemini...")
        response = model.generate_content(query)
        
        print(f"\n📥 Response:")
        print(response.text)
        
        # Check for function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        print(f"\n✅ Function called: {part.function_call.name}")
                        print(f"   Args: {dict(part.function_call.args)}")
                        return True
        
        print(f"\n⚠️ No function call detected")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("🔍 DEBUGGING CHAT + MODEL B INTEGRATION")
    print("="*80)
    
    results = []
    
    # Test 1: Direct function call
    print("\n" + "="*80)
    print("Step 1: Test direct function call")
    print("="*80)
    results.append(("Direct Function Call", test_direct_gemini_function()))
    
    # Test 2: Gemini with function calling
    print("\n" + "="*80)
    print("Step 2: Test Gemini with function calling")
    print("="*80)
    results.append(("Gemini Function Calling", test_gemini_with_function_calling()))
    
    # Test 3: Full chat endpoint
    print("\n" + "="*80)
    print("Step 3: Test full chat endpoint")
    print("="*80)
    test_chat_simple()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for name, passed in results:
        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"
        print(f"{icon} {status:6s} - {name}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS:")
    print("="*80)
    
    if not results[0][1]:
        print("\n❌ Direct function call failed")
        print("   → Check if Model B wrapper is working")
        print("   → Run: python backend/model_b_wrapper.py")
    
    if not results[1][1]:
        print("\n❌ Gemini function calling failed")
        print("   → Gemini might not recognize the query as planting-related")
        print("   → Try more explicit queries like:")
        print("      'ตรวจสอบว่าวันนี้เหมาะปลูกพริกในเชียงใหม่ไหม'")
        print("      'ช่วงไหนเหมาะปลูกพริกในเชียงใหม่'")
    
    print()

if __name__ == "__main__":
    main()

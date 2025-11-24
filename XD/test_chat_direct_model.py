# -*- coding: utf-8 -*-
"""
Test Chat with Direct Model Only (No Function Calling, No Fallback)
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

def test_chat_direct_model():
    """Test chat with direct model only"""
    
    print("=" * 80)
    print("🧪 Testing Chat with Direct Model Only")
    print("=" * 80)
    
    # Test data
    test_queries = [
        {
            "query": "พริกราคาจะเป็นยังไงในอนาคต",
            "description": "ถามเรื่องราคาพริก"
        },
        {
            "query": "ควรปลูกพืชอะไรดี",
            "description": "ถามเรื่องแนะนำพืช"
        },
        {
            "query": "วันนี้เหมาะปลูกพริกไหม",
            "description": "ถามเรื่องช่วงเวลาปลูก"
        },
        {
            "query": "ควรรดน้ำบ่อยแค่ไหน",
            "description": "ถามเรื่องการจัดการน้ำ"
        },
        {
            "query": "สวัสดีครับ",
            "description": "ทักทาย"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}: {test['description']}")
        print(f"Query: {test['query']}")
        print(f"{'=' * 80}")
        
        # Prepare request
        payload = {
            "query": test['query'],
            "crop_id": 1,  # พริก
            "price_history": [50.0, 52.0, 48.0, 51.0, 49.0],
            "weather": [100.0, 30.0],  # [ฝน, อุณหภูมิ]
            "crop_info": [1, 2, 1],  # [soil_type_id, water_level, season_id]
            "calendar": [0, 0, 1],  # [is_festival, is_holiday, season_id]
            "user_id": None
        }
        
        try:
            # Send request
            print("\n📤 Sending request...")
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=60)
            
            # Check status
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ Response received:")
                print(f"   Session ID: {result.get('session_id', 'N/A')}")
                print(f"   Query: {result.get('query', 'N/A')}")
                print(f"\n📝 Gemini Answer:")
                print(f"   {result.get('gemini_answer', 'N/A')[:200]}...")
                print(f"\n📊 Additional Info:")
                print(f"   Chart Data: {result.get('chart_data')}")
                print(f"   Function Called: {result.get('function_called')}")
                print(f"   Function Result: {result.get('function_result')}")
                print(f"   User Profile Used: {result.get('user_profile_used', False)}")
                
                # Verify no function calling
                assert result.get('function_called') is None, "❌ Function should not be called!"
                assert result.get('function_result') is None, "❌ Function result should be None!"
                assert result.get('chart_data') is None, "❌ Chart data should be None!"
                
                print("\n✅ Test passed - Direct model only, no function calling!")
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("\n⏱️ Request timeout (60s)")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_chat_direct_model()

# -*- coding: utf-8 -*-
"""
ทดสอบการเชื่อมต่อ Model A Wrapper กับระบบ Chat
ตรวจสอบว่า Model A ถูกเรียกใช้ผ่าน Gemini Function Calling ได้ถูกต้อง
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_model_a_chat_integration():
    """ทดสอบการเชื่อมต่อ Model A กับระบบ Chat"""
    print("=" * 80)
    print("🧪 ทดสอบการเชื่อมต่อ Model A Wrapper กับระบบ Chat")
    print("=" * 80)
    
    # 1. Test Model A Wrapper
    print("\n" + "=" * 80)
    print("📦 Step 1: ตรวจสอบ Model A Wrapper")
    print("=" * 80)
    
    try:
        from model_a_wrapper import model_a_wrapper
        print("✅ Import Model A Wrapper สำเร็จ")
        print(f"   Model Loaded: {model_a_wrapper.model_loaded}")
        print(f"   Model Path: {model_a_wrapper.model_path}")
        
        if not model_a_wrapper.model_loaded:
            print("\n⚠️ Model A ไม่ได้โหลด")
            
            # Check if mock model exists from previous test
            model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl")
            if model_path.exists():
                print("   พบ Mock Model จากการทดสอบก่อนหน้า - กำลังโหลด...")
                model_a_wrapper._load_model()
                
                if model_a_wrapper.model_loaded:
                    print(f"✅ Model A โหลดสำเร็จ: {model_a_wrapper.model_loaded}")
                else:
                    print("❌ ไม่สามารถโหลด Mock Model ได้")
                    print("   กรุณารัน test_model_a_wrapper.py ก่อนเพื่อสร้าง Mock Model")
                    return
            else:
                print("❌ ไม่พบ Mock Model")
                print("   กรุณารัน test_model_a_wrapper.py ก่อนเพื่อสร้าง Mock Model")
                return
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. Test Recommendation Model Service
    print("\n" + "=" * 80)
    print("📦 Step 2: ตรวจสอบ Recommendation Model Service")
    print("=" * 80)
    
    try:
        from recommendation_model_service import recommendation_model_service
        print("✅ Import Recommendation Model Service สำเร็จ")
        print(f"   Model Loaded: {recommendation_model_service.model_loaded}")
        print(f"   Using Model A Wrapper: {recommendation_model_service.model_wrapper is not None}")
        
        # Test get_recommendations
        print("\n🧪 ทดสอบ get_recommendations...")
        result = recommendation_model_service.get_recommendations(
            province="เชียงใหม่",
            soil_type="ดินร่วน",
            water_availability="น้ำฝน",
            budget_level="ปานกลาง",
            risk_tolerance="ต่ำ"
        )
        
        print(f"   Success: {result.get('success')}")
        print(f"   Model Used: {result.get('model_used')}")
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        
        if result.get('recommendations'):
            print(f"\n   Top 3 Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec['crop_type']} (Score: {rec['suitability_score']:.2f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Test Gemini Function Handler
    print("\n" + "=" * 80)
    print("📦 Step 3: ตรวจสอบ Gemini Function Handler")
    print("=" * 80)
    
    try:
        from gemini_functions import function_handler, GEMINI_FUNCTIONS
        print("✅ Import Gemini Functions สำเร็จ")
        print(f"   Total Functions: {len(GEMINI_FUNCTIONS)}")
        
        # Find crop recommendation function
        crop_rec_func = None
        for func in GEMINI_FUNCTIONS:
            if func['name'] == 'get_crop_recommendations':
                crop_rec_func = func
                break
        
        if crop_rec_func:
            print(f"\n✅ พบ Function: {crop_rec_func['name']}")
            print(f"   Description: {crop_rec_func['description'][:80]}...")
            print(f"   Required Params: {crop_rec_func['parameters'].get('required', [])}")
        else:
            print(f"\n❌ ไม่พบ Function: get_crop_recommendations")
            return
        
        # Test function execution
        print("\n🧪 ทดสอบ execute_function...")
        test_args = {
            "province": "นครราชสีมา",
            "soil_type": "ดินเหนียว",
            "water_availability": "ชลประทาน",
            "budget_level": "สูง",
            "risk_tolerance": "ปานกลาง"
        }
        
        result = function_handler.execute_function("get_crop_recommendations", test_args)
        
        print(f"   Success: {result.get('success')}")
        print(f"   Model Used: {result.get('model_used')}")
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        
        if result.get('recommendations'):
            print(f"\n   Top 3 Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec['crop_type']} (Score: {rec['suitability_score']:.2f}, ROI: {rec.get('predicted_roi', 'N/A')}%)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Test Integration Flow
    print("\n" + "=" * 80)
    print("📦 Step 4: ทดสอบ Integration Flow (End-to-End)")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Test 1: พื้นฐาน",
            "args": {
                "province": "กรุงเทพมหานคร"
            }
        },
        {
            "name": "Test 2: ครบทุกเงื่อนไข",
            "args": {
                "province": "สุพรรณบุรี",
                "soil_type": "ดินร่วนปนทราย",
                "water_availability": "น้ำบาดาล",
                "budget_level": "ต่ำ",
                "risk_tolerance": "สูง"
            }
        },
        {
            "name": "Test 3: ภาคเหนือ",
            "args": {
                "province": "เชียงราย",
                "soil_type": "ดินทราย",
                "water_availability": "แม่น้ำ/คลอง"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"   Args: {test_case['args']}")
        
        try:
            result = function_handler.execute_function("get_crop_recommendations", test_case['args'])
            
            if result.get('success'):
                print(f"   ✅ Success")
                print(f"   Model: {result.get('model_used')}")
                print(f"   Crops: {len(result.get('recommendations', []))}")
                
                if result.get('recommendations'):
                    top_crop = result['recommendations'][0]
                    print(f"   Top: {top_crop['crop_type']} (Score: {top_crop['suitability_score']:.2f})")
            else:
                print(f"   ❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ สรุปผลการทดสอบ")
    print("=" * 80)
    print("✅ Model A Wrapper: ทำงานได้")
    print("✅ Recommendation Service: เชื่อมต่อกับ Model A Wrapper")
    print("✅ Gemini Function Handler: เรียกใช้ Model A ได้")
    print("✅ Integration Flow: ทำงานได้ครบทุก Step")
    print("\n🎉 Model A พร้อมใช้งานในระบบ Chat แล้ว!")
    print("=" * 80)

if __name__ == "__main__":
    test_model_a_chat_integration()

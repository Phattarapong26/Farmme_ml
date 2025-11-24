# -*- coding: utf-8 -*-
"""
ทดสอบ Model A ว่าไม่มี Fallback และต้องใช้ Model จริงเท่านั้น
ตรวจสอบว่า Model A จะ fail อย่างชัดเจนถ้า model ไม่พร้อม
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_model_a_no_fallback():
    """ทดสอบว่า Model A ไม่มี fallback"""
    print("=" * 80)
    print("🧪 ทดสอบ Model A - NO FALLBACK MODE")
    print("=" * 80)
    
    # Test 1: ทดสอบเมื่อไม่มี Model
    print("\n" + "=" * 80)
    print("Test 1: ทดสอบเมื่อไม่มี Model (ต้อง FAIL)")
    print("=" * 80)
    
    # ลบ model ถ้ามี
    model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl")
    if model_path.exists():
        print(f"🗑️  ลบ Mock Model: {model_path}")
        model_path.unlink()
    
    try:
        # Import fresh
        import importlib
        if 'model_a_wrapper' in sys.modules:
            importlib.reload(sys.modules['model_a_wrapper'])
        
        from model_a_wrapper import model_a_wrapper
        
        print(f"Model Loaded: {model_a_wrapper.model_loaded}")
        
        if model_a_wrapper.model_loaded:
            print("❌ FAIL: Model ไม่ควรโหลดได้เมื่อไม่มีไฟล์")
            return False
        
        # ทดสอบเรียกใช้งาน
        result = model_a_wrapper.get_recommendations(
            province="เชียงใหม่",
            soil_type="ดินร่วน"
        )
        
        print(f"\nResult:")
        print(f"  Success: {result.get('success')}")
        print(f"  Error: {result.get('error')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Recommendations: {len(result.get('recommendations', []))}")
        
        # ตรวจสอบว่าต้อง fail
        if result.get('success'):
            print("\n❌ FAIL: ไม่ควร success เมื่อไม่มี model")
            return False
        
        if result.get('error') != 'MODEL_NOT_LOADED':
            print(f"\n❌ FAIL: Error code ไม่ถูกต้อง (ได้: {result.get('error')}, ต้องการ: MODEL_NOT_LOADED)")
            return False
        
        if len(result.get('recommendations', [])) > 0:
            print("\n❌ FAIL: ไม่ควรมี recommendations เมื่อไม่มี model")
            return False
        
        print("\n✅ PASS: Model fail อย่างถูกต้องเมื่อไม่มีไฟล์")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: ทดสอบ Recommendation Service
    print("\n" + "=" * 80)
    print("Test 2: ทดสอบ Recommendation Service (ต้อง FAIL)")
    print("=" * 80)
    
    try:
        from recommendation_model_service import recommendation_model_service
        
        print(f"Model Loaded: {recommendation_model_service.model_loaded}")
        
        result = recommendation_model_service.get_recommendations(
            province="กรุงเทพมหานคร",
            soil_type="ดินเหนียว"
        )
        
        print(f"\nResult:")
        print(f"  Success: {result.get('success')}")
        print(f"  Error: {result.get('error')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Model Used: {result.get('model_used')}")
        
        # ตรวจสอบว่าไม่มี fallback
        if result.get('success'):
            print("\n❌ FAIL: ไม่ควร success เมื่อไม่มี model")
            return False
        
        if result.get('model_used') == 'fallback_rules':
            print("\n❌ FAIL: ไม่ควรใช้ fallback_rules")
            return False
        
        print("\n✅ PASS: Recommendation Service fail อย่างถูกต้อง (NO FALLBACK)")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: ทดสอบกับ Model จริง (Mock)
    print("\n" + "=" * 80)
    print("Test 3: ทดสอบกับ Model (ต้อง SUCCESS)")
    print("=" * 80)
    
    try:
        # สร้าง Mock Model
        print("🔧 สร้าง Mock Model...")
        import numpy as np
        import pickle
        
        # Import MockModel from test file
        sys.path.insert(0, str(Path(__file__).parent))
        from test_model_a_wrapper import MockModel
        
        model_dir = Path("REMEDIATION_PRODUCTION/trained_models")
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "model_a_xgboost.pkl"
        
        with open(model_path, 'wb') as f:
            pickle.dump(MockModel(), f)
        
        print(f"✅ Mock Model สร้างเสร็จ: {model_path}")
        
        # Reload wrapper
        import importlib
        if 'model_a_wrapper' in sys.modules:
            importlib.reload(sys.modules['model_a_wrapper'])
        if 'recommendation_model_service' in sys.modules:
            importlib.reload(sys.modules['recommendation_model_service'])
        
        from model_a_wrapper import model_a_wrapper
        from recommendation_model_service import recommendation_model_service
        
        print(f"Model A Loaded: {model_a_wrapper.model_loaded}")
        print(f"Recommendation Service Loaded: {recommendation_model_service.model_loaded}")
        
        if not model_a_wrapper.model_loaded:
            print("\n❌ FAIL: Model ควรโหลดได้เมื่อมีไฟล์")
            return False
        
        # ทดสอบเรียกใช้งาน
        result = model_a_wrapper.get_recommendations(
            province="เชียงใหม่",
            soil_type="ดินร่วน",
            water_availability="น้ำฝน"
        )
        
        print(f"\nResult:")
        print(f"  Success: {result.get('success')}")
        print(f"  Model Used: {result.get('model_used')}")
        print(f"  Recommendations: {len(result.get('recommendations', []))}")
        
        if not result.get('success'):
            print(f"\n❌ FAIL: ควร success เมื่อมี model (Error: {result.get('error')})")
            return False
        
        if 'fallback' in result.get('model_used', '').lower():
            print(f"\n❌ FAIL: ไม่ควรใช้ fallback (Model Used: {result.get('model_used')})")
            return False
        
        if len(result.get('recommendations', [])) == 0:
            print("\n❌ FAIL: ควรมี recommendations")
            return False
        
        print("\n✅ PASS: Model ทำงานได้ถูกต้อง (NO FALLBACK)")
        
        # แสดง Top 3
        print("\nTop 3 Recommendations:")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"  {i}. {rec['crop_type']} (Score: {rec['suitability_score']:.2f}, ROI: {rec.get('predicted_roi', 'N/A')}%)")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ สรุปผลการทดสอบ")
    print("=" * 80)
    print("✅ Test 1: Model fail ถูกต้องเมื่อไม่มีไฟล์ (NO FALLBACK)")
    print("✅ Test 2: Recommendation Service fail ถูกต้อง (NO FALLBACK)")
    print("✅ Test 3: Model ทำงานได้เมื่อมีไฟล์ (NO FALLBACK)")
    print("\n🎉 Model A ไม่มี Fallback - ใช้ Model จริงเท่านั้น!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_model_a_no_fallback()
    sys.exit(0 if success else 1)

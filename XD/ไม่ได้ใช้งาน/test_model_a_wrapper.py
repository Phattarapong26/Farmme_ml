# -*- coding: utf-8 -*-
"""
ทดสอบ Model A Wrapper
ทดสอบการทำงานของ Model A (Crop Recommendation) ใน wrapper
"""

import sys
from pathlib import Path
import numpy as np
import pickle

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Mock Model class (must be at module level for pickle)
class MockModel:
    """Simple mock model that predicts ROI"""
    def __init__(self):
        self.n_features_in_ = 19  # New model with 19 features
    
    def predict(self, X):
        """Predict ROI based on simple heuristics"""
        # X shape: (n_samples, 19)
        # Features: [planting_area, yield, growth_days, water_req, investment, risk, ...]
        
        results = []
        for row in X:
            # Simple heuristic: higher yield and lower investment = higher ROI
            planting_area = row[0]
            expected_yield = row[1]
            growth_days = row[2]
            investment = row[4]
            
            # Calculate simple ROI
            # Assume price = 50 baht/kg
            revenue = expected_yield * 50
            roi = ((revenue - investment) / investment) * 100
            
            # Add some randomness
            roi += np.random.uniform(-20, 20)
            
            # Clip to reasonable range
            roi = max(50, min(300, roi))
            
            results.append(roi)
        
        return np.array(results)

def create_mock_model():
    """สร้าง mock model สำหรับทดสอบ"""
    print("\n🔧 สร้าง Mock Model สำหรับทดสอบ...")
    
    # Save mock model
    model_dir = Path("REMEDIATION_PRODUCTION/trained_models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "model_a_xgboost.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(MockModel(), f)
    
    print(f"✅ Mock Model สร้างเสร็จแล้วที่: {model_path}")
    return model_path

def test_model_a_wrapper():
    """ทดสอบ Model A Wrapper"""
    print("=" * 80)
    print("🧪 ทดสอบ Model A Wrapper (Crop Recommendation)")
    print("=" * 80)
    
    # Import wrapper
    try:
        from model_a_wrapper import model_a_wrapper
        print("✅ Import Model A Wrapper สำเร็จ")
    except Exception as e:
        print(f"❌ Import Model A Wrapper ล้มเหลว: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check if model is loaded
    print("\n" + "=" * 80)
    print("📊 สถานะ Model A")
    print("=" * 80)
    print(f"Model Loaded: {model_a_wrapper.model_loaded}")
    print(f"Model Path: {model_a_wrapper.model_path}")
    if hasattr(model_a_wrapper, 'n_features'):
        print(f"Features Required: {model_a_wrapper.n_features}")
    if model_a_wrapper.model:
        print(f"Model Type: {type(model_a_wrapper.model).__name__}")
    
    # If model not loaded, create mock model and reload
    if not model_a_wrapper.model_loaded:
        print("\n⚠️ Model A ไม่ได้โหลด - กำลังสร้าง Mock Model...")
        mock_path = create_mock_model()
        
        # Reload wrapper
        print("\n🔄 กำลังโหลด Model ใหม่...")
        model_a_wrapper._load_model()
        
        if not model_a_wrapper.model_loaded:
            print("\n❌ ไม่สามารถโหลด Mock Model ได้")
            return
        
        print(f"✅ Mock Model โหลดสำเร็จ!")
        print(f"   Model Path: {model_a_wrapper.model_path}")
        print(f"   Features Required: {model_a_wrapper.n_features}")
    
    # Test cases
    test_cases = [
        {
            "name": "Test 1: พื้นฐาน - จังหวัดเชียงใหม่",
            "province": "เชียงใหม่",
            "soil_type": None,
            "water_availability": None,
            "budget_level": None,
            "risk_tolerance": None
        },
        {
            "name": "Test 2: ดินร่วน + น้ำฝน",
            "province": "นครราชสีมา",
            "soil_type": "ดินร่วน",
            "water_availability": "น้ำฝน",
            "budget_level": None,
            "risk_tolerance": None
        },
        {
            "name": "Test 3: ดินเหนียว + ชลประทาน + งบปานกลาง",
            "province": "สุพรรณบุรี",
            "soil_type": "ดินเหนียว",
            "water_availability": "ชลประทาน",
            "budget_level": "ปานกลาง",
            "risk_tolerance": None
        },
        {
            "name": "Test 4: ครบทุกเงื่อนไข",
            "province": "กรุงเทพมหานคร",
            "soil_type": "ดินร่วนปนทราย",
            "water_availability": "น้ำบาดาล",
            "budget_level": "สูง",
            "risk_tolerance": "ต่ำ"
        },
        {
            "name": "Test 5: ดินทราย + แม่น้ำ/คลอง",
            "province": "ชลบุรี",
            "soil_type": "ดินทราย",
            "water_availability": "แม่น้ำ/คลอง",
            "budget_level": "ต่ำ",
            "risk_tolerance": "สูง"
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"🧪 {test_case['name']}")
        print("=" * 80)
        print(f"จังหวัด: {test_case['province']}")
        print(f"ประเภทดิน: {test_case['soil_type'] or 'ไม่ระบุ'}")
        print(f"แหล่งน้ำ: {test_case['water_availability'] or 'ไม่ระบุ'}")
        print(f"งบประมาณ: {test_case['budget_level'] or 'ไม่ระบุ'}")
        print(f"ความเสี่ยง: {test_case['risk_tolerance'] or 'ไม่ระบุ'}")
        
        try:
            result = model_a_wrapper.get_recommendations(
                province=test_case['province'],
                soil_type=test_case['soil_type'],
                water_availability=test_case['water_availability'],
                budget_level=test_case['budget_level'],
                risk_tolerance=test_case['risk_tolerance']
            )
            
            print(f"\n{'✅' if result['success'] else '❌'} Success: {result['success']}")
            
            if result['success']:
                recommendations = result.get('recommendations', [])
                print(f"📊 จำนวนคำแนะนำ: {len(recommendations)}")
                print(f"🤖 Model Used: {result.get('model_used', 'unknown')}")
                print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
                
                if recommendations:
                    print(f"\n🌾 Top 5 Recommendations:")
                    print("-" * 80)
                    for j, rec in enumerate(recommendations[:5], 1):
                        print(f"\n{j}. {rec['crop_type']}")
                        print(f"   Suitability Score: {rec['suitability_score']:.2f}")
                        print(f"   Predicted ROI: {rec['predicted_roi']:.2f}%")
                        print(f"   Expected Yield: {rec['expected_yield_kg_per_rai']:,} kg/rai")
                        print(f"   Estimated Revenue: {rec['estimated_revenue_per_rai']:,} บาท/ไร่")
                        print(f"   Growth Days: {rec['growth_days']} วัน")
                        print(f"   Investment Cost: {rec['investment_cost']:,} บาท/ไร่")
                        print(f"   Water Requirement: {rec['water_requirement']}")
                        print(f"   Risk Level: {rec['risk_level']}")
                        print(f"   Soil Preference: {rec['soil_preference']}")
                        if rec.get('reasons'):
                            print(f"   Reasons: {', '.join(rec['reasons'])}")
                else:
                    print(f"\n⚠️ ไม่มีคำแนะนำ")
                    if result.get('message'):
                        print(f"   Message: {result['message']}")
            else:
                print(f"❌ Error: {result.get('error', 'UNKNOWN')}")
                print(f"   Message: {result.get('message', 'No message')}")
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ การทดสอบเสร็จสิ้น")
    print("=" * 80)

if __name__ == "__main__":
    test_model_a_wrapper()

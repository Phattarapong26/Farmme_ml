# -*- coding: utf-8 -*-
"""
ทดสอบ Model A ว่าแนะนำพืชเหมือนเดิมทุกเดือนหรือไม่
Test if Model A recommends the same crops every month
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from model_a_wrapper import model_a_wrapper

def test_monthly_recommendations():
    """ทดสอบคำแนะนำในแต่ละเดือน"""
    
    print("=" * 80)
    print("🌾 ทดสอบ Model A - คำแนะนำในแต่ละเดือนของปี")
    print("=" * 80)
    print()
    
    # เงื่อนไขทดสอบ
    test_conditions = {
        "province": "เชียงใหม่",
        "soil_type": "ดินร่วน",
        "water_availability": "ชลประทาน",
        "budget_level": "ปานกลาง",
        "risk_tolerance": "ปานกลาง"
    }
    
    print("📋 เงื่อนไขการทดสอบ:")
    for key, value in test_conditions.items():
        print(f"   - {key}: {value}")
    print()
    
    # เดือนทั้งหมด
    months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    
    # เก็บผลลัพธ์แต่ละเดือน
    monthly_results = {}
    
    print("🔍 กำลังทดสอบแต่ละเดือน...")
    print()
    
    for month_idx, month_name in enumerate(months, 1):
        print(f"📅 เดือน {month_name} (เดือนที่ {month_idx})")
        print("-" * 60)
        
        # เรียก Model A
        result = model_a_wrapper.get_recommendations(**test_conditions)
        
        if result.get("success"):
            recommendations = result.get("recommendations", [])
            
            if recommendations:
                # แสดง Top 5
                print(f"   ✅ พบคำแนะนำ {len(recommendations)} รายการ")
                print(f"   🏆 Top 5 พืชที่แนะนำ:")
                
                top_5_crops = []
                for i, rec in enumerate(recommendations[:5], 1):
                    crop_name = rec['crop_type']
                    score = rec['suitability_score']
                    roi = rec.get('predicted_roi', 0)
                    
                    print(f"      {i}. {crop_name}")
                    print(f"         - คะแนน: {score:.2f}")
                    print(f"         - ROI: {roi:.2f}%")
                    
                    top_5_crops.append(crop_name)
                
                # เก็บผลลัพธ์
                monthly_results[month_name] = {
                    "total": len(recommendations),
                    "top_5": top_5_crops,
                    "top_1": recommendations[0]['crop_type'],
                    "model_used": result.get("model_used", "unknown")
                }
            else:
                print("   ⚠️ ไม่พบคำแนะนำ")
                monthly_results[month_name] = {
                    "total": 0,
                    "top_5": [],
                    "top_1": None,
                    "model_used": result.get("model_used", "unknown")
                }
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
            monthly_results[month_name] = {
                "total": 0,
                "top_5": [],
                "top_1": None,
                "error": result.get('message')
            }
        
        print()
    
    # วิเคราะห์ผลลัพธ์
    print("=" * 80)
    print("📊 สรุปผลการทดสอบ")
    print("=" * 80)
    print()
    
    # ตรวจสอบว่าคำแนะนำเหมือนกันทุกเดือนหรือไม่
    all_top_1 = [result.get("top_1") for result in monthly_results.values() if result.get("top_1")]
    unique_top_1 = set(all_top_1)
    
    print(f"🔍 การวิเคราะห์:")
    print(f"   - จำนวนเดือนที่ทดสอบ: {len(months)}")
    print(f"   - จำนวนเดือนที่มีคำแนะนำ: {len(all_top_1)}")
    print()
    
    if len(unique_top_1) == 1:
        print("   ⚠️ พืชอันดับ 1 เหมือนกันทุกเดือน!")
        print(f"   พืชที่แนะนำ: {list(unique_top_1)[0]}")
        print()
        print("   💡 สรุป: Model A แนะนำพืชเดิมทุกเดือน (ไม่คำนึงถึงฤดูกาล)")
    else:
        print(f"   ✅ พืชอันดับ 1 แตกต่างกัน มี {len(unique_top_1)} พืชที่แตกต่าง")
        print(f"   พืชที่แนะนำ: {', '.join(unique_top_1)}")
        print()
        print("   💡 สรุป: Model A แนะนำพืชที่แตกต่างกันตามเดือน")
    
    print()
    print("📋 รายละเอียดแต่ละเดือน:")
    print()
    
    for month_name, result in monthly_results.items():
        top_1 = result.get("top_1", "ไม่มี")
        total = result.get("total", 0)
        print(f"   {month_name:12s} -> อันดับ 1: {top_1:20s} (รวม {total} พืช)")
    
    print()
    print("=" * 80)
    
    # ตรวจสอบ Top 5 ของแต่ละเดือน
    print()
    print("🔍 การเปรียบเทียบ Top 5 แต่ละเดือน:")
    print()
    
    # เปรียบเทียบเดือนแรกกับเดือนอื่นๆ
    first_month = months[0]
    first_top_5 = set(monthly_results[first_month].get("top_5", []))
    
    all_same = True
    for month_name in months[1:]:
        current_top_5 = set(monthly_results[month_name].get("top_5", []))
        
        if first_top_5 != current_top_5:
            all_same = False
            diff = first_top_5.symmetric_difference(current_top_5)
            print(f"   {month_name}: แตกต่างจาก {first_month}")
            print(f"      พืชที่ต่างกัน: {', '.join(diff)}")
    
    if all_same:
        print(f"   ⚠️ Top 5 เหมือนกันทุกเดือน!")
        print(f"   พืชที่แนะนำ: {', '.join(first_top_5)}")
    else:
        print(f"   ✅ Top 5 มีความแตกต่างกันในบางเดือน")
    
    print()
    print("=" * 80)
    print("✅ การทดสอบเสร็จสมบูรณ์")
    print("=" * 80)

if __name__ == "__main__":
    test_monthly_recommendations()

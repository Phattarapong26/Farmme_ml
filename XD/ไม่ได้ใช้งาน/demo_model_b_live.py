"""
Model B - Live Demo
แสดงการใช้งาน Model B แบบ interactive
"""

from backend.model_b_wrapper import get_model_b
from datetime import datetime, timedelta
import json

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_result(result):
    """Print formatted result"""
    print(f"\n📊 ผลการทำนาย:")
    print(f"   {'✅' if result['is_good_window'] else '❌'} เหมาะสม: {result['is_good_window']}")
    print(f"   🎯 ความมั่นใจ: {result['confidence']:.2%}")
    print(f"   💡 คำแนะนำ: {result['recommendation']}")
    print(f"   📝 เหตุผล: {result['reason']}")

def demo_1_check_today():
    """Demo 1: ตรวจสอบวันนี้"""
    print_header("DEMO 1: ตรวจสอบวันนี้เหมาะปลูกไหม")
    
    model_b = get_model_b()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📅 วันที่: {today}")
    print(f"🌶️ พืช: พริก")
    print(f"📍 จังหวัด: เชียงใหม่")
    
    result = model_b.predict_planting_window(
        crop_type='พริก',
        province='เชียงใหม่',
        planting_date=today
    )
    
    print_result(result)

def demo_2_check_specific_date():
    """Demo 2: ตรวจสอบวันที่กำหนด"""
    print_header("DEMO 2: ตรวจสอบวันที่กำหนด")
    
    model_b = get_model_b()
    
    # ทดสอบหลายวัน
    test_dates = [
        ('2024-06-15', 'ฤดูฝน'),
        ('2024-01-15', 'ฤดูหนาว'),
        ('2024-04-15', 'ฤดูร้อน')
    ]
    
    for date, season in test_dates:
        print(f"\n{'─'*80}")
        print(f"📅 วันที่: {date} ({season})")
        print(f"🌶️ พืช: พริก")
        print(f"📍 จังหวัด: เชียงใหม่")
        
        result = model_b.predict_planting_window(
            crop_type='พริก',
            province='เชียงใหม่',
            planting_date=date
        )
        
        icon = '✅' if result['is_good_window'] else '❌'
        print(f"   {icon} {result['recommendation']} ({result['confidence']:.1%})")

def demo_3_calendar():
    """Demo 3: ปฏิทินการปลูก"""
    print_header("DEMO 3: ปฏิทินการปลูก 6 เดือนข้างหน้า")
    
    model_b = get_model_b()
    
    print(f"\n🌶️ พืช: พริก")
    print(f"📍 จังหวัด: เชียงใหม่")
    print(f"📅 ช่วงเวลา: 6 เดือนข้างหน้า")
    
    # Generate calendar
    monthly_predictions = []
    good_windows = []
    
    current_date = datetime.now()
    
    for month_offset in range(6):
        target_date = current_date + timedelta(days=30 * month_offset)
        date_str = target_date.strftime('%Y-%m-%d')
        
        result = model_b.predict_planting_window(
            crop_type='พริก',
            province='เชียงใหม่',
            planting_date=date_str
        )
        
        monthly_predictions.append({
            'month': target_date.strftime('%Y-%m'),
            'is_good': result['is_good_window'],
            'confidence': result['confidence']
        })
        
        if result['is_good_window']:
            good_windows.append(target_date.strftime('%Y-%m'))
    
    # Display calendar
    print(f"\n📅 ปฏิทินการปลูก:")
    for pred in monthly_predictions:
        icon = '✅' if pred['is_good'] else '❌'
        print(f"   {icon} {pred['month']}: {'เหมาะสม' if pred['is_good'] else 'ไม่เหมาะสม'} ({pred['confidence']:.1%})")
    
    # Summary
    good_count = len(good_windows)
    total_count = len(monthly_predictions)
    
    print(f"\n📊 สรุป:")
    print(f"   ✅ เดือนที่เหมาะสม: {good_count}/{total_count} ({good_count/total_count*100:.0f}%)")
    if good_windows:
        print(f"   🌟 เดือนที่แนะนำ: {', '.join(good_windows)}")

def demo_4_compare_provinces():
    """Demo 4: เปรียบเทียบจังหวัด"""
    print_header("DEMO 4: เปรียบเทียบจังหวัด")
    
    model_b = get_model_b()
    
    today = datetime.now().strftime('%Y-%m-%d')
    provinces = ['เชียงใหม่', 'กรุงเทพมหานคร', 'นครราชสีมา']
    
    print(f"\n📅 วันที่: {today}")
    print(f"🌶️ พืช: พริก")
    print(f"📍 เปรียบเทียบ: {', '.join(provinces)}")
    
    results = []
    
    for province in provinces:
        result = model_b.predict_planting_window(
            crop_type='พริก',
            province=province,
            planting_date=today
        )
        results.append({
            'province': province,
            'is_good': result['is_good_window'],
            'confidence': result['confidence'],
            'reason': result['reason']
        })
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n🏆 อันดับความเหมาะสม:")
    for i, r in enumerate(results, 1):
        icon = '✅' if r['is_good'] else '❌'
        print(f"\n   {i}. {icon} {r['province']}")
        print(f"      ความมั่นใจ: {r['confidence']:.2%}")
        print(f"      เหตุผล: {r['reason']}")

def demo_5_compare_crops():
    """Demo 5: เปรียบเทียบพืช"""
    print_header("DEMO 5: เปรียบเทียบพืชต่างชนิด")
    
    model_b = get_model_b()
    
    today = datetime.now().strftime('%Y-%m-%d')
    crops = ['พริก', 'มะเขือเทศ', 'ข้าว']
    province = 'เชียงใหม่'
    
    print(f"\n📅 วันที่: {today}")
    print(f"📍 จังหวัด: {province}")
    print(f"🌱 เปรียบเทียบ: {', '.join(crops)}")
    
    results = []
    
    for crop in crops:
        result = model_b.predict_planting_window(
            crop_type=crop,
            province=province,
            planting_date=today
        )
        results.append({
            'crop': crop,
            'is_good': result['is_good_window'],
            'confidence': result['confidence'],
            'recommendation': result['recommendation']
        })
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n🏆 พืชที่เหมาะสมที่สุด:")
    for i, r in enumerate(results, 1):
        icon = '✅' if r['is_good'] else '❌'
        print(f"   {i}. {icon} {r['crop']}: {r['confidence']:.2%} - {r['recommendation']}")

def demo_6_batch_prediction():
    """Demo 6: ทำนายหลายรายการพร้อมกัน"""
    print_header("DEMO 6: ทำนายหลายรายการพร้อมกัน")
    
    model_b = get_model_b()
    
    # Prepare batch data
    batch_data = [
        {'crop_type': 'พริก', 'province': 'เชียงใหม่', 'planting_date': '2024-06-15'},
        {'crop_type': 'มะเขือเทศ', 'province': 'กรุงเทพมหานคร', 'planting_date': '2024-06-15'},
        {'crop_type': 'ข้าว', 'province': 'นครราชสีมา', 'planting_date': '2024-07-01'},
    ]
    
    print(f"\n📦 ทำนาย {len(batch_data)} รายการ:")
    
    results = model_b.predict_batch(batch_data)
    
    for i, (data, result) in enumerate(zip(batch_data, results), 1):
        print(f"\n   {i}. {data['crop_type']} @ {data['province']} ({data['planting_date']})")
        if 'error' not in result:
            icon = '✅' if result['is_good_window'] else '❌'
            print(f"      {icon} {result['recommendation']} ({result['confidence']:.1%})")
        else:
            print(f"      ❌ Error: {result['error']}")

def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("🌱 MODEL B - LIVE DEMO")
    print("="*80)
    print("\nแสดงความสามารถของ Model B - Planting Window Prediction")
    
    try:
        # Demo 1: Check today
        demo_1_check_today()
        
        # Demo 2: Check specific dates
        demo_2_check_specific_date()
        
        # Demo 3: Calendar
        demo_3_calendar()
        
        # Demo 4: Compare provinces
        demo_4_compare_provinces()
        
        # Demo 5: Compare crops
        demo_5_compare_crops()
        
        # Demo 6: Batch prediction
        demo_6_batch_prediction()
        
        # Summary
        print("\n" + "="*80)
        print("✅ DEMO COMPLETE")
        print("="*80)
        print("\n🎯 Model B สามารถ:")
        print("   1. ตรวจสอบวันที่เฉพาะเจาะจง")
        print("   2. สร้างปฏิทินการปลูก")
        print("   3. เปรียบเทียบจังหวัด")
        print("   4. เปรียบเทียบพืช")
        print("   5. ทำนายหลายรายการพร้อมกัน")
        print("\n💬 ใช้งานผ่าน:")
        print("   - Chat with Gemini AI")
        print("   - REST API")
        print("   - Python wrapper")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

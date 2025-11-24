"""
Test Chat Crop Default Behavior
"""
import sys
sys.path.append('backend')

from utils.constants import CROP_MAP
from utils.helpers import get_crop_name_from_id, get_crop_id_from_name

def test_crop_mapping():
    """Test crop ID mapping"""
    print("\n" + "="*60)
    print("🔍 Testing Crop ID Mapping")
    print("="*60)
    
    # Show first 10 crops
    print("\n📋 First 10 Crops in CROP_MAP:")
    for i, (crop_name, crop_id) in enumerate(list(CROP_MAP.items())[:10]):
        print(f"  {crop_id:2d}. {crop_name}")
    
    # Test specific IDs
    print("\n" + "="*60)
    print("🧪 Testing Specific IDs")
    print("="*60)
    
    test_ids = [0, 1, 10, 19]
    for test_id in test_ids:
        crop_name = get_crop_name_from_id(test_id)
        print(f"  ID {test_id:2d} → {crop_name}")
    
    # Test reverse mapping
    print("\n" + "="*60)
    print("🔄 Testing Reverse Mapping")
    print("="*60)
    
    test_crops = ['พริก', 'คะน้า', 'กระชาย', 'มะเขือเทศ']
    for crop in test_crops:
        crop_id = get_crop_id_from_name(crop)
        print(f"  {crop:15s} → ID {crop_id}")
    
    # Check what happens with default values
    print("\n" + "="*60)
    print("⚠️ Default Value Behavior")
    print("="*60)
    
    print(f"\n  If crop_id = 0:")
    print(f"    → {get_crop_name_from_id(0)}")
    
    print(f"\n  If crop_id = 1:")
    print(f"    → {get_crop_name_from_id(1)}")
    
    print(f"\n  If crop_id not in map:")
    print(f"    → {get_crop_name_from_id(999)}")
    
    # Recommendation
    print("\n" + "="*60)
    print("💡 Recommendations")
    print("="*60)
    
    print("\n  Problem:")
    print("    • กระชาย (ID=1) is the first crop")
    print("    • If frontend sends crop_id=1 as default, it becomes กระชาย")
    
    print("\n  Solutions:")
    print("    1. Change CROP_MAP order - put popular crops first")
    print("       Example: พริก=1, คะน้า=2, มะเขือเทศ=3, ...")
    
    print("\n    2. Frontend should send actual crop_id, not default")
    print("       Example: Let user select crop before chat")
    
    print("\n    3. Backend should handle crop_id=0 as 'no crop selected'")
    print("       Example: Ask user to select crop first")
    
    # Show popular crops
    print("\n" + "="*60)
    print("🌾 Suggested Popular Crops Order")
    print("="*60)
    
    popular_crops = [
        'พริก', 'คะน้า', 'มะเขือเทศ', 'ผักบุ้ง', 'กวางตุ้ง',
        'ข้าวโพดเลี้ยงสัตว์', 'มันสำปะหลัง', 'อ้อย', 'ข่า', 'ขมิ้นชัน'
    ]
    
    print("\n  Recommended order:")
    for i, crop in enumerate(popular_crops, 1):
        current_id = CROP_MAP.get(crop, 0)
        print(f"    {i:2d}. {crop:20s} (currently ID={current_id})")

if __name__ == "__main__":
    test_crop_mapping()

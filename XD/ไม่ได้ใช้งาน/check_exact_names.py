"""Check exact crop and province names in database"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from database import SessionLocal, CropPrice
from sqlalchemy import distinct

db = SessionLocal()

print("="*80)
print("Checking Exact Names in Database")
print("="*80)

# Get provinces
print("\nProvinces (first 5):")
provinces = db.query(distinct(CropPrice.province)).limit(5).all()
for i, (prov,) in enumerate(provinces, 1):
    print(f"{i}. '{prov}'")

# Get crops
print("\nCrops (first 10):")
crops = db.query(distinct(CropPrice.crop_type)).limit(10).all()
for i, (crop,) in enumerate(crops, 1):
    print(f"{i}. '{crop}'")

# Test exact match
print("\nTesting exact matches:")
test_crop = "พริก"
test_province = "เชียงใหม่"

result = db.query(CropPrice).filter(
    CropPrice.crop_type == test_crop,
    CropPrice.province == test_province
).first()

if result:
    print(f"✅ Found: {test_crop} in {test_province}")
    print(f"   Price: {result.price_per_kg} baht/kg")
    print(f"   Date: {result.date}")
else:
    print(f"❌ NOT FOUND: {test_crop} in {test_province}")
    
    # Try to find similar
    print(f"\nSearching for similar crops...")
    similar_crops = db.query(distinct(CropPrice.crop_type)).filter(
        CropPrice.crop_type.contains('พ')
    ).limit(5).all()
    
    if similar_crops:
        print("Found crops containing 'พ':")
        for crop, in similar_crops:
            print(f"  - '{crop}'")
    
    print(f"\nSearching for similar provinces...")
    similar_provinces = db.query(distinct(CropPrice.province)).filter(
        CropPrice.province.contains('เชียง')
    ).limit(5).all()
    
    if similar_provinces:
        print("Found provinces containing 'เชียง':")
        for prov, in similar_provinces:
            print(f"  - '{prov}'")

db.close()
print("\n" + "="*80)

"""Check what crops and provinces are in database"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from database import SessionLocal, CropPrice
from sqlalchemy import distinct, func

db = SessionLocal()

print("="*80)
print("Database Content Check")
print("="*80)

# Get sample crops
print("\nSample Crops (first 20):")
crops = db.query(distinct(CropPrice.crop_type)).limit(20).all()
for i, (crop,) in enumerate(crops, 1):
    # Count records for this crop
    count = db.query(CropPrice).filter(CropPrice.crop_type == crop).count()
    print(f"{i}. {crop} ({count:,} records)")

# Get sample provinces
print("\nSample Provinces (first 10):")
provinces = db.query(distinct(CropPrice.province)).limit(10).all()
for i, (prov,) in enumerate(provinces, 1):
    count = db.query(CropPrice).filter(CropPrice.province == prov).count()
    print(f"{i}. {prov} ({count:,} records)")

# Check specific combinations
print("\nChecking specific combinations:")
test_cases = [
    ("พริก", "เชียงใหม่"),
    ("มะเขือเทศ", "เชียงใหม่"),
    ("ข้าว", "สุพรรณบุรี"),
]

for crop, province in test_cases:
    count = db.query(CropPrice).filter(
        CropPrice.crop_type == crop,
        CropPrice.province == province
    ).count()
    
    if count > 0:
        latest = db.query(CropPrice).filter(
            CropPrice.crop_type == crop,
            CropPrice.province == province
        ).order_by(CropPrice.date.desc()).first()
        
        print(f"✅ {crop} in {province}: {count:,} records")
        print(f"   Latest: {latest.date} | {latest.price_per_kg} baht/kg")
    else:
        print(f"❌ {crop} in {province}: NO DATA")

db.close()
print("\n" + "="*80)

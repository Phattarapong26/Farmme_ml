"""
Compare price_forecast_service vs model_c_v31_service
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from model_c_v31_service import model_c_v31_service
from database import SessionLocal

print("=" * 70)
print("🔍 Comparing Services")
print("=" * 70)

# Test with model_c_v31_service (direct prediction)
print("\n1️⃣ model_c_v31_service (Direct Prediction):")
result1 = model_c_v31_service.predict_price(
    crop_type="มะเขือเทศ",
    province="เชียงใหม่",
    current_price=42.0,
    days_ahead=[7, 30, 90, 180]
)

if result1['success']:
    for pred in result1['predictions']:
        print(f"   Day {pred['days_ahead']:3d}: {pred['predicted_price']:6.2f} baht/kg")

# Test with price_forecast_service (iterative prediction)
print("\n2️⃣ price_forecast_service (Iterative Prediction):")
from app.services.price_forecast_service import price_forecast_service

db = SessionLocal()
try:
    for days in [7, 30, 90, 180]:
        result2 = price_forecast_service.forecast_price(
            province="เชียงใหม่",
            crop_type="มะเขือเทศ",
            days_ahead=days,
            current_price=42.0,
            db_session=db
        )
        
        if result2['success'] and 'daily_forecasts' in result2:
            last_price = result2['daily_forecasts'][-1]['predicted_price']
            print(f"   Day {days:3d}: {last_price:6.2f} baht/kg")
finally:
    db.close()

print("\n" + "=" * 70)
print("📊 Analysis:")
print("   model_c_v31_service: Each prediction is independent")
print("   price_forecast_service: Each day builds on previous")
print("=" * 70)

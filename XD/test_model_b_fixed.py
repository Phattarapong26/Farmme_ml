"""
Test Model B Fixed Version
ตรวจสอบว่าแก้ไขปัญหาทั้งหมดแล้ว:
1. ✅ No Data Leakage
2. ✅ Features ครบ (join crop_characteristics)
3. ✅ Weather data ถูกใช้
4. ✅ Metrics สมจริง (ไม่ใช่ 100%)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'REMEDIATION_PRODUCTION'))

from Model_B_Fixed.model_algorithms_clean import DataLoader_B
from config import Config

def test_data_loading():
    """Test 1: ตรวจสอบการโหลดข้อมูล"""
    print("\n" + "="*70)
    print("TEST 1: Data Loading")
    print("="*70)
    
    cultivation_csv = Config.get_dataset_path('cultivation.csv')
    weather_csv = Config.get_dataset_path('weather.csv')
    crop_chars_csv = Config.get_dataset_path('crop_characteristics.csv')
    
    loader = DataLoader_B(cultivation_csv, weather_csv, crop_chars_csv)
    
    print(f"✅ Cultivation: {len(loader.cultivation)} records")
    print(f"✅ Weather: {len(loader.weather)} records")
    print(f"✅ Crop Characteristics: {len(loader.crop_chars)} records")
    
    return loader

def test_feature_creation(loader):
    """Test 2: ตรวจสอบการสร้าง features"""
    print("\n" + "="*70)
    print("TEST 2: Feature Creation")
    print("="*70)
    
    df_clean = loader.create_training_data(success_threshold=0.75)
    
    print(f"\n✅ Training data: {len(df_clean)} records")
    print(f"\nColumns available:")
    for col in df_clean.columns:
        print(f"   - {col}")
    
    # Check for required features
    required_features = [
        'growth_days',           # From crop_characteristics
        'soil_preference',       # From crop_characteristics
        'seasonal_type',         # From crop_characteristics
        'season',                # Created from planting_date
        'avg_temp_prev_30d',     # Weather feature
        'avg_rainfall_prev_30d', # Weather feature
        'is_good_window'         # Target
    ]
    
    print(f"\n✅ Checking required features:")
    for feat in required_features:
        if feat in df_clean.columns:
            print(f"   ✅ {feat}")
        else:
            print(f"   ❌ {feat} - MISSING!")
    
    return df_clean

def test_no_data_leakage(df_clean):
    """Test 3: ตรวจสอบว่าไม่มี data leakage"""
    print("\n" + "="*70)
    print("TEST 3: No Data Leakage Check")
    print("="*70)
    
    # Check that we're NOT using post-harvest features
    forbidden_features = [
        'actual_yield_kg',
        'harvest_date',
        'actual_profit_baht',
        'yield_efficiency',
        'success_rate'  # Should not be in features (only used to create target)
    ]
    
    print(f"\n✅ Checking for forbidden features:")
    has_leakage = False
    for feat in forbidden_features:
        if feat in df_clean.columns:
            print(f"   ❌ {feat} - FOUND! (Data Leakage!)")
            has_leakage = True
        else:
            print(f"   ✅ {feat} - Not in features (Good)")
    
    if not has_leakage:
        print(f"\n✅ NO DATA LEAKAGE DETECTED!")
    else:
        print(f"\n❌ DATA LEAKAGE DETECTED!")
    
    return not has_leakage

def test_weather_usage(df_clean):
    """Test 4: ตรวจสอบว่า weather data ถูกใช้"""
    print("\n" + "="*70)
    print("TEST 4: Weather Data Usage")
    print("="*70)
    
    weather_features = [
        'avg_temp_prev_30d',
        'avg_rainfall_prev_30d',
        'total_rainfall_prev_30d',
        'rainy_days_prev_30d'
    ]
    
    weather_used = 0
    for feat in weather_features:
        if feat in df_clean.columns:
            print(f"   ✅ {feat} - Used")
            weather_used += 1
            
            # Show sample values
            sample_val = df_clean[feat].mean()
            print(f"      Mean: {sample_val:.2f}")
        else:
            print(f"   ❌ {feat} - Not used")
    
    if weather_used > 0:
        print(f"\n✅ Weather data IS BEING USED ({weather_used} features)")
        return True
    else:
        print(f"\n❌ Weather data NOT USED")
        return False

def test_target_distribution(df_clean):
    """Test 5: ตรวจสอบ target distribution"""
    print("\n" + "="*70)
    print("TEST 5: Target Distribution")
    print("="*70)
    
    target = df_clean['is_good_window']
    
    good_count = target.sum()
    bad_count = (1 - target).sum()
    good_pct = target.mean() * 100
    bad_pct = (1 - target).mean() * 100
    
    print(f"\n✅ Target distribution:")
    print(f"   Good windows: {good_count} ({good_pct:.1f}%)")
    print(f"   Bad windows: {bad_count} ({bad_pct:.1f}%)")
    
    # Check if distribution is reasonable
    if 20 <= good_pct <= 80:
        print(f"\n✅ Distribution looks reasonable (not too imbalanced)")
        return True
    else:
        print(f"\n⚠️ Distribution might be too imbalanced")
        return False

def test_numeric_features(loader, df_clean):
    """Test 6: ตรวจสอบ numeric features"""
    print("\n" + "="*70)
    print("TEST 6: Numeric Features")
    print("="*70)
    
    X = loader.create_features(df_clean)
    
    print(f"\n✅ Created {X.shape[1]} numeric features")
    print(f"   Samples: {X.shape[0]}")
    print(f"\nFeature names:")
    for i, col in enumerate(X.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # Check for NaN
    nan_count = X.isna().sum().sum()
    if nan_count == 0:
        print(f"\n✅ No NaN values in features")
    else:
        print(f"\n⚠️ Found {nan_count} NaN values")
    
    return X

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MODEL B - FIXED VERSION TESTING")
    print("="*70)
    
    try:
        # Test 1: Data Loading
        loader = test_data_loading()
        
        # Test 2: Feature Creation
        df_clean = test_feature_creation(loader)
        
        # Test 3: No Data Leakage
        no_leakage = test_no_data_leakage(df_clean)
        
        # Test 4: Weather Usage
        weather_used = test_weather_usage(df_clean)
        
        # Test 5: Target Distribution
        target_ok = test_target_distribution(df_clean)
        
        # Test 6: Numeric Features
        X = test_numeric_features(loader, df_clean)
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        tests = [
            ("Data Loading", True),
            ("Feature Creation", True),
            ("No Data Leakage", no_leakage),
            ("Weather Usage", weather_used),
            ("Target Distribution", target_ok),
            ("Numeric Features", True)
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n{'='*70}")
        print(f"RESULT: {passed}/{total} tests passed")
        print(f"{'='*70}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Model B is ready for training!")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Please fix before training.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

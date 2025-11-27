#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Model C Wrapper - ตรวจสอบว่า Model C โหลดได้จริงหรือไม่
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_model_c_wrapper():
    """Test Model C Wrapper"""
    print("\n" + "="*80)
    print("🧪 TEST MODEL C WRAPPER")
    print("="*80)
    
    try:
        # Import wrapper
        print("\n📦 Importing Model C Wrapper...")
        from model_c_wrapper import ModelCWrapper
        
        # Create instance
        print("🔧 Creating Model C instance...")
        wrapper = ModelCWrapper()
        
        # Check if model loaded
        print(f"\n✅ Model loaded: {wrapper.model_loaded}")
        
        if wrapper.model_loaded:
            print(f"   Version: {wrapper.model_version}")
            print(f"   Algorithm: {wrapper.algorithm}")
            print(f"   Model path: {wrapper.model_path}")
            
            # Check stratified models
            if hasattr(wrapper, 'model_low'):
                print(f"\n✅ Stratified Models Found:")
                print(f"   - Low model: {type(wrapper.model_low).__name__}")
                print(f"   - Medium model: {type(wrapper.model_medium).__name__}")
                print(f"   - High model: {type(wrapper.model_high).__name__}")
                print(f"   - Low threshold: {wrapper.low_threshold:.2f}")
                print(f"   - High threshold: {wrapper.high_threshold:.2f}")
            
            # Check features
            if hasattr(wrapper, 'feature_names'):
                print(f"\n✅ Features: {len(wrapper.feature_names)}")
                print(f"   First 5 features: {wrapper.feature_names[:5]}")
            
            # Get model info
            print("\n📊 Model Info:")
            info = wrapper.get_model_info()
            for key, value in info.items():
                print(f"   {key}: {value}")
            
            # Test prediction (simple test)
            print("\n🧪 Testing prediction...")
            try:
                result = wrapper.predict_price(
                    crop_type='พริก',
                    province='เชียงใหม่',
                    days_ahead=30
                )
                
                if result.get('success'):
                    print(f"✅ Prediction successful!")
                    print(f"   Current price: {result.get('current_price')} บาท/กก.")
                    print(f"   Predictions: {len(result.get('predictions', []))} timeframes")
                    print(f"   Confidence: {result.get('confidence')}")
                    print(f"   Trend: {result.get('price_trend')}")
                else:
                    print(f"⚠️  Prediction returned error: {result.get('error')}")
                    print(f"   Message: {result.get('message')}")
                    
            except Exception as e:
                print(f"❌ Prediction test failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Model not loaded!")
            
        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)

if __name__ == "__main__":
    test_model_c_wrapper()

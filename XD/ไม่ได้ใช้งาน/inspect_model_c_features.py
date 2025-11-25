#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspect Model C Features
ดูว่า Model C ใช้ feature อะไรบ้างในการพยากรณ์ราคา
"""

import pickle
import sys
from pathlib import Path

def inspect_model_c():
    """ตรวจสอบ Model C features"""
    print("="*70)
    print("🔍 MODEL C FEATURE INSPECTION")
    print("="*70)
    
    # Load Model C
    model_path = "REMEDIATION_PRODUCTION/models_production/model_c_price_forecast.pkl"
    
    print(f"\n📂 Loading: {model_path}")
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print("✅ Model loaded successfully!")
        
        # Check structure
        print(f"\n📋 Model Structure:")
        print(f"   Type: {type(model_data)}")
        
        if isinstance(model_data, dict):
            print(f"   Keys: {list(model_data.keys())}")
            
            # Get features
            if 'feature_cols' in model_data:
                features = model_data['feature_cols']
                print(f"\n✅ Found {len(features)} features!")
                
                print(f"\n📊 FEATURES USED BY MODEL C:")
                print("="*70)
                
                for i, feature in enumerate(features, 1):
                    print(f"{i:2d}. {feature}")
                
                # Categorize features
                print(f"\n📂 FEATURE CATEGORIES:")
                print("="*70)
                
                price_features = [f for f in features if 'price' in f.lower()]
                temporal_features = [f for f in features if any(x in f.lower() for x in ['month', 'day', 'year', 'sin', 'cos'])]
                location_features = [f for f in features if any(x in f.lower() for x in ['province', 'crop', 'region'])]
                other_features = [f for f in features if f not in price_features + temporal_features + location_features]
                
                if price_features:
                    print(f"\n💰 Price-related features ({len(price_features)}):")
                    for f in price_features:
                        print(f"   - {f}")
                
                if temporal_features:
                    print(f"\n📅 Temporal features ({len(temporal_features)}):")
                    for f in temporal_features:
                        print(f"   - {f}")
                
                if location_features:
                    print(f"\n📍 Location/Crop features ({len(location_features)}):")
                    for f in location_features:
                        print(f"   - {f}")
                
                if other_features:
                    print(f"\n🔧 Other features ({len(other_features)}):")
                    for f in other_features:
                        print(f"   - {f}")
            
            # Get model info
            if 'model' in model_data:
                model = model_data['model']
                print(f"\n🤖 Model Information:")
                print(f"   Type: {type(model).__name__}")
                
                # Check for feature importances
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    features = model_data.get('feature_cols', [])
                    
                    print(f"\n⭐ TOP 10 MOST IMPORTANT FEATURES:")
                    print("="*70)
                    
                    # Sort by importance
                    feature_importance = list(zip(features, importances))
                    feature_importance.sort(key=lambda x: x[1], reverse=True)
                    
                    for i, (feature, importance) in enumerate(feature_importance[:10], 1):
                        bar = "█" * int(importance * 50)
                        print(f"{i:2d}. {feature:25s} {importance:.4f} {bar}")
                    
                    # Show least important
                    print(f"\n📉 LEAST IMPORTANT FEATURES:")
                    print("="*70)
                    for i, (feature, importance) in enumerate(feature_importance[-5:], 1):
                        bar = "█" * int(importance * 50)
                        print(f"{i:2d}. {feature:25s} {importance:.4f} {bar}")
            
            # Model type
            if 'model_type' in model_data:
                print(f"\n🏷️  Model Type: {model_data['model_type']}")
        
        else:
            print(f"   Model is not a dictionary: {type(model_data)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_price_forecast_service():
    """ตรวจสอบ price_forecast_service ว่าสร้าง features ยังไง"""
    print("\n" + "="*70)
    print("🔍 PRICE FORECAST SERVICE - FEATURE ENGINEERING")
    print("="*70)
    
    try:
        sys.path.insert(0, 'backend/app/services')
        from backend.app.services.price_forecast_service import PriceForecastService
        
        service = PriceForecastService()
        
        print(f"\n✅ Service loaded")
        print(f"   Model loaded: {service.model_loaded}")
        print(f"   Features: {len(service.feature_cols) if service.feature_cols else 0}")
        
        if service.feature_cols:
            print(f"\n📋 Features from service:")
            for i, f in enumerate(service.feature_cols, 1):
                print(f"   {i:2d}. {f}")
        
        # Check _get_forecast_context method
        print(f"\n🔧 Feature Engineering Process:")
        print("="*70)
        
        import inspect
        source = inspect.getsource(service._get_forecast_context)
        
        # Extract feature creation lines
        lines = source.split('\n')
        feature_lines = [l.strip() for l in lines if "context['" in l or 'context["' in l]
        
        print("\n📝 Features created in _get_forecast_context():")
        for line in feature_lines[:20]:  # Show first 20
            if '=' in line:
                print(f"   {line}")
        
    except Exception as e:
        print(f"⚠️ Could not load service: {e}")

def main():
    inspect_model_c()
    check_price_forecast_service()
    
    print("\n" + "="*70)
    print("✅ INSPECTION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

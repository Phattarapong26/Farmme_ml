#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Model Audit - Find Hidden Issues
ตรวจสอบ model ทั้ง 4 ตัวอย่างละเอียดเพื่อหาจุดผิดพลาด
"""

import sys
sys.path.insert(0, 'backend')

import pickle
import numpy as np
from pathlib import Path

def audit_model_file(model_path, model_name):
    """Audit a single model file for issues"""
    print(f"\n{'='*70}")
    print(f"🔍 AUDITING: {model_name}")
    print(f"{'='*70}")
    
    issues = []
    warnings = []
    info = []
    
    # Check 1: File exists
    if not Path(model_path).exists():
        issues.append(f"❌ File does not exist: {model_path}")
        return issues, warnings, info
    
    info.append(f"✅ File exists: {model_path}")
    
    # Check 2: File size
    file_size = Path(model_path).stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    info.append(f"📦 File size: {file_size_mb:.2f} MB")
    
    if file_size < 1024:  # Less than 1KB
        issues.append(f"❌ File too small ({file_size} bytes) - likely corrupted")
    elif file_size_mb > 500:  # More than 500MB
        warnings.append(f"⚠️ File very large ({file_size_mb:.2f} MB) - may cause memory issues")
    
    # Check 3: Can load the file
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        info.append("✅ Model file loads successfully")
    except Exception as e:
        issues.append(f"❌ Cannot load model: {e}")
        return issues, warnings, info
    
    # Check 4: Model structure
    if isinstance(model_data, dict):
        info.append(f"📋 Model is a dictionary with keys: {list(model_data.keys())}")
        
        # Check for common keys
        if 'model' not in model_data:
            warnings.append("⚠️ No 'model' key in dictionary - may need special handling")
        
        # Check for scaler
        if 'scaler' in model_data:
            info.append("✅ Scaler found in model data")
        else:
            warnings.append("⚠️ No scaler found - predictions may not be normalized")
            
    else:
        info.append(f"📋 Model type: {type(model_data).__name__}")
    
    # Check 5: Model has predict method
    try:
        model_obj = model_data.get('model') if isinstance(model_data, dict) else model_data
        if hasattr(model_obj, 'predict'):
            info.append("✅ Model has predict() method")
        else:
            issues.append("❌ Model does not have predict() method")
    except Exception as e:
        warnings.append(f"⚠️ Cannot check predict method: {e}")
    
    # Check 6: Try a dummy prediction
    try:
        model_obj = model_data.get('model') if isinstance(model_data, dict) else model_data
        
        # Try to infer number of features
        if hasattr(model_obj, 'n_features_in_'):
            n_features = model_obj.n_features_in_
            info.append(f"✅ Model expects {n_features} features")
            
            # Try dummy prediction
            dummy_input = np.zeros((1, n_features))
            prediction = model_obj.predict(dummy_input)
            info.append(f"✅ Dummy prediction successful: {prediction}")
        else:
            warnings.append("⚠️ Cannot determine number of features - skipping dummy prediction")
            
    except Exception as e:
        warnings.append(f"⚠️ Dummy prediction failed: {e}")
    
    # Check 7: Model attributes
    try:
        model_obj = model_data.get('model') if isinstance(model_data, dict) else model_data
        
        # Check for common sklearn attributes
        attrs_to_check = ['feature_importances_', 'classes_', 'coef_', 'intercept_']
        found_attrs = []
        for attr in attrs_to_check:
            if hasattr(model_obj, attr):
                found_attrs.append(attr)
        
        if found_attrs:
            info.append(f"📊 Model attributes: {', '.join(found_attrs)}")
    except:
        pass
    
    return issues, warnings, info


def audit_wrapper(wrapper_name, wrapper_module):
    """Audit a wrapper for issues"""
    print(f"\n{'='*70}")
    print(f"🔍 AUDITING WRAPPER: {wrapper_name}")
    print(f"{'='*70}")
    
    issues = []
    warnings = []
    info = []
    
    try:
        exec(f"from {wrapper_module} import {wrapper_name.lower()}")
        wrapper = eval(wrapper_name.lower())
        
        # Check 1: Model loaded
        if wrapper.model_loaded:
            info.append(f"✅ Wrapper loaded model successfully")
        else:
            issues.append(f"❌ Wrapper failed to load model")
        
        # Check 2: Model path
        if wrapper.model_path:
            info.append(f"📂 Model path: {wrapper.model_path}")
        else:
            warnings.append("⚠️ No model path set")
        
        # Check 3: Check for required methods
        required_methods = ['predict', 'get_model_info']
        for method in required_methods:
            # Check various method name patterns
            method_variants = [
                method,
                f"{method}_price",
                f"{method}_planting_window",
                f"get_harvest_decision"
            ]
            
            has_method = any(hasattr(wrapper, m) for m in method_variants)
            if has_method:
                info.append(f"✅ Has prediction method")
                break
        else:
            warnings.append(f"⚠️ No standard prediction method found")
        
        # Check 4: Try get_model_info if available
        if hasattr(wrapper, 'get_model_info'):
            try:
                model_info = wrapper.get_model_info()
                info.append(f"✅ Model info: {model_info}")
            except Exception as e:
                warnings.append(f"⚠️ get_model_info() failed: {e}")
        
    except Exception as e:
        issues.append(f"❌ Cannot load wrapper: {e}")
    
    return issues, warnings, info


def main():
    """Run comprehensive audit"""
    print("="*70)
    print("🔍 COMPREHENSIVE MODEL AUDIT")
    print("="*70)
    print("Checking all 4 models for hidden issues...")
    
    all_issues = []
    all_warnings = []
    
    # Model paths
    models = {
        "Model A (Crop Recommendation)": "REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl",
        "Model B (Planting Window)": "REMEDIATION_PRODUCTION/trained_models/model_b_logistic.pkl",
        "Model C (Price Prediction)": "REMEDIATION_PRODUCTION/models_production/model_c_price_forecast.pkl",
        "Model D (Harvest Decision)": "REMEDIATION_PRODUCTION/trained_models/model_d_thompson_sampling.pkl"
    }
    
    # Audit each model file
    for model_name, model_path in models.items():
        issues, warnings, info = audit_model_file(model_path, model_name)
        
        print(f"\n📊 Results for {model_name}:")
        print("-" * 70)
        
        if issues:
            print("\n❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            all_issues.extend([(model_name, issue) for issue in issues])
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
            all_warnings.extend([(model_name, warning) for warning in warnings])
        
        if info:
            print("\n✅ INFO:")
            for i in info:
                print(f"  {i}")
    
    # Audit wrappers
    wrappers = {
        "model_a_wrapper": "model_a_wrapper",
        "model_b_wrapper": "model_b_wrapper",
        "model_c_wrapper": "model_c_wrapper",
        "model_d_wrapper": "model_d_wrapper"
    }
    
    for wrapper_name, wrapper_module in wrappers.items():
        issues, warnings, info = audit_wrapper(wrapper_name, wrapper_module)
        
        print(f"\n📊 Results for {wrapper_name}:")
        print("-" * 70)
        
        if issues:
            print("\n❌ ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            all_issues.extend([(wrapper_name, issue) for issue in issues])
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
            all_warnings.extend([(wrapper_name, warning) for warning in warnings])
        
        if info:
            print("\n✅ INFO:")
            for i in info:
                print(f"  {i}")
    
    # Final summary
    print("\n" + "="*70)
    print("📋 FINAL AUDIT SUMMARY")
    print("="*70)
    
    if all_issues:
        print(f"\n❌ CRITICAL ISSUES FOUND: {len(all_issues)}")
        for model, issue in all_issues:
            print(f"  [{model}] {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS: {len(all_warnings)}")
        for model, warning in all_warnings:
            print(f"  [{model}] {warning}")
    else:
        print("\n✅ NO WARNINGS")
    
    print("\n" + "="*70)
    if not all_issues:
        print("✅ ALL MODELS READY FOR PRODUCTION")
    else:
        print("⚠️  PLEASE FIX ISSUES BEFORE PRODUCTION")
    print("="*70)


if __name__ == "__main__":
    main()

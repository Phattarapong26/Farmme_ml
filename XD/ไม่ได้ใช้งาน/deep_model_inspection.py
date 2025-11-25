#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deep Model Inspection - Check for missing dependencies
"""

import pickle
import sys
from pathlib import Path

def inspect_pickle_dependencies(model_path, model_name):
    """Check what modules a pickle file depends on"""
    print(f"\n{'='*70}")
    print(f"🔬 DEEP INSPECTION: {model_name}")
    print(f"{'='*70}")
    
    # Read pickle file and find all module references
    try:
        with open(model_path, 'rb') as f:
            content = f.read()
        
        # Look for module names in pickle content
        content_str = str(content)
        
        # Common problematic patterns
        issues = []
        warnings = []
        
        # Check for custom module dependencies
        if b'Model_A_Fixed' in content:
            issues.append("❌ Depends on 'Model_A_Fixed' module (missing)")
        if b'Model_B_Fixed' in content:
            issues.append("❌ Depends on 'Model_B_Fixed' module (missing)")
        if b'Model_D_L4_Bandit' in content:
            issues.append("❌ Depends on 'Model_D_L4_Bandit' module (missing)")
        
        # Check for sklearn
        if b'sklearn' in content:
            print("✅ Uses sklearn (standard library)")
        
        # Check for xgboost
        if b'xgboost' in content:
            print("✅ Uses xgboost")
        
        # Check for custom classes
        if b'__main__' in content:
            warnings.append("⚠️ Contains classes from __main__ (may cause issues)")
        
        # Try to load with error details
        print("\n🔍 Attempting to load...")
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            print("✅ Model loads successfully!")
            print(f"   Type: {type(data)}")
            if isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
        except ModuleNotFoundError as e:
            issues.append(f"❌ Missing module: {e}")
        except Exception as e:
            issues.append(f"❌ Load error: {e}")
        
        return issues, warnings
        
    except Exception as e:
        return [f"❌ Cannot read file: {e}"], []


def check_wrapper_imports():
    """Check if wrappers can import their dependencies"""
    print(f"\n{'='*70}")
    print(f"🔬 CHECKING WRAPPER DEPENDENCIES")
    print(f"{'='*70}")
    
    wrappers = {
        "Model A": "backend/model_a_wrapper.py",
        "Model B": "backend/model_b_wrapper.py",
        "Model C": "backend/model_c_wrapper.py",
        "Model D": "backend/model_d_wrapper.py"
    }
    
    for name, path in wrappers.items():
        print(f"\n📄 {name} Wrapper ({path}):")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for problematic imports
            if 'Model_A_Fixed' in content:
                print("  ⚠️ References Model_A_Fixed")
            if 'Model_B_Fixed' in content:
                print("  ⚠️ References Model_B_Fixed")
            if 'Model_D_L4_Bandit' in content:
                print("  ⚠️ References Model_D_L4_Bandit")
            
            # Check for proper error handling
            if 'try:' in content and 'except' in content:
                print("  ✅ Has error handling")
            else:
                print("  ⚠️ Limited error handling")
                
        except Exception as e:
            print(f"  ❌ Cannot read: {e}")


def main():
    print("="*70)
    print("🔬 DEEP MODEL INSPECTION")
    print("="*70)
    print("Checking for missing dependencies and hidden issues...")
    
    models = {
        "Model A": "REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl",
        "Model B": "REMEDIATION_PRODUCTION/trained_models/model_b_logistic.pkl",
        "Model C": "REMEDIATION_PRODUCTION/models_production/model_c_price_forecast.pkl",
        "Model D": "REMEDIATION_PRODUCTION/trained_models/model_d_thompson_sampling.pkl"
    }
    
    all_issues = []
    all_warnings = []
    
    for name, path in models.items():
        issues, warnings = inspect_pickle_dependencies(path, name)
        
        if issues:
            print("\n❌ ISSUES:")
            for issue in issues:
                print(f"  {issue}")
            all_issues.extend(issues)
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
            all_warnings.extend(warnings)
    
    # Check wrappers
    check_wrapper_imports()
    
    # Summary
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    
    if all_issues:
        print(f"\n❌ CRITICAL ISSUES: {len(all_issues)}")
        for issue in set(all_issues):
            print(f"  {issue}")
        
        print("\n💡 RECOMMENDED FIXES:")
        if any('Model_A_Fixed' in str(i) for i in all_issues):
            print("  1. Model A: Re-train without custom Model_A_Fixed class")
            print("     OR: Add Model_A_Fixed.py to REMEDIATION_PRODUCTION/")
        
        if any('Model_B_Fixed' in str(i) for i in all_issues):
            print("  2. Model B: Re-train without custom Model_B_Fixed class")
            print("     OR: Add Model_B_Fixed.py to REMEDIATION_PRODUCTION/")
        
        if any('Model_D_L4_Bandit' in str(i) for i in all_issues):
            print("  3. Model D: Re-train without custom Model_D_L4_Bandit class")
            print("     OR: Add Model_D_L4_Bandit/ module to REMEDIATION_PRODUCTION/")
    else:
        print("\n✅ NO CRITICAL DEPENDENCY ISSUES")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS: {len(all_warnings)}")
        for warning in set(all_warnings):
            print(f"  {warning}")


if __name__ == "__main__":
    main()

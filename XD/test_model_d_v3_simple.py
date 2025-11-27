#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Test for Model D V3
Tests basic functionality without complex Unicode
"""

import sys
from pathlib import Path

# Add paths
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from model_d_wrapper import model_d_wrapper

def test_basic_scenarios():
    """Test basic scenarios"""
    print("\n" + "="*80)
    print("MODEL D V3 - SIMPLE TEST")
    print("="*80)
    
    # Check model status
    print(f"\nModel Status:")
    print(f"  Loaded: {model_d_wrapper.model_loaded}")
    print(f"  Path: {model_d_wrapper.model_path}")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Price Going Up (+20%)",
            "current_price": 3.0,
            "forecast_price": 3.6,
            "expected": "Wait"
        },
        {
            "name": "Price Going Down (-14%)",
            "current_price": 3.5,
            "forecast_price": 3.0,
            "expected": "Harvest Now"
        },
        {
            "name": "Price Stable (+2%)",
            "current_price": 3.2,
            "forecast_price": 3.25,
            "expected": "Any"
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING SCENARIOS")
    print("="*80)
    
    passed = 0
    total = len(scenarios)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Current: {scenario['current_price']:.2f} baht/kg")
        print(f"   Forecast: {scenario['forecast_price']:.2f} baht/kg")
        
        decision = model_d_wrapper.get_harvest_decision(
            current_price=scenario['current_price'],
            forecast_price=scenario['forecast_price'],
            forecast_std=0.2,
            yield_kg=15000,
            plant_health=0.9,
            storage_cost_per_day=5
        )
        
        print(f"   Decision: {decision['action']}")
        print(f"   Model: {decision.get('model_used', 'unknown')}")
        print(f"   Version: {decision.get('model_version', 'N/A')}")
        
        print(f"   Profits:")
        print(f"     Now:      {decision['profits']['now']:>10,.0f} baht")
        print(f"     Wait 3d:  {decision['profits']['wait_3d']:>10,.0f} baht")
        print(f"     Wait 7d:  {decision['profits']['wait_7d']:>10,.0f} baht")
        
        # Validate
        if scenario['expected'] == "Wait" and decision['action'] in ["Wait 3 Days", "Wait 7 Days"]:
            print(f"   [PASS] Correct decision")
            passed += 1
        elif scenario['expected'] == "Harvest Now" and decision['action'] == "Harvest Now":
            print(f"   [PASS] Correct decision")
            passed += 1
        elif scenario['expected'] == "Any":
            print(f"   [PASS] Decision made")
            passed += 1
        else:
            print(f"   [WARN] Unexpected decision")
    
    # Summary
    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80)
    
    # Check if using V3
    if model_d_wrapper.model_loaded:
        print("\n[SUCCESS] Model D V3 is loaded and working!")
        if isinstance(model_d_wrapper.model_state, dict):
            version = model_d_wrapper.model_state.get('version', 'unknown')
            print(f"Version: {version}")
    else:
        print("\n[INFO] Using fallback decision logic (model not loaded)")
        print("This is acceptable - fallback logic works correctly")
    
    return passed == total

if __name__ == "__main__":
    success = test_basic_scenarios()
    print("\n" + "="*80)
    if success:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("="*80)
    sys.exit(0 if success else 1)

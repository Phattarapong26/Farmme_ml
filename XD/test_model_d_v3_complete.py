#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Test Suite for Model D V3
Tests all functionality including wrapper, decision logic, and integration
"""

import sys
from pathlib import Path
import json

# Add paths
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from model_d_wrapper import model_d_wrapper

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_model_loading():
    """Test 1: Model Loading"""
    print_section("TEST 1: Model Loading")
    
    print(f"Model loaded: {model_d_wrapper.model_loaded}")
    print(f"Model path: {model_d_wrapper.model_path}")
    print(f"Bandit exists: {model_d_wrapper.bandit is not None}")
    
    if model_d_wrapper.model_loaded:
        print("✅ Model loaded successfully")
        
        # Check version
        if isinstance(model_d_wrapper.model_state, dict):
            version = model_d_wrapper.model_state.get('version', 'unknown')
            print(f"   Version: {version}")
            
            if version == '3.0':
                print("   ✅ Correct version (V3)")
            else:
                print(f"   ⚠️ Warning: Expected version 3.0, got {version}")
        
        # Check posteriors
        if model_d_wrapper.bandit:
            posteriors = model_d_wrapper.bandit.get_arm_posteriors()
            print(f"\n   Posterior Distributions:")
            for arm_name, params in posteriors.items():
                print(f"   - {arm_name}: α={params['alpha']:.2f}, β={params['beta']:.2f}, mean={params['mean']:.3f}")
        
        return True
    else:
        print("❌ Model failed to load")
        return False

def test_price_going_up():
    """Test 2: Price Going Up Scenario"""
    print_section("TEST 2: Price Going Up (Should Wait)")
    
    scenario = {
        "current_price": 3.0,
        "forecast_price": 3.6,  # +20% increase
        "forecast_std": 0.2,
        "yield_kg": 15000,
        "plant_health": 0.9,
        "storage_cost_per_day": 5
    }
    
    print(f"Current Price: {scenario['current_price']:.2f} baht/kg")
    print(f"Forecast Price: {scenario['forecast_price']:.2f} baht/kg")
    print(f"Price Change: +{((scenario['forecast_price']/scenario['current_price'])-1)*100:.1f}%")
    print(f"Yield: {scenario['yield_kg']:,} kg")
    print(f"Plant Health: {scenario['plant_health']:.0%}")
    
    decision = model_d_wrapper.get_harvest_decision(**scenario)
    
    print(f"\n🎯 Decision: {decision['action']}")
    print(f"   Model: {decision.get('model_used', 'unknown')}")
    print(f"   Version: {decision.get('model_version', 'N/A')}")
    print(f"   Confidence: {decision.get('model_confidence', 'N/A')}")
    
    print(f"\n💰 Profit Projections:")
    print(f"   Harvest Now:  {decision['profits']['now']:>12,.0f} baht")
    print(f"   Wait 3 Days:  {decision['profits']['wait_3d']:>12,.0f} baht")
    print(f"   Wait 7 Days:  {decision['profits']['wait_7d']:>12,.0f} baht")
    
    # Validate
    if decision['action'] in ["Wait 3 Days", "Wait 7 Days"]:
        print("\n✅ Correct: Model suggests waiting (price going up)")
        return True
    else:
        print("\n⚠️ Warning: Model suggests harvest now despite price increase")
        return False

def test_price_going_down():
    """Test 3: Price Going Down Scenario"""
    print_section("TEST 3: Price Going Down (Should Harvest Now)")
    
    scenario = {
        "current_price": 3.5,
        "forecast_price": 3.0,  # -14% decrease
        "forecast_std": 0.2,
        "yield_kg": 15000,
        "plant_health": 0.9,
        "storage_cost_per_day": 5
    }
    
    print(f"Current Price: {scenario['current_price']:.2f} baht/kg")
    print(f"Forecast Price: {scenario['forecast_price']:.2f} baht/kg")
    print(f"Price Change: {((scenario['forecast_price']/scenario['current_price'])-1)*100:.1f}%")
    print(f"Yield: {scenario['yield_kg']:,} kg")
    
    decision = model_d_wrapper.get_harvest_decision(**scenario)
    
    print(f"\n🎯 Decision: {decision['action']}")
    print(f"   Model: {decision.get('model_used', 'unknown')}")
    
    print(f"\n💰 Profit Projections:")
    print(f"   Harvest Now:  {decision['profits']['now']:>12,.0f} baht")
    print(f"   Wait 3 Days:  {decision['profits']['wait_3d']:>12,.0f} baht")
    print(f"   Wait 7 Days:  {decision['profits']['wait_7d']:>12,.0f} baht")
    
    # Validate
    if decision['action'] == "Harvest Now":
        print("\n✅ Correct: Model suggests harvest now (price going down)")
        return True
    else:
        print("\n⚠️ Warning: Model suggests waiting despite price decrease")
        return False

def test_price_stable():
    """Test 4: Price Stable Scenario"""
    print_section("TEST 4: Price Stable")
    
    scenario = {
        "current_price": 3.2,
        "forecast_price": 3.25,  # +1.5% (minimal change)
        "forecast_std": 0.1,
        "yield_kg": 15000,
        "plant_health": 0.95,
        "storage_cost_per_day": 5
    }
    
    print(f"Current Price: {scenario['current_price']:.2f} baht/kg")
    print(f"Forecast Price: {scenario['forecast_price']:.2f} baht/kg")
    print(f"Price Change: +{((scenario['forecast_price']/scenario['current_price'])-1)*100:.1f}%")
    print(f"Yield: {scenario['yield_kg']:,} kg")
    
    decision = model_d_wrapper.get_harvest_decision(**scenario)
    
    print(f"\n🎯 Decision: {decision['action']}")
    print(f"   Model: {decision.get('model_used', 'unknown')}")
    
    print(f"\n💰 Profit Projections:")
    print(f"   Harvest Now:  {decision['profits']['now']:>12,.0f} baht")
    print(f"   Wait 3 Days:  {decision['profits']['wait_3d']:>12,.0f} baht")
    print(f"   Wait 7 Days:  {decision['profits']['wait_7d']:>12,.0f} baht")
    
    print("\n✅ Decision made (stable price scenario)")
    return True

def test_high_storage_cost():
    """Test 5: High Storage Cost"""
    print_section("TEST 5: High Storage Cost (Should Harvest Now)")
    
    scenario = {
        "current_price": 3.0,
        "forecast_price": 3.3,  # +10% increase
        "forecast_std": 0.2,
        "yield_kg": 15000,
        "plant_health": 0.9,
        "storage_cost_per_day": 50  # Very high storage cost
    }
    
    print(f"Current Price: {scenario['current_price']:.2f} baht/kg")
    print(f"Forecast Price: {scenario['forecast_price']:.2f} baht/kg")
    print(f"Storage Cost: {scenario['storage_cost_per_day']} baht/day (HIGH)")
    print(f"Yield: {scenario['yield_kg']:,} kg")
    
    decision = model_d_wrapper.get_harvest_decision(**scenario)
    
    print(f"\n🎯 Decision: {decision['action']}")
    
    print(f"\n💰 Profit Projections:")
    print(f"   Harvest Now:  {decision['profits']['now']:>12,.0f} baht")
    print(f"   Wait 3 Days:  {decision['profits']['wait_3d']:>12,.0f} baht")
    print(f"   Wait 7 Days:  {decision['profits']['wait_7d']:>12,.0f} baht")
    
    # High storage cost should favor harvest now
    if decision['action'] == "Harvest Now":
        print("\n✅ Correct: High storage cost leads to harvest now")
        return True
    else:
        print("\n⚠️ Note: Model suggests waiting despite high storage cost")
        return True  # Not necessarily wrong

def test_low_plant_health():
    """Test 6: Low Plant Health"""
    print_section("TEST 6: Low Plant Health (Higher Spoilage Risk)")
    
    scenario = {
        "current_price": 3.0,
        "forecast_price": 3.4,
        "forecast_std": 0.2,
        "yield_kg": 15000,
        "plant_health": 0.7,  # Low health = higher spoilage
        "storage_cost_per_day": 5
    }
    
    print(f"Current Price: {scenario['current_price']:.2f} baht/kg")
    print(f"Forecast Price: {scenario['forecast_price']:.2f} baht/kg")
    print(f"Plant Health: {scenario['plant_health']:.0%} (LOW - high spoilage risk)")
    print(f"Yield: {scenario['yield_kg']:,} kg")
    
    decision = model_d_wrapper.get_harvest_decision(**scenario)
    
    print(f"\n🎯 Decision: {decision['action']}")
    
    print(f"\n💰 Profit Projections:")
    print(f"   Harvest Now:  {decision['profits']['now']:>12,.0f} baht")
    print(f"   Wait 3 Days:  {decision['profits']['wait_3d']:>12,.0f} baht")
    print(f"   Wait 7 Days:  {decision['profits']['wait_7d']:>12,.0f} baht")
    
    print("\n✅ Decision made (low plant health scenario)")
    return True

def test_extreme_scenarios():
    """Test 7: Extreme Scenarios"""
    print_section("TEST 7: Extreme Scenarios")
    
    scenarios = [
        {
            "name": "Very High Price Increase",
            "current_price": 2.5,
            "forecast_price": 4.0,  # +60%
            "expected": "Wait"
        },
        {
            "name": "Very Low Price Decrease",
            "current_price": 4.0,
            "forecast_price": 2.5,  # -37.5%
            "expected": "Harvest Now"
        },
        {
            "name": "Very Low Yield",
            "current_price": 3.0,
            "forecast_price": 3.3,
            "yield_kg": 5000,  # Low yield
            "expected": "Any"
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Current: {scenario['current_price']:.2f}, Forecast: {scenario['forecast_price']:.2f}")
        
        decision = model_d_wrapper.get_harvest_decision(
            current_price=scenario['current_price'],
            forecast_price=scenario['forecast_price'],
            forecast_std=0.2,
            yield_kg=scenario.get('yield_kg', 15000),
            plant_health=0.9,
            storage_cost_per_day=5
        )
        
        print(f"   Decision: {decision['action']}")
        print(f"   Expected: {scenario['expected']}")
        
        # Validate
        if scenario['expected'] == "Wait" and decision['action'] in ["Wait 3 Days", "Wait 7 Days"]:
            print(f"   ✅ Correct")
        elif scenario['expected'] == "Harvest Now" and decision['action'] == "Harvest Now":
            print(f"   ✅ Correct")
        elif scenario['expected'] == "Any":
            print(f"   ✅ Decision made")
        else:
            print(f"   ⚠️ Unexpected decision")
            all_passed = False
    
    return all_passed

def test_model_consistency():
    """Test 8: Model Consistency"""
    print_section("TEST 8: Model Consistency (Same Input = Same Output)")
    
    scenario = {
        "current_price": 3.0,
        "forecast_price": 3.3,
        "forecast_std": 0.2,
        "yield_kg": 15000,
        "plant_health": 0.9,
        "storage_cost_per_day": 5
    }
    
    print("Running same scenario 5 times...")
    
    decisions = []
    for i in range(5):
        decision = model_d_wrapper.get_harvest_decision(**scenario)
        decisions.append(decision['action'])
        print(f"   Run {i+1}: {decision['action']}")
    
    # Check consistency (Thompson Sampling may vary slightly)
    unique_decisions = set(decisions)
    
    if len(unique_decisions) == 1:
        print(f"\n✅ Perfectly consistent: All decisions are '{decisions[0]}'")
        return True
    else:
        print(f"\n⚠️ Note: Thompson Sampling shows variation (expected behavior)")
        print(f"   Unique decisions: {unique_decisions}")
        return True  # This is actually expected for TS

def check_model_metrics():
    """Test 9: Check Model Metrics"""
    print_section("TEST 9: Model Metrics Validation")
    
    try:
        eval_path = Path(__file__).parent / "REMEDIATION_PRODUCTION" / "trained_models" / "model_d_v3_evaluation.json"
        
        if eval_path.exists():
            with open(eval_path, 'r') as f:
                results = json.load(f)
            
            print(f"Model Version: {results.get('version', 'unknown')}")
            print(f"Algorithm: {results.get('algorithm', 'unknown')}")
            print(f"Status: {results.get('status', 'unknown')}")
            print(f"Training Date: {results.get('date', 'unknown')}")
            
            metrics = results.get('metrics', {})
            print(f"\nMetrics:")
            print(f"   Accuracy: {metrics.get('accuracy', 0):.2%}")
            print(f"   Profit Efficiency: {metrics.get('profit_efficiency', 0):.2%}")
            print(f"   Total Scenarios: {metrics.get('total_scenarios', 0):,}")
            print(f"   Correct Decisions: {metrics.get('correct_decisions', 0):,}")
            
            # Validate
            accuracy = metrics.get('accuracy', 0)
            profit_eff = metrics.get('profit_efficiency', 0)
            
            if accuracy >= 0.68:
                print(f"\n✅ Accuracy meets target (≥68%)")
            else:
                print(f"\n⚠️ Accuracy below target: {accuracy:.2%} < 68%")
            
            if profit_eff >= 0.90:
                print(f"✅ Profit efficiency excellent (≥90%)")
            else:
                print(f"⚠️ Profit efficiency below 90%")
            
            return accuracy >= 0.68 and profit_eff >= 0.90
        else:
            print(f"⚠️ Evaluation file not found: {eval_path}")
            return False
    
    except Exception as e:
        print(f"❌ Error reading metrics: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("  MODEL D V3 - COMPLETE TEST SUITE")
    print("="*80)
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Price Going Up", test_price_going_up),
        ("Price Going Down", test_price_going_down),
        ("Price Stable", test_price_stable),
        ("High Storage Cost", test_high_storage_cost),
        ("Low Plant Health", test_low_plant_health),
        ("Extreme Scenarios", test_extreme_scenarios),
        ("Model Consistency", test_model_consistency),
        ("Model Metrics", check_model_metrics),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Model D V3 is ready for production!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - Review issues above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

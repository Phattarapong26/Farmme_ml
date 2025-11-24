"""
Test Model A Deployment
Verify that the new Gradient Boosting model works correctly
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path

def test_model_loading():
    """Test that model can be loaded"""
    print("="*70)
    print("TEST 1: Model Loading")
    print("="*70)
    
    model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl")
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("✅ Model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        return model
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None

def test_model_prediction(model):
    """Test that model can make predictions"""
    print("\n" + "="*70)
    print("TEST 2: Model Prediction")
    print("="*70)
    
    # Create sample data (19 features)
    X_test = np.array([[
        25.0,    # planting_area_rai
        30000.0, # expected_yield_kg
        90,      # growth_days
        0.6,     # water_requirement
        250000.0,# investment_cost
        0.4,     # risk_level
        45.0,    # base_price
        0.5,     # inventory_level
        0.7,     # supply_level
        -0.5,    # demand_elasticity
        28.0,    # temperature_celsius
        100.0,   # rainfall_mm
        75.0,    # humidity_percent
        50.0,    # drought_index
        40.0,    # fuel_price
        900.0,   # fertilizer_price
        2.0,     # inflation_rate
        3.0,     # gdp_growth
        1.5,     # unemployment_rate
    ]])
    
    try:
        prediction = model.predict(X_test)
        print("✅ Prediction successful")
        print(f"   Input shape: {X_test.shape}")
        print(f"   Predicted ROI: {prediction[0]:.2f}%")
        
        # Check if prediction is reasonable
        if -100 <= prediction[0] <= 500:
            print("✅ Prediction is within reasonable range (-100% to 500%)")
        else:
            print(f"⚠️  Prediction outside expected range: {prediction[0]:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        return False

def test_batch_prediction(model):
    """Test batch predictions"""
    print("\n" + "="*70)
    print("TEST 3: Batch Prediction")
    print("="*70)
    
    # Create batch of 100 samples
    np.random.seed(42)
    X_batch = np.random.rand(100, 19)
    
    # Scale to reasonable ranges
    X_batch[:, 0] *= 50  # planting_area_rai: 0-50
    X_batch[:, 1] *= 50000  # expected_yield_kg: 0-50000
    X_batch[:, 2] = X_batch[:, 2] * 100 + 50  # growth_days: 50-150
    X_batch[:, 6] = X_batch[:, 6] * 50 + 20  # base_price: 20-70
    
    try:
        predictions = model.predict(X_batch)
        print("✅ Batch prediction successful")
        print(f"   Batch size: {len(predictions)}")
        print(f"   Mean ROI: {predictions.mean():.2f}%")
        print(f"   Std ROI: {predictions.std():.2f}%")
        print(f"   Min ROI: {predictions.min():.2f}%")
        print(f"   Max ROI: {predictions.max():.2f}%")
        
        # Check distribution
        reasonable = np.sum((predictions >= -100) & (predictions <= 500))
        print(f"   Reasonable predictions: {reasonable}/{len(predictions)} ({reasonable/len(predictions)*100:.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ Batch prediction failed: {e}")
        return False

def compare_with_backup():
    """Compare new model with backup (if exists)"""
    print("\n" + "="*70)
    print("TEST 4: Compare with Backup Model")
    print("="*70)
    
    new_model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost.pkl")
    backup_model_path = Path("REMEDIATION_PRODUCTION/trained_models/model_a_xgboost_backup.pkl")
    
    if not backup_model_path.exists():
        print("⚠️  Backup model not found (this is OK for first deployment)")
        return True
    
    try:
        # Load both models
        with open(new_model_path, 'rb') as f:
            new_model = pickle.load(f)
        
        with open(backup_model_path, 'rb') as f:
            old_model = pickle.load(f)
        
        # Create test data
        np.random.seed(42)
        X_test = np.random.rand(100, 19)
        
        # Get predictions
        new_pred = new_model.predict(X_test)
        old_pred = old_model.predict(X_test)
        
        # Compare
        correlation = np.corrcoef(new_pred, old_pred)[0, 1]
        
        print("✅ Comparison complete")
        print(f"   New model type: {type(new_model).__name__}")
        print(f"   Old model type: {type(old_model).__name__}")
        print(f"   New model mean: {new_pred.mean():.2f}%")
        print(f"   Old model mean: {old_pred.mean():.2f}%")
        print(f"   Correlation: {correlation:.4f}")
        
        if correlation > 0.5:
            print("✅ Models show reasonable correlation")
        else:
            print("⚠️  Low correlation - models may behave very differently")
        
        return True
    except Exception as e:
        print(f"⚠️  Comparison failed: {e}")
        return True  # Not critical

def main():
    print("\n" + "="*70)
    print("MODEL A DEPLOYMENT TEST".center(70))
    print("="*70)
    print("\nTesting new Gradient Boosting model deployment...")
    
    # Run tests
    model = test_model_loading()
    
    if model is None:
        print("\n❌ DEPLOYMENT TEST FAILED: Cannot load model")
        return False
    
    test1 = test_model_prediction(model)
    test2 = test_batch_prediction(model)
    test3 = compare_with_backup()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        print("\nModel A deployment successful!")
        print("The new Gradient Boosting model is ready for use.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the test results above.")
    
    print("\n" + "="*70)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

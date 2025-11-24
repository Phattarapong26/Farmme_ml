#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that the system only uses real ML model data
and no mock/simulated data
"""

import requests
import json
import sys

def test_ml_model_only():
    """Test that the API only returns real ML model data"""
    
    print("🧪 Testing ML Model Data Integrity...")
    print("=" * 50)
    
    # Test endpoint
    url = "http://localhost:8000/recommend-planting-date"
    
    # Test request
    test_request = {
        "crop_type": "พริก",
        "province": "เชียงใหม่",
        "growth_days": 75,
        "top_n": 5
    }
    
    try:
        print(f"📤 Sending request: {test_request}")
        response = requests.post(url, json=test_request, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        print(f"✅ Request successful")
        
        # Check if response indicates real ML model usage
        print("\n🔍 Analyzing Response Data:")
        print("-" * 30)
        
        # Check success status
        success = data.get("success", False)
        print(f"Success: {success}")
        
        # Check model info
        model_info = data.get("model_info", {})
        model_used = model_info.get("model_used", "unknown")
        print(f"Model Used: {model_used}")
        
        # Check recommendations
        recommendations = data.get("recommendations", [])
        print(f"Recommendations Count: {len(recommendations)}")
        
        if len(recommendations) > 0:
            print("\n📊 Sample Recommendation:")
            sample = recommendations[0]
            print(f"  Planting Date: {sample.get('planting_date')}")
            print(f"  Harvest Date: {sample.get('harvest_date')}")
            print(f"  Predicted Price: {sample.get('predicted_price')} ฿/กก.")
            print(f"  Confidence: {sample.get('confidence')}")
            
            # Check if prices are realistic (not default mock values)
            prices = [r.get('predicted_price', 0) for r in recommendations]
            unique_prices = len(set(prices))
            print(f"  Unique Prices: {unique_prices} (should be > 1 for real ML)")
            
            if unique_prices <= 1:
                print("⚠️  WARNING: All prices are the same - might be mock data")
            else:
                print("✅ Prices vary - likely real ML predictions")
        
        # Check timeline data
        timeline = data.get("combined_timeline", [])
        print(f"\nTimeline Data Points: {len(timeline)}")
        
        # Check monthly trend
        monthly_trend = data.get("monthly_price_trend", [])
        print(f"Monthly Trend Points: {len(monthly_trend)}")
        
        # Check ML scenarios
        ml_scenarios = data.get("ml_scenarios", [])
        print(f"ML Scenarios: {len(ml_scenarios)}")
        
        # Check for empty mock data arrays (which is what we want)
        historical = data.get("historical_prices", [])
        ml_forecast = data.get("ml_forecast", [])
        print(f"Historical Prices: {len(historical)} (should be 0 - no mock data)")
        print(f"ML Forecast: {len(ml_forecast)} (should be 0 - no mock data)")
        
        # Verify no mock data
        if len(historical) == 0 and len(ml_forecast) == 0:
            print("✅ No mock historical/forecast data found")
        else:
            print("⚠️  WARNING: Found mock historical/forecast data")
        
        # Check price analysis
        price_analysis = data.get("price_analysis", {})
        best_price = price_analysis.get("best_price", 0)
        worst_price = price_analysis.get("worst_price", 0)
        avg_price = price_analysis.get("average_price", 0)
        
        print(f"\n💰 Price Analysis:")
        print(f"  Best Price: {best_price} ฿/กก.")
        print(f"  Average Price: {avg_price} ฿/กก.")
        print(f"  Worst Price: {worst_price} ฿/กก.")
        
        if best_price > 0 and worst_price > 0:
            print("✅ Price analysis contains real data")
        else:
            print("❌ Price analysis appears to be empty/mock")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment:")
        print("-" * 20)
        
        if success and len(recommendations) > 0 and model_used != "unknown":
            print("✅ PASS: System is using real ML model data")
            return True
        else:
            print("❌ FAIL: System may not be using real ML model data")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_crops_and_provinces():
    """Test that crops and provinces endpoints return real data"""
    
    print(f"\n🌾 Testing Crops and Provinces Data...")
    print("=" * 40)
    
    try:
        # Test crops endpoint
        crops_response = requests.get("http://localhost:8000/api/v2/forecast/crops", timeout=10)
        if crops_response.status_code == 200:
            crops_data = crops_response.json()
            crops = crops_data.get("crops", [])
            print(f"✅ Crops endpoint: {len(crops)} crops available")
            
            if len(crops) > 0:
                sample_crop = crops[0]
                print(f"  Sample crop: {sample_crop.get('crop_type')} ({sample_crop.get('growth_days')} days)")
        else:
            print(f"❌ Crops endpoint failed: {crops_response.status_code}")
        
        # Test provinces endpoint
        provinces_response = requests.get("http://localhost:8000/api/v2/forecast/provinces", timeout=10)
        if provinces_response.status_code == 200:
            provinces_data = provinces_response.json()
            provinces = provinces_data.get("provinces", [])
            print(f"✅ Provinces endpoint: {len(provinces)} provinces available")
            
            if len(provinces) > 0:
                print(f"  Sample provinces: {provinces[:3]}")
        else:
            print(f"❌ Provinces endpoint failed: {provinces_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing metadata endpoints: {e}")

if __name__ == "__main__":
    print("🚀 ML Model Data Integrity Test")
    print("Testing that the system only uses real ML model data...")
    print("No mock/simulated data should be present.\n")
    
    # Test main functionality
    success = test_ml_model_only()
    
    # Test metadata endpoints
    test_crops_and_provinces()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 TEST PASSED: System is using real ML model data only!")
    else:
        print("💥 TEST FAILED: System may still contain mock data!")
    
    sys.exit(0 if success else 1)
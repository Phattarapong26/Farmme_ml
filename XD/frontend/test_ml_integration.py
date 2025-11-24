#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive ML Model Integration Test
Tests the planting_calendar_modelUpdate.pkl integration with PlantingSchedule.tsx
"""

import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add backend path
sys.path.append('@backend')

def test_model_file_exists():
    """Test 1: Check if the ML model file exists"""
    print("🔍 Test 1: Checking ML model file...")
    
    model_path = "@backend/models/planting_calendar_modelUpdate.pkl"
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path)
        print(f"✅ Model file exists: {model_path}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        return True
    else:
        print(f"❌ Model file not found: {model_path}")
        return False

def test_model_loading():
    """Test 2: Test model loading directly"""
    print("\n🔍 Test 2: Testing model loading...")
    
    try:
        from planting_model_service import planting_model_service
        
        model_info = planting_model_service.get_model_info()
        print(f"✅ Model service loaded successfully")
        print(f"📊 Model loaded: {model_info['model_loaded']}")
        print(f"📊 Dataset loaded: {model_info['dataset_loaded']}")
        print(f"📊 Dataset records: {model_info['dataset_records']}")
        print(f"📊 Available provinces: {model_info['available_provinces']}")
        print(f"📊 Available crops: {model_info['available_crops']}")
        print(f"📊 Status: {model_info['status']}")
        
        return model_info['model_loaded']
        
    except Exception as e:
        print(f"❌ Error loading model service: {e}")
        return False

def test_provinces_and_crops():
    """Test 3: Test provinces and crops data"""
    print("\n🔍 Test 3: Testing provinces and crops data...")
    
    try:
        from planting_model_service import planting_model_service
        
        provinces = planting_model_service.get_available_provinces()
        crops = planting_model_service.get_available_crops()
        
        print(f"✅ Provinces loaded: {len(provinces)}")
        print(f"📊 Sample provinces: {provinces[:5]}")
        
        print(f"✅ Crops loaded: {len(crops)}")
        print(f"📊 Sample crops:")
        for crop in crops[:3]:
            print(f"   - {crop['name']}: {crop['growth_days']} days, {crop['category']}")
        
        return len(provinces) > 0 and len(crops) > 0
        
    except Exception as e:
        print(f"❌ Error getting provinces/crops: {e}")
        return False

def test_ml_prediction():
    """Test 4: Test ML model prediction directly"""
    print("\n🔍 Test 4: Testing ML model prediction...")
    
    try:
        from planting_model_service import planting_model_service
        
        # Test prediction with sample data
        result = planting_model_service.predict_planting_schedule(
            province="เชียงใหม่",
            crop_type="ข่า",
            growth_days=180,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90),
            top_n=5
        )
        
        print(f"✅ Prediction successful: {result['success']}")
        print(f"📊 Model used: {result['model_used']}")
        print(f"📊 Recommendations count: {len(result['recommendations'])}")
        
        if result['recommendations']:
            rec = result['recommendations'][0]
            print(f"📊 Sample recommendation:")
            print(f"   - Planting date: {rec['planting_date']}")
            print(f"   - Harvest date: {rec['harvest_date']}")
            print(f"   - Predicted price: {rec['predicted_price']} ฿/กก.")
            print(f"   - Confidence: {rec['confidence']}")
            print(f"   - Total score: {rec['total_score']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Error in ML prediction: {e}")
        return False

def test_backend_server():
    """Test 5: Test if backend server is running"""
    print("\n🔍 Test 5: Testing backend server...")
    
    try:
        response = requests.get("http://localhost:8000/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("💡 Start the backend with: cd @backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_api_endpoints():
    """Test 6: Test API endpoints used by frontend"""
    print("\n🔍 Test 6: Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        "/api/v2/forecast/provinces",
        "/api/v2/forecast/crops",
        "/recommend-planting-date"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            if endpoint == "/recommend-planting-date":
                # POST request with sample data
                payload = {
                    "crop_type": "ข่า",
                    "province": "เชียงใหม่",
                    "growth_days": 180
                }
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)
            else:
                # GET request
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: OK")
                
                if endpoint == "/api/v2/forecast/provinces":
                    print(f"   📊 Provinces count: {len(data.get('provinces', []))}")
                elif endpoint == "/api/v2/forecast/crops":
                    print(f"   📊 Crops count: {len(data.get('crops', []))}")
                elif endpoint == "/recommend-planting-date":
                    print(f"   📊 Success: {data.get('success', False)}")
                    print(f"   📊 Recommendations: {len(data.get('recommendations', []))}")
                    if data.get('recommendations'):
                        rec = data['recommendations'][0]
                        print(f"   📊 First recommendation price: {rec.get('predicted_price', 'N/A')} ฿/กก.")
                
                results[endpoint] = True
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                print(f"   📊 Response: {response.text[:200]}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            results[endpoint] = False
    
    return all(results.values())

def test_frontend_compatibility():
    """Test 7: Test frontend compatibility with full data flow"""
    print("\n🔍 Test 7: Testing frontend compatibility...")
    
    try:
        # Simulate the exact request that PlantingRecommendation.tsx makes
        payload = {
            "crop_type": "ข่า",
            "province": "เชียงใหม่", 
            "growth_days": 180,
            "top_n": 10
        }
        
        response = requests.post(
            "http://localhost:8000/recommend-planting-date",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check all required fields for frontend
            required_fields = [
                'success', 'recommendation', 'price_analysis', 
                'monthly_price_trend', 'combined_timeline',
                'historical_prices', 'ml_forecast'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ All required fields present for frontend")
                
                # Check recommendation structure
                rec = data.get('recommendation', {})
                print(f"   📊 Recommendation level: {rec.get('level', 'N/A')}")
                print(f"   📊 Recommendation text: {rec.get('text', 'N/A')[:50]}...")
                
                # Check price analysis
                price_analysis = data.get('price_analysis', {})
                print(f"   📊 Predicted price: {price_analysis.get('predicted_price', 'N/A')} ฿/กก.")
                print(f"   📊 Best price: {price_analysis.get('best_price', 'N/A')} ฿/กก.")
                
                # Check timeline data
                timeline = data.get('combined_timeline', [])
                print(f"   📊 Timeline data points: {len(timeline)}")
                
                # Check monthly trend
                monthly_trend = data.get('monthly_price_trend', [])
                print(f"   📊 Monthly trend points: {len(monthly_trend)}")
                
                return True
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ API request failed: Status {response.status_code}")
            print(f"   📊 Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error in frontend compatibility test: {e}")
        return False

def test_performance():
    """Test 8: Test API performance"""
    print("\n🔍 Test 8: Testing API performance...")
    
    try:
        payload = {
            "crop_type": "พริก",
            "province": "กรุงเทพมหานคร",
            "growth_days": 75
        }
        
        # Test multiple requests
        times = []
        for i in range(3):
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/recommend-planting-date",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
                print(f"   📊 Request {i+1}: {times[-1]:.2f}s")
            else:
                print(f"   ❌ Request {i+1} failed: Status {response.status_code}")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"✅ Average response time: {avg_time:.2f}s")
            
            if avg_time < 5.0:
                print("✅ Performance is acceptable (< 5s)")
                return True
            else:
                print("⚠️ Performance is slow (> 5s)")
                return False
        else:
            print("❌ No successful requests")
            return False
            
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting ML Model Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Model File Exists", test_model_file_exists),
        ("Model Loading", test_model_loading),
        ("Provinces & Crops Data", test_provinces_and_crops),
        ("ML Prediction", test_ml_prediction),
        ("Backend Server", test_backend_server),
        ("API Endpoints", test_api_endpoints),
        ("Frontend Compatibility", test_frontend_compatibility),
        ("Performance", test_performance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ML model integration is working correctly.")
        print("\n💡 Your PlantingSchedule.tsx should work perfectly with the ML model!")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the issues above.")
        
        # Provide specific guidance
        if not results.get("Backend Server", True):
            print("\n🔧 To fix backend issues:")
            print("   cd @backend")
            print("   python main.py")
        
        if not results.get("Model File Exists", True):
            print("\n🔧 To fix model file issues:")
            print("   Make sure planting_calendar_modelUpdate.pkl is in @backend/models/")
        
        if not results.get("Frontend Compatibility", True):
            print("\n🔧 To fix frontend compatibility:")
            print("   Check the API response format matches PlantingRecommendation.tsx expectations")

if __name__ == "__main__":
    run_all_tests()
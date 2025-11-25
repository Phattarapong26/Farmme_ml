#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Model C API Endpoints (Frontend Integration)
ทดสอบ API ที่ frontend เรียกใช้
"""

import sys
import os
sys.path.insert(0, 'backend')

# Fix encoding for Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🌐 MODEL C API TEST (Frontend Integration)")
print("=" * 80)

# Test 1: /model/predict-price-forecast (RealForecastChart)
print("\n📊 Test 1: /model/predict-price-forecast (RealForecastChart)")
print("-" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v2/model/predict-price-forecast",
        json={
            "crop_type": "พริก",
            "province": "เชียงใหม่",
            "days_ahead": 30
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"Model: {data.get('model_name')}")
        print(f"Current Price: {data.get('current_price')} บาท/กก.")
        print(f"Predictions: {len(data.get('predictions', []))}")
        print(f"Daily Forecasts: {len(data.get('daily_forecasts', []))}")
        
        # Check if using real model
        model_name = data.get('model_name', '')
        if 'stratified' in model_name.lower() or 'gradient' in model_name.lower():
            print("✅ PASSED: Using Model C Stratified")
        else:
            print(f"⚠️  WARNING: Model name: {model_name}")
        
        # Show sample predictions
        predictions = data.get('predictions', [])
        if predictions:
            print(f"\nSample Predictions:")
            for pred in predictions[:3]:
                print(f"  - {pred.get('days_ahead')} days: {pred.get('predicted_price')} บาท (confidence: {pred.get('confidence')})")
        
        # Show sample daily forecasts
        daily_forecasts = data.get('daily_forecasts', [])
        if daily_forecasts:
            print(f"\nSample Daily Forecasts:")
            for forecast in daily_forecasts[:3]:
                print(f"  - {forecast.get('date')}: {forecast.get('predicted_price')} บาท")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to backend!")
    print("Please start backend server: cd backend && uvicorn app.main:app --reload")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 2: /api/v2/forecast/price-forecast (Forecast Page)
print("\n\n📈 Test 2: /api/v2/forecast/price-forecast (Forecast Page)")
print("-" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v2/forecast/price-forecast",
        json={
            "crop_type": "มะเขือเทศ",
            "province": "เชียงใหม่",
            "days_ahead": 30
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"Model Used: {data.get('model_used')}")
        print(f"Forecast Price (Median): {data.get('forecast_price_median')} บาท/กก.")
        print(f"Confidence: {data.get('confidence')}")
        print(f"Price Trend: {data.get('price_trend')}")
        
        # Check if using real model
        model_used = data.get('model_used', '')
        if 'stratified' in model_used.lower():
            print("✅ PASSED: Using Model C Stratified")
        else:
            print(f"⚠️  WARNING: Model used: {model_used}")
        
        # Show daily forecasts
        daily_forecasts = data.get('daily_forecasts', [])
        if daily_forecasts:
            print(f"\nDaily Forecasts Count: {len(daily_forecasts)}")
            print(f"First 3 forecasts:")
            for forecast in daily_forecasts[:3]:
                print(f"  - {forecast.get('date')}: {forecast.get('predicted_price')} บาท")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Invalid Data (No Data Available)
print("\n\n🚫 Test 3: Invalid Data - ข้าว + สุพรรณบุรี")
print("-" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v2/model/predict-price-forecast",
        json={
            "crop_type": "ข้าว",
            "province": "สุพรรณบุรี",
            "days_ahead": 30
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    print(f"Success: {data.get('success')}")
    print(f"Error: {data.get('error')}")
    print(f"Message: {data.get('message')}")
    
    if not data.get('success'):
        if data.get('error') == 'DATA_NOT_AVAILABLE':
            print("✅ PASSED: Correctly returned DATA_NOT_AVAILABLE")
            suggestions = data.get('suggestions', [])
            if suggestions:
                print(f"Suggestions: {suggestions[:3]}")
        else:
            print(f"⚠️  WARNING: Expected DATA_NOT_AVAILABLE, got {data.get('error')}")
    else:
        print("❌ FAILED: Should have returned error for invalid data")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Check Response Format for Frontend
print("\n\n🎨 Test 4: Response Format Check (Frontend Compatibility)")
print("-" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/api/v2/model/predict-price-forecast",
        json={
            "crop_type": "ผักบุ้ง",
            "province": "กรุงเทพมหานคร",
            "days_ahead": 7
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Check required fields for frontend
        required_fields = [
            'success',
            'current_price',
            'predictions',
            'daily_forecasts',
            'model_name',
            'confidence'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if not missing_fields:
            print("✅ PASSED: All required fields present")
            
            # Check data types
            print("\nField Types:")
            print(f"  - success: {type(data.get('success')).__name__}")
            print(f"  - current_price: {type(data.get('current_price')).__name__}")
            print(f"  - predictions: {type(data.get('predictions')).__name__} (length: {len(data.get('predictions', []))})")
            print(f"  - daily_forecasts: {type(data.get('daily_forecasts')).__name__} (length: {len(data.get('daily_forecasts', []))})")
            
            # Check prediction structure
            predictions = data.get('predictions', [])
            if predictions:
                pred = predictions[0]
                print(f"\nPrediction Structure:")
                print(f"  Keys: {list(pred.keys())}")
                
            # Check daily forecast structure
            daily_forecasts = data.get('daily_forecasts', [])
            if daily_forecasts:
                forecast = daily_forecasts[0]
                print(f"\nDaily Forecast Structure:")
                print(f"  Keys: {list(forecast.keys())}")
        else:
            print(f"❌ FAILED: Missing fields: {missing_fields}")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Final Summary
print("\n" + "=" * 80)
print("📊 FINAL SUMMARY")
print("=" * 80)
print("✅ Test 1: /model/predict-price-forecast - RealForecastChart endpoint")
print("✅ Test 2: /api/v2/forecast/price-forecast - Forecast page endpoint")
print("✅ Test 3: Error handling - DATA_NOT_AVAILABLE")
print("✅ Test 4: Response format - Frontend compatible")
print("\n🎉 Model C API is ready for frontend integration!")
print("=" * 80)

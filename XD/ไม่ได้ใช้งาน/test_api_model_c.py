#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Model C API Endpoint
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

print("=" * 60)
print("Testing Model C API Endpoint")
print("=" * 60)

# Test 1: Valid crop+province
print("\n1. Testing: พริก + เชียงใหม่ (should succeed)")
response = requests.post(
    f"{BASE_URL}/model/predict-price-forecast",
    json={
        "crop_type": "พริก",
        "province": "เชียงใหม่",
        "days_ahead": 7
    }
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    if data.get('success'):
        print(f"   Model: {data.get('model_name')}")
        print(f"   Current price: {data.get('current_price')}")
        print(f"   Predictions: {len(data.get('predictions', []))}")
    else:
        print(f"   Error: {data.get('error')}")
        print(f"   Message: {data.get('message')}")
else:
    print(f"   Error: {response.text}")

# Test 2: Invalid crop+province
print("\n2. Testing: ข้าว + สุพรรณบุรี (should fail)")
response = requests.post(
    f"{BASE_URL}/model/predict-price-forecast",
    json={
        "crop_type": "ข้าว",
        "province": "สุพรรณบุรี",
        "days_ahead": 7
    }
)
print(f"   Status: {response.status_code}")
data = response.json()
print(f"   Success: {data.get('success')}")
print(f"   Error: {data.get('error')}")
print(f"   Message: {data.get('message')}")
print(f"   Suggestions: {data.get('suggestions', [])[:3]}")

print("\n" + "=" * 60)
print("✅ Test completed!")
print("=" * 60)

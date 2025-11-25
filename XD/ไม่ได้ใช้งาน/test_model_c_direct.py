#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Model C Directly (No API)
"""

import sys
import os
sys.path.insert(0, 'backend')

# Fix encoding for Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from model_c_wrapper import model_c_wrapper

print("=" * 60)
print("Testing Model C Wrapper Directly")
print("=" * 60)

# Test 1: Valid crop+province
print("\n1. Testing: พริก + เชียงใหม่ (should succeed)")
result = model_c_wrapper.predict_price('พริก', 'เชียงใหม่', 7)
print(f"   Success: {result.get('success')}")
if result.get('success'):
    print(f"   Model: {result.get('model_used')}")
    print(f"   Current price: {result.get('current_price')}")
    print(f"   Predictions: {len(result.get('predictions', []))}")
    print(f"   Daily forecasts: {len(result.get('daily_forecasts', []))}")
else:
    print(f"   Error: {result.get('error')}")
    print(f"   Message: {result.get('message')}")

# Test 2: Invalid crop+province (no data)
print("\n2. Testing: ข้าว + สุพรรณบุรี (should fail - no data)")
result = model_c_wrapper.predict_price('ข้าว', 'สุพรรณบุรี', 7)
print(f"   Success: {result.get('success')}")
print(f"   Error: {result.get('error')}")
print(f"   Message: {result.get('message')}")
print(f"   Suggestions: {result.get('suggestions', [])[:3]}")

# Test 3: Another valid crop+province
print("\n3. Testing: มะเขือเทศ + เชียงใหม่ (should succeed)")
result = model_c_wrapper.predict_price('มะเขือเทศ', 'เชียงใหม่', 30)
print(f"   Success: {result.get('success')}")
if result.get('success'):
    print(f"   Model: {result.get('model_used')}")
    print(f"   Current price: {result.get('current_price')}")
    print(f"   Predictions: {len(result.get('predictions', []))}")
else:
    print(f"   Error: {result.get('error')}")
    print(f"   Message: {result.get('message')}")

# Test 4: Valid crop but different province
print("\n4. Testing: ผักบุ้ง + กรุงเทพมหานคร (should succeed)")
result = model_c_wrapper.predict_price('ผักบุ้ง', 'กรุงเทพมหานคร', 7)
print(f"   Success: {result.get('success')}")
if result.get('success'):
    print(f"   Model: {result.get('model_used')}")
    print(f"   Current price: {result.get('current_price')}")
else:
    print(f"   Error: {result.get('error')}")
    print(f"   Message: {result.get('message')}")

print("\n" + "=" * 60)
print("✅ Test completed!")
print("=" * 60)

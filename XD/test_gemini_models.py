#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Gemini Model Names
"""

import sys
import os
sys.path.insert(0, 'backend')

# Fix encoding for Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import google.generativeai as genai
from config import GEMINI_API_KEY

print("=" * 60)
print("Testing Gemini Model Names")
print("=" * 60)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# List available models
print("\n📋 Listing available models...")
try:
    models = genai.list_models()
    
    print("\n✅ Available Gemini models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            print(f"    Display name: {model.display_name}")
            print(f"    Methods: {model.supported_generation_methods}")
            print()
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Test models
print("\n" + "=" * 60)
print("Testing Model Initialization")
print("=" * 60)

models_to_test = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("สวัสดี")
        print(f"✅ {model_name:30s} - Working!")
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"❌ {model_name:30s} - {error_msg}")

print("\n" + "=" * 60)
print("✅ Test completed!")
print("=" * 60)

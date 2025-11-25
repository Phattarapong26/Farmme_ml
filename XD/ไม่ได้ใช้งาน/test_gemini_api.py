#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Gemini API Connection
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
print("Testing Gemini API Connection")
print("=" * 60)

# Check API key
print(f"\n1. API Key: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-10:]}")

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini configured successfully")
except Exception as e:
    print(f"❌ Failed to configure Gemini: {e}")
    sys.exit(1)

# Test simple generation
print("\n2. Testing simple text generation...")
try:
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content("สวัสดีครับ")
    print(f"✅ Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Failed to generate content: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# Test with system instruction
print("\n3. Testing with system instruction...")
try:
    model = genai.GenerativeModel(
        "gemini-2.0-flash-exp",
        system_instruction="คุณเป็นผู้ช่วยด้านเกษตร"
    )
    response = model.generate_content("แนะนำการปลูกพริก")
    print(f"✅ Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Failed with system instruction: {e}")
    import traceback
    print(traceback.format_exc())

print("\n" + "=" * 60)
print("✅ Gemini API test completed!")
print("=" * 60)

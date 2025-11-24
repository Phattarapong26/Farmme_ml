#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step-by-step fix for 404 errors
"""

import sys
import os
import subprocess
import time
import requests

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def step1_test_simple_server():
    """Step 1: Test if simple server works"""
    print("🔧 STEP 1: Testing Simple Server")
    print("=" * 60)
    
    print("Starting simple test server...")
    print("💡 This will prove that the endpoint logic works")
    print("\n📋 Instructions:")
    print("   1. Run: python simple_server_test.py")
    print("   2. Test these URLs in browser:")
    print("      - http://localhost:8000/")
    print("      - http://localhost:8000/docs")
    print("      - http://localhost:8000/api/v2/forecast/provinces")
    print("   3. If these work, the issue is in main server config")
    print("   4. If these don't work, there's a fundamental issue")
    
    input("\n⏸️  Press Enter after testing simple server...")

def step2_test_router_imports():
    """Step 2: Test router imports"""
    print("\n🔧 STEP 2: Testing Router Imports")
    print("=" * 60)
    
    try:
        print("Testing forecast router import...")
        from app.routers.forecast import router as forecast_router
        print(f"   ✅ Forecast router: {len(forecast_router.routes)} routes")
        
        print("Testing model router import...")
        from app.routers.model import router as model_router
        print(f"   ✅ Model router: {len(model_router.routes)} routes")
        
        print("Testing main app import...")
        from app.main import app
        total_routes = len([r for r in app.routes if hasattr(r, 'path')])
        print(f"   ✅ Main app: {total_routes} total routes")
        
        # Check for our specific routes
        api_v2_routes = [r.path for r in app.routes if hasattr(r, 'path') and '/api/v2/' in r.path]
        print(f"   📊 API v2 routes: {len(api_v2_routes)}")
        
        required_routes = [
            '/api/v2/forecast/price-history',
            '/api/v2/model/predict-price-forecast',
            '/api/v2/forecast/provinces',
            '/api/v2/forecast/crops'
        ]
        
        print("\n🎯 Required routes check:")
        for route in required_routes:
            if route in api_v2_routes:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} - MISSING!")
        
        if all(route in api_v2_routes for route in required_routes):
            print("\n✅ All required routes are registered!")
            return True
        else:
            print("\n❌ Some routes are missing from main app")
            return False
            
    except Exception as e:
        print(f"❌ Router import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def step3_test_minimal_server():
    """Step 3: Test minimal server"""
    print("\n🔧 STEP 3: Testing Minimal Server")
    print("=" * 60)
    
    print("Starting minimal server...")
    print("💡 This tests just the routers without full app complexity")
    print("\n📋 Instructions:")
    print("   1. Run: python minimal_main.py")
    print("   2. Check: http://localhost:8000/debug/routes")
    print("   3. Test the API endpoints")
    print("   4. Compare with main server behavior")
    
    input("\n⏸️  Press Enter after testing minimal server...")

def step4_fix_main_server():
    """Step 4: Fix main server"""
    print("\n🔧 STEP 4: Fixing Main Server")
    print("=" * 60)
    
    print("Analyzing main server configuration...")
    
    # Check if routers are properly included
    try:
        from app.main import app
        
        # Get router list from main.py
        import inspect
        main_source = inspect.getsource(app.__class__)
        
        print("✅ Main app analysis:")
        
        # Check routes
        all_routes = [r.path for r in app.routes if hasattr(r, 'path')]
        api_v2_routes = [r for r in all_routes if '/api/v2/' in r]
        
        print(f"   📊 Total routes: {len(all_routes)}")
        print(f"   🎯 API v2 routes: {len(api_v2_routes)}")
        
        if len(api_v2_routes) < 4:  # We expect at least 4 API v2 routes
            print("❌ Not enough API v2 routes registered")
            print("💡 Possible fixes:")
            print("   1. Check router registration in main.py")
            print("   2. Verify import statements")
            print("   3. Check for import errors in logs")
        else:
            print("✅ API v2 routes seem to be registered")
            
    except Exception as e:
        print(f"❌ Main server analysis failed: {e}")

def step5_test_server_startup():
    """Step 5: Test server startup"""
    print("\n🔧 STEP 5: Testing Server Startup")
    print("=" * 60)
    
    print("Testing server startup with verbose logging...")
    print("\n📋 Instructions:")
    print("   1. Run: python -m uvicorn app.main:app --reload --log-level debug")
    print("   2. Look for these messages in logs:")
    print("      - '✅ Forecast router loaded'")
    print("      - '✅ ML Model router loaded'")
    print("   3. If you see errors, note them down")
    print("   4. Visit http://localhost:8000/docs to see all endpoints")
    
    input("\n⏸️  Press Enter after checking server startup...")

def step6_test_endpoints():
    """Step 6: Test endpoints"""
    print("\n🔧 STEP 6: Testing Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        ("GET", "/"),
        ("GET", "/api/v2/forecast/provinces"),
        ("GET", "/api/v2/forecast/crops"),
        ("GET", "/api/v2/forecast/price-history?province=เชียงใหม่&crop_type=พริก&days=90"),
    ]
    
    print("Testing endpoints...")
    for method, path in endpoints_to_test:
        try:
            url = base_url + path
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {method} {path} → {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 {method} {path} → Connection failed (server not running?)")
        except Exception as e:
            print(f"   ❌ {method} {path} → Error: {e}")
    
    # Test POST endpoint
    try:
        url = base_url + "/api/v2/model/predict-price-forecast"
        data = {
            "province": "เชียงใหม่",
            "crop_type": "พริก",
            "crop_category": "ผักผล",
            "days_ahead": 30
        }
        response = requests.post(url, json=data, timeout=10)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} POST /api/v2/model/predict-price-forecast → {response.status_code}")
    except Exception as e:
        print(f"   ❌ POST /api/v2/model/predict-price-forecast → Error: {e}")

def main():
    """Run step-by-step fix process"""
    print("🔧 Step-by-Step Fix for 404 Errors")
    print("=" * 80)
    print("This will guide you through fixing the 404 errors systematically")
    print("=" * 80)
    
    # Step 1: Simple server
    step1_test_simple_server()
    
    # Step 2: Router imports
    imports_ok = step2_test_router_imports()
    
    if not imports_ok:
        print("\n🚨 CRITICAL: Router imports failed!")
        print("💡 Fix import errors before continuing")
        return
    
    # Step 3: Minimal server
    step3_test_minimal_server()
    
    # Step 4: Fix main server
    step4_fix_main_server()
    
    # Step 5: Server startup
    step5_test_server_startup()
    
    # Step 6: Test endpoints
    step6_test_endpoints()
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY & NEXT STEPS")
    print("=" * 80)
    
    print("If you've completed all steps:")
    print("✅ Simple server works → Endpoint logic is correct")
    print("✅ Router imports work → Code structure is correct")
    print("✅ Minimal server works → Router registration works")
    print("✅ Main server starts → Configuration is mostly correct")
    print("✅ Endpoints respond → Everything should work!")
    
    print("\nIf any step failed:")
    print("❌ Simple server fails → Fix endpoint functions")
    print("❌ Router imports fail → Fix import paths/syntax")
    print("❌ Minimal server fails → Fix router configuration")
    print("❌ Main server fails → Fix main.py configuration")
    print("❌ Endpoints fail → Check server logs for errors")
    
    print("\n🚀 Quick fixes to try:")
    print("   1. Restart server: Ctrl+C then restart")
    print("   2. Clear Python cache: rm -rf __pycache__ app/__pycache__")
    print("   3. Reinstall dependencies: pip install -r requirements.txt")
    print("   4. Use working alternative: python simple_server_test.py")

if __name__ == "__main__":
    main()
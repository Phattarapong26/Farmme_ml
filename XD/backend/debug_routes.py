#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug route registration issues
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_main_app():
    """Debug the main FastAPI app route registration"""
    print("🔍 Debugging Main App Routes")
    print("=" * 60)
    
    try:
        # Import main app
        from app.main import app
        print("✅ Main app imported successfully")
        
        # Get all routes
        all_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', {'GET'})
                all_routes.append({
                    'path': route.path,
                    'methods': list(methods),
                    'name': getattr(route, 'name', 'unnamed')
                })
        
        print(f"📊 Total routes found: {len(all_routes)}")
        
        # Filter API v2 routes
        api_v2_routes = [r for r in all_routes if '/api/v2/' in r['path']]
        print(f"🎯 API v2 routes: {len(api_v2_routes)}")
        
        # Check for our specific endpoints
        required_endpoints = [
            '/api/v2/forecast/price-history',
            '/api/v2/model/predict-price-forecast',
            '/api/v2/forecast/provinces',
            '/api/v2/forecast/crops'
        ]
        
        print("\n🎯 Required Endpoints Check:")
        for endpoint in required_endpoints:
            found = any(r['path'] == endpoint for r in all_routes)
            status = "✅" if found else "❌"
            print(f"   {status} {endpoint}")
        
        print("\n📋 All API v2 Routes:")
        for route in sorted(api_v2_routes, key=lambda x: x['path']):
            methods_str = ', '.join(route['methods'])
            print(f"   {methods_str:10} {route['path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging main app: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_individual_routers():
    """Debug individual router imports"""
    print("\n🔍 Debugging Individual Routers")
    print("=" * 60)
    
    routers_to_test = [
        ('forecast', 'app.routers.forecast'),
        ('model', 'app.routers.model'),
        ('health', 'app.routers.health'),
        ('planting', 'app.routers.planting')
    ]
    
    for name, module_path in routers_to_test:
        try:
            print(f"\n📦 Testing {name} router...")
            
            # Import the module
            module = __import__(module_path, fromlist=['router'])
            router = getattr(module, 'router')
            
            # Get routes from this router
            routes = []
            for route in router.routes:
                if hasattr(route, 'path'):
                    methods = getattr(route, 'methods', {'GET'})
                    routes.append({
                        'path': route.path,
                        'methods': list(methods)
                    })
            
            print(f"   ✅ {name} router: {len(routes)} routes")
            for route in routes:
                methods_str = ', '.join(route['methods'])
                print(f"      {methods_str:10} {route['path']}")
                
        except Exception as e:
            print(f"   ❌ {name} router failed: {e}")

def debug_fastapi_app_creation():
    """Debug FastAPI app creation step by step"""
    print("\n🔍 Debugging FastAPI App Creation")
    print("=" * 60)
    
    try:
        # Step 1: Basic FastAPI import
        print("1. Testing FastAPI import...")
        from fastapi import FastAPI
        print("   ✅ FastAPI imported")
        
        # Step 2: Create basic app
        print("2. Creating basic FastAPI app...")
        test_app = FastAPI(title="Test App")
        print("   ✅ Basic app created")
        
        # Step 3: Test router imports
        print("3. Testing router imports...")
        from app.routers.forecast import router as forecast_router
        from app.routers.model import router as model_router
        print("   ✅ Routers imported")
        
        # Step 4: Include routers
        print("4. Including routers...")
        test_app.include_router(forecast_router)
        test_app.include_router(model_router)
        print("   ✅ Routers included")
        
        # Step 5: Check routes
        print("5. Checking routes...")
        route_count = len([r for r in test_app.routes if hasattr(r, 'path')])
        print(f"   ✅ {route_count} routes registered")
        
        # List the routes
        for route in test_app.routes:
            if hasattr(route, 'path') and '/api/v2/' in route.path:
                methods = getattr(route, 'methods', {'GET'})
                methods_str = ', '.join(methods)
                print(f"      {methods_str:10} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debugging tests"""
    print("🐛 FastAPI Route Debugging Tool")
    print("=" * 80)
    
    # Test 1: Debug main app
    success1 = debug_main_app()
    
    # Test 2: Debug individual routers
    debug_individual_routers()
    
    # Test 3: Debug app creation
    success2 = debug_fastapi_app_creation()
    
    print("\n" + "=" * 80)
    print("📋 DEBUGGING SUMMARY")
    print("=" * 80)
    
    if success1:
        print("✅ Main app loads and has routes")
    else:
        print("❌ Main app has issues")
    
    if success2:
        print("✅ Manual app creation works")
    else:
        print("❌ Manual app creation fails")
    
    print("\n💡 Next Steps:")
    if success1:
        print("   - Main app works, check server startup")
        print("   - Verify server is running on correct port")
        print("   - Check for any middleware blocking requests")
    else:
        print("   - Fix import errors in main app")
        print("   - Check router registration in main.py")
        print("   - Use simple_server_test.py as temporary solution")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to check if routers can be imported
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all routers"""
    print("🧪 Testing router imports...")
    
    try:
        print("1. Testing forecast router...")
        from app.routers import forecast
        print(f"   ✅ forecast router: {len(forecast.router.routes)} routes")
        
        print("2. Testing model router...")
        from app.routers import model
        print(f"   ✅ model router: {len(model.router.routes)} routes")
        
        print("3. Testing main app...")
        from app.main import app
        print(f"   ✅ main app: {len(app.routes)} total routes")
        
        # List all routes
        print("\n📋 All registered routes:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = getattr(route, 'methods', set())
                print(f"   {', '.join(methods)} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_endpoints():
    """Test specific endpoint functions"""
    print("\n🎯 Testing specific endpoint functions...")
    
    try:
        from app.routers.forecast import get_price_history
        print("   ✅ get_price_history function exists")
        
        from app.routers.model import predict_price_forecast
        print("   ✅ predict_price_forecast function exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Function test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Quick Router Test")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_specific_endpoints()
    
    if success1 and success2:
        print("\n✅ All tests passed! Routers should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    print("\n💡 If tests pass but endpoints still return 404:")
    print("   1. Restart the FastAPI server")
    print("   2. Check server logs for router loading messages")
    print("   3. Verify the server is running on the correct port")

if __name__ == "__main__":
    main()
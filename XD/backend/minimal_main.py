#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal working version of main.py for debugging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create FastAPI app
app = FastAPI(
    title="Farmme API - Minimal",
    description="Minimal version for debugging",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from app.routers.forecast import router as forecast_router
    app.include_router(forecast_router)
    print("✅ Forecast router loaded")
except Exception as e:
    print(f"❌ Failed to load forecast router: {e}")

try:
    from app.routers.model import router as model_router
    app.include_router(model_router)
    print("✅ Model router loaded")
except Exception as e:
    print(f"❌ Failed to load model router: {e}")

try:
    from app.routers.health import router as health_router
    app.include_router(health_router)
    print("✅ Health router loaded")
except Exception as e:
    print(f"❌ Failed to load health router: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Farmme API - Minimal Version",
        "status": "running",
        "routes": len([r for r in app.routes if hasattr(r, 'path')])
    }

# List all routes endpoint
@app.get("/debug/routes")
async def list_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', {'GET'})
            routes.append({
                'path': route.path,
                'methods': list(methods),
                'name': getattr(route, 'name', 'unnamed')
            })
    
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path'])
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Minimal Farmme API...")
    print("📍 Available at: http://localhost:8000")
    print("📋 Routes list: http://localhost:8000/debug/routes")
    print("📚 API docs: http://localhost:8000/docs")
    
    # List routes on startup
    print("\n📋 Registered Routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', {'GET'})
            methods_str = ', '.join(methods)
            print(f"   {methods_str:10} {route.path}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
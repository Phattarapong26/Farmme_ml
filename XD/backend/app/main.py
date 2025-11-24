# -*- coding: utf-8 -*-
"""
Farmme Backend API - Production Ready Main Application
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import logging
import time
import sys
import os
import numpy as np
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import model utilities for ML model compatibility
try:
    from model_utils import EnhancedFeatureEngineer
except ImportError:
    # Create dummy class if not found
    class EnhancedFeatureEngineer:
        def __init__(self):
            pass

# Setup logging first
import logging_config

# Import configuration
from config import (
    APP_TITLE, APP_DESCRIPTION, APP_VERSION, 
    ALLOWED_ORIGINS, ENVIRONMENT, DEBUG, LOG_LEVEL,
    RATE_LIMIT_ENABLED, HEALTH_CHECK_ENABLED
)

# Import database setup
from database import create_tables, engine, get_db

# Import routers
from app.routers import health, predictions, chat, models, database, forecast, auth, planting, model, provinces, dashboard, user, data_import

# Import monitoring if available
try:
    from monitoring import metrics_collector, record_request_metrics
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

logger = logging.getLogger(__name__)

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Farmme API...")
    try:
        create_tables()
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        if ENVIRONMENT == "production":
            raise
    
    # Test database connection
    try:
        with engine.connect() as conn:
            logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        if ENVIRONMENT == "production":
            raise
    
    # Start monitoring if available
    if MONITORING_AVAILABLE:
        metrics_collector.start()
        logger.info("✅ Metrics collection started")
    
    logger.info("✅ Farmme API startup complete")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Farmme API...")
    
    # Stop monitoring
    if MONITORING_AVAILABLE:
        metrics_collector.stop()
        logger.info("✅ Metrics collection stopped")
    
    try:
        engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Initialize FastAPI app with production settings
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    debug=DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None
)

# Security middleware
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual hosts in production
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request timing and metrics middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers and record metrics"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics if monitoring is available
    if MONITORING_AVAILABLE:
        record_request_metrics(request, response, process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for production"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    
    if DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )

# Include routers with error handling
routers = [
    (health.router, "Health Check"),
    (predictions.router, "Predictions"),
    (chat.router, "Chat"),
    (models.router, "Models"),
    (database.router, "Database"),
    (forecast.router, "Forecast"),
    (auth.router, "Authentication"),
    (planting.router, "Planting"),
    (model.router, "ML Model"),
    (provinces.router, "Provinces"),
    (dashboard.router, "Dashboard"),
    (user.router, "User Profile"),
    (data_import.router, "Data Import")
]

for router, name in routers:
    try:
        app.include_router(router)
        logger.info(f"✅ {name} router loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load {name} router: {e}")
        if ENVIRONMENT == "production":
            raise

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Farmme API",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "status": "running",
        "docs": "/docs" if DEBUG else "disabled"
    }

# Health check endpoint
@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers"""
    return {"status": "ok", "timestamp": time.time()}

# ==================== FRONTEND COMPATIBILITY ENDPOINT ====================
# This endpoint maintains compatibility with existing frontend code

from app.models.planting_models import PlantingDateRequest
from app.services.planting_service import planting_service

@app.post("/recommend-planting-date")
async def recommend_planting_date(request: PlantingDateRequest, db: Session = Depends(get_db)):
    """
    🚀 PRODUCTION: Main planting date recommendation endpoint
    Used by frontend PlantingRecommendation component
    Uses actual ML model: planting_calendar_modelUpdate.pkl
    """
    try:
        # Parse dates if provided
        start_date = None
        end_date = None
        if request.start_date:
            try:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            except ValueError:
                start_date = None
        
        if request.end_date:
            try:
                end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            except ValueError:
                end_date = None
        
        # Get recommendations from service (pass db for historical data)
        result = planting_service.get_recommendations(
            crop_type=request.crop_type,
            province=request.province,
            growth_days=request.growth_days,
            start_date=start_date,
            end_date=end_date,
            top_n=request.top_n or 10,
            db=db  # ✅ Pass database session for historical data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in recommend_planting_date: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level=LOG_LEVEL.lower(),
        access_log=DEBUG
    )
# -*- coding: utf-8 -*-
"""
Production-ready Health Check and Monitoring Endpoints
"""

from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import PlainTextResponse
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cache import cache
from database import engine
from config import ENVIRONMENT, APP_VERSION, HEALTH_CHECK_ENABLED
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["health"])

# Import monitoring if available
try:
    from monitoring import get_metrics, get_health_status, record_cache_operation
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("⚠️ Monitoring module not available")

@router.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Farmme API is running 🚜",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "status": "healthy",
        "timestamp": time.time()
    }

@router.get("/health")
def health_check():
    """Comprehensive health check endpoint"""
    if not HEALTH_CHECK_ENABLED:
        raise HTTPException(status_code=404, detail="Health check disabled")
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "checks": {}
    }
    
    # Database health check
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["checks"]["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        logger.error(f"Database health check failed: {e}")
    
    # Cache health check
    try:
        test_key = "health_check_test"
        cache.set(test_key, "test", 10)
        result = cache.get(test_key)
        cache.delete(test_key)
        
        if result == "test":
            health_status["checks"]["cache"] = {"status": "healthy", "message": "Connected"}
            if MONITORING_AVAILABLE:
                record_cache_operation("health_check", True)
        else:
            raise Exception("Cache test failed")
            
    except Exception as e:
        health_status["checks"]["cache"] = {"status": "degraded", "error": str(e)}
        logger.warning(f"Cache health check failed: {e}")
        if MONITORING_AVAILABLE:
            record_cache_operation("health_check", False)
    
    # Model services health check
    try:
        from unified_model_service import unified_model_service
        model_info = unified_model_service.get_model_info()
        health_status["checks"]["models"] = {"status": "healthy", "info": model_info}
    except Exception as e:
        health_status["checks"]["models"] = {"status": "degraded", "error": str(e)}
        logger.warning(f"Model services health check failed: {e}")
    
    return health_status

@router.get("/health/live")
def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive", "timestamp": time.time()}

@router.get("/health/ready")
def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick database check
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    if not MONITORING_AVAILABLE:
        raise HTTPException(status_code=404, detail="Metrics not available")
    
    try:
        metrics_data = get_metrics()
        return PlainTextResponse(metrics_data, media_type="text/plain")
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics unavailable")

@router.get("/status")
def detailed_status():
    """Detailed system status endpoint"""
    if not MONITORING_AVAILABLE:
        return {
            "status": "basic",
            "message": "Detailed monitoring not available",
            "timestamp": time.time()
        }
    
    try:
        return get_health_status()
    except Exception as e:
        logger.error(f"Status endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Status unavailable")

@router.get("/ping")
def ping():
    """Simple ping endpoint for load balancers"""
    return {"status": "ok", "timestamp": time.time()}
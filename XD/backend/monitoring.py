# -*- coding: utf-8 -*-
"""
Production Monitoring for Farmme API
"""

import time
import logging
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import psutil
import threading

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'farmme_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'farmme_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'farmme_active_connections',
    'Number of active connections'
)

MODEL_PREDICTIONS = Counter(
    'farmme_model_predictions_total',
    'Total number of model predictions',
    ['model_type', 'status']
)

CACHE_OPERATIONS = Counter(
    'farmme_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'status']
)

SYSTEM_CPU_USAGE = Gauge(
    'farmme_system_cpu_usage_percent',
    'System CPU usage percentage'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'farmme_system_memory_usage_percent',
    'System memory usage percentage'
)

DATABASE_CONNECTIONS = Gauge(
    'farmme_database_connections',
    'Number of database connections'
)

class MetricsCollector:
    """Collect system and application metrics"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start metrics collection"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collect_system_metrics)
            self.thread.daemon = True
            self.thread.start()
            logger.info("✅ Metrics collection started")
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("🛑 Metrics collection stopped")
    
    def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while self.running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                SYSTEM_CPU_USAGE.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                SYSTEM_MEMORY_USAGE.set(memory.percent)
                
                # Sleep for 10 seconds before next collection
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(10)

# Global metrics collector
metrics_collector = MetricsCollector()

def record_request_metrics(request: Request, response: Response, process_time: float):
    """Record request metrics"""
    try:
        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(process_time)
        
    except Exception as e:
        logger.error(f"Error recording request metrics: {e}")

def record_model_prediction(model_type: str, success: bool):
    """Record model prediction metrics"""
    try:
        status = "success" if success else "error"
        MODEL_PREDICTIONS.labels(
            model_type=model_type,
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"Error recording model prediction metrics: {e}")

def record_cache_operation(operation: str, success: bool):
    """Record cache operation metrics"""
    try:
        status = "success" if success else "error"
        CACHE_OPERATIONS.labels(
            operation=operation,
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"Error recording cache operation metrics: {e}")

def get_metrics() -> str:
    """Get Prometheus metrics"""
    return generate_latest()

def get_health_status() -> Dict[str, Any]:
    """Get application health status"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application status
        status = {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "application": {
                "uptime_seconds": time.time() - start_time,
                "version": "1.0.0"
            }
        }
        
        # Health checks
        if cpu_percent > 90:
            status["status"] = "warning"
            status["warnings"] = status.get("warnings", [])
            status["warnings"].append("High CPU usage")
        
        if memory.percent > 90:
            status["status"] = "warning" 
            status["warnings"] = status.get("warnings", [])
            status["warnings"].append("High memory usage")
        
        if disk.percent > 90:
            status["status"] = "warning"
            status["warnings"] = status.get("warnings", [])
            status["warnings"].append("High disk usage")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Track application start time
start_time = time.time()

logger.info("📊 Monitoring module loaded")
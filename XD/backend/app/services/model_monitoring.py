"""
Model C v3.1 Monitoring Service
Track model performance, usage, and health metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelMonitoring:
    """Monitor Model C v3.1 performance and usage"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()
        self.prediction_count = 0
        self.error_count = 0
        self.fallback_count = 0
        
        # Performance tracking
        self.response_times = []
        self.confidence_scores = []
        
        # Model version tracking
        self.model_version = None
        self.model_loaded_at = None
        
    def log_model_load(self, version: str, success: bool, load_time: float):
        """Log model loading event"""
        self.model_version = version
        self.model_loaded_at = datetime.now()
        
        logger.info(f"📊 Model Load Event:")
        logger.info(f"   Version: {version}")
        logger.info(f"   Success: {success}")
        logger.info(f"   Load Time: {load_time:.3f}s")
        
        self.metrics['model_loads'].append({
            'timestamp': datetime.now().isoformat(),
            'version': version,
            'success': success,
            'load_time': load_time
        })
    
    def log_prediction(
        self,
        crop_type: str,
        province: str,
        days_ahead: int,
        model_used: str,
        confidence: float,
        response_time: float,
        success: bool
    ):
        """Log prediction event"""
        self.prediction_count += 1
        
        if not success:
            self.error_count += 1
        
        if 'fallback' in model_used.lower():
            self.fallback_count += 1
        
        self.response_times.append(response_time)
        self.confidence_scores.append(confidence)
        
        # Log to file
        logger.info(f"🔮 Prediction Event:")
        logger.info(f"   Crop: {crop_type} in {province}")
        logger.info(f"   Days: {days_ahead}")
        logger.info(f"   Model: {model_used}")
        logger.info(f"   Confidence: {confidence:.2f}")
        logger.info(f"   Response Time: {response_time:.3f}s")
        logger.info(f"   Success: {success}")
        
        # Store metrics
        self.metrics['predictions'].append({
            'timestamp': datetime.now().isoformat(),
            'crop_type': crop_type,
            'province': province,
            'days_ahead': days_ahead,
            'model_used': model_used,
            'confidence': confidence,
            'response_time': response_time,
            'success': success
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict):
        """Log error event"""
        self.error_count += 1
        
        logger.error(f"❌ Error Event:")
        logger.error(f"   Type: {error_type}")
        logger.error(f"   Message: {error_message}")
        logger.error(f"   Context: {context}")
        
        self.metrics['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context
        })
    
    def get_summary(self) -> Dict:
        """Get monitoring summary"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate statistics
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0
        
        # Calculate percentiles
        if self.response_times:
            sorted_times = sorted(self.response_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            p50 = p95 = p99 = 0
        
        # Calculate rates
        error_rate = (self.error_count / self.prediction_count * 100) if self.prediction_count > 0 else 0
        fallback_rate = (self.fallback_count / self.prediction_count * 100) if self.prediction_count > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'model_version': self.model_version,
            'model_loaded_at': self.model_loaded_at.isoformat() if self.model_loaded_at else None,
            'predictions': {
                'total': self.prediction_count,
                'errors': self.error_count,
                'fallbacks': self.fallback_count,
                'error_rate': round(error_rate, 2),
                'fallback_rate': round(fallback_rate, 2)
            },
            'performance': {
                'avg_response_time': round(avg_response_time, 3),
                'p50_response_time': round(p50, 3),
                'p95_response_time': round(p95, 3),
                'p99_response_time': round(p99, 3),
                'avg_confidence': round(avg_confidence, 2)
            }
        }
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Get recent predictions"""
        predictions = self.metrics.get('predictions', [])
        return predictions[-limit:]
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Get recent errors"""
        errors = self.metrics.get('errors', [])
        return errors[-limit:]
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'summary': self.get_summary(),
                    'metrics': dict(self.metrics)
                }, f, indent=2)
            
            logger.info(f"✅ Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to export metrics: {e}")
    
    def check_health(self) -> Dict:
        """Check system health"""
        summary = self.get_summary()
        
        # Health checks
        checks = {
            'model_loaded': self.model_version is not None,
            'error_rate_ok': summary['predictions']['error_rate'] < 5.0,
            'fallback_rate_ok': summary['predictions']['fallback_rate'] < 20.0,
            'response_time_ok': summary['performance']['avg_response_time'] < 1.0,
            'confidence_ok': summary['performance']['avg_confidence'] > 0.7
        }
        
        # Overall health
        all_healthy = all(checks.values())
        
        return {
            'healthy': all_healthy,
            'checks': checks,
            'summary': summary
        }


# Global instance
model_monitoring = ModelMonitoring()


# Decorator for monitoring predictions
def monitor_prediction(func):
    """Decorator to monitor prediction functions"""
    import time
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Extract info from result
            model_used = result.get('model_used', 'unknown')
            confidence = result.get('confidence_score', 0.0)
            success = result.get('success', False)
            
            # Extract request info from kwargs
            request = kwargs.get('request')
            if request:
                model_monitoring.log_prediction(
                    crop_type=request.crop_type,
                    province=request.province,
                    days_ahead=request.days_ahead,
                    model_used=model_used,
                    confidence=confidence,
                    response_time=response_time,
                    success=success
                )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            model_monitoring.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={'args': str(args), 'kwargs': str(kwargs)}
            )
            
            raise
    
    return wrapper


if __name__ == "__main__":
    # Test monitoring
    print("Testing Model Monitoring...")
    
    # Simulate model load
    model_monitoring.log_model_load("3.1_seasonal_aware_retrained", True, 1.2)
    
    # Simulate predictions
    model_monitoring.log_prediction(
        crop_type="มะเขือเทศ",
        province="เชียงใหม่",
        days_ahead=30,
        model_used="model_c",
        confidence=0.85,
        response_time=0.15,
        success=True
    )
    
    model_monitoring.log_prediction(
        crop_type="ข้าว",
        province="สุพรรณบุรี",
        days_ahead=90,
        model_used="fallback",
        confidence=0.60,
        response_time=0.08,
        success=True
    )
    
    # Get summary
    summary = model_monitoring.get_summary()
    print("\nMonitoring Summary:")
    print(json.dumps(summary, indent=2))
    
    # Check health
    health = model_monitoring.check_health()
    print("\nHealth Check:")
    print(json.dumps(health, indent=2))

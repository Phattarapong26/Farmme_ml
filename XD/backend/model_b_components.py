# -*- coding: utf-8 -*-
"""
Model B Components
WeatherDataCache, ModelLoader, and FallbackManager
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from model_b_core import (
    ModelBConfig,
    WeatherDataLoadError,
    WeatherDataNotFoundError,
    ModelLoadError
)

logger = logging.getLogger(__name__)


# ============================================================================
# Weather Data Cache
# ============================================================================

class WeatherDataCache:
    """Cache weather data for fast access"""
    
    def __init__(self, weather_csv_path: Path, config: ModelBConfig = None):
        self.weather_csv_path = weather_csv_path
        self.config = config or ModelBConfig()
        
        # Caches
        self._cache: Dict[str, pd.DataFrame] = {}  # province -> dataframe
        self._monthly_cache: Dict[Tuple[str, int], Dict] = {}  # (province, month) -> weather dict
        self._loaded = False
        self._df: Optional[pd.DataFrame] = None
    
    def load(self) -> bool:
        """
        Load weather data from CSV
        
        Returns:
            True if loaded successfully
        """
        try:
            if not self.weather_csv_path.exists():
                logger.warning(f"Weather data file not found: {self.weather_csv_path}")
                return False
            
            # Load CSV
            self._df = pd.read_csv(self.weather_csv_path, parse_dates=['date'])
            logger.info(f"✅ Loaded weather data: {len(self._df)} records from {self.weather_csv_path}")
            
            # Pre-cache by province
            for province in self._df['province'].unique():
                province_data = self._df[self._df['province'] == province].copy()
                province_data['date'] = pd.to_datetime(province_data['date'])
                province_data = province_data.sort_values('date')
                self._cache[province] = province_data
            
            logger.info(f"   Cached {len(self._cache)} provinces")
            self._loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load weather data: {e}")
            self._loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if weather data is loaded"""
        return self._loaded
    
    def get_weather(
        self,
        province: str,
        date: pd.Timestamp,
        use_historical: bool = False
    ) -> Optional[Dict[str, float]]:
        """
        Get weather data for province and date
        
        Args:
            province: Province name (normalized)
            date: Target date
            use_historical: Use monthly average if True
        
        Returns:
            Dict with temperature, rainfall, humidity, drought_index, data_type
        """
        if not self._loaded:
            logger.warning("Weather data not loaded")
            return None
        
        # Get province data from cache
        if province not in self._cache:
            logger.warning(f"No weather data for province: {province}")
            return None
        
        province_data = self._cache[province]
        
        # If use_historical or date is in future, use monthly average
        if use_historical or date > pd.Timestamp.now():
            return self._get_monthly_average(province, date.month)
        
        # Try exact date match
        date_str = date.strftime('%Y-%m-%d')
        exact_match = province_data[province_data['date'] == date_str]
        
        if len(exact_match) > 0:
            row = exact_match.iloc[0]
            return {
                'temperature': float(row['temperature_celsius']),
                'rainfall': float(row['rainfall_mm']),
                'humidity': float(row['humidity_percent']),
                'drought_index': float(row['drought_index']),
                'data_type': 'actual'
            }
        
        # Fall back to recent average (past 7 days)
        past_data = province_data[province_data['date'] <= date].tail(7)
        
        if len(past_data) > 0:
            return {
                'temperature': float(past_data['temperature_celsius'].mean()),
                'rainfall': float(past_data['rainfall_mm'].mean()),
                'humidity': float(past_data['humidity_percent'].mean()),
                'drought_index': float(past_data['drought_index'].mean()),
                'data_type': 'recent_average'
            }
        
        # No data available
        return None
    
    def _get_monthly_average(self, province: str, month: int) -> Optional[Dict]:
        """
        Get cached monthly average
        
        Args:
            province: Province name
            month: Month number (1-12)
        
        Returns:
            Weather dict or None
        """
        cache_key = (province, month)
        
        # Check cache
        if cache_key in self._monthly_cache:
            return self._monthly_cache[cache_key]
        
        # Calculate and cache
        result = self._calculate_monthly_average(province, month)
        if result:
            self._monthly_cache[cache_key] = result
        
        return result
    
    def _calculate_monthly_average(self, province: str, month: int) -> Optional[Dict]:
        """
        Calculate monthly average from historical data
        
        Args:
            province: Province name
            month: Month number (1-12)
        
        Returns:
            Weather dict or None
        """
        if province not in self._cache:
            return None
        
        province_data = self._cache[province].copy()
        province_data['month'] = province_data['date'].dt.month
        month_data = province_data[province_data['month'] == month]
        
        if len(month_data) == 0:
            return None
        
        return {
            'temperature': float(month_data['temperature_celsius'].mean()),
            'rainfall': float(month_data['rainfall_mm'].mean()),
            'humidity': float(month_data['humidity_percent'].mean()),
            'drought_index': float(month_data['drought_index'].mean()),
            'data_type': 'historical_average'
        }
    
    def get_provinces(self) -> List[str]:
        """Get list of available provinces"""
        return list(self._cache.keys())


# ============================================================================
# Model Loader
# ============================================================================

class ModelLoader:
    """Load ML models with fallback"""
    
    MODEL_PRIORITY = [
        ("model_b_logistic.pkl", "gradboost"),  # Deployed model
        ("model_b_gradboost_full.pkl", "gradboost"),
        ("model_b_xgboost_full.pkl", "xgboost"),
        ("model_b_random_forest_full.pkl", "random_forest"),
    ]
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.model_type = None
        self.model_path = None
        self._loaded = False
    
    def load(self) -> bool:
        """
        Load model with priority order
        
        Returns:
            True if model loaded successfully
        """
        for model_file, model_type in self.MODEL_PRIORITY:
            model_path = self.models_dir / model_file
            
            if not model_path.exists():
                continue
            
            try:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                # Extract model and scaler
                if isinstance(model_data, dict):
                    self.model = model_data.get('model')
                    self.scaler = model_data.get('scaler')
                else:
                    self.model = model_data
                    self.scaler = None
                
                self.model_path = model_path
                self.model_type = model_type
                self._loaded = True
                
                # Log success
                model_class = type(self.model).__name__
                logger.info(f"✅ Model B loaded from: {model_path.name}")
                logger.info(f"   Model type: {model_class}")
                logger.info(f"   Labeled as: {model_type}")
                
                return True
                
            except Exception as e:
                logger.warning(f"Failed to load {model_file}: {e}")
                continue
        
        logger.warning("⚠️ Model B not found, will use fallback")
        self._loaded = False
        return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded and self.model is not None
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        if not self._loaded:
            return {
                'loaded': False,
                'model_type': None,
                'model_path': None
            }
        
        return {
            'loaded': True,
            'model_type': self.model_type,
            'model_path': str(self.model_path) if self.model_path else None,
            'model_class': type(self.model).__name__ if self.model else None,
            'has_scaler': self.scaler is not None
        }


# ============================================================================
# Fallback Manager
# ============================================================================

class FallbackManager:
    """Manage fallback usage and rate limiting"""
    
    def __init__(self, config: ModelBConfig = None):
        self.config = config or ModelBConfig()
        self._fallback_history: List[Tuple[datetime, str]] = []  # (timestamp, method)
    
    def should_allow_fallback(self) -> bool:
        """
        Check if fallback is allowed (rate limit)
        
        Returns:
            True if fallback is allowed
        """
        self._cleanup_old_records()
        
        # Count fallbacks in last minute
        recent_count = len(self._fallback_history)
        
        if recent_count >= self.config.MAX_FALLBACKS_PER_MINUTE:
            logger.warning(f"Fallback rate limit exceeded: {recent_count} fallbacks in last minute")
            return False
        
        return True
    
    def record_fallback(self, method: str):
        """
        Record fallback usage
        
        Args:
            method: Fallback method used (e.g., "weather_based", "rule_based")
        """
        self._fallback_history.append((datetime.now(), method))
        logger.info(f"Fallback recorded: {method}")
    
    def get_stats(self) -> Dict:
        """
        Get fallback statistics
        
        Returns:
            Dict with fallback stats
        """
        self._cleanup_old_records()
        
        # Count by method
        method_counts = {}
        for _, method in self._fallback_history:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        return {
            'total_fallbacks_last_minute': len(self._fallback_history),
            'by_method': method_counts,
            'rate_limit': self.config.MAX_FALLBACKS_PER_MINUTE,
            'is_limited': len(self._fallback_history) >= self.config.MAX_FALLBACKS_PER_MINUTE
        }
    
    def _cleanup_old_records(self):
        """Remove records older than 1 minute"""
        cutoff = datetime.now() - timedelta(minutes=1)
        self._fallback_history = [
            (ts, method) for ts, method in self._fallback_history
            if ts > cutoff
        ]

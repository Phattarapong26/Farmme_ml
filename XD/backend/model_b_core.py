# -*- coding: utf-8 -*-
"""
Model B Core Components
Production-ready components for Model B Wrapper
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum
import numpy as np


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class PredictionResult:
    """Result from prediction engine"""
    is_good_window: bool
    confidence: float
    probability_good: float
    probability_bad: float
    method_used: str  # "ml_model", "weather_based", "rule_based"
    reasons: List[str]
    raw_prediction: Optional[int] = None
    raw_probability: Optional[np.ndarray] = None


# ============================================================================
# Error Hierarchy
# ============================================================================

class ModelBError(Exception):
    """Base exception for Model B Wrapper"""
    pass


class ValidationError(ModelBError):
    """Base validation error"""
    pass


class InvalidDateError(ValidationError):
    """Invalid date format or value"""
    pass


class InvalidProvinceError(ValidationError):
    """Invalid province name"""
    pass


class InvalidSoilParamsError(ValidationError):
    """Invalid soil parameters"""
    pass


class MissingParameterError(ValidationError):
    """Required parameter is missing"""
    pass


class ModelError(ModelBError):
    """Base model error"""
    pass


class ModelLoadError(ModelError):
    """Failed to load model"""
    pass


class ModelPredictionError(ModelError):
    """Failed to make prediction"""
    pass


class FeatureEngineeringError(ModelError):
    """Failed to engineer features"""
    pass


class DataError(ModelBError):
    """Base data error"""
    pass


class WeatherDataNotFoundError(DataError):
    """Weather data not found for province/date"""
    pass


class WeatherDataLoadError(DataError):
    """Failed to load weather data"""
    pass


class FallbackError(ModelBError):
    """Base fallback error"""
    pass


class FallbackRateLimitError(FallbackError):
    """Fallback rate limit exceeded"""
    pass


# ============================================================================
# Configuration
# ============================================================================

class ModelBConfig:
    """Configuration for Model B Wrapper"""
    
    # Version
    MODEL_VERSION = "2.0.0"
    
    # Paths (will be set dynamically)
    MODELS_DIR = None
    WEATHER_CSV = None
    
    # Performance
    CACHE_SIZE = 100
    PREDICTION_TIMEOUT = 5.0  # seconds
    
    # Fallback
    MAX_FALLBACKS_PER_MINUTE = 3
    FALLBACK_CONFIDENCE_PENALTY = 0.10
    
    # Confidence thresholds
    ML_MODEL_CONFIDENCE = 0.85
    WEATHER_BASED_CONFIDENCE = 0.75
    RULE_BASED_CONFIDENCE = 0.65
    LOW_CONFIDENCE_THRESHOLD = 0.70
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Province aliases
    PROVINCE_ALIASES = {
        # Thai short forms
        'กรุงเทพ': 'กรุงเทพมหานคร',
        'กทม': 'กรุงเทพมหานคร',
        'กทม.': 'กรุงเทพมหานคร',
        
        # English names
        'Bangkok': 'กรุงเทพมหานคร',
        'Nakhon Pathom': 'นครปฐม',
        'Samut Prakan': 'สมุทรปราการ',
        'Nonthaburi': 'นนทบุรี',
        'Pathum Thani': 'ปทุมธานี',
        'Samut Sakhon': 'สมุทรสาคร',
        
        # Common variations
        'นครปฐม': 'Nakhon Pathom',
        'สมุทรปราการ': 'Samut Prakan',
        'นนทบุรี': 'Nonthaburi',
        'ปทุมธานี': 'Pathum Thani',
        'สมุทรสาคร': 'Samut Sakhon',
    }
    
    # Validation ranges
    SOIL_PH_MIN = 0.0
    SOIL_PH_MAX = 14.0
    SOIL_NUTRIENTS_MIN = 0.0
    DAYS_TO_MATURITY_MIN = 30
    DAYS_TO_MATURITY_MAX = 365
    
    # Weather thresholds
    TEMP_MIN_GOOD = 20.0
    TEMP_MAX_GOOD = 30.0
    TEMP_MIN_ACCEPTABLE = 15.0
    TEMP_MAX_ACCEPTABLE = 36.0
    
    RAINFALL_MIN_GOOD = 10.0
    RAINFALL_MAX_GOOD = 50.0
    RAINFALL_MAX_ACCEPTABLE = 100.0
    RAINFALL_MIN_DRY = 5.0
    
    HUMIDITY_MIN_GOOD = 60.0
    HUMIDITY_MAX_GOOD = 80.0
    HUMIDITY_MIN_ACCEPTABLE = 50.0
    HUMIDITY_MAX_ACCEPTABLE = 90.0
    
    DROUGHT_INDEX_MAX_ACCEPTABLE = 100.0
    DROUGHT_INDEX_MAX_SEVERE = 120.0
    
    # Season definitions
    WINTER_MONTHS = [11, 12, 1, 2]
    SUMMER_MONTHS = [3, 4, 5]
    RAINY_MONTHS = [6, 7, 8, 9, 10]
    
    # Thai month names
    THAI_MONTHS = {
        1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม",
        4: "เมษายน", 5: "พฤษภาคม", 6: "มิถุนายน",
        7: "กรกฎาคม", 8: "สิงหาคม", 9: "กันยายน",
        10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
    }
    
    @classmethod
    def get_thai_month(cls, month: int) -> str:
        """Get Thai month name"""
        return cls.THAI_MONTHS.get(month, "")
    
    @classmethod
    def get_season(cls, month: int) -> str:
        """Get season from month"""
        if month in cls.WINTER_MONTHS:
            return "Winter"
        elif month in cls.SUMMER_MONTHS:
            return "Summer"
        else:
            return "Rainy"
    
    @classmethod
    def normalize_province(cls, province: str) -> str:
        """Normalize province name using aliases"""
        if not province:
            return province
        
        # Try exact match first
        if province in cls.PROVINCE_ALIASES:
            return cls.PROVINCE_ALIASES[province]
        
        # Try case-insensitive match
        province_lower = province.lower()
        for alias, normalized in cls.PROVINCE_ALIASES.items():
            if alias.lower() == province_lower:
                return normalized
        
        # Return original if no match
        return province

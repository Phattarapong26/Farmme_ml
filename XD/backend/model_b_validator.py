# -*- coding: utf-8 -*-
"""
Model B Input Validator
Validates and normalizes all inputs for Model B predictions
"""

import logging
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from datetime import datetime

from model_b_core import (
    ModelBConfig,
    InvalidDateError,
    InvalidProvinceError,
    InvalidSoilParamsError,
    MissingParameterError
)

logger = logging.getLogger(__name__)


class InputValidator:
    """Validate and normalize all inputs for Model B"""
    
    def __init__(self, config: ModelBConfig = None):
        self.config = config or ModelBConfig()
    
    def validate_prediction_input(
        self,
        planting_date: str,
        province: str,
        soil_type: Optional[str] = None,
        soil_ph: Optional[float] = None,
        soil_nutrients: Optional[float] = None,
        days_to_maturity: Optional[int] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate all inputs for prediction
        
        Args:
            planting_date: Date string (YYYY-MM-DD)
            province: Province name
            soil_type: Soil type (optional)
            soil_ph: Soil pH 0-14 (optional)
            soil_nutrients: Soil nutrients >=0 (optional)
            days_to_maturity: Days to maturity 30-365 (optional)
        
        Returns:
            (is_valid, normalized_params, error_message)
        """
        try:
            # Check required parameters
            if not planting_date:
                return False, None, "Missing required parameter: planting_date"
            if not province:
                return False, None, "Missing required parameter: province"
            
            # Validate date
            is_valid, parsed_date, error = self.validate_date(planting_date)
            if not is_valid:
                return False, None, error
            
            # Normalize province
            normalized_province = self.normalize_province(province)
            if not normalized_province:
                return False, None, f"Invalid province: {province}"
            
            # Validate soil parameters
            is_valid, error = self.validate_soil_params(soil_ph, soil_nutrients)
            if not is_valid:
                return False, None, error
            
            # Validate days to maturity
            if days_to_maturity is not None:
                is_valid, error = self.validate_days_to_maturity(days_to_maturity)
                if not is_valid:
                    return False, None, error
            
            # Build normalized parameters
            normalized_params = {
                'planting_date': parsed_date,
                'province': normalized_province,
                'soil_type': soil_type,
                'soil_ph': soil_ph,
                'soil_nutrients': soil_nutrients,
                'days_to_maturity': days_to_maturity
            }
            
            return True, normalized_params, None
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, None, f"Validation failed: {str(e)}"
    
    def validate_date(self, date_str: str) -> Tuple[bool, Optional[pd.Timestamp], Optional[str]]:
        """
        Validate date format and parse
        
        Args:
            date_str: Date string
        
        Returns:
            (is_valid, parsed_date, error_message)
        """
        try:
            # Try to parse date
            parsed_date = pd.to_datetime(date_str)
            
            # Check if date is reasonable (not too far in past or future)
            now = pd.Timestamp.now()
            min_date = now - pd.DateOffset(years=10)
            max_date = now + pd.DateOffset(years=5)
            
            if parsed_date < min_date:
                return False, None, f"Date too far in the past: {date_str}"
            if parsed_date > max_date:
                return False, None, f"Date too far in the future: {date_str}"
            
            return True, parsed_date, None
            
        except ValueError as e:
            return False, None, f"Invalid date format. Expected YYYY-MM-DD, got '{date_str}'"
        except Exception as e:
            return False, None, f"Date parsing error: {str(e)}"
    
    def validate_soil_params(
        self,
        soil_ph: Optional[float],
        soil_nutrients: Optional[float]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate soil parameters
        
        Args:
            soil_ph: Soil pH (optional)
            soil_nutrients: Soil nutrients (optional)
        
        Returns:
            (is_valid, error_message)
        """
        # Validate soil pH
        if soil_ph is not None:
            if not isinstance(soil_ph, (int, float)):
                return False, f"Invalid soil_ph type. Expected number, got {type(soil_ph).__name__}"
            
            if soil_ph < self.config.SOIL_PH_MIN or soil_ph > self.config.SOIL_PH_MAX:
                return False, f"Invalid soil_ph. Must be between {self.config.SOIL_PH_MIN} and {self.config.SOIL_PH_MAX}, got {soil_ph}"
        
        # Validate soil nutrients
        if soil_nutrients is not None:
            if not isinstance(soil_nutrients, (int, float)):
                return False, f"Invalid soil_nutrients type. Expected number, got {type(soil_nutrients).__name__}"
            
            if soil_nutrients < self.config.SOIL_NUTRIENTS_MIN:
                return False, f"Invalid soil_nutrients. Must be non-negative, got {soil_nutrients}"
        
        return True, None
    
    def validate_days_to_maturity(self, days: int) -> Tuple[bool, Optional[str]]:
        """
        Validate days to maturity
        
        Args:
            days: Days to maturity
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(days, int):
            return False, f"Invalid days_to_maturity type. Expected integer, got {type(days).__name__}"
        
        if days < self.config.DAYS_TO_MATURITY_MIN or days > self.config.DAYS_TO_MATURITY_MAX:
            return False, f"Invalid days_to_maturity. Must be between {self.config.DAYS_TO_MATURITY_MIN} and {self.config.DAYS_TO_MATURITY_MAX}, got {days}"
        
        return True, None
    
    def normalize_province(self, province: str) -> str:
        """
        Normalize province name using alias mapping
        
        Args:
            province: Province name (Thai or English)
        
        Returns:
            Normalized province name
        """
        if not province:
            return province
        
        # Use config's normalize method
        normalized = self.config.normalize_province(province)
        
        # Log if normalization occurred
        if normalized != province:
            logger.debug(f"Province normalized: '{province}' -> '{normalized}'")
        
        return normalized
    
    def validate_calendar_input(
        self,
        province: str,
        crop_type: str = "พริก",
        months_ahead: int = 12,
        soil_type: Optional[str] = None,
        soil_ph: Optional[float] = None,
        soil_nutrients: Optional[float] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate inputs for planting calendar
        
        Args:
            province: Province name
            crop_type: Crop type
            months_ahead: Number of months to analyze (1-24)
            soil_type: Soil type (optional)
            soil_ph: Soil pH (optional)
            soil_nutrients: Soil nutrients (optional)
        
        Returns:
            (is_valid, normalized_params, error_message)
        """
        try:
            # Check required parameters
            if not province:
                return False, None, "Missing required parameter: province"
            
            # Normalize province
            normalized_province = self.normalize_province(province)
            if not normalized_province:
                return False, None, f"Invalid province: {province}"
            
            # Validate months_ahead
            if not isinstance(months_ahead, int):
                return False, None, f"Invalid months_ahead type. Expected integer, got {type(months_ahead).__name__}"
            
            if months_ahead < 1 or months_ahead > 24:
                return False, None, f"Invalid months_ahead. Must be between 1 and 24, got {months_ahead}"
            
            # Validate soil parameters
            is_valid, error = self.validate_soil_params(soil_ph, soil_nutrients)
            if not is_valid:
                return False, None, error
            
            # Build normalized parameters
            normalized_params = {
                'province': normalized_province,
                'crop_type': crop_type,
                'months_ahead': months_ahead,
                'soil_type': soil_type,
                'soil_ph': soil_ph,
                'soil_nutrients': soil_nutrients
            }
            
            return True, normalized_params, None
            
        except Exception as e:
            logger.error(f"Calendar validation error: {e}")
            return False, None, f"Validation failed: {str(e)}"

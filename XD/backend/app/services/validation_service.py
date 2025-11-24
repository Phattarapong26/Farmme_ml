# -*- coding: utf-8 -*-
"""
Validation Service for User Profile Data
Ensures data compatibility with ML models
"""

from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Valid values that match ML model requirements
VALID_VALUES = {
    'soil_type': ['ดินร่วน', 'ดินร่วนปนทราย', 'ดินเหนียว', 'ดินทราย'],
    'water_availability': ['สูง', 'ปานกลาง', 'ต่ำ'],
    'budget_level': ['สูง', 'ปานกลาง', 'ต่ำ'],
    'risk_tolerance': ['สูง', 'ปานกลาง', 'ต่ำ']
}


def validate_province(province: str, db: Session) -> bool:
    """
    Validate that province exists in database
    
    Args:
        province: Province name in Thai
        db: Database session
        
    Returns:
        True if province exists, False otherwise
    """
    if not province:
        return True  # Optional field
    
    try:
        from sqlalchemy import text
        
        # First check if database has any provinces
        count_query = text("""
            SELECT COUNT(DISTINCT province) 
            FROM (
                SELECT province FROM crop_prices
                UNION
                SELECT province FROM weather_data
                UNION
                SELECT province FROM crop_cultivation
            ) AS all_provinces
        """)
        
        count_result = db.execute(count_query).fetchone()
        province_count = count_result[0] if count_result else 0
        
        # If database is empty, allow any province (development mode)
        if province_count == 0:
            logger.info(f"Province validation skipped - database is empty (development mode)")
            return True
        
        # Query all unique provinces from multiple tables
        query = text("""
            SELECT DISTINCT province 
            FROM (
                SELECT province FROM crop_prices
                UNION
                SELECT province FROM weather_data
                UNION
                SELECT province FROM crop_cultivation
            ) AS all_provinces
            WHERE province = :province
            LIMIT 1
        """)
        
        result = db.execute(query, {"province": province}).fetchone()
        return result is not None
        
    except Exception as e:
        logger.error(f"Error validating province: {e}")
        return False


def validate_soil_type(soil_type: str) -> bool:
    """
    Validate soil type matches ML model values
    
    Args:
        soil_type: Soil type in Thai
        
    Returns:
        True if valid, False otherwise
    """
    if not soil_type:
        return True  # Optional field
    
    return soil_type in VALID_VALUES['soil_type']


def validate_water_availability(water: str) -> bool:
    """
    Validate water availability matches ML model values
    
    Args:
        water: Water availability level
        
    Returns:
        True if valid, False otherwise
    """
    if not water:
        return True  # Optional field
    
    return water in VALID_VALUES['water_availability']


def validate_budget_level(budget: str) -> bool:
    """
    Validate budget level matches ML model values
    
    Args:
        budget: Budget level
        
    Returns:
        True if valid, False otherwise
    """
    if not budget:
        return True  # Optional field
    
    return budget in VALID_VALUES['budget_level']


def validate_risk_tolerance(risk: str) -> bool:
    """
    Validate risk tolerance matches ML model values
    
    Args:
        risk: Risk tolerance level
        
    Returns:
        True if valid, False otherwise
    """
    if not risk:
        return True  # Optional field
    
    return risk in VALID_VALUES['risk_tolerance']


def validate_user_profile(profile_data: dict, db: Session) -> Tuple[bool, List[str]]:
    """
    Validate complete user profile data
    
    Args:
        profile_data: Dictionary containing user profile fields
        db: Database session
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate province
    province = profile_data.get('province')
    if province and not validate_province(province, db):
        errors.append(f"จังหวัด '{province}' ไม่มีในระบบ")
    
    # Validate soil type
    soil_type = profile_data.get('soil_type')
    if soil_type and not validate_soil_type(soil_type):
        valid_types = ', '.join(VALID_VALUES['soil_type'])
        errors.append(f"ประเภทดินไม่ถูกต้อง กรุณาเลือก: {valid_types}")
    
    # Validate water availability
    water = profile_data.get('water_availability')
    if water and not validate_water_availability(water):
        valid_levels = ', '.join(VALID_VALUES['water_availability'])
        errors.append(f"ระดับแหล่งน้ำไม่ถูกต้อง กรุณาเลือก: {valid_levels}")
    
    # Validate budget level
    budget = profile_data.get('budget_level')
    if budget and not validate_budget_level(budget):
        valid_levels = ', '.join(VALID_VALUES['budget_level'])
        errors.append(f"ระดับงบประมาณไม่ถูกต้อง กรุณาเลือก: {valid_levels}")
    
    # Validate risk tolerance
    risk = profile_data.get('risk_tolerance')
    if risk and not validate_risk_tolerance(risk):
        valid_levels = ', '.join(VALID_VALUES['risk_tolerance'])
        errors.append(f"ระดับความเสี่ยงไม่ถูกต้อง กรุณาเลือก: {valid_levels}")
    
    is_valid = len(errors) == 0
    
    if not is_valid:
        logger.warning(f"Profile validation failed: {errors}")
    
    return is_valid, errors


def get_valid_values() -> dict:
    """
    Get dictionary of all valid values for profile fields
    
    Returns:
        Dictionary with valid values for each field
    """
    return VALID_VALUES.copy()

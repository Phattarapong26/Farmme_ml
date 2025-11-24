# -*- coding: utf-8 -*-
"""
Dashboard API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import logging
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from app.services.dashboard_service import get_dashboard_overview
from app.utils.redis_client import cache_get, cache_set

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_dashboard_overview_endpoint(
    province: str = Query(..., description="Province name"),
    days_back: int = Query(30, description="Number of days for historical data"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data for a province with Redis caching
    
    Parameters:
    - province: Province name (required)
    - days_back: Number of days to look back for historical data (default: 30)
    
    Returns:
    - Comprehensive dashboard data including statistics, price history, weather data, and crop distribution
    """
    try:
        # Generate cache key
        cache_key = f"dashboard:overview:{province}:{days_back}"
        
        # Try to get from cache
        cached_data = cache_get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for dashboard overview: {province}")
            cached_data["cached"] = True
            return cached_data
        
        # Cache miss - fetch from database
        logger.info(f"Cache miss for dashboard overview: {province}")
        data = get_dashboard_overview(db, province, days_back)
        
        # Store in cache with 5 minute TTL
        cache_set(cache_key, data, ttl=300)
        
        return data
        
    except Exception as e:
        logger.error(f"Error in dashboard overview endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard data: {str(e)}"
        )


@router.get("/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """
    Get list of all available provinces
    
    Returns:
    - List of province names
    """
    try:
        from sqlalchemy import text, distinct
        from database import CropPrice
        
        # Get unique provinces from crop_prices table
        provinces = db.query(distinct(CropPrice.province)).order_by(CropPrice.province).all()
        
        return {
            "success": True,
            "provinces": [p[0] for p in provinces if p[0]]
        }
    except Exception as e:
        logger.error(f"Error fetching provinces: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch provinces: {str(e)}"
        )

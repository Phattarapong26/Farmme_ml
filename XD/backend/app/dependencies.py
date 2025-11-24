# -*- coding: utf-8 -*-
"""
Dependencies for FastAPI endpoints
"""

from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from cache import cache
from model_registry import model_registry
from unified_model_service import unified_model_service

# Database dependency
def get_database() -> Session:
    """Get database session"""
    return next(get_db())

# Cache dependency
def get_cache():
    """Get cache instance"""
    return cache

# Model services
def get_unified_model_service():
    """Get unified model service"""
    return unified_model_service

def get_model_registry():
    """Get model registry"""
    return model_registry
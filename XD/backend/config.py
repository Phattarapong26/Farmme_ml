# -*- coding: utf-8 -*-
"""
Configuration for Farmme API - Production Ready
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# Load environment variables from .env file in backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

logger = logging.getLogger(__name__)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# API Keys with validation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "mock-api-key":
    if ENVIRONMENT == "production":
        raise ValueError("GEMINI_API_KEY is required in production")
    else:
        GEMINI_API_KEY = "mock-api-key"
        logger.warning("⚠️ Using mock Gemini API key in development")

# App Configuration
APP_TITLE = "Farmme API"
APP_DESCRIPTION = "Smart Farming Recommendation System"
APP_VERSION = "1.0.0"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
if SECRET_KEY == "dev-secret-key-change-in-production" and ENVIRONMENT == "production":
    raise ValueError("SECRET_KEY must be set in production")

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:3000", 
    "http://localhost:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://phattarapong26.github.io",  # GitHub Pages
]

# Add production origins if specified
PRODUCTION_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if PRODUCTION_ORIGINS and PRODUCTION_ORIGINS[0]:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in PRODUCTION_ORIGINS])

# Redis Configuration with validation
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = True

try:
    import redis
    # Test Redis connection
    r = redis.from_url(REDIS_URL)
    r.ping()
    logger.info("✅ Redis connection successful")
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
    REDIS_ENABLED = False

# Cache TTL (Time To Live) in seconds
CACHE_TTL_PREDICTIONS = int(os.getenv("CACHE_TTL_PREDICTIONS", "3600"))  # 1 hour
CACHE_TTL_RECOMMENDATIONS = int(os.getenv("CACHE_TTL_RECOMMENDATIONS", "1800"))  # 30 minutes

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./farmme_mock.db")

# ML Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/")
DEFAULT_MODEL_VERSION = os.getenv("DEFAULT_MODEL_VERSION", "1.0.0")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Health Check Configuration
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "30"))

# Model Service Configuration
MODEL_TIMEOUT = int(os.getenv("MODEL_TIMEOUT", "30"))  # seconds
MODEL_RETRY_ATTEMPTS = int(os.getenv("MODEL_RETRY_ATTEMPTS", "3"))

logger.info(f"✅ Configuration loaded for environment: {ENVIRONMENT}")
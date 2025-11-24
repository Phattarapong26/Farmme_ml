# -*- coding: utf-8 -*-
"""
Production Logging Configuration for Farmme API
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from config import LOG_LEVEL, ENVIRONMENT

def setup_logging():
    """Setup production-ready logging configuration"""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    if ENVIRONMENT == "production":
        console_handler.setFormatter(simple_formatter)
    else:
        console_handler.setFormatter(detailed_formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handlers for production
    if ENVIRONMENT == "production":
        # Main application log
        file_handler = logging.handlers.RotatingFileHandler(
            "logs/farmme_api.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            "logs/farmme_errors.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Access log for uvicorn
        access_handler = logging.handlers.RotatingFileHandler(
            "logs/farmme_access.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(simple_formatter)
        
        # Configure uvicorn access logger
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.handlers = [access_handler]
        uvicorn_access.propagate = False
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": logging.INFO,
        "uvicorn.error": logging.INFO,
        "fastapi": logging.INFO,
        "sqlalchemy.engine": logging.WARNING,  # Reduce SQL query noise
        "redis": logging.WARNING,
        "httpx": logging.WARNING,
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging configured for {ENVIRONMENT} environment")
    logger.info(f"Log level: {LOG_LEVEL}")
    
    return root_logger

# Setup logging when module is imported
setup_logging()
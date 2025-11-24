# -*- coding: utf-8 -*-
"""
Database Module for Farmme API - Production Ready
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Generator
import logging
import os

# Import config
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Production-ready SQLAlchemy setup with connection pooling - PostgreSQL only
def create_database_engine():
    """Create PostgreSQL database engine with production-ready configuration"""
    try:
        # Validate PostgreSQL URL
        if "postgresql" not in DATABASE_URL:
            raise ValueError(
                f"❌ Invalid DATABASE_URL: PostgreSQL is required. "
                f"Current URL does not contain 'postgresql'. "
                f"Please set DATABASE_URL environment variable to a valid PostgreSQL connection string."
            )
        
        # PostgreSQL production configuration
        # Optimized for cloud database (Supabase)
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,           # Reduced for cloud database
            max_overflow=20,        # Reduced for cloud database
            pool_pre_ping=True,     # Keep for connection health checks
            pool_recycle=3600,      # Recycle connections every hour
            echo=False,             # Set to True for debugging
            connect_args={
                "connect_timeout": 30,  # Increased for cloud latency
                "application_name": "farmme_api"
            }
        )
        logger.info("✅ PostgreSQL engine configured with connection pooling")
        
        # Test connection
        with engine.connect() as conn:
            logger.info("✅ PostgreSQL connection test successful")
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL database engine creation failed: {e}")
        logger.error("💡 Please ensure:")
        logger.error("   1. PostgreSQL server is running")
        logger.error("   2. DATABASE_URL environment variable is set correctly")
        logger.error("   3. Database credentials are valid")
        logger.error("   4. Network connectivity to database server")
        raise RuntimeError(f"Failed to connect to PostgreSQL database: {e}") from e

engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Profile fields
    province = Column(String)
    water_availability = Column(String)
    budget_level = Column(String)
    experience_crops = Column(Text)  # JSON string
    risk_tolerance = Column(String)
    time_constraint = Column(Integer)
    preference = Column(String)
    soil_type = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CropPrediction(Base):
    __tablename__ = "crop_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, index=True)
    crop_type = Column(String, index=True)
    province = Column(String, index=True)
    predicted_price = Column(Float)
    confidence = Column(Float)
    
    # Legacy fields for compatibility
    price_history = Column(Text)  # JSON string
    weather_data = Column(Text)   # JSON string
    crop_info = Column(Text)      # JSON string
    calendar_data = Column(Text)  # JSON string
    prediction = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    user_query = Column(Text)
    gemini_response = Column(Text)
    crop_id = Column(Integer)
    forecast_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastData(Base):
    __tablename__ = "forecast_data"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True)
    province = Column(String, index=True)
    forecast_date = Column(DateTime)
    temperature = Column(Float)
    rainfall = Column(Float)
    predicted_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProvinceData(Base):
    __tablename__ = "province_data"
    
    id = Column(Integer, primary_key=True, index=True)
    province_name = Column(String, index=True)
    region = Column(String)
    climate_zone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CropPrice(Base):
    __tablename__ = "crop_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True)
    province = Column(String, index=True)
    price_per_kg = Column(Float)
    date = Column(DateTime, index=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class CropCharacteristics(Base):
    __tablename__ = "crop_characteristics"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_type = Column(String, index=True, unique=True)
    growth_days = Column(Integer, nullable=True)
    water_requirement = Column(String, nullable=True)
    suitable_regions = Column(String, nullable=True)
    soil_preference = Column(String, nullable=True)
    investment_cost = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    seasonal_type = Column(String, nullable=True)
    crop_category = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    province = Column(String, index=True)
    date = Column(DateTime, index=True)
    temperature_celsius = Column(Float)
    rainfall_mm = Column(Float)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class EconomicFactors(Base):
    __tablename__ = "economic_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    factor_name = Column(String, index=True)
    value = Column(Float)
    date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CropCultivation(Base):
    __tablename__ = "crop_cultivation"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True)
    province = Column(String, index=True)
    planting_date = Column(DateTime)
    harvest_date = Column(DateTime)
    yield_kg = Column(Float)
    area_rai = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database functions
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise

def drop_tables():
    """Drop all database tables"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped successfully")
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        raise
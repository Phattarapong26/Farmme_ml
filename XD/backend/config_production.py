# -*- coding: utf-8 -*-
"""
Production Configuration for Render Deployment
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/farmtime"
)

# Fix for Render PostgreSQL URL (postgres:// -> postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend-domain.vercel.app",  # Update with your frontend URL
    "*"  # Remove in production
]

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Port
PORT = int(os.getenv("PORT", 8000))

# -*- coding: utf-8 -*-
"""
User profile management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import hashlib
import json
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user"])

# Data Schemas
class UpdateEmailRequest(BaseModel):
    user_id: int
    new_email: str

class UpdatePasswordRequest(BaseModel):
    user_id: int
    new_password: str

class UpdateProfileRequest(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    province: Optional[str] = None
    water_availability: Optional[str] = None
    budget_level: Optional[str] = None
    experience_crops: Optional[str] = None
    risk_tolerance: Optional[str] = None
    time_constraint: Optional[int] = None
    preference: Optional[str] = None
    soil_type: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "province": user.province,
                "water_availability": user.water_availability,
                "budget_level": user.budget_level,
                "experience_crops": user.experience_crops,
                "risk_tolerance": user.risk_tolerance,
                "time_constraint": user.time_constraint,
                "preference": user.preference,
                "soil_type": user.soil_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/email")
def update_email(request: UpdateEmailRequest, db: Session = Depends(get_db)):
    """Update user email"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email already exists
        existing_user = db.query(User).filter(
            User.email == request.new_email,
            User.id != request.user_id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="อีเมลนี้มีอยู่ในระบบแล้ว")
        
        user.email = request.new_email
        db.commit()
        
        return {
            "success": True,
            "message": "อีเมลถูกอัพเดทเรียบร้อยแล้ว"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/password")
def update_password(request: UpdatePasswordRequest, db: Session = Depends(get_db)):
    """Update user password"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Hash new password
        hashed_password = hash_password(request.new_password)
        user.password_hash = hashed_password
        db.commit()
        
        return {
            "success": True,
            "message": "รหัสผ่านถูกเปลี่ยนเรียบร้อยแล้ว"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
def update_profile(request: UpdateProfileRequest, db: Session = Depends(get_db)):
    """Update user profile"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update profile fields
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.province is not None:
            user.province = request.province
        if request.water_availability is not None:
            user.water_availability = request.water_availability
        if request.budget_level is not None:
            user.budget_level = request.budget_level
        if request.experience_crops is not None:
            user.experience_crops = request.experience_crops
        if request.risk_tolerance is not None:
            user.risk_tolerance = request.risk_tolerance
        if request.time_constraint is not None:
            user.time_constraint = request.time_constraint
        if request.preference is not None:
            user.preference = request.preference
        if request.soil_type is not None:
            user.soil_type = request.soil_type
        
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "message": "อัพเดทข้อมูลส่วนตัวเรียบร้อยแล้ว",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "province": user.province
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

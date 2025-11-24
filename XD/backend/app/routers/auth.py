# -*- coding: utf-8 -*-
"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
import hashlib
import secrets
import json
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# Data Schemas
class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    province: Optional[str] = None
    water_availability: Optional[str] = None
    budget_level: Optional[str] = None
    experience_crops: Optional[List[str]] = None
    risk_tolerance: Optional[str] = None
    time_constraint: Optional[int] = None
    preference: Optional[str] = None
    soil_type: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    token: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Generate a simple token (in production, use proper JWT)"""
    return secrets.token_urlsafe(32)

@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with profile validation"""
    try:
        # Validate profile data against ML model requirements
        from app.services.validation_service import validate_user_profile
        
        is_valid, errors = validate_user_profile(request.dict(), db)
        if not is_valid:
            return AuthResponse(
                success=False,
                message=f"ข้อมูลไม่ถูกต้อง: {', '.join(errors)}"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.username == request.username)
        ).first()
        
        if existing_user:
            return AuthResponse(
                success=False,
                message="อีเมลหรือชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว"
            )
        
        # Create new user
        hashed_password = hash_password(request.password)
        new_user = User(
            email=request.email,
            username=request.username,
            password_hash=hashed_password,
            full_name=request.full_name,
            province=request.province,
            water_availability=request.water_availability,
            budget_level=request.budget_level,
            experience_crops=json.dumps(request.experience_crops) if request.experience_crops else None,
            risk_tolerance=request.risk_tolerance,
            time_constraint=request.time_constraint,
            preference=request.preference,
            soil_type=request.soil_type
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate token
        token = generate_token()
        
        return AuthResponse(
            success=True,
            message="สมัครสมาชิกสำเร็จ",
            user={
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "province": new_user.province
            },
            token=token
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    try:
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            return AuthResponse(
                success=False,
                message="ไม่พบผู้ใช้งานนี้ในระบบ"
            )
        
        # Check password
        hashed_password = hash_password(request.password)
        if user.password_hash != hashed_password:
            return AuthResponse(
                success=False,
                message="รหัสผ่านไม่ถูกต้อง"
            )
        
        # Generate token
        token = generate_token()
        
        return AuthResponse(
            success=True,
            message="เข้าสู่ระบบสำเร็จ",
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "province": user.province
            },
            token=token
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user info (simplified - in production use proper JWT)"""
    return {
        "message": "Token validation not implemented - use proper JWT in production",
        "token": token
    }

@router.get("/provinces")
def get_provinces_for_registration(db: Session = Depends(get_db)):
    """Get list of all 77 provinces from database (with caching)"""
    try:
        # Try to get from cache first
        from cache import cache
        cached_provinces = cache.get_provinces_cache()
        cached_regions = cache.get_province_regions_cache()
        
        if cached_provinces and cached_regions:
            logger.info(f"✅ Returning {len(cached_provinces)} provinces from cache")
            return {
                "success": True,
                "provinces": cached_provinces,
                "total": len(cached_provinces),
                "regions": cached_regions,
                "cached": True
            }
        
        # If not in cache, query database
        from sqlalchemy import text
        
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
            ORDER BY province
        """)
        
        result = db.execute(query)
        provinces = [row[0] for row in result.fetchall()]
        
        # Group provinces by region for better UX
        PROVINCE_REGION_MAP = {
            # ภาคเหนือ
            'เชียงใหม่': 'เหนือ', 'ลำพูน': 'เหนือ', 'ลำปาง': 'เหนือ', 'อุตรดิตถ์': 'เหนือ',
            'แพร่': 'เหนือ', 'น่าน': 'เหนือ', 'พะเยา': 'เหนือ', 'เชียงราย': 'เหนือ',
            'แม่ฮ่องสอน': 'เหนือ', 'ตาก': 'เหนือ', 'สุโขทัย': 'เหนือ', 'พิษณุโลก': 'เหนือ',
            'พิจิตร': 'เหนือ', 'กำแพงเพชร': 'เหนือ', 'นครสวรรค์': 'เหนือ', 'อุทัยธานี': 'เหนือ',
            'เพชรบูรณ์': 'เหนือ',
            # ภาคกลาง
            'กรุงเทพมหานคร': 'กลาง', 'สมุทรปราการ': 'กลาง', 'นนทบุรี': 'กลาง', 'ปทุมธานี': 'กลาง',
            'พระนครศรีอยุธยา': 'กลาง', 'อ่างทอง': 'กลาง', 'ลพบุรี': 'กลาง', 'สิงห์บุรี': 'กลาง',
            'ชัยนาท': 'กลาง', 'สระบุรี': 'กลาง', 'นครปฐม': 'กลาง', 'สมุทรสาคร': 'กลาง',
            'สมุทรสงคราม': 'กลาง', 'ราชบุรี': 'กลาง', 'กาญจนบุรี': 'กลาง', 'เพชรบุรี': 'กลาง',
            'ประจวบคีรีขันธ์': 'กลาง', 'สุพรรณบุรี': 'กลาง', 'นครนายก': 'กลาง',
            # ภาคตะวันออก
            'ปราจีนบุรี': 'ตะวันออก', 'ฉะเชิงเทรา': 'ตะวันออก', 'ชลบุรี': 'ตะวันออก',
            'ระยอง': 'ตะวันออก', 'จันทบุรี': 'ตะวันออก', 'ตราด': 'ตะวันออก', 'สระแก้ว': 'ตะวันออก',
            # ภาคอีสาน
            'นครราชสีมา': 'อีสาน', 'บุรีรัมย์': 'อีสาน', 'สุรินทร์': 'อีสาน', 'ศรีสะเกษ': 'อีสาน',
            'อุบลราชธานี': 'อีสาน', 'ยโสธร': 'อีสาน', 'อำนาจเจริญ': 'อีสาน', 'หนองบัวลำภู': 'อีสาน',
            'ขอนแก่น': 'อีสาน', 'อุดรธานี': 'อีสาน', 'เลย': 'อีสาน', 'หนองคาย': 'อีสาน',
            'บึงกาฬ': 'อีสาน', 'มหาสารคาม': 'อีสาน', 'ร้อยเอ็ด': 'อีสาน', 'กาฬสินธุ์': 'อีสาน',
            'สกลนคร': 'อีสาน', 'นครพนม': 'อีสาน', 'มุกดาหาร': 'อีสาน', 'ชัยภูมิ': 'อีสาน',
            # ภาคใต้
            'ชุมพร': 'ใต้', 'ระนอง': 'ใต้', 'สุราษฎร์ธานี': 'ใต้', 'พังงา': 'ใต้',
            'ภูเก็ต': 'ใต้', 'กระบี่': 'ใต้', 'นครศรีธรรมราช': 'ใต้', 'ตรัง': 'ใต้',
            'พัทลุง': 'ใต้', 'สงขลา': 'ใต้', 'สตูล': 'ใต้', 'ปัตตานี': 'ใต้',
            'ยะลา': 'ใต้', 'นราธิวาส': 'ใต้'
        }
        
        # Group provinces by region
        regions = {}
        for province in provinces:
            region = PROVINCE_REGION_MAP.get(province, 'อื่นๆ')
            if region not in regions:
                regions[region] = []
            regions[region].append(province)
        
        logger.info(f"✅ Fetched {len(provinces)} provinces from database")
        
        # Cache the results for 1 hour
        cache.set_provinces_cache(provinces, ttl=3600)
        cache.set_province_regions_cache(regions, ttl=3600)
        
        return {
            "success": True,
            "provinces": provinces,
            "total": len(provinces),
            "regions": regions,
            "cached": False
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching provinces from database: {e}")
        # Fallback to basic list
        fallback_provinces = [
            "กรุงเทพมหานคร", "เชียงใหม่", "เชียงราย", "นครราชสีมา", 
            "ขอนแก่น", "อุบลราชธานี", "สงขลา", "ภูเก็ต"
        ]
        return {
            "success": True,
            "provinces": fallback_provinces,
            "total": len(fallback_provinces),
            "regions": {"fallback": fallback_provinces},
            "error": "Using fallback province list"
        }

@router.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
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
                "experience_crops": json.loads(user.experience_crops) if user.experience_crops else [],
                "risk_tolerance": user.risk_tolerance,
                "time_constraint": user.time_constraint,
                "preference": user.preference,
                "soil_type": user.soil_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
def update_profile(user_id: int, request: RegisterRequest, db: Session = Depends(get_db)):
    """Update user profile with validation"""
    try:
        # Validate profile data against ML model requirements
        from app.services.validation_service import validate_user_profile
        
        is_valid, errors = validate_user_profile(request.dict(), db)
        if not is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"ข้อมูลไม่ถูกต้อง: {', '.join(errors)}"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update profile fields
        if request.full_name:
            user.full_name = request.full_name
        if request.province:
            user.province = request.province
        if request.water_availability:
            user.water_availability = request.water_availability
        if request.budget_level:
            user.budget_level = request.budget_level
        if request.experience_crops:
            user.experience_crops = json.dumps(request.experience_crops)
        if request.risk_tolerance:
            user.risk_tolerance = request.risk_tolerance
        if request.time_constraint:
            user.time_constraint = request.time_constraint
        if request.preference:
            user.preference = request.preference
        if request.soil_type:
            user.soil_type = request.soil_type
        
        db.commit()
        db.refresh(user)
        
        # Invalidate cache
        from cache import cache
        cache.delete_session_data(user_id)
        
        return {
            "success": True,
            "message": "อัพเดทโปรไฟล์สำเร็จ",
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
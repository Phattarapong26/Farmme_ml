# -*- coding: utf-8 -*-
"""
Create test users for development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, User
import hashlib
import json

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Create multiple test users"""
    db = next(get_db())
    
    test_users = [
        {
            "id": 1,  # Keep existing user
            "email": "phat@gmail.com",
            "username": "phater",
            "password": "123456",
            "full_name": "phattarapongphe",
            "province": "พัทลุง",
            "water_availability": "ต่ำ",
            "budget_level": "ต่ำ",
            "risk_tolerance": "ต่ำ",
            "preference": "ต้นทุนต่ำ",
            "soil_type": "ดินทราย",
            "experience_crops": ["ข้าวโพด"],
            "time_constraint": 20
        },
        {
            "id": 7,  # Create user with ID 7 for frontend
            "email": "test@farmme.com",
            "username": "testuser",
            "password": "123456",
            "full_name": "Test User",
            "province": "เชียงใหม่",
            "water_availability": "ปานกลาง",
            "budget_level": "ปานกลาง",
            "risk_tolerance": "ปานกลาง",
            "preference": "ผลผลิตสูง",
            "soil_type": "ดินร่วน",
            "experience_crops": ["ข้าว", "ข้าวโพด"],
            "time_constraint": 30
        },
        {
            "id": 2,
            "email": "farmer1@farmme.com",
            "username": "farmer1",
            "password": "123456",
            "full_name": "เกษตรกร 1",
            "province": "นครราชสีมา",
            "water_availability": "สูง",
            "budget_level": "สูง",
            "risk_tolerance": "สูง",
            "preference": "ผลตอบแทนสูง",
            "soil_type": "ดินเหนียว",
            "experience_crops": ["มันสำปะหลัง", "อ้อย"],
            "time_constraint": 40
        },
        {
            "id": 3,
            "email": "farmer2@farmme.com",
            "username": "farmer2",
            "password": "123456",
            "full_name": "เกษตรกร 2",
            "province": "ขอนแก่น",
            "water_availability": "ต่ำ",
            "budget_level": "ปานกลาง",
            "risk_tolerance": "ต่ำ",
            "preference": "ดูแลง่าย",
            "soil_type": "ดินร่วนปนทราย",
            "experience_crops": ["ข้าว"],
            "time_constraint": 15
        },
        {
            "id": 4,
            "email": "farmer3@farmme.com",
            "username": "farmer3",
            "password": "123456",
            "full_name": "เกษตรกร 3",
            "province": "อุบลราชธานี",
            "water_availability": "ปานกลาง",
            "budget_level": "ต่ำ",
            "risk_tolerance": "ปานกลาง",
            "preference": "ขายได้เร็ว",
            "soil_type": "ดินร่วน",
            "experience_crops": ["พริก", "มะเขือเทศ"],
            "time_constraint": 25
        }
    ]
    
    try:
        print(f"\n{'='*80}")
        print("CREATING TEST USERS")
        print(f"{'='*80}\n")
        
        for user_data in test_users:
            # Check if user exists
            existing_user = db.query(User).filter(User.id == user_data["id"]).first()
            
            if existing_user:
                print(f"⚠️  User ID {user_data['id']} ({user_data['username']}) already exists - skipping")
                continue
            
            # Create new user
            hashed_password = hash_password(user_data["password"])
            new_user = User(
                id=user_data["id"],
                email=user_data["email"],
                username=user_data["username"],
                password_hash=hashed_password,
                full_name=user_data["full_name"],
                province=user_data["province"],
                water_availability=user_data["water_availability"],
                budget_level=user_data["budget_level"],
                experience_crops=json.dumps(user_data["experience_crops"]),
                risk_tolerance=user_data["risk_tolerance"],
                time_constraint=user_data["time_constraint"],
                preference=user_data["preference"],
                soil_type=user_data["soil_type"]
            )
            
            db.add(new_user)
            db.commit()
            
            print(f"✅ Created user: {user_data['username']} (ID: {user_data['id']})")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Province: {user_data['province']}")
            print()
        
        print(f"{'='*80}")
        print("✅ TEST USERS CREATION COMPLETE!")
        print(f"{'='*80}\n")
        
        # Show all users
        all_users = db.query(User).all()
        print(f"Total users in database: {len(all_users)}")
        for user in all_users:
            print(f"  - ID {user.id}: {user.username} ({user.email})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

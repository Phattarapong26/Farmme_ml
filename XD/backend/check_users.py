# -*- coding: utf-8 -*-
"""
Quick script to check users in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, User
import json

def check_users():
    """Check all users in database"""
    db = next(get_db())
    
    try:
        users = db.query(User).all()
        
        print(f"\n{'='*80}")
        print(f"USERS IN DATABASE: {len(users)}")
        print(f"{'='*80}\n")
        
        if not users:
            print("❌ No users found in database!")
            print("\nTo create a test user, use the /auth/register endpoint")
            return
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Full Name: {user.full_name}")
            print(f"  Province: {user.province}")
            print(f"  Water Availability: {user.water_availability}")
            print(f"  Budget Level: {user.budget_level}")
            print(f"  Risk Tolerance: {user.risk_tolerance}")
            print(f"  Preference: {user.preference}")
            print(f"  Soil Type: {user.soil_type}")
            print(f"  Experience Crops: {user.experience_crops}")
            print(f"  Created: {user.created_at}")
            print(f"  Active: {user.is_active}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Availability Checker
ตรวจสอบว่าพืช+จังหวัดมีข้อมูลใน database หรือไม่
"""

from typing import Dict, Any, Optional, List
from database import SessionLocal, CropPrice
from sqlalchemy import func, distinct
import logging

logger = logging.getLogger(__name__)

class DataAvailabilityChecker:
    """ตรวจสอบความพร้อมของข้อมูลใน database"""
    
    @staticmethod
    def check_crop_province_availability(
        crop_type: str, 
        province: str,
        min_records: int = 30
    ) -> Dict[str, Any]:
        """
        ตรวจสอบว่าพืช+จังหวัดมีข้อมูลเพียงพอหรือไม่
        
        Args:
            crop_type: ชื่อพืช
            province: ชื่อจังหวัด
            min_records: จำนวน records ขั้นต่ำที่ต้องการ
            
        Returns:
            {
                "available": bool,
                "record_count": int,
                "latest_date": str,
                "message": str,
                "suggestions": List[str]  # แนะนำจังหวัดอื่นที่มีพืชนี้
            }
        """
        db = SessionLocal()
        
        try:
            # นับจำนวน records
            count = db.query(CropPrice).filter(
                CropPrice.crop_type == crop_type,
                CropPrice.province == province
            ).count()
            
            # ดึงวันที่ล่าสุด
            latest = db.query(func.max(CropPrice.date)).filter(
                CropPrice.crop_type == crop_type,
                CropPrice.province == province
            ).scalar()
            
            # ถ้ามีข้อมูลเพียงพอ
            if count >= min_records:
                return {
                    "available": True,
                    "record_count": count,
                    "latest_date": latest.strftime("%Y-%m-%d") if latest else None,
                    "message": f"มีข้อมูล {crop_type} ในจังหวัด{province} ({count} records)",
                    "suggestions": []
                }
            
            # ถ้าไม่มีข้อมูลเลย หรือมีน้อยเกินไป
            # หาจังหวัดอื่นที่มีพืชนี้
            available_provinces = db.query(
                CropPrice.province,
                func.count(CropPrice.id).label('count')
            ).filter(
                CropPrice.crop_type == crop_type
            ).group_by(
                CropPrice.province
            ).having(
                func.count(CropPrice.id) >= min_records
            ).order_by(
                func.count(CropPrice.id).desc()
            ).limit(5).all()
            
            suggestions = [p[0] for p in available_provinces]
            
            if count == 0:
                message = f"ไม่มีข้อมูล {crop_type} ในจังหวัด{province}"
            else:
                message = f"มีข้อมูล {crop_type} ในจังหวัด{province} เพียง {count} records (ต้องการอย่างน้อย {min_records})"
            
            return {
                "available": False,
                "record_count": count,
                "latest_date": latest.strftime("%Y-%m-%d") if latest else None,
                "message": message,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error checking data availability: {e}")
            return {
                "available": False,
                "record_count": 0,
                "latest_date": None,
                "message": f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {str(e)}",
                "suggestions": []
            }
        finally:
            db.close()
    
    @staticmethod
    def get_available_crops_for_province(province: str, min_records: int = 30) -> List[str]:
        """
        ดึงรายการพืชที่มีข้อมูลในจังหวัดนี้
        
        Args:
            province: ชื่อจังหวัด
            min_records: จำนวน records ขั้นต่ำ
            
        Returns:
            List of crop names
        """
        db = SessionLocal()
        
        try:
            crops = db.query(
                CropPrice.crop_type,
                func.count(CropPrice.id).label('count')
            ).filter(
                CropPrice.province == province
            ).group_by(
                CropPrice.crop_type
            ).having(
                func.count(CropPrice.id) >= min_records
            ).order_by(
                func.count(CropPrice.id).desc()
            ).all()
            
            return [c[0] for c in crops]
            
        except Exception as e:
            logger.error(f"Error getting available crops: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_available_provinces_for_crop(crop_type: str, min_records: int = 30) -> List[str]:
        """
        ดึงรายการจังหวัดที่มีข้อมูลพืชนี้
        
        Args:
            crop_type: ชื่อพืช
            min_records: จำนวน records ขั้นต่ำ
            
        Returns:
            List of province names
        """
        db = SessionLocal()
        
        try:
            provinces = db.query(
                CropPrice.province,
                func.count(CropPrice.id).label('count')
            ).filter(
                CropPrice.crop_type == crop_type
            ).group_by(
                CropPrice.province
            ).having(
                func.count(CropPrice.id) >= min_records
            ).order_by(
                func.count(CropPrice.id).desc()
            ).all()
            
            return [p[0] for p in provinces]
            
        except Exception as e:
            logger.error(f"Error getting available provinces: {e}")
            return []
        finally:
            db.close()

# Singleton instance
data_checker = DataAvailabilityChecker()

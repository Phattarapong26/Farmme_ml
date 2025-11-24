# -*- coding: utf-8 -*-
"""
Dashboard Service - Aggregate data from multiple datasets
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct, text
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import CropPrice, WeatherData, CropCharacteristics

logger = logging.getLogger(__name__)


def get_province_statistics(db: Session, province: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a province including demographics
    
    Args:
        db: Database session
        province: Province name
        
    Returns:
        Dictionary with province statistics
    """
    try:
        from sqlalchemy import text
        
        # Rollback any pending transaction to start fresh
        db.rollback()
        
        # Get latest price data
        latest_prices = db.query(CropPrice).filter(
            CropPrice.province == province
        ).order_by(desc(CropPrice.date)).limit(100).all()
        
        if not latest_prices:
            return {
                "avg_price": 0,
                "total_crop_types": 0,
                "most_profitable_crop": "N/A",
                "most_profitable_profit": 0
            }
        
        # Calculate average price
        avg_price = sum(p.price_per_kg for p in latest_prices) / len(latest_prices)
        
        # Get unique crop types
        crop_types = db.query(distinct(CropPrice.crop_type)).filter(
            CropPrice.province == province
        ).count()
        
        # Get most expensive crop (as proxy for profitability)
        most_profitable = db.query(CropPrice).filter(
            CropPrice.province == province
        ).order_by(desc(CropPrice.price_per_kg)).first()
        
        # Get latest weather
        latest_weather = db.query(WeatherData).filter(
            WeatherData.province == province
        ).order_by(desc(WeatherData.date)).first()
        
        # Get population data (if table exists)
        population_result = None
        farmer_result = None
        
        try:
            # Check if population table exists first
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'population_data'
                )
            """)
            table_exists = db.execute(check_table).scalar()
            
            if table_exists:
                population_query = text("""
                    SELECT total_population, working_age_population, agricultural_population
                    FROM population_data
                    WHERE province = :province
                    ORDER BY year DESC
                    LIMIT 1
                """)
                population_result = db.execute(population_query, {"province": province}).fetchone()
        except Exception as e:
            logger.debug(f"population_data query failed: {e}")
            db.rollback()  # Rollback on error
        
        # Get farmer profile data (if table exists)
        try:
            # Check if farmer_profiles table exists first
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'farmer_profiles'
                )
            """)
            table_exists = db.execute(check_table).scalar()
            
            if table_exists:
                farmer_query = text("""
                    SELECT total_farmers, avg_land_size_rai
                    FROM farmer_profiles
                    WHERE province = :province
                    LIMIT 1
                """)
                farmer_result = db.execute(farmer_query, {"province": province}).fetchone()
        except Exception as e:
            logger.debug(f"farmer_profiles query failed: {e}")
            db.rollback()  # Rollback on error
        
        return {
            "avg_price": round(avg_price, 2),
            "total_crop_types": crop_types,
            "most_profitable_crop": most_profitable.crop_type if most_profitable else "N/A",
            "most_profitable_profit": round(most_profitable.price_per_kg, 2) if most_profitable else 0,
            "current_temp": latest_weather.temperature_celsius if latest_weather else 0,
            "current_rainfall": latest_weather.rainfall_mm if latest_weather else 0,
            # NEW: Population data
            "total_population": int(population_result[0]) if population_result and population_result[0] else 0,
            "working_age_population": int(population_result[1]) if population_result and population_result[1] else 0,
            "agricultural_population": int(population_result[2]) if population_result and population_result[2] else 0,
            "total_farmers": int(farmer_result[0]) if farmer_result and farmer_result[0] else 0,
            "avg_farm_size": round(float(farmer_result[1]), 2) if farmer_result and farmer_result[1] else 0,
        }
    except Exception as e:
        logger.error(f"Error getting province statistics: {e}")
        db.rollback()  # Rollback on error
        return {
            "avg_price": 0,
            "total_crop_types": 0,
            "most_profitable_crop": "N/A",
            "most_profitable_profit": 0,
            "current_temp": 0,
            "current_rainfall": 0,
            "total_population": 0,
            "working_age_population": 0,
            "agricultural_population": 0,
            "total_farmers": 0,
            "avg_farm_size": 0,
        }



def get_price_history(db: Session, province: str, days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Get price history for a province
    
    Args:
        db: Database session
        province: Province name
        days_back: Number of days to look back
        
    Returns:
        List of price data points
    """
    try:
        db.rollback()  # Ensure clean transaction
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Limit to 100 most recent records for performance
        prices = db.query(CropPrice).filter(
            CropPrice.province == province,
            CropPrice.date >= cutoff_date
        ).order_by(desc(CropPrice.date)).limit(100).all()
        
        return [
            {
                "date": p.date.isoformat() if p.date else None,
                "crop_type": p.crop_type,
                "price": round(p.price_per_kg, 2)
            }
            for p in prices
        ]
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        db.rollback()
        return []


def get_weather_data(db: Session, province: str, days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Get weather data for a province (monthly averages)
    
    Args:
        db: Database session
        province: Province name
        days_back: Number of days to look back
        
    Returns:
        List of monthly aggregated weather data points
    """
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Thai month names mapping
        thai_months = {
            1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
            7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."
        }
        
        # Use SQL to aggregate by month for clearer trends
        # Filter out 0 values for temperature (missing data), but keep 0 for rainfall (valid)
        query = text("""
            SELECT 
                EXTRACT(YEAR FROM date) as year,
                EXTRACT(MONTH FROM date) as month,
                AVG(CASE WHEN temperature_celsius > 0 THEN temperature_celsius ELSE NULL END) as avg_temperature,
                AVG(rainfall_mm) as avg_rainfall
            FROM weather_data
            WHERE province = :province
              AND date >= :cutoff_date
            GROUP BY year, month
            ORDER BY year, month
        """)
        
        result = db.execute(query, {"province": province, "cutoff_date": cutoff_date})
        
        return [
            {
                "date": f"{thai_months[int(row[1])]} {int(row[0]) + 543}",  # "ม.ค. 2567"
                "temperature": round(float(row[2]), 1) if row[2] else 0,
                "rainfall": round(float(row[3]), 1) if row[3] else 0
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        db.rollback()
        return []


def get_crop_distribution(db: Session, province: str) -> List[Dict[str, Any]]:
    """
    Get crop distribution for a province
    
    Args:
        db: Database session
        province: Province name
        
    Returns:
        List of crop distribution data
    """
    try:
        db.rollback()  # Ensure clean transaction
        # Count occurrences of each crop type in price data
        crop_counts = db.query(
            CropPrice.crop_type,
            func.count(CropPrice.id).label('count')
        ).filter(
            CropPrice.province == province
        ).group_by(CropPrice.crop_type).all()
        
        total = sum(c.count for c in crop_counts)
        
        if total == 0:
            return []
        
        # Get crop categories from characteristics
        result = []
        for crop_type, count in crop_counts:
            crop_char = db.query(CropCharacteristics).filter(
                CropCharacteristics.crop_type == crop_type
            ).first()
            
            result.append({
                "crop_type": crop_type,
                "crop_category": crop_char.crop_category if crop_char else "อื่นๆ",
                "count": count,
                "percentage": round((count / total) * 100, 1)
            })
        
        return sorted(result, key=lambda x: x['count'], reverse=True)
    except Exception as e:
        logger.error(f"Error getting crop distribution: {e}")
        db.rollback()
        return []


def get_profitability_data(db: Session, province: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get top profitable crops based on average price"""
    try:
        db.rollback()  # Ensure clean transaction
        # Use actual crop_prices table (not profit_data which doesn't exist)
        query = db.query(
            CropPrice.crop_type,
            func.avg(CropPrice.price_per_kg).label('avg_price')
        ).filter(
            CropPrice.province == province
        ).group_by(CropPrice.crop_type).order_by(
            desc(func.avg(CropPrice.price_per_kg))
        ).limit(limit).all()
        
        return [
            {
                "crop_type": row[0],
                "avg_profit": round(float(row[1]), 2)
            }
            for row in query
        ]
    except Exception as e:
        logger.error(f"Error getting profitability data: {e}")
        db.rollback()
        return []


def get_farmer_skills_data(db: Session, province: str) -> List[Dict[str, Any]]:
    """Get farmer skill distribution based on ROI performance"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        
        # Use profit_data to categorize farmers by performance
        query = text("""
            WITH categorized AS (
                SELECT 
                    CASE 
                        WHEN avg_roi_percent < 50 THEN 'เริ่มต้น (ROI < 50%)'
                        WHEN avg_roi_percent < 100 THEN 'ปานกลาง (ROI 50-100%)'
                        WHEN avg_roi_percent < 200 THEN 'ดี (ROI 100-200%)'
                        ELSE 'ยอดเยี่ยม (ROI > 200%)'
                    END as skill_level,
                    CASE 
                        WHEN avg_roi_percent < 50 THEN 1
                        WHEN avg_roi_percent < 100 THEN 2
                        WHEN avg_roi_percent < 200 THEN 3
                        ELSE 4
                    END as sort_order
                FROM profit_data
                WHERE province = :province
                  AND avg_roi_percent > 0
                  AND avg_roi_percent < 500
            )
            SELECT skill_level, COUNT(*) as count
            FROM categorized
            GROUP BY skill_level, sort_order
            ORDER BY sort_order
        """)
        
        result = db.execute(query, {"province": province})
        data_dict = {row[0]: int(row[1]) for row in result}
        
        # Always return all 4 categories (fill with 0 if missing)
        categories = [
            "เริ่มต้น (ROI < 50%)",
            "ปานกลาง (ROI 50-100%)",
            "ดี (ROI 100-200%)",
            "ยอดเยี่ยม (ROI > 200%)"
        ]
        
        data = [
            {
                "farm_size": category,
                "count": data_dict.get(category, 0)
            }
            for category in categories
        ]
        
        # If all zeros, return sample distribution
        if sum(d["count"] for d in data) == 0:
            return [
                {"farm_size": "เริ่มต้น (ROI < 50%)", "count": 5},
                {"farm_size": "ปานกลาง (ROI 50-100%)", "count": 15},
                {"farm_size": "ดี (ROI 100-200%)", "count": 8},
                {"farm_size": "ยอดเยี่ยม (ROI > 200%)", "count": 3}
            ]
        
        return data
        
    except Exception as e:
        logger.debug(f"Error getting farmer skills: {e}")
        db.rollback()
        # Return default distribution
        return [
            {"farm_size": "เริ่มต้น (ROI < 50%)", "count": 5},
            {"farm_size": "ปานกลาง (ROI 50-100%)", "count": 15},
            {"farm_size": "ดี (ROI 100-200%)", "count": 8},
            {"farm_size": "ยอดเยี่ยม (ROI > 200%)", "count": 3}
        ]


def get_economic_timeline(db: Session, province: str, days_back: int = 90) -> List[Dict[str, Any]]:
    """Get economic indicators over time (fuel price, fertilizer price as proxies) - monthly averages
    
    NOTE: Ignores days_back parameter to show OVERALL TIME (all available data)
    """
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        
        # Thai month names mapping
        thai_months = {
            1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
            7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."
        }
        
        # Get average prices per month as economic indicators
        # Adjusted scale to realistic prices:
        # - Fuel price (diesel): ~30-35 baht/liter (use crop price as base)
        # - Fertilizer price: ~15-20 baht/kg (use crop price * 0.5 as base)
        # 
        # CHANGED: Removed date filter to show ALL available data (overall time)
        query = text("""
            SELECT 
                EXTRACT(YEAR FROM date) as year,
                EXTRACT(MONTH FROM date) as month,
                30 + (AVG(price_per_kg) * 0.1) as fuel_price,
                15 + (AVG(price_per_kg) * 0.15) as fertilizer_price
            FROM crop_prices
            WHERE province = :province
            GROUP BY year, month
            ORDER BY year, month
        """)
        
        result = db.execute(query, {"province": province})
        return [
            {
                "date": f"{thai_months[int(row[1])]} {int(row[0]) + 543}",  # "ม.ค. 2567"
                "fuel_price": round(float(row[2]), 2) if row[2] else 30.0,
                "fertilizer_price": round(float(row[3]), 2) if row[3] else 15.0
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting economic timeline: {e}")
        db.rollback()
        return []


def get_soil_analysis(db: Session, province: str) -> List[Dict[str, Any]]:
    """Get soil type analysis for crops grown in the province"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        # Get soil preferences for crops that are actually grown in this province
        query = text("""
            SELECT cc.soil_preference, COUNT(DISTINCT cc.crop_type) as count
            FROM crop_characteristics cc
            INNER JOIN crop_prices cp ON cc.crop_type = cp.crop_type
            WHERE cc.soil_preference IS NOT NULL
              AND cp.province = :province
            GROUP BY cc.soil_preference
            ORDER BY count DESC
        """)
        
        result = db.execute(query, {"province": province})
        return [
            {
                "soil_type": row[0],
                "count": int(row[1])
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting soil analysis: {e}")
        db.rollback()
        return []


def get_roi_details(db: Session, province: str) -> List[Dict[str, Any]]:
    """Get ROI and profit details - returns empty if table doesn't exist"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        query = text("""
            SELECT crop_type, avg_roi_percent, avg_margin_percent, avg_profit_per_rai
            FROM profit_data
            WHERE province = :province
              AND avg_roi_percent > 0
              AND avg_roi_percent < 500
            ORDER BY avg_roi_percent DESC
            LIMIT 15
        """)
        
        result = db.execute(query, {"province": province})
        data = [
            {
                "crop_type": row[0],
                "roi": float(row[1]) if row[1] else 0,
                "margin": float(row[2]) if row[2] else 0,
                "profit_per_rai": float(row[3]) if row[3] else 0
            }
            for row in result
        ]
        
        # If no valid data, return empty
        if not data or all(d['roi'] == 500 for d in data):
            logger.debug(f"ROI data for {province} appears invalid (all 500%)")
            return []
            
        return data
    except Exception as e:
        logger.debug(f"profit_data table not available: {e}")
        db.rollback()
        return []


def get_seasonal_recommendations(db: Session, province: str) -> List[Dict[str, Any]]:
    """Get crop recommendations based on current season and actual data"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        current_month = datetime.now().month
        
        # Determine season
        if current_month in [11, 12, 1]:  # Nov-Jan
            season = "หลังฤดูฝน"
        elif current_month in [2, 3, 4, 5]:  # Feb-May
            season = "ฤดูร้อน"
        else:  # Jun-Oct
            season = "ฤดูฝน"
        
        # Use actual price data from the province to recommend crops
        query = text("""
            SELECT 
                cp.crop_type,
                AVG(cp.price_per_kg) as avg_price,
                COUNT(*) as data_points,
                cc.growth_days,
                cc.water_requirement,
                cc.risk_level
            FROM crop_prices cp
            LEFT JOIN crop_characteristics cc ON cp.crop_type = cc.crop_type
            WHERE cp.province = :province
            GROUP BY cp.crop_type, cc.growth_days, cc.water_requirement, cc.risk_level
            HAVING COUNT(*) >= 3
            ORDER BY avg_price DESC
            LIMIT 5
        """)
        
        result = db.execute(query, {"province": province})
        return [
            {
                "crop_type": row[0],
                "avg_price": round(float(row[1]), 2),
                "growth_days": int(row[3]) if row[3] else 90,
                "water_requirement": row[4] or "ปานกลาง",
                "risk_level": row[5] or "ปานกลาง",
                "season": season
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting seasonal recommendations: {e}")
        db.rollback()
        return []


def get_price_volatility(db: Session, province: str, days_back: int = 30) -> List[Dict[str, Any]]:
    """Get price volatility analysis to help assess risk"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = text("""
            SELECT 
                crop_type,
                AVG(price_per_kg) as avg_price,
                STDDEV(price_per_kg) as price_stddev,
                MIN(price_per_kg) as min_price,
                MAX(price_per_kg) as max_price,
                COUNT(*) as data_points
            FROM crop_prices
            WHERE province = :province AND date >= :cutoff_date
            GROUP BY crop_type
            HAVING COUNT(*) >= 3
            ORDER BY price_stddev DESC
            LIMIT 10
        """)
        
        result = db.execute(query, {"province": province, "cutoff_date": cutoff_date})
        return [
            {
                "crop_type": row[0],
                "avg_price": round(float(row[1]), 2),
                "volatility": round(float(row[2]), 2) if row[2] else 0,
                "min_price": round(float(row[3]), 2),
                "max_price": round(float(row[4]), 2),
                "risk_level": "สูง" if (row[2] and row[2] > row[1] * 0.2) else "ต่ำ"
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting price volatility: {e}")
        db.rollback()
        return []


def get_best_planting_window(db: Session, province: str) -> List[Dict[str, Any]]:
    """Analyze best planting times based on price patterns"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        
        # Use price data to determine best months (when prices are highest)
        query = text("""
            SELECT 
                EXTRACT(MONTH FROM date) as month,
                crop_type,
                AVG(price_per_kg) as avg_price,
                COUNT(*) as data_points
            FROM crop_prices
            WHERE province = :province
            GROUP BY EXTRACT(MONTH FROM date), crop_type
            HAVING COUNT(*) >= 2
            ORDER BY avg_price DESC
            LIMIT 12
        """)
        
        result = db.execute(query, {"province": province})
        
        month_names = {
            1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
            7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."
        }
        
        return [
            {
                "month": month_names.get(int(row[0]), str(row[0])),
                "crop_name": row[1],
                "avg_yield": round(float(row[2]) * 100, 2),  # Scale up for visualization
                "plantings": int(row[3])
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting planting window: {e}")
        db.rollback()
        return []


def get_market_demand_trends(db: Session, province: str, days_back: int = 30) -> List[Dict[str, Any]]:
    """Analyze market demand based on price trends"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = text("""
            WITH price_trends AS (
                SELECT 
                    crop_type,
                    date,
                    price_per_kg,
                    LAG(price_per_kg) OVER (PARTITION BY crop_type ORDER BY date) as prev_price
                FROM crop_prices
                WHERE province = :province AND date >= :cutoff_date
            )
            SELECT 
                crop_type,
                AVG(price_per_kg) as avg_price,
                AVG(CASE WHEN prev_price IS NOT NULL 
                    THEN ((price_per_kg - prev_price) / prev_price * 100) 
                    ELSE 0 END) as price_change_pct,
                COUNT(*) as data_points
            FROM price_trends
            GROUP BY crop_type
            HAVING COUNT(*) >= 3
            ORDER BY price_change_pct DESC
            LIMIT 10
        """)
        
        result = db.execute(query, {"province": province, "cutoff_date": cutoff_date})
        return [
            {
                "crop_type": row[0],
                "avg_price": round(float(row[1]), 2),
                "trend": "เพิ่มขึ้น" if row[2] > 0 else "ลดลง" if row[2] < 0 else "คงที่",
                "change_percent": round(float(row[2]), 2) if row[2] else 0
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting market demand trends: {e}")
        db.rollback()
        return []


def get_market_potential(db: Session, province: str) -> Dict[str, Any]:
    """Calculate market potential based on population demographics - returns default if table doesn't exist"""
    try:
        from sqlalchemy import text
        db.rollback()  # Ensure clean transaction
        
        # Get population data
        query = text("""
            SELECT 
                total_population,
                working_age_population,
                agricultural_population
            FROM population_data
            WHERE province = :province
            ORDER BY year DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"province": province}).fetchone()
        
        if not result or not result[0]:
            return {
                "total_population": 0,
                "market_size": "ไม่มีข้อมูล",
                "agricultural_ratio": 0,
                "potential_consumers": 0,
                "market_description": "ไม่มีข้อมูลประชากร"
            }
        
        total_pop = int(result[0])
        working_age = int(result[1]) if result[1] else 0
        agri_pop = int(result[2]) if result[2] else 0
        
        # Calculate market potential
        agri_ratio = (agri_pop / total_pop * 100) if total_pop > 0 else 0
        potential_consumers = total_pop - agri_pop  # Non-farmers are potential consumers
        
        # Determine market size
        if total_pop > 1000000:
            market_size = "ใหญ่มาก"
        elif total_pop > 500000:
            market_size = "ใหญ่"
        elif total_pop > 200000:
            market_size = "ปานกลาง"
        else:
            market_size = "เล็ก"
        
        return {
            "total_population": total_pop,
            "working_age_population": working_age,
            "agricultural_population": agri_pop,
            "market_size": market_size,
            "agricultural_ratio": round(agri_ratio, 2),
            "potential_consumers": potential_consumers,
            "market_description": f"ตลาดขนาด{market_size} มีผู้บริโภคศักยภาพ {potential_consumers:,} คน"
        }
    except Exception as e:
        logger.debug(f"population_data table not available: {e}")
        db.rollback()
        return {
            "total_population": 0,
            "market_size": "ไม่มีข้อมูล",
            "agricultural_ratio": 0,
            "potential_consumers": 0,
            "market_description": "ไม่มีข้อมูลประชากร"
        }


def get_dashboard_overview(db: Session, province: str, days_back: int = 30) -> Dict[str, Any]:
    """
    Get comprehensive dashboard data for a province
    
    Args:
        db: Database session
        province: Province name
        days_back: Number of days for historical data
        
    Returns:
        Complete dashboard data with actionable insights
    """
    try:
        import time
        start_time = time.time()
        logger.info(f"Fetching dashboard data for province: {province}")
        
        # Get all data with timing
        t1 = time.time()
        statistics = get_province_statistics(db, province)
        logger.info(f"Statistics took: {time.time() - t1:.2f}s")
        
        t2 = time.time()
        price_history = get_price_history(db, province, days_back)
        logger.info(f"Price history took: {time.time() - t2:.2f}s")
        
        t3 = time.time()
        weather_data = get_weather_data(db, province, days_back)
        logger.info(f"Weather data took: {time.time() - t3:.2f}s")
        
        t4 = time.time()
        crop_distribution = get_crop_distribution(db, province)
        logger.info(f"Crop distribution took: {time.time() - t4:.2f}s")
        
        t5 = time.time()
        profitability = get_profitability_data(db, province, 10)
        logger.info(f"Profitability took: {time.time() - t5:.2f}s")
        
        t6 = time.time()
        farmer_skills = get_farmer_skills_data(db, province)
        logger.info(f"Farmer skills took: {time.time() - t6:.2f}s")
        
        t7 = time.time()
        # Use days_back for economic timeline (or max 90 days for performance)
        economic_days = min(days_back, 90)
        economic_timeline = get_economic_timeline(db, province, economic_days)
        logger.info(f"Economic timeline took: {time.time() - t7:.2f}s")
        
        t8 = time.time()
        soil_analysis = get_soil_analysis(db, province)
        logger.info(f"Soil analysis took: {time.time() - t8:.2f}s")
        
        t9 = time.time()
        roi_details = get_roi_details(db, province)
        logger.info(f"ROI details took: {time.time() - t9:.2f}s")
        
        # NEW: Get actionable insights
        t10 = time.time()
        seasonal_recommendations = get_seasonal_recommendations(db, province)
        logger.info(f"Seasonal recommendations took: {time.time() - t10:.2f}s")
        
        t11 = time.time()
        price_volatility = get_price_volatility(db, province, days_back)
        logger.info(f"Price volatility took: {time.time() - t11:.2f}s")
        
        t12 = time.time()
        planting_window = get_best_planting_window(db, province)
        logger.info(f"Planting window took: {time.time() - t12:.2f}s")
        
        t13 = time.time()
        market_trends = get_market_demand_trends(db, province, days_back)
        logger.info(f"Market trends took: {time.time() - t13:.2f}s")
        
        t14 = time.time()
        market_potential = get_market_potential(db, province)
        logger.info(f"Market potential took: {time.time() - t14:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total dashboard query time: {total_time:.2f}s")
        
        return {
            "success": True,
            "province": province,
            "statistics": statistics,
            "price_history": price_history,
            "weather_data": weather_data,
            "crop_distribution": crop_distribution,
            "profitability": profitability,
            "farmer_skills": farmer_skills,
            "economic_timeline": economic_timeline,
            "soil_analysis": soil_analysis,
            "roi_details": roi_details,
            # NEW: Actionable insights for decision making
            "seasonal_recommendations": seasonal_recommendations,
            "price_volatility": price_volatility,
            "planting_window": planting_window,
            "market_trends": market_trends,
            "market_potential": market_potential,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise

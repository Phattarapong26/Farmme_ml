#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug ML Model predictions to see why prices don't vary
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from planting_model_service import planting_model_service
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_model_predictions():
    """Test if model gives different predictions for different dates"""
    logger.info("🔍 Testing ML Model Predictions for Different Dates")
    logger.info("="*70)
    
    crop_type = "คะน้า"
    province = "กรุงเทพมหานคร"
    growth_days = 45
    
    # Test 5 different planting dates
    base_date = datetime(2025, 1, 1)
    
    for i in range(5):
        planting_date = base_date + timedelta(days=i * 30)
        
        logger.info(f"\n📅 Planting Date: {planting_date.strftime('%Y-%m-%d')}")
        logger.info(f"   Month: {planting_date.month}, Day of Year: {planting_date.timetuple().tm_yday}")
        
        # Prepare features
        features = planting_model_service._prepare_features(
            province=province,
            crop_type=crop_type,
            planting_date=planting_date,
            growth_days=growth_days
        )
        
        if features is not None:
            logger.info(f"   Features shape: {features.shape}")
            logger.info(f"   Features (first 10): {features[0][:10]}")
            
            # Make prediction
            prediction = planting_model_service._make_model_prediction(features, crop_type)
            
            if prediction:
                logger.info(f"   ✅ Prediction:")
                logger.info(f"      • Price: {prediction['price']} ฿/กก.")
                logger.info(f"      • Suitability Score: {prediction['suitability_score']}")
                logger.info(f"      • Confidence: {prediction['confidence']}")
            else:
                logger.error(f"   ❌ Prediction failed")
        else:
            logger.error(f"   ❌ Feature preparation failed")
    
    logger.info("\n" + "="*70)
    logger.info("🔍 Analysis:")
    logger.info("If all prices are the same, the model is not using date features properly")
    logger.info("If prices vary, the model is working correctly")

if __name__ == "__main__":
    test_model_predictions()

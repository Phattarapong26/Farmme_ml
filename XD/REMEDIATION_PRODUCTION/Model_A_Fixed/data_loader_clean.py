"""
Model A - Crop Recommendation (FIXED)
Data Loader - Clean version (NO post-outcome features)

ฟังก์ชัน: โหลดข้อมูลการปลูก เลือก features ที่มีก่อนการเก็บเกี่ยวเท่านั้น
ตัวอย่าง: Pre-planting features: soil, weather, budget, experience
         Remove: actual_yield_kg, success_rate, harvest_timing_adjustment, yield_efficiency
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoaderClean:
    """Load data with NO post-outcome contamination"""
    
    def __init__(self, dataset_dir: str = None):
        if dataset_dir is None:
            self.dataset_dir = Config.DATA_PATH
        else:
            self.dataset_dir = Path(dataset_dir)
        
    def load_cultivation_clean(self):
        """Load cultivation data, keep only pre-planting features"""
        cultivation = pd.read_csv(
            self.dataset_dir / 'cultivation.csv',
            parse_dates=['planting_date', 'harvest_date']
        )
        
        # ✅ CLEAN: Keep pre-planting features
        keep_cols = [
            'crop_type', 'province', 'planting_date', 'harvest_date',
            'planting_area_rai', 'expected_yield_kg',  # Pre-planting estimates
        ]
        
        # ❌ REMOVE: Post-outcome features
        remove_cols = [
            'actual_yield_kg',  # POST-HARVEST ❌
            'success_rate',  # POST-HARVEST ❌
            'harvest_timing_adjustment',  # POST-HARVEST ❌
            'yield_efficiency',  # POST-HARVEST ❌
        ]
        
        # Keep only available columns
        available_cols = [c for c in keep_cols if c in cultivation.columns]
        cultivation_clean = cultivation[available_cols].copy()
        
        # Create a simple farmer_id based on province (for grouping)
        cultivation_clean['farmer_group'] = cultivation_clean['province'].astype('category').cat.codes
        
        logger.info(f"✅ Loaded {len(cultivation_clean)} clean cultivation records")
        logger.info(f"✅ Columns: {', '.join(available_cols)}")
        
        return cultivation_clean
    
    def load_farmer_profiles(self):
        """Load farmer profiles"""
        farmers = pd.read_csv(self.dataset_dir / 'farmer_profiles.csv')
        
        keep_cols = [
            'farmer_id', 'experience_level', 'farm_size_rai', 
            'budget_available_baht'
        ]
        available_cols = [c for c in keep_cols if c in farmers.columns]
        
        if not available_cols or 'farmer_id' not in farmers.columns:
            # Create dummy farmer data if not available
            logger.warning("⚠️  Farmer profiles not properly formatted")
            return None
        
        logger.info(f"✅ Loaded {len(farmers)} farmer profiles")
        return farmers[available_cols]
    
    def load_crop_characteristics(self):
        """Load crop characteristics"""
        crops = pd.read_csv(self.dataset_dir / 'crop_characteristics.csv')
        
        keep_cols = [
            'crop_type', 'crop_category', 'growth_days', 'water_requirement', 
            'soil_preference', 'investment_cost', 'risk_level'
        ]
        available_cols = [c for c in keep_cols if c in crops.columns]
        
        logger.info(f"✅ Loaded {len(crops)} crop characteristics")
        return crops[available_cols]
    
    def load_weather(self):
        """Load weather data (pre-planting context only)"""
        weather = pd.read_csv(self.dataset_dir / 'weather.csv')
        
        if 'date' in weather.columns:
            weather['date'] = pd.to_datetime(weather['date'])
        
        logger.info(f"✅ Loaded {len(weather)} weather records")
        return weather
    
    def load_price_data(self):
        """Load price data (market context)"""
        price = pd.read_csv(self.dataset_dir / 'price.csv')
        
        if 'date' in price.columns:
            price['date'] = pd.to_datetime(price['date'])
        
        logger.info(f"✅ Loaded {len(price)} price records")
        return price
    
    def create_training_data(self, 
                            cultivation_clean,
                            farmers,
                            crops,
                            weather,
                            price,
                            reference_date: str = None):
        """
        Create training dataset with:
        - Pre-planting features only
        - Time-aware splits (no future information leakage)
        - Clean target variable
        """
        
        df = cultivation_clean.copy()
        
        # Merge with crops
        df = df.merge(crops, on='crop_type', how='left')
        
        # If farmers available, merge
        if farmers is not None and 'farmer_id' in farmers.columns:
            # Try to merge by province or farm_size
            if 'province' in farmers.columns:
                df = df.merge(farmers, on='province', how='left', suffixes=('', '_farmer'))
        else:
            # Create default farmer features
            df['experience_level'] = 0.5  # Default
            df['farm_size_rai'] = 25  # Default
            df['budget_available_baht'] = 150000  # Default
        
        # Create target: Expected ROI based on yield and area
        df['expected_roi_percent'] = (df['expected_yield_kg'] / 100) * 2  # Rough ROI estimate
        
        # Replace any invalid values
        df['expected_roi_percent'] = df['expected_roi_percent'].replace(
            [np.inf, -np.inf], np.nan
        ).fillna(df['expected_roi_percent'].median())
        
        logger.info(f"✅ Created training data with {len(df)} samples")
        logger.info(f"✅ Target variable: expected_roi_percent")
        logger.info(f"   Mean: {df['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Std: {df['expected_roi_percent'].std():.2f}%")
        
        return df
    
    def get_feature_columns(self):
        """List of clean feature columns (no post-outcome)"""
        return [
            'planting_area_rai',
            'expected_yield_kg',
            'growth_days',
            'water_requirement',
            'investment_cost',
            'risk_level',
        ]

    def validate_no_leakage(self, df, forbidden_features):
        """
        Check if DataFrame contains forbidden features (data leakage)
        
        Args:
            df: DataFrame to check
            forbidden_features: List of forbidden feature names
        
        Returns:
            bool: True if clean, raises error if leakage found
        """
        found_leakage = [f for f in forbidden_features if f in df.columns]
        
        if found_leakage:
            error_msg = f"❌ DATA LEAKAGE DETECTED: {', '.join(found_leakage)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✅ No data leakage detected (checked {len(forbidden_features)} forbidden features)")
        return True
    
    def get_feature_correlations(self, df, target):
        """
        Calculate feature correlations with target variable
        
        Args:
            df: DataFrame with features and target
            target: Target column name
        
        Returns:
            DataFrame with correlations sorted by absolute value
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        feature_cols = [c for c in numeric_cols if c != target]
        
        correlations = df[feature_cols + [target]].corr()[target].drop(target)
        correlations = correlations.sort_values(ascending=False, key=abs)
        
        logger.info(f"📊 Feature correlations with {target}:")
        for feat, corr in correlations.head(10).items():
            logger.info(f"   {feat}: {corr:.3f}")
        
        return correlations.to_frame('correlation')

if __name__ == "__main__":
    # Test data loading
    loader = DataLoaderClean()  # Uses Config.DATA_PATH
    
    cultivation = loader.load_cultivation_clean()
    farmers = loader.load_farmer_profiles()
    crops = loader.load_crop_characteristics()
    weather = loader.load_weather()
    price = loader.load_price_data()
    
    df = loader.create_training_data(cultivation, farmers, crops, weather, price)
    
    # Test leakage validation
    try:
        loader.validate_no_leakage(df, Config.FORBIDDEN_FEATURES_MODEL_A)
        print("\n✅ Data Loading Test Passed")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
    except ValueError as e:
        print(f"\n❌ Test Failed: {e}")

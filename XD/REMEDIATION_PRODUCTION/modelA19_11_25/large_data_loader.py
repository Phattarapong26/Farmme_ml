"""
Large Data Loader for Model A
Uses FARMME_GPU_DATASET.csv (2.2M+ rows) for training
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LargeDataLoader:
    """Load large FARMME_GPU_DATASET for Model A training"""
    
    def __init__(self, dataset_path=None):
        """
        Initialize large data loader
        
        Args:
            dataset_path: Path to FARMME_GPU_DATASET.csv
        """
        if dataset_path is None:
            self.dataset_path = Config.DATA_PATH / 'FARMME_GPU_DATASET.csv'
        else:
            self.dataset_path = Path(dataset_path)
            
    def load_and_prepare(self, sample_size=None) -> pd.DataFrame:
        """
        Load and prepare large dataset for Model A
        
        Args:
            sample_size: Optional - limit number of rows (None = load all)
            
        Returns:
            pd.DataFrame: Prepared dataset
        """
        logger.info(f"📥 Loading FARMME_GPU_DATASET...")
        
        # Load dataset
        if sample_size:
            logger.info(f"   Sampling {sample_size:,} rows...")
            df = pd.read_csv(self.dataset_path, nrows=sample_size)
        else:
            logger.info(f"   Loading ALL rows (this may take a while)...")
            df = pd.read_csv(self.dataset_path)
        
        logger.info(f"✅ Loaded {len(df):,} rows")
        
        # Parse date
        df['date'] = pd.to_datetime(df['date'])
        
        # Create features for Model A
        df_model_a = self._create_model_a_features(df)
        
        # Validate no leakage
        self._validate_no_leakage(df_model_a)
        
        logger.info(f"✅ Prepared {len(df_model_a):,} samples for Model A")
        logger.info(f"   Features: {df_model_a.shape[1]} columns")
        logger.info(f"   Date range: {df_model_a['date'].min()} to {df_model_a['date'].max()}")
        
        return df_model_a
    
    def _create_model_a_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create Model A features from FARMME_GPU_DATASET
        
        Model A predicts ROI based on:
        - Crop characteristics
        - Market conditions
        - Weather
        - Economic factors
        """
        logger.info("🔧 Creating Model A features...")
        
        # Select relevant features (pre-planting only, no future information)
        features = df[[
            'date',
            'province',
            'crop_type',
            'crop_id',
            'base_price',  # Historical base price
            'inventory_level',
            'storage_level',
            'planting_activity',
            'supply_level',
            'demand_elasticity',
            'income_elasticity',
            'temperature_celsius',
            'rainfall_mm',
            'humidity_percent',
            'drought_index',
            'fuel_price',
            'fertilizer_price',
            'inflation_rate',
            'gdp_growth',
            'unemployment_rate',
            'vegetable_demand_index',
            'herb_demand_index',
            'baht_usd_rate',
            'avg_income',
            'income_inequality',
            'rural_share',
        ]].copy()
        
        # Create synthetic planting features (simulate cultivation data)
        np.random.seed(42)
        features['planting_area_rai'] = np.random.uniform(5, 50, len(features))
        features['expected_yield_kg'] = features['planting_area_rai'] * np.random.uniform(800, 1500, len(features))
        
        # Add crop characteristics (from crop_id)
        features['growth_days'] = 60 + (features['crop_id'] % 10) * 10  # 60-150 days
        features['water_requirement'] = 0.3 + (features['crop_id'] % 5) * 0.15  # 0.3-0.9
        features['investment_cost'] = features['planting_area_rai'] * np.random.uniform(5000, 15000, len(features))
        features['risk_level'] = 0.2 + (features['crop_id'] % 4) * 0.2  # 0.2-0.8
        
        # Create target: Expected ROI
        # ROI = (Expected Revenue - Investment Cost) / Investment Cost * 100
        features['expected_revenue'] = features['expected_yield_kg'] * features['base_price']
        features['expected_roi_percent'] = (
            (features['expected_revenue'] - features['investment_cost']) / 
            features['investment_cost'] * 100
        )
        
        # Clean invalid values
        features['expected_roi_percent'] = features['expected_roi_percent'].replace(
            [np.inf, -np.inf], np.nan
        )
        
        # Remove extreme outliers (keep ROI between -100% and 500%)
        features = features[
            (features['expected_roi_percent'] >= -100) & 
            (features['expected_roi_percent'] <= 500)
        ].copy()
        
        # Fill remaining NaN with median
        features['expected_roi_percent'] = features['expected_roi_percent'].fillna(
            features['expected_roi_percent'].median()
        )
        
        logger.info(f"   Target variable (expected_roi_percent):")
        logger.info(f"   Mean: {features['expected_roi_percent'].mean():.2f}%")
        logger.info(f"   Std: {features['expected_roi_percent'].std():.2f}%")
        logger.info(f"   Min: {features['expected_roi_percent'].min():.2f}%")
        logger.info(f"   Max: {features['expected_roi_percent'].max():.2f}%")
        
        return features
    
    def _validate_no_leakage(self, df: pd.DataFrame):
        """Validate that no post-outcome features are present"""
        forbidden_features = [
            'price_next_day',  # Future price
            'actual_yield_kg',
            'success_rate',
            'harvest_timing_adjustment',
            'yield_efficiency',
            'actual_revenue',
            'actual_profit',
        ]
        
        found_leakage = [f for f in forbidden_features if f in df.columns]
        
        if found_leakage:
            error_msg = f"❌ DATA LEAKAGE DETECTED: {', '.join(found_leakage)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✅ No data leakage detected")
    
    def get_feature_columns(self):
        """List of feature columns for training"""
        return [
            'planting_area_rai',
            'expected_yield_kg',
            'growth_days',
            'water_requirement',
            'investment_cost',
            'risk_level',
            'base_price',
            'inventory_level',
            'supply_level',
            'demand_elasticity',
            'temperature_celsius',
            'rainfall_mm',
            'humidity_percent',
            'drought_index',
            'fuel_price',
            'fertilizer_price',
            'inflation_rate',
            'gdp_growth',
            'unemployment_rate',
        ]

if __name__ == "__main__":
    # Test large data loader
    loader = LargeDataLoader()
    
    # Test with sample
    df = loader.load_and_prepare(sample_size=10000)
    
    print(f"\n✅ Large Data Loader Test Passed")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:10]}...")
    print(f"Target stats: mean={df['expected_roi_percent'].mean():.2f}%, std={df['expected_roi_percent'].std():.2f}%")

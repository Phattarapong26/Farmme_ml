"""
Minimal Data Loader for Model A Retraining
Uses stratified sampling to create minimal dataset (max 1000 samples)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from Model_A_Fixed.data_loader_clean import DataLoaderClean
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalDataLoader:
    """Load and sample minimal dataset with stratified sampling"""
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize minimal data loader
        
        Args:
            max_samples: Maximum number of samples to keep (default: 1000)
        """
        self.max_samples = max_samples
        self.base_loader = DataLoaderClean()
        self.original_size = 0
        self.sampled_size = 0
        
    def load_and_sample(self) -> pd.DataFrame:
        """
        Load full dataset and sample to minimal size using stratified sampling
        
        Returns:
            pd.DataFrame: Sampled dataset
        """
        logger.info(f"📥 Loading full dataset...")
        
        # Load all datasets using base loader
        cultivation = self.base_loader.load_cultivation_clean()
        farmers = self.base_loader.load_farmer_profiles()
        crops = self.base_loader.load_crop_characteristics()
        weather = self.base_loader.load_weather()
        price = self.base_loader.load_price_data()
        
        # Create full training dataset
        df_full = self.base_loader.create_training_data(
            cultivation, farmers, crops, weather, price
        )
        
        self.original_size = len(df_full)
        logger.info(f"✅ Loaded {self.original_size} total records")
        
        # Sample if dataset is larger than max_samples
        if len(df_full) > self.max_samples:
            logger.info(f"🎯 Sampling to {self.max_samples} records using stratified sampling...")
            df_sampled = self._stratified_sample(df_full)
        else:
            logger.info(f"✅ Dataset size ({len(df_full)}) <= max_samples ({self.max_samples}), using full dataset")
            df_sampled = df_full
        
        self.sampled_size = len(df_sampled)
        
        # Validate sample
        self.validate_sample(df_full, df_sampled)
        
        # Log statistics
        self._log_statistics(df_full, df_sampled)
        
        return df_sampled
    
    def _stratified_sample(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform stratified sampling by crop_type
        
        Args:
            df: Full dataset
            
        Returns:
            pd.DataFrame: Sampled dataset
        """
        # Use crop_type for stratification
        if 'crop_type' not in df.columns:
            logger.warning("⚠️  crop_type not found, using random sampling")
            return df.sample(n=self.max_samples, random_state=42)
        
        # Calculate samples per crop type (proportional)
        crop_counts = df['crop_type'].value_counts()
        crop_proportions = crop_counts / len(df)
        
        samples_per_crop = (crop_proportions * self.max_samples).round().astype(int)
        
        # Adjust to ensure total equals max_samples
        while samples_per_crop.sum() > self.max_samples:
            # Reduce from largest group
            max_idx = samples_per_crop.idxmax()
            samples_per_crop[max_idx] -= 1
        
        while samples_per_crop.sum() < self.max_samples:
            # Add to largest group
            max_idx = samples_per_crop.idxmax()
            samples_per_crop[max_idx] += 1
        
        # Sample from each crop type
        sampled_dfs = []
        for crop_type, n_samples in samples_per_crop.items():
            crop_df = df[df['crop_type'] == crop_type]
            if len(crop_df) >= n_samples:
                sampled = crop_df.sample(n=n_samples, random_state=42)
            else:
                # If not enough samples, take all
                sampled = crop_df
            sampled_dfs.append(sampled)
        
        df_sampled = pd.concat(sampled_dfs, ignore_index=True)
        
        # Shuffle
        df_sampled = df_sampled.sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info(f"✅ Stratified sampling complete: {len(df_sampled)} samples")
        
        return df_sampled
    
    def validate_sample(self, df_full: pd.DataFrame, df_sampled: pd.DataFrame) -> bool:
        """
        Validate that sample maintains crop distribution
        
        Args:
            df_full: Original full dataset
            df_sampled: Sampled dataset
            
        Returns:
            bool: True if validation passes
        """
        logger.info("🔍 Validating sample distribution...")
        
        if 'crop_type' not in df_full.columns:
            logger.warning("⚠️  Cannot validate distribution (crop_type not found)")
            return True
        
        # Compare crop type distributions
        full_dist = df_full['crop_type'].value_counts(normalize=True).sort_index()
        sample_dist = df_sampled['crop_type'].value_counts(normalize=True).sort_index()
        
        # Calculate maximum difference
        common_crops = set(full_dist.index) & set(sample_dist.index)
        max_diff = 0
        for crop in common_crops:
            diff = abs(full_dist[crop] - sample_dist[crop])
            max_diff = max(max_diff, diff)
        
        logger.info(f"✅ Distribution validation:")
        logger.info(f"   Max difference: {max_diff:.4f} ({max_diff*100:.2f}%)")
        
        if max_diff > 0.15:  # 15% threshold
            logger.warning(f"⚠️  Large distribution difference detected: {max_diff:.4f}")
        else:
            logger.info(f"✅ Distribution maintained (difference < 15%)")
        
        return True
    
    def _log_statistics(self, df_full: pd.DataFrame, df_sampled: pd.DataFrame):
        """Log comparison statistics between full and sampled datasets"""
        logger.info("\n" + "="*70)
        logger.info("DATASET STATISTICS COMPARISON".center(70))
        logger.info("="*70)
        
        logger.info(f"\n📊 Size:")
        logger.info(f"   Original: {len(df_full):,} samples")
        logger.info(f"   Sampled:  {len(df_sampled):,} samples")
        logger.info(f"   Ratio:    {len(df_sampled)/len(df_full)*100:.1f}%")
        
        # Target variable statistics
        if 'expected_roi_percent' in df_full.columns:
            logger.info(f"\n📊 Target Variable (expected_roi_percent):")
            logger.info(f"   Original - Mean: {df_full['expected_roi_percent'].mean():.2f}%, Std: {df_full['expected_roi_percent'].std():.2f}%")
            logger.info(f"   Sampled  - Mean: {df_sampled['expected_roi_percent'].mean():.2f}%, Std: {df_sampled['expected_roi_percent'].std():.2f}%")
        
        # Crop type distribution
        if 'crop_type' in df_full.columns:
            logger.info(f"\n📊 Crop Type Distribution:")
            full_crops = df_full['crop_type'].value_counts()
            sample_crops = df_sampled['crop_type'].value_counts()
            
            for crop in full_crops.index[:5]:  # Top 5 crops
                full_pct = full_crops[crop] / len(df_full) * 100
                sample_pct = sample_crops.get(crop, 0) / len(df_sampled) * 100
                logger.info(f"   {crop}: {full_pct:.1f}% → {sample_pct:.1f}%")
        
        logger.info("="*70 + "\n")

if __name__ == "__main__":
    # Test minimal data loader
    loader = MinimalDataLoader(max_samples=1000)
    df = loader.load_and_sample()
    
    print(f"\n✅ Minimal Data Loader Test Passed")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")

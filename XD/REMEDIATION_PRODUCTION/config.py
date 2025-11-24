"""
Configuration file for ML Farming Pipeline
All paths, hyperparameters, and settings in one place
"""

from pathlib import Path

class Config:
    """Central configuration for all models and pipeline"""
    
    # ==================== PATHS ====================
    # Base paths (relative to project root)
    BASE_DIR = Path(__file__).parent.parent
    DATA_PATH = BASE_DIR / 'buildingModel.py' / 'Dataset'
    MODEL_PATH = BASE_DIR / 'REMEDIATION_PRODUCTION' / 'trained_models'
    OUTPUT_PATH = BASE_DIR / 'REMEDIATION_PRODUCTION' / 'outputs'
    LOG_PATH = BASE_DIR / 'REMEDIATION_PRODUCTION' / 'logs'
    
    # Ensure directories exist
    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    
    # ==================== MODEL A CONFIG ====================
    MODEL_A_ALGORITHM = 'nsga2'  # Options: 'nsga2', 'xgboost', 'rf'
    MODEL_A_POPULATION_SIZE = 100
    MODEL_A_GENERATIONS = 50
    MODEL_A_EXPECTED_R2_MIN = 0.45
    MODEL_A_EXPECTED_R2_MAX = 0.55
    
    # Minimal training config
    MODEL_A_MINIMAL_SAMPLES = 1000
    MODEL_A_ALGORITHMS = ['xgboost', 'rf_ensemble', 'gradboost']
    BUBBLE_CHART_DPI = 300
    BUBBLE_SIZE_MIN = 100
    BUBBLE_SIZE_MAX = 1000
    
    # ==================== MODEL B CONFIG ====================
    MODEL_B_ALGORITHM = 'xgboost'  # Options: 'xgboost', 'logistic'
    MODEL_B_THRESHOLD = 0.5
    MODEL_B_EXPECTED_F1_MIN = 0.70
    MODEL_B_EXPECTED_F1_MAX = 0.75
    MODEL_B_EMBARGO_DAYS = 7  # Days gap between train/val/test
    
    # ==================== MODEL C CONFIG ====================
    MODEL_C_ALGORITHM = 'prophet'  # Options: 'prophet', 'arima', 'lstm'
    MODEL_C_UPDATE_FREQUENCY = 'daily'
    MODEL_C_FORECAST_HORIZON = 120  # days
    MODEL_C_EXPECTED_R2_MIN = 0.99
    MODEL_C_EXPECTED_RMSE_MAX = 0.30  # baht/kg
    MODEL_C_EXPECTED_MAPE_MAX = 0.005  # 0.5%
    
    # ==================== MODEL D CONFIG ====================
    MODEL_D_ALPHA_INIT = 1.0  # Thompson Sampling prior
    MODEL_D_BETA_INIT = 1.0   # Thompson Sampling prior
    MODEL_D_REWARD_THRESHOLD = 0.8
    MODEL_D_EXPECTED_ACCURACY = 0.68
    MODEL_D_EXPECTED_PROFIT_ERROR = 0.20  # ±20%
    
    # ==================== PIPELINE CONFIG ====================
    PIPELINE_TIMEOUT = 10  # seconds
    ENABLE_FALLBACK = True
    
    # ==================== DATA VALIDATION CONFIG ====================
    MAX_MISSING_VALUES_PERCENT = 5.0  # Maximum 5% missing values allowed
    MIN_FEATURE_CORRELATION = 0.05  # Minimum correlation with target
    OVERFITTING_THRESHOLD = 0.15  # Max gap between train and val metrics
    
    # ==================== MONITORING CONFIG ====================
    DRIFT_THRESHOLD = 0.10  # 10% performance degradation threshold
    PERFORMANCE_LOG_INTERVAL = 100  # Log every N predictions
    
    # ==================== FORBIDDEN FEATURES ====================
    # Features that cause data leakage (post-outcome features)
    FORBIDDEN_FEATURES_MODEL_A = [
        'actual_yield_kg',
        'success_rate',
        'harvest_timing_adjustment',
        'yield_efficiency'
    ]
    
    FORBIDDEN_FEATURES_MODEL_B = [
        'harvest_date',
        'actual_yield_kg',
        'success_rate'
    ]
    
    FORBIDDEN_FEATURES_MODEL_D = [
        'actual_harvest_date',
        'future_price',
        'days_since_planting'  # If calculated from harvest_date
    ]
    
    # ==================== LOGGING CONFIG ====================
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_dataset_path(cls, filename):
        """Get full path to dataset file"""
        return cls.DATA_PATH / filename
    
    @classmethod
    def get_model_path(cls, model_name):
        """Get full path to saved model"""
        return cls.MODEL_PATH / f"{model_name}.pkl"
    
    @classmethod
    def get_output_path(cls, model_name, output_type='evaluation'):
        """Get output directory for model evaluation plots"""
        output_dir = cls.OUTPUT_PATH / f"{model_name}_{output_type}"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    @classmethod
    def get_log_path(cls, log_name):
        """Get full path to log file"""
        return cls.LOG_PATH / f"{log_name}.log"

if __name__ == "__main__":
    print("✅ Configuration loaded successfully")
    print(f"📁 Data Path: {Config.DATA_PATH}")
    print(f"📁 Model Path: {Config.MODEL_PATH}")
    print(f"📁 Output Path: {Config.OUTPUT_PATH}")
    print(f"📁 Log Path: {Config.LOG_PATH}")

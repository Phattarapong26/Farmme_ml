# Design Document

## Overview

ระบบ ML Backend Integration จะแทนที่ legacy model services ใน Backend FastAPI ด้วยโมเดล ML จริงจาก REMEDIATION_PRODUCTION โดยรักษา API interface เดิมไว้เพื่อให้ Frontend ไม่ต้องแก้ไขโค้ด การออกแบบเน้นการสร้าง service layer ที่ wrap โมเดล ML และให้ fallback mechanisms เมื่อโมเดลมีปัญหา

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Backend FastAPI Application                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  API Endpoints Layer                      │  │
│  │  /recommend-planting-date  /models  /predictions         │  │
│  │  /api/v1/harvest-decision (NEW)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ML Model Service Layer                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Model A  │ │ Model B  │ │ Model C  │ │ Model D  │   │  │
│  │  │ Service  │ │ Service  │ │ Service  │ │ Service  │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Model Loading & Caching                      │  │
│  │  - Load .pkl files from REMEDIATION_PRODUCTION           │  │
│  │  - Cache loaded models in memory                         │  │
│  │  - Fallback to legacy models if loading fails           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              REMEDIATION_PRODUCTION/trained_models/             │
│  model_a_xgboost.pkl  model_b_xgboost.pkl                      │
│  model_c_price_forecast.pkl  model_d_thompson_sampling.pkl     │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Backward Compatibility**: รักษา existing API endpoints ไว้
2. **Gradual Migration**: แทนที่ทีละ service โดยไม่ทำลาย existing functionality
3. **Fallback Strategy**: ถ้าโมเดลใหม่ fail ให้ fallback ไปใช้ legacy model
4. **Minimal Frontend Changes**: Frontend ไม่ต้องแก้ไขโค้ด
5. **Clean Architecture**: แยก service layer ออกจาก API layer

## Architecture

### Component Overview


ระบบประกอบด้วย 6 components หลัก:

1. **ML Model Service Layer**: Service classes ที่ wrap โมเดล ML
2. **Model Loader**: โหลดและ cache โมเดลจาก .pkl files
3. **API Endpoints**: FastAPI routes ที่เรียกใช้ services
4. **Request/Response Models**: Pydantic models สำหรับ validation
5. **Error Handling**: จัดการ errors และ fallback mechanisms
6. **Configuration**: Environment variables และ path configuration

### Replacement Strategy

**Phase 1: Replace Model A (Crop Recommendation)**
- แทนที่ `recommendation_model_service.py`
- ใช้ Model A (XGBoost, Random Forest, NSGA-II)
- รักษา existing endpoint interface

**Phase 2: Replace Model B (Planting Calendar)**
- แทนที่ `planting_model_service.py`
- ใช้ Model B (XGBoost Classifier, Temporal GB)
- รักษา `/recommend-planting-date` endpoint

**Phase 3: Replace Model C (Price Prediction)**
- แทนที่ `price_prediction_service.py`
- ใช้ Model C (Time Series Forecasting)
- รักษา existing price prediction endpoints

**Phase 4: Add Model D (Harvest Decision)**
- เพิ่ม endpoint ใหม่ `/api/v1/harvest-decision`
- ใช้ Model D (Thompson Sampling)
- Feature ใหม่ที่ไม่มีใน legacy system

## Components and Interfaces

### 1. ML Model Service Layer

**Purpose**: Wrap โมเดล ML และให้ interface สำหรับ API endpoints

#### Model A Service - Crop Recommendation

```python
# backend/app/services/model_a_service.py

from typing import Dict, Any, List, Optional
import numpy as np
import pickle
import logging

logger = logging.getLogger(__name__)

class ModelAService:
    """Service for Model A - Crop Recommendation"""
    
    def __init__(self, model_path: str = None):
        self.model_xgboost = None
        self.model_rf = None
        self.model_nsga2 = None
        self.model_loaded = False
        self.model_path = model_path or self._get_default_path()
        
        # Load models
        self._load_models()
    
    def _get_default_path(self) -> str:
        """Get default model path"""
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(backend_dir, "..", "REMEDIATION_PRODUCTION", "trained_models")
    
    def _load_models(self):
        """Load Model A trained models"""
        try:
            import os
            
            # Load XGBoost (primary)
            xgb_path = os.path.join(self.model_path, "model_a_xgboost.pkl")
            if os.path.exists(xgb_path):
                with open(xgb_path, 'rb') as f:
                    self.model_xgboost = pickle.load(f)
                logger.info(f"✅ Model A XGBoost loaded from {xgb_path}")
            
            # Load Random Forest (fallback)
            rf_path = os.path.join(self.model_path, "model_a_rf_ensemble.pkl")
            if os.path.exists(rf_path):
                with open(rf_path, 'rb') as f:
                    self.model_rf = pickle.load(f)
                logger.info(f"✅ Model A Random Forest loaded from {rf_path}")
            
            self.model_loaded = (self.model_xgboost is not None or self.model_rf is not None)
            
        except Exception as e:
            logger.error(f"❌ Failed to load Model A: {e}")
            self.model_loaded = False
    
    def get_recommendations(
        self,
        province: str,
        soil_type: str,
        soil_ph: float,
        budget_baht: float,
        farmer_experience_years: int,
        farm_size_rai: float = 10.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get crop recommendations
        
        Returns format compatible with existing API:
        {
            "success": True,
            "recommendations": [
                {
                    "crop_type": str,
                    "suitability_score": float,
                    "expected_yield_kg_per_rai": int,
                    "estimated_revenue_per_rai": int,
                    "roi_percent": float,
                    "risk_score": float,
                    "total_profit_baht": float,
                    "confidence": float,
                    "reasons": List[str]
                }
            ],
            "model_used": str,
            "confidence": float
        }
        """
        try:
            if not self.model_loaded:
                return self._fallback_recommendations(province, soil_type, budget_baht)
            
            # Prepare features
            features = self._prepare_features(
                province, soil_type, soil_ph, budget_baht,
                farmer_experience_years, farm_size_rai, **kwargs
            )
            
            # Try XGBoost first
            if self.model_xgboost:
                try:
                    predictions = self.model_xgboost.predict(features)
                    recommendations = self._format_recommendations(
                        predictions, farm_size_rai, "xgboost"
                    )
                    return recommendations
                except Exception as e:
                    logger.warning(f"XGBoost prediction failed: {e}, trying Random Forest")
            
            # Fallback to Random Forest
            if self.model_rf:
                try:
                    predictions = self.model_rf.predict(features)
                    recommendations = self._format_recommendations(
                        predictions, farm_size_rai, "random_forest"
                    )
                    return recommendations
                except Exception as e:
                    logger.error(f"Random Forest prediction failed: {e}")
            
            # Final fallback
            return self._fallback_recommendations(province, soil_type, budget_baht)
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {e}")
            return self._fallback_recommendations(province, soil_type, budget_baht)
    
    def _prepare_features(self, province, soil_type, soil_ph, budget_baht,
                         farmer_experience_years, farm_size_rai, **kwargs) -> np.ndarray:
        """Prepare features for Model A"""
        # Implementation details...
        pass
    
    def _format_recommendations(self, predictions, farm_size_rai, model_used) -> Dict:
        """Format predictions to match API response"""
        # Implementation details...
        pass
    
    def _fallback_recommendations(self, province, soil_type, budget_baht) -> Dict:
        """Fallback to legacy recommendation logic"""
        from recommendation_model_service import recommendation_model_service
        return recommendation_model_service.get_recommendations(
            province=province,
            soil_type=soil_type,
            budget_level=self._map_budget_level(budget_baht)
        )
    
    def _map_budget_level(self, budget_baht: float) -> str:
        """Map budget to level"""
        if budget_baht < 50000:
            return "ต่ำ"
        elif budget_baht < 200000:
            return "ปานกลาง"
        else:
            return "สูง"
```



#### Model B Service - Planting Calendar

```python
# backend/app/services/model_b_service.py

class ModelBService:
    """Service for Model B - Planting Window Classification"""
    
    def __init__(self, model_path: str = None):
        self.model_logistic = None  # Primary (F1=0.868, best performance)
        self.model_xgboost = None   # Fallback option 1
        self.model_temporal_gb = None  # Fallback option 2
        self.model_loaded = False
        self.model_path = model_path or self._get_default_path()
        
        self._load_models()
    
    def _load_models(self):
        """Load Model B trained models"""
        try:
            import os
            import pickle
            
            # Load Logistic Regression (primary - best F1 score 0.868)
            logistic_path = os.path.join(self.model_path, "model_b_logistic.pkl")
            if os.path.exists(logistic_path):
                with open(logistic_path, 'rb') as f:
                    self.model_logistic = pickle.load(f)
                logger.info(f"✅ Model B Logistic Regression loaded (F1=0.868)")
            
            # Load XGBoost (fallback 1)
            xgb_path = os.path.join(self.model_path, "model_b_xgboost.pkl")
            if os.path.exists(xgb_path):
                with open(xgb_path, 'rb') as f:
                    self.model_xgboost = pickle.load(f)
                logger.info(f"✅ Model B XGBoost loaded (fallback)")
            
            # Load Temporal GB (fallback 2)
            tgb_path = os.path.join(self.model_path, "model_b_temporal_gb.pkl")
            if os.path.exists(tgb_path):
                with open(tgb_path, 'rb') as f:
                    self.model_temporal_gb = pickle.load(f)
                logger.info(f"✅ Model B Temporal GB loaded (fallback)")
            
            self.model_loaded = (self.model_logistic is not None)
            
        except Exception as e:
            logger.error(f"❌ Failed to load Model B: {e}")
            self.model_loaded = False
    
    def get_planting_recommendations(
        self,
        crop_type: str,
        province: str,
        growth_days: int,
        start_date: datetime = None,
        end_date: datetime = None,
        top_n: int = 5,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get planting date recommendations
        
        Returns format compatible with /recommend-planting-date:
        {
            "success": True,
            "province": str,
            "crop_type": str,
            "growth_days": int,
            "recommendations": [
                {
                    "planting_date": str,
                    "harvest_date": str,
                    "classification": str,  # Good/Bad
                    "confidence": float,
                    "expected_germination_rate": float,
                    "predicted_price": float,
                    "total_score": float,
                    "season": str,
                    "reasons": List[str]
                }
            ],
            "model_used": str
        }
        """
        try:
            if not self.model_loaded:
                return self._fallback_planting_recommendations(
                    crop_type, province, growth_days, start_date, end_date, top_n
                )
            
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=365)
            
            recommendations = []
            current_date = start_date
            
            # Evaluate planting dates
            while current_date <= end_date and len(recommendations) < top_n * 2:
                # Prepare features for this date
                features = self._prepare_features(
                    crop_type, province, current_date, db
                )
                
                # Predict classification (Good/Bad)
                # Try Logistic Regression first (best performance)
                model_to_use = self.model_logistic or self.model_xgboost or self.model_temporal_gb
                
                if model_to_use:
                    try:
                        prediction = model_to_use.predict(features)[0]
                        proba = model_to_use.predict_proba(features)[0] if hasattr(model_to_use, 'predict_proba') else [0.5, 0.5]
                        
                        classification = "Good" if prediction == 1 else "Bad"
                        confidence = float(proba[prediction])
                        
                        if classification == "Good":
                            harvest_date = current_date + timedelta(days=growth_days)
                            
                            recommendations.append({
                                "planting_date": current_date.strftime("%Y-%m-%d"),
                                "harvest_date": harvest_date.strftime("%Y-%m-%d"),
                                "classification": classification,
                                "confidence": round(confidence, 3),
                                "expected_germination_rate": round(confidence * 0.95, 3),
                                "predicted_price": self._estimate_price(crop_type, harvest_date),
                                "total_score": round(confidence, 3),
                                "season": self._get_season_name(current_date.month),
                                "reasons": self._generate_reasons(classification, confidence)
                            })
                    except Exception as e:
                        logger.warning(f"Prediction failed for {current_date}: {e}")
                
                current_date += timedelta(days=7)  # Check weekly
            
            # Sort by total score and take top N
            recommendations.sort(key=lambda x: x['total_score'], reverse=True)
            recommendations = recommendations[:top_n]
            
            return {
                "success": True,
                "province": province,
                "crop_type": crop_type,
                "growth_days": growth_days,
                "recommendations": recommendations,
                "model_used": "model_b_logistic" if self.model_logistic else "model_b_xgboost",
                "model_version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"Error in get_planting_recommendations: {e}")
            return self._fallback_planting_recommendations(
                crop_type, province, growth_days, start_date, end_date, top_n
            )
    
    def _prepare_features(self, crop_type, province, planting_date, db) -> np.ndarray:
        """Prepare features for Model B"""
        # Get weather data from database or use seasonal averages
        # Add temporal features (month_sin, month_cos, day_sin, day_cos)
        # Implementation details...
        pass
    
    def _fallback_planting_recommendations(self, crop_type, province, growth_days,
                                          start_date, end_date, top_n) -> Dict:
        """Fallback to legacy planting service"""
        from planting_model_service import planting_model_service
        return planting_model_service.predict_planting_schedule(
            province=province,
            crop_type=crop_type,
            growth_days=growth_days,
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )
```



#### Model C Service - Price Forecast

```python
# backend/app/services/model_c_service.py

class ModelCService:
    """Service for Model C - Price Forecast"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_loaded = False
        self.model_path = model_path or self._get_default_path()
        
        self._load_model()
    
    def _load_model(self):
        """Load Model C trained model"""
        try:
            import os
            import pickle
            
            model_file = os.path.join(self.model_path, "model_c_price_forecast.pkl")
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"✅ Model C Price Forecast loaded")
                self.model_loaded = True
            else:
                logger.warning(f"⚠️ Model C file not found: {model_file}")
                self.model_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Failed to load Model C: {e}")
            self.model_loaded = False
    
    def predict_price(
        self,
        crop_type: str,
        province: str,
        days_ahead: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Predict crop price for future dates
        
        Returns format compatible with existing price prediction API:
        {
            "success": True,
            "crop_type": str,
            "province": str,
            "predictions": [
                {
                    "days_ahead": int,
                    "predicted_price": float,
                    "confidence": float,
                    "price_range": {
                        "min": float,
                        "max": float
                    }
                }
            ],
            "current_price": float,
            "price_trend": str,  # increasing/decreasing/stable
            "trend_percentage": float,
            "market_insights": List[str],
            "best_selling_period": str,
            "model_used": str
        }
        """
        try:
            if not self.model_loaded:
                return self._fallback_price_prediction(crop_type, province, days_ahead)
            
            # Get historical prices from database
            historical_prices = self._get_historical_prices(crop_type, province, db)
            
            # Generate predictions for multiple timeframes
            predictions = []
            for days in [7, 30, 90, 180]:
                if days > days_ahead:
                    break
                
                # Prepare features
                features = self._prepare_features(
                    crop_type, province, days, historical_prices
                )
                
                # Make prediction
                if hasattr(self.model, 'predict'):
                    predicted_price = self.model.predict(features)[0]
                    confidence = self._calculate_confidence(days, historical_prices)
                    price_range = self._calculate_price_range(predicted_price, confidence)
                    
                    predictions.append({
                        "days_ahead": days,
                        "predicted_price": round(float(predicted_price), 2),
                        "confidence": round(confidence, 2),
                        "price_range": {
                            "min": round(price_range[0], 2),
                            "max": round(price_range[1], 2)
                        }
                    })
            
            if not predictions:
                return self._fallback_price_prediction(crop_type, province, days_ahead)
            
            # Analyze trend
            current_price = historical_prices[-1] if historical_prices else predictions[0]["predicted_price"]
            trend_analysis = self._analyze_price_trend(current_price, predictions)
            
            return {
                "success": True,
                "crop_type": crop_type,
                "province": province,
                "predictions": predictions,
                "current_price": round(float(current_price), 2),
                "price_trend": trend_analysis["trend"],
                "trend_percentage": trend_analysis["percentage"],
                "market_insights": self._generate_market_insights(crop_type, predictions, trend_analysis),
                "best_selling_period": self._recommend_selling_period(predictions),
                "model_used": "model_c_price_forecast",
                "confidence": round(np.mean([p["confidence"] for p in predictions]), 2)
            }
            
        except Exception as e:
            logger.error(f"Error in predict_price: {e}")
            return self._fallback_price_prediction(crop_type, province, days_ahead)
    
    def _prepare_features(self, crop_type, province, days_ahead, historical_prices) -> np.ndarray:
        """Prepare features for Model C"""
        # Implementation details...
        pass
    
    def _get_historical_prices(self, crop_type, province, db) -> List[float]:
        """Get historical prices from database"""
        # Implementation details...
        pass
    
    def _fallback_price_prediction(self, crop_type, province, days_ahead) -> Dict:
        """Fallback to legacy price prediction"""
        from price_prediction_service import price_prediction_service
        return price_prediction_service.predict_price(
            crop_type=crop_type,
            province=province,
            days_ahead=days_ahead
        )
```



#### Model D Service - Harvest Decision (NEW)

```python
# backend/app/services/model_d_service.py

class ModelDService:
    """Service for Model D - Harvest Decision Engine"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_loaded = False
        self.model_path = model_path or self._get_default_path()
        
        self._load_model()
    
    def _load_model(self):
        """Load Model D trained model"""
        try:
            import os
            import pickle
            
            model_file = os.path.join(self.model_path, "model_d_thompson_sampling.pkl")
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"✅ Model D Thompson Sampling loaded")
                self.model_loaded = True
            else:
                logger.warning(f"⚠️ Model D file not found: {model_file}")
                self.model_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Failed to load Model D: {e}")
            self.model_loaded = False
    
    def get_harvest_decision(
        self,
        current_price: float,
        forecast_price_median: float,
        forecast_price_std: float,
        plant_health_score: float,
        yield_kg: float,
        storage_cost_per_day: float = 10.0,
        plant_age_days: int = None
    ) -> Dict[str, Any]:
        """
        Get harvest decision recommendation
        
        Returns:
        {
            "success": True,
            "recommended_action": str,  # "Harvest Now", "Wait 3 Days", "Wait 7 Days"
            "action_confidence": float,
            "profit_projections": {
                "harvest_now": float,
                "wait_3_days": float,
                "wait_7_days": float
            },
            "profit_difference": float,
            "risk_assessment": str,
            "reasons": List[str],
            "model_used": str
        }
        """
        try:
            if not self.model_loaded:
                return self._fallback_harvest_decision(
                    current_price, forecast_price_median, yield_kg
                )
            
            # Prepare context for Thompson Sampling
            context = {
                'current_price': current_price,
                'forecast_price_median': forecast_price_median,
                'forecast_price_std': forecast_price_std,
                'plant_health_score': plant_health_score,
                'yield_kg': yield_kg,
                'storage_cost_per_day': storage_cost_per_day,
                'plant_age_days': plant_age_days or 90
            }
            
            # Get decision from Thompson Sampling
            if hasattr(self.model, 'decide'):
                decision = self.model.decide(context)
                
                return {
                    "success": True,
                    "recommended_action": decision['recommended_action'],
                    "action_confidence": round(decision['action_confidence'], 3),
                    "profit_projections": decision['profit_projections'],
                    "profit_difference": round(
                        decision['profit_projections'][decision['recommended_action'].lower().replace(' ', '_')] -
                        decision['profit_projections']['harvest_now'],
                        2
                    ),
                    "risk_assessment": decision.get('risk_assessment', 'ปานกลาง'),
                    "reasons": decision.get('reasons', []),
                    "model_used": "model_d_thompson_sampling"
                }
            else:
                return self._fallback_harvest_decision(
                    current_price, forecast_price_median, yield_kg
                )
                
        except Exception as e:
            logger.error(f"Error in get_harvest_decision: {e}")
            return self._fallback_harvest_decision(
                current_price, forecast_price_median, yield_kg
            )
    
    def _fallback_harvest_decision(self, current_price, forecast_price, yield_kg) -> Dict:
        """Simple rule-based fallback"""
        # Calculate simple profit projections
        profit_now = current_price * yield_kg
        profit_wait_3 = forecast_price * yield_kg * 0.98 - (10 * 3)  # 2% spoilage, storage cost
        profit_wait_7 = forecast_price * yield_kg * 0.95 - (10 * 7)  # 5% spoilage, storage cost
        
        # Determine best action
        profits = {
            "harvest_now": profit_now,
            "wait_3_days": profit_wait_3,
            "wait_7_days": profit_wait_7
        }
        
        best_action = max(profits, key=profits.get)
        
        return {
            "success": True,
            "recommended_action": best_action.replace('_', ' ').title(),
            "action_confidence": 0.7,
            "profit_projections": {k: round(v, 2) for k, v in profits.items()},
            "profit_difference": round(profits[best_action] - profit_now, 2),
            "risk_assessment": "ปานกลาง",
            "reasons": ["คำนวณจากราคาและต้นทุนการเก็บรักษา"],
            "model_used": "fallback_rule_based"
        }
```

### 2. Model Loader and Caching

```python
# backend/app/services/model_loader.py

import os
import pickle
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelLoader:
    """Centralized model loading and caching"""
    
    def __init__(self):
        self._cache = {}
        self.base_path = self._get_base_path()
    
    def _get_base_path(self) -> str:
        """Get base path for models"""
        # Try environment variable first
        env_path = os.getenv('ML_MODELS_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Default to REMEDIATION_PRODUCTION
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        default_path = os.path.join(backend_dir, "..", "REMEDIATION_PRODUCTION", "trained_models")
        
        if os.path.exists(default_path):
            return default_path
        
        logger.warning(f"⚠️ Model path not found: {default_path}")
        return default_path
    
    def load_model(self, model_name: str, cache: bool = True) -> Optional[Any]:
        """
        Load a model from file
        
        Args:
            model_name: Name of model file (e.g., 'model_a_xgboost.pkl')
            cache: Whether to cache the loaded model
        
        Returns:
            Loaded model object or None if loading fails
        """
        # Check cache first
        if cache and model_name in self._cache:
            logger.info(f"✅ Returning cached model: {model_name}")
            return self._cache[model_name]
        
        # Load from file
        model_path = os.path.join(self.base_path, model_name)
        
        if not os.path.exists(model_path):
            logger.error(f"❌ Model file not found: {model_path}")
            return None
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            logger.info(f"✅ Model loaded: {model_name}")
            
            # Cache if requested
            if cache:
                self._cache[model_name] = model
            
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            return None
    
    def clear_cache(self, model_name: Optional[str] = None):
        """Clear model cache"""
        if model_name:
            if model_name in self._cache:
                del self._cache[model_name]
                logger.info(f"✅ Cache cleared for: {model_name}")
        else:
            self._cache.clear()
            logger.info("✅ All model cache cleared")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "base_path": self.base_path,
            "cached_models": list(self._cache.keys()),
            "cache_size": len(self._cache)
        }

# Global model loader instance
model_loader = ModelLoader()
```



### 3. API Endpoints Integration

#### Update Existing Endpoints

```python
# backend/app/main.py - Update existing endpoint

from app.services.model_a_service import ModelAService
from app.services.model_b_service import ModelBService
from app.services.model_c_service import ModelCService

# Initialize services at startup
model_a_service = None
model_b_service = None
model_c_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    global model_a_service, model_b_service, model_c_service
    
    # Startup
    logger.info("🚀 Starting Farmme API...")
    
    # Load ML models
    try:
        model_a_service = ModelAService()
        logger.info("✅ Model A Service initialized")
    except Exception as e:
        logger.error(f"❌ Model A Service failed: {e}")
    
    try:
        model_b_service = ModelBService()
        logger.info("✅ Model B Service initialized")
    except Exception as e:
        logger.error(f"❌ Model B Service failed: {e}")
    
    try:
        model_c_service = ModelCService()
        logger.info("✅ Model C Service initialized")
    except Exception as e:
        logger.error(f"❌ Model C Service failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Farmme API...")

# Update existing endpoint to use new service
@app.post("/recommend-planting-date")
async def recommend_planting_date(request: PlantingDateRequest, db: Session = Depends(get_db)):
    """
    🔄 UPDATED: Now uses Model B Service
    """
    try:
        if model_b_service and model_b_service.model_loaded:
            # Use new Model B
            result = model_b_service.get_planting_recommendations(
                crop_type=request.crop_type,
                province=request.province,
                growth_days=request.growth_days,
                start_date=datetime.strptime(request.start_date, "%Y-%m-%d") if request.start_date else None,
                end_date=datetime.strptime(request.end_date, "%Y-%m-%d") if request.end_date else None,
                top_n=request.top_n or 10,
                db=db
            )
            return result
        else:
            # Fallback to legacy service
            logger.warning("⚠️ Model B not loaded, using legacy service")
            result = planting_service.get_recommendations(
                crop_type=request.crop_type,
                province=request.province,
                growth_days=request.growth_days,
                start_date=datetime.strptime(request.start_date, "%Y-%m-%d") if request.start_date else None,
                end_date=datetime.strptime(request.end_date, "%Y-%m-%d") if request.end_date else None,
                top_n=request.top_n or 10,
                db=db
            )
            return result
        
    except Exception as e:
        logger.error(f"Error in recommend_planting_date: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

#### Add New Endpoint for Model D

```python
# backend/app/routers/harvest.py (NEW FILE)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["harvest"])

class HarvestDecisionRequest(BaseModel):
    """Request model for harvest decision"""
    current_price: float = Field(..., gt=0, description="Current market price (baht/kg)")
    forecast_price_median: float = Field(..., gt=0, description="Forecasted price median (baht/kg)")
    forecast_price_std: float = Field(..., ge=0, description="Forecasted price standard deviation")
    plant_health_score: float = Field(..., ge=0, le=100, description="Plant health score (0-100)")
    yield_kg: float = Field(..., gt=0, description="Expected yield (kg)")
    storage_cost_per_day: float = Field(default=10.0, ge=0, description="Storage cost per day (baht)")
    plant_age_days: int = Field(default=None, ge=0, description="Plant age in days (optional)")

class HarvestDecisionResponse(BaseModel):
    """Response model for harvest decision"""
    success: bool
    recommended_action: str
    action_confidence: float
    profit_projections: Dict[str, float]
    profit_difference: float
    risk_assessment: str
    reasons: list
    model_used: str

@router.post("/harvest-decision", response_model=HarvestDecisionResponse)
async def get_harvest_decision(request: HarvestDecisionRequest):
    """
    🆕 NEW ENDPOINT: Get harvest decision recommendation
    
    Uses Model D (Thompson Sampling) to recommend when to harvest
    """
    try:
        from app.services.model_d_service import model_d_service
        
        result = model_d_service.get_harvest_decision(
            current_price=request.current_price,
            forecast_price_median=request.forecast_price_median,
            forecast_price_std=request.forecast_price_std,
            plant_health_score=request.plant_health_score,
            yield_kg=request.yield_kg,
            storage_cost_per_day=request.storage_cost_per_day,
            plant_age_days=request.plant_age_days
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_harvest_decision: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

### 4. Request and Response Models

```python
# backend/app/models/ml_models.py (NEW FILE)

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class CropRecommendationRequest(BaseModel):
    """Request model for crop recommendation"""
    province: str = Field(..., description="Thai province name")
    soil_type: str = Field(..., description="Soil type")
    soil_ph: float = Field(..., ge=4.0, le=8.5, description="Soil pH (4.0-8.5)")
    soil_nitrogen: Optional[float] = Field(None, ge=0, description="Soil nitrogen (mg/kg)")
    soil_phosphorus: Optional[float] = Field(None, ge=0, description="Soil phosphorus (mg/kg)")
    soil_potassium: Optional[float] = Field(None, ge=0, description="Soil potassium (mg/kg)")
    avg_temperature: Optional[float] = Field(None, ge=15, le=45, description="Average temperature (°C)")
    avg_rainfall: Optional[float] = Field(None, ge=0, description="Average rainfall (mm)")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity (%)")
    budget_baht: float = Field(..., gt=0, description="Budget (baht)")
    farmer_experience_years: int = Field(..., ge=0, description="Farmer experience (years)")
    farm_size_rai: float = Field(default=10.0, gt=0, description="Farm size (rai)")
    water_availability: Optional[str] = Field(None, description="Water availability")
    
    @validator('soil_type')
    def validate_soil_type(cls, v):
        valid_types = ['ดินร่วน', 'ดินร่วนปนทราย', 'ดินเหนียว', 'ดินทราย']
        if v not in valid_types:
            raise ValueError(f'soil_type must be one of {valid_types}')
        return v

class CropRecommendation(BaseModel):
    """Single crop recommendation"""
    crop_type: str
    suitability_score: float
    expected_yield_kg_per_rai: int
    estimated_revenue_per_rai: int
    roi_percent: float
    risk_score: float
    total_profit_baht: float
    confidence: float
    growth_days: int
    reasons: List[str]

class CropRecommendationResponse(BaseModel):
    """Response model for crop recommendation"""
    success: bool
    recommendations: List[CropRecommendation]
    model_used: str
    confidence: float

class PlantingWindowRequest(BaseModel):
    """Request model for planting window check"""
    crop_type: str = Field(..., description="Crop type")
    province: str = Field(..., description="Province")
    soil_moisture_percent: float = Field(..., ge=0, le=100, description="Soil moisture (%)")
    recent_rainfall_mm: float = Field(..., ge=0, description="Recent rainfall (mm)")
    temperature_c: float = Field(..., ge=15, le=45, description="Temperature (°C)")
    humidity_percent: float = Field(..., ge=0, le=100, description="Humidity (%)")
    soil_temperature_c: Optional[float] = Field(None, ge=10, le=40, description="Soil temperature (°C)")
    wind_speed_kmh: Optional[float] = Field(None, ge=0, description="Wind speed (km/h)")

class PlantingWindowResponse(BaseModel):
    """Response model for planting window"""
    success: bool
    classification: str  # Good/Bad
    confidence: float
    expected_germination_rate: float
    optimal_time_range: Optional[str]
    risk_level: str
    reasons: List[str]
    weather_warnings: List[str]
    model_used: str

class PriceForecastRequest(BaseModel):
    """Request model for price forecast"""
    crop_type: str = Field(..., description="Crop type")
    province: str = Field(..., description="Province")
    days_ahead: int = Field(default=30, ge=1, le=180, description="Days ahead to forecast (1-180)")
    current_price: Optional[float] = Field(None, gt=0, description="Current price (optional)")

class PricePrediction(BaseModel):
    """Single price prediction"""
    days_ahead: int
    predicted_price: float
    confidence: float
    price_range: Dict[str, float]

class PriceForecastResponse(BaseModel):
    """Response model for price forecast"""
    success: bool
    crop_type: str
    province: str
    predictions: List[PricePrediction]
    current_price: float
    price_trend: str
    trend_percentage: float
    market_insights: List[str]
    best_selling_period: str
    model_used: str
    confidence: float
```



### 5. Error Handling Strategy

```python
# backend/app/utils/error_handlers.py (NEW FILE)

import logging
from typing import Callable, Any, Dict
from functools import wraps

logger = logging.getLogger(__name__)

def with_fallback(fallback_func: Callable):
    """
    Decorator to add fallback functionality to model predictions
    
    Usage:
        @with_fallback(fallback_function)
        def predict_something(...):
            # Try ML model prediction
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Try primary function
                result = func(*args, **kwargs)
                
                # Check if result indicates failure
                if isinstance(result, dict) and not result.get('success', True):
                    logger.warning(f"{func.__name__} returned failure, trying fallback")
                    return fallback_func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}, using fallback")
                try:
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    return {
                        "success": False,
                        "error": str(e),
                        "fallback_error": str(fallback_error)
                    }
        
        return wrapper
    return decorator

def with_timeout(seconds: int = 10):
    """
    Decorator to add timeout to model predictions
    
    Usage:
        @with_timeout(seconds=5)
        def predict_something(...):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"{func.__name__} exceeded {seconds} seconds")
            
            # Set timeout (Unix only)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                
                result = func(*args, **kwargs)
                
                signal.alarm(0)  # Cancel alarm
                return result
                
            except TimeoutError as e:
                logger.error(f"Timeout: {e}")
                return {
                    "success": False,
                    "error": f"Prediction timeout after {seconds} seconds"
                }
            except Exception as e:
                signal.alarm(0)  # Cancel alarm
                raise e
        
        return wrapper
    return decorator

class ModelError(Exception):
    """Base exception for model errors"""
    pass

class ModelLoadError(ModelError):
    """Exception raised when model loading fails"""
    pass

class ModelPredictionError(ModelError):
    """Exception raised when model prediction fails"""
    pass

class FeaturePreparationError(ModelError):
    """Exception raised when feature preparation fails"""
    pass
```

### 6. Configuration Management

```python
# backend/config.py - Add ML model configuration

import os
from pathlib import Path

# ML Model Configuration
ML_MODELS_PATH = os.getenv(
    'ML_MODELS_PATH',
    str(Path(__file__).parent.parent / 'REMEDIATION_PRODUCTION' / 'trained_models')
)

# Model A Configuration
MODEL_A_XGBOOST_PATH = os.getenv('MODEL_A_XGBOOST_PATH', 'model_a_xgboost.pkl')
MODEL_A_RF_PATH = os.getenv('MODEL_A_RF_PATH', 'model_a_rf_ensemble.pkl')
MODEL_A_NSGA2_PATH = os.getenv('MODEL_A_NSGA2_PATH', 'model_a_nsga2.pkl')
MODEL_A_PRIMARY_ALGORITHM = os.getenv('MODEL_A_PRIMARY_ALGORITHM', 'xgboost')  # xgboost, rf, nsga2

# Model B Configuration
MODEL_B_LOGISTIC_PATH = os.getenv('MODEL_B_LOGISTIC_PATH', 'model_b_logistic.pkl')
MODEL_B_XGBOOST_PATH = os.getenv('MODEL_B_XGBOOST_PATH', 'model_b_xgboost.pkl')
MODEL_B_TEMPORAL_GB_PATH = os.getenv('MODEL_B_TEMPORAL_GB_PATH', 'model_b_temporal_gb.pkl')
MODEL_B_PRIMARY_ALGORITHM = os.getenv('MODEL_B_PRIMARY_ALGORITHM', 'logistic')  # logistic has best F1=0.868

# Model C Configuration
MODEL_C_PATH = os.getenv('MODEL_C_PATH', 'model_c_price_forecast.pkl')
MODEL_C_UPDATE_FREQUENCY = os.getenv('MODEL_C_UPDATE_FREQUENCY', 'daily')  # daily, weekly, manual

# Model D Configuration
MODEL_D_PATH = os.getenv('MODEL_D_PATH', 'model_d_thompson_sampling.pkl')
MODEL_D_ALPHA_INIT = float(os.getenv('MODEL_D_ALPHA_INIT', '1.0'))
MODEL_D_BETA_INIT = float(os.getenv('MODEL_D_BETA_INIT', '1.0'))

# Model Performance Thresholds
MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('MODEL_CONFIDENCE_THRESHOLD', '0.6'))
MODEL_PREDICTION_TIMEOUT = int(os.getenv('MODEL_PREDICTION_TIMEOUT', '10'))  # seconds

# Fallback Configuration
ENABLE_FALLBACK = os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true'
FALLBACK_TO_LEGACY = os.getenv('FALLBACK_TO_LEGACY', 'true').lower() == 'true'

# Caching Configuration
CACHE_ML_PREDICTIONS = os.getenv('CACHE_ML_PREDICTIONS', 'true').lower() == 'true'
CACHE_TTL_ML_PREDICTIONS = int(os.getenv('CACHE_TTL_ML_PREDICTIONS', '3600'))  # 1 hour

# Logging Configuration
ML_LOG_LEVEL = os.getenv('ML_LOG_LEVEL', 'INFO')
ML_LOG_FILE = os.getenv('ML_LOG_FILE', 'logs/ml_models.log')
```

```python
# backend/.env.example - Add ML configuration

# ML Model Paths
ML_MODELS_PATH=../REMEDIATION_PRODUCTION/trained_models

# Model A - Crop Recommendation
MODEL_A_PRIMARY_ALGORITHM=xgboost
MODEL_A_XGBOOST_PATH=model_a_xgboost.pkl
MODEL_A_RF_PATH=model_a_rf_ensemble.pkl

# Model B - Planting Calendar
MODEL_B_PRIMARY_ALGORITHM=logistic
MODEL_B_LOGISTIC_PATH=model_b_logistic.pkl
MODEL_B_XGBOOST_PATH=model_b_xgboost.pkl

# Model C - Price Forecast
MODEL_C_PATH=model_c_price_forecast.pkl
MODEL_C_UPDATE_FREQUENCY=daily

# Model D - Harvest Decision
MODEL_D_PATH=model_d_thompson_sampling.pkl

# Performance Settings
MODEL_CONFIDENCE_THRESHOLD=0.6
MODEL_PREDICTION_TIMEOUT=10

# Fallback Settings
ENABLE_FALLBACK=true
FALLBACK_TO_LEGACY=true

# Caching
CACHE_ML_PREDICTIONS=true
CACHE_TTL_ML_PREDICTIONS=3600
```

## Data Models

### Feature Engineering

```python
# backend/app/utils/feature_engineering.py (NEW FILE)

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

class FeatureEngineer:
    """Feature engineering utilities for ML models"""
    
    @staticmethod
    def add_temporal_features(date: datetime) -> Dict[str, float]:
        """Add temporal features (cyclic encoding)"""
        month = date.month
        day_of_year = date.timetuple().tm_yday
        
        return {
            'month': month,
            'day_of_year': day_of_year,
            'month_sin': np.sin(2 * np.pi * month / 12),
            'month_cos': np.cos(2 * np.pi * month / 12),
            'day_sin': np.sin(2 * np.pi * day_of_year / 365),
            'day_cos': np.cos(2 * np.pi * day_of_year / 365),
            'is_rainy_season': 1 if month in [6, 7, 8, 9, 10] else 0,
            'is_winter': 1 if month in [11, 12, 1, 2] else 0,
            'is_summer': 1 if month in [3, 4, 5] else 0
        }
    
    @staticmethod
    def encode_province(province: str) -> int:
        """Encode province to numeric"""
        # Simple hash-based encoding
        return hash(province) % 100
    
    @staticmethod
    def encode_crop_type(crop_type: str) -> int:
        """Encode crop type to numeric"""
        return hash(crop_type) % 50
    
    @staticmethod
    def get_region_from_province(province: str) -> str:
        """Get region from province"""
        PROVINCE_REGION_MAP = {
            'เชียงใหม่': 'เหนือ', 'ลำพูน': 'เหนือ', 'ลำปาง': 'เหนือ',
            'กรุงเทพมหานคร': 'กลาง', 'สมุทรปราการ': 'กลาง',
            'นครราชสีมา': 'อีสาน', 'ขอนแก่น': 'อีสาน',
            'ภูเก็ต': 'ใต้', 'สงขลา': 'ใต้',
            # ... more provinces
        }
        return PROVINCE_REGION_MAP.get(province, 'กลาง')
    
    @staticmethod
    def get_seasonal_weather(month: int) -> Dict[str, float]:
        """Get seasonal weather averages"""
        temperature_map = {
            1: 26.0, 2: 28.0, 3: 30.0, 4: 32.0, 5: 31.0, 6: 29.0,
            7: 28.5, 8: 28.5, 9: 28.0, 10: 28.0, 11: 27.0, 12: 26.0
        }
        
        rainfall_map = {
            1: 15.0, 2: 25.0, 3: 40.0, 4: 80.0, 5: 150.0, 6: 180.0,
            7: 200.0, 8: 220.0, 9: 250.0, 10: 180.0, 11: 60.0, 12: 20.0
        }
        
        return {
            'temperature': temperature_map.get(month, 28.0),
            'rainfall': rainfall_map.get(month, 100.0)
        }
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_model_services.py (NEW FILE)

import pytest
from app.services.model_a_service import ModelAService
from app.services.model_b_service import ModelBService
from app.services.model_c_service import ModelCService
from app.services.model_d_service import ModelDService

class TestModelAService:
    """Test Model A Service"""
    
    def test_model_loading(self):
        """Test that Model A loads successfully"""
        service = ModelAService()
        assert service is not None
        # Model may not be loaded if files don't exist, that's ok
    
    def test_get_recommendations(self):
        """Test crop recommendations"""
        service = ModelAService()
        result = service.get_recommendations(
            province="เชียงใหม่",
            soil_type="ดินร่วน",
            soil_ph=6.5,
            budget_baht=100000,
            farmer_experience_years=5,
            farm_size_rai=10.0
        )
        
        assert result['success'] == True
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        assert 'model_used' in result
    
    def test_fallback_mechanism(self):
        """Test fallback when model not loaded"""
        service = ModelAService(model_path="/nonexistent/path")
        result = service.get_recommendations(
            province="เชียงใหม่",
            soil_type="ดินร่วน",
            soil_ph=6.5,
            budget_baht=100000,
            farmer_experience_years=5
        )
        
        # Should still return results via fallback
        assert result['success'] == True
        assert result['model_used'] in ['fallback', 'fallback_rules']

class TestModelBService:
    """Test Model B Service"""
    
    def test_planting_recommendations(self):
        """Test planting date recommendations"""
        service = ModelBService()
        result = service.get_planting_recommendations(
            crop_type="คะน้า",
            province="เชียงใหม่",
            growth_days=45,
            top_n=5
        )
        
        assert result['success'] == True
        assert 'recommendations' in result
        assert len(result['recommendations']) <= 5

class TestModelCService:
    """Test Model C Service"""
    
    def test_price_prediction(self):
        """Test price forecast"""
        service = ModelCService()
        result = service.predict_price(
            crop_type="พริก",
            province="เชียงใหม่",
            days_ahead=30
        )
        
        assert result['success'] == True
        assert 'predictions' in result
        assert 'price_trend' in result

class TestModelDService:
    """Test Model D Service"""
    
    def test_harvest_decision(self):
        """Test harvest decision"""
        service = ModelDService()
        result = service.get_harvest_decision(
            current_price=50.0,
            forecast_price_median=55.0,
            forecast_price_std=5.0,
            plant_health_score=90.0,
            yield_kg=1000.0
        )
        
        assert result['success'] == True
        assert 'recommended_action' in result
        assert result['recommended_action'] in ['Harvest Now', 'Wait 3 Days', 'Wait 7 Days']
        assert 'profit_projections' in result
```

### Integration Tests

```python
# backend/tests/test_api_integration.py (NEW FILE)

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIIntegration:
    """Test API endpoints with ML models"""
    
    def test_planting_date_endpoint(self):
        """Test /recommend-planting-date endpoint"""
        response = client.post("/recommend-planting-date", json={
            "crop_type": "คะน้า",
            "province": "เชียงใหม่",
            "growth_days": 45,
            "top_n": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'recommendations' in data
    
    def test_harvest_decision_endpoint(self):
        """Test /api/v1/harvest-decision endpoint"""
        response = client.post("/api/v1/harvest-decision", json={
            "current_price": 50.0,
            "forecast_price_median": 55.0,
            "forecast_price_std": 5.0,
            "plant_health_score": 90.0,
            "yield_kg": 1000.0,
            "storage_cost_per_day": 10.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'recommended_action' in data
    
    def test_models_list_endpoint(self):
        """Test /models endpoint"""
        response = client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert 'models' in data
```

## Deployment

### Directory Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── model_a_service.py      # NEW
│   │   ├── model_b_service.py      # NEW
│   │   ├── model_c_service.py      # NEW
│   │   ├── model_d_service.py      # NEW
│   │   └── model_loader.py         # NEW
│   ├── routers/
│   │   ├── harvest.py              # NEW
│   │   └── ... (existing routers)
│   ├── models/
│   │   ├── ml_models.py            # NEW
│   │   └── ... (existing models)
│   ├── utils/
│   │   ├── error_handlers.py       # NEW
│   │   ├── feature_engineering.py  # NEW
│   │   └── ... (existing utils)
│   └── main.py                     # UPDATED
├── tests/
│   ├── test_model_services.py      # NEW
│   └── test_api_integration.py     # NEW
├── logs/
│   └── ml_models.log               # NEW
├── .env                            # UPDATED
├── .env.example                    # UPDATED
├── config.py                       # UPDATED
├── requirements.txt                # UPDATED
└── README.md                       # UPDATED

REMEDIATION_PRODUCTION/
└── trained_models/
    ├── model_a_xgboost.pkl
    ├── model_a_rf_ensemble.pkl
    ├── model_a_nsga2.pkl
    ├── model_b_xgboost.pkl
    ├── model_b_temporal_gb.pkl
    ├── model_c_price_forecast.pkl
    └── model_d_thompson_sampling.pkl
```

### Deployment Steps

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env to set ML_MODELS_PATH
```

3. **Verify Model Files**
```bash
ls -la ../REMEDIATION_PRODUCTION/trained_models/
```

4. **Run Tests**
```bash
pytest tests/test_model_services.py -v
pytest tests/test_api_integration.py -v
```

5. **Start Server**
```bash
python run.py
# or
uvicorn app.main:app --reload
```

6. **Verify Integration**
```bash
curl http://localhost:8000/models
curl -X POST http://localhost:8000/recommend-planting-date \
  -H "Content-Type: application/json" \
  -d '{"crop_type":"คะน้า","province":"เชียงใหม่","growth_days":45}'
```

### Monitoring

```python
# backend/app/utils/monitoring.py - Add ML model monitoring

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MLModelMonitor:
    """Monitor ML model performance"""
    
    def __init__(self):
        self.metrics = {
            'model_a': {'predictions': 0, 'errors': 0, 'avg_time': 0},
            'model_b': {'predictions': 0, 'errors': 0, 'avg_time': 0},
            'model_c': {'predictions': 0, 'errors': 0, 'avg_time': 0},
            'model_d': {'predictions': 0, 'errors': 0, 'avg_time': 0}
        }
    
    def log_prediction(self, model_name: str, duration: float, success: bool):
        """Log prediction metrics"""
        if model_name not in self.metrics:
            return
        
        self.metrics[model_name]['predictions'] += 1
        if not success:
            self.metrics[model_name]['errors'] += 1
        
        # Update average time
        n = self.metrics[model_name]['predictions']
        old_avg = self.metrics[model_name]['avg_time']
        new_avg = (old_avg * (n-1) + duration) / n
        self.metrics[model_name]['avg_time'] = new_avg
        
        logger.info(f"Model {model_name}: {duration:.3f}s, success={success}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics

# Global monitor instance
ml_monitor = MLModelMonitor()
```

## Security Considerations

1. **Model File Protection**: Store model files outside web root
2. **Input Validation**: Use Pydantic models for all inputs
3. **Rate Limiting**: Implement rate limiting on ML endpoints
4. **Error Messages**: Don't expose internal errors to clients
5. **Logging**: Log all predictions for audit trail

## Performance Optimization

1. **Model Caching**: Cache loaded models in memory
2. **Prediction Caching**: Cache predictions for identical inputs
3. **Lazy Loading**: Load models only when needed
4. **Async Processing**: Use async for I/O operations
5. **Connection Pooling**: Reuse database connections


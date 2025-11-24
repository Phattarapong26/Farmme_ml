# -*- coding: utf-8 -*-
"""
Model D Wrapper for Chat Integration
Wraps Model D (Harvest Decision Engine - Thompson Sampling) for use in chat
"""

import logging
import pickle
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add REMEDIATION_PRODUCTION to path
backend_dir = Path(__file__).parent
remediation_dir = backend_dir.parent / "REMEDIATION_PRODUCTION"
sys.path.insert(0, str(remediation_dir))

# Add Model_D_L4_Bandit to path (required for loading pickled model)
sys.path.insert(0, str(remediation_dir / "Model_D_L4_Bandit"))

logger = logging.getLogger(__name__)

class ModelDWrapper:
    """Wrapper for Model D - Harvest Decision Engine"""
    
    def __init__(self):
        self.model_state = None
        self.bandit = None
        self.model_loaded = False
        self.model_path = None
        
        # Try to load Model D
        self._load_model()
    
    def _load_model(self):
        """Load Model D from trained_models"""
        try:
            model_path = remediation_dir / "trained_models" / "model_d_thompson_sampling.pkl"
            
            if model_path.exists():
                try:
                    with open(model_path, 'rb') as f:
                        self.model_state = pickle.load(f)
                    
                    # Extract bandit from model state
                    if isinstance(self.model_state, dict):
                        self.bandit = self.model_state.get('bandit')
                    else:
                        self.bandit = self.model_state
                    
                    self.model_path = model_path
                    self.model_loaded = True
                    logger.info(f"✅ Model D loaded from: {model_path}")
                    
                    # Log posteriors
                    if self.bandit:
                        posteriors = self.bandit.get_arm_posteriors()
                        logger.info(f"   Posteriors: {posteriors}")
                    
                except Exception as e:
                    logger.error(f"Failed to load model_d_thompson_sampling.pkl: {e}")
                    self.model_loaded = False
            else:
                logger.warning(f"⚠️ Model D not found at: {model_path}")
                self.model_loaded = False
            
        except Exception as e:
            logger.error(f"Error loading Model D: {e}")
            self.model_loaded = False
    
    def get_harvest_decision(
        self,
        current_price: float,
        forecast_price: float,
        forecast_std: float = 0.2,
        yield_kg: float = 15000,
        plant_health: float = 0.9,
        storage_cost_per_day: float = 10
    ) -> Dict[str, Any]:
        """
        Get harvest timing decision
        
        Args:
            current_price: Current market price (baht/kg)
            forecast_price: Forecasted price from Model C (baht/kg)
            forecast_std: Standard deviation of forecast
            yield_kg: Expected harvest yield (kg)
            plant_health: Plant health score (0-1, higher is better)
            storage_cost_per_day: Storage cost per day (baht)
            
        Returns:
            Dict with decision and profit projections
        """
        try:
            if not self.model_loaded or not self.bandit:
                return self._fallback_decision(
                    current_price, forecast_price, yield_kg, storage_cost_per_day
                )
            
            # Use Thompson Sampling
            try:
                from Model_D_L4_Bandit.thompson_sampling import (
                    HarvestDecisionEngine, HarvestProfitCalculator
                )
                
                # Create engine with loaded bandit
                engine = HarvestDecisionEngine()
                engine.bandit = self.bandit
                
                # Make decision with Thompson Sampling
                decision = engine.decide(
                    current_price=current_price,
                    forecast_price_median=forecast_price,
                    forecast_price_std=forecast_std,
                    yield_kg=yield_kg,
                    plant_health_score=plant_health,
                    storage_cost_per_day=storage_cost_per_day,
                    use_thompson=True
                )
                
                # HYBRID APPROACH: Override if Thompson Sampling is clearly wrong
                price_increase = (forecast_price - current_price) / current_price
                
                # If price going up significantly but model says harvest now → override
                if price_increase > 0.12 and decision['action'] == "Harvest Now":
                    if decision['profits']['wait_7d'] > decision['profits']['now']:
                        logger.info(f"Override: Price up {price_increase*100:.1f}%, switching to Wait 7 Days")
                        decision['action'] = "Wait 7 Days"
                        decision['action_idx'] = 2
                        decision['override'] = True
                elif price_increase > 0.07 and decision['action'] == "Harvest Now":
                    if decision['profits']['wait_3d'] > decision['profits']['now']:
                        logger.info(f"Override: Price up {price_increase*100:.1f}%, switching to Wait 3 Days")
                        decision['action'] = "Wait 3 Days"
                        decision['action_idx'] = 1
                        decision['override'] = True
                
                # If price going down but model says wait → override
                elif price_increase < -0.05 and decision['action'] != "Harvest Now":
                    logger.info(f"Override: Price down {abs(price_increase)*100:.1f}%, switching to Harvest Now")
                    decision['action'] = "Harvest Now"
                    decision['action_idx'] = 0
                    decision['override'] = True
                
                return {
                    "success": True,
                    "action": decision['action'],
                    "profits": decision['profits'],
                    "details": {
                        "now": {
                            "profit": decision['details']['wait_0d']['expected_profit'],
                            "yield": decision['details']['wait_0d']['remaining_yield'],
                            "price": decision['details']['wait_0d']['expected_price'],
                            "storage_cost": 0
                        },
                        "wait_3d": {
                            "profit": decision['details']['wait_3d']['expected_profit'],
                            "yield": decision['details']['wait_3d']['remaining_yield'],
                            "price": decision['details']['wait_3d']['expected_price'],
                            "storage_cost": decision['details']['wait_3d']['storage_cost']
                        },
                        "wait_7d": {
                            "profit": decision['details']['wait_7d']['expected_profit'],
                            "yield": decision['details']['wait_7d']['remaining_yield'],
                            "price": decision['details']['wait_7d']['expected_price'],
                            "storage_cost": decision['details']['wait_7d']['storage_cost']
                        }
                    },
                    "confidence": decision['confidence'],
                    "model_used": "thompson_sampling",
                    "model_confidence": 0.85
                }
                
            except Exception as e:
                logger.warning(f"Thompson Sampling failed: {e}, using fallback")
                return self._fallback_decision(
                    current_price, forecast_price, yield_kg, storage_cost_per_day
                )
                
        except Exception as e:
            logger.error(f"Error in get_harvest_decision: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_decision(
                current_price, forecast_price, yield_kg, storage_cost_per_day
            )
    
    def _fallback_decision(
        self, current_price: float, forecast_price: float,
        yield_kg: float, storage_cost_per_day: float
    ) -> Dict[str, Any]:
        """Simple rule-based fallback decision"""
        logger.warning("Using fallback harvest decision")
        
        # Simple rule: if price expected to increase > 5%, wait
        price_increase = (forecast_price - current_price) / current_price
        
        # Calculate simple profits
        profit_now = current_price * yield_kg
        profit_wait_3d = forecast_price * yield_kg * 0.98 - (storage_cost_per_day * 3)
        profit_wait_7d = forecast_price * yield_kg * 0.95 - (storage_cost_per_day * 7)
        
        # Decide
        if price_increase > 0.10 and profit_wait_7d > profit_now:
            action = "Wait 7 Days"
            reason = f"ราคาคาดว่าจะขึ้น {price_increase*100:.1f}% (มาก)"
        elif price_increase > 0.05 and profit_wait_3d > profit_now:
            action = "Wait 3 Days"
            reason = f"ราคาคาดว่าจะขึ้น {price_increase*100:.1f}%"
        else:
            action = "Harvest Now"
            if price_increase < 0:
                reason = f"ราคาคาดว่าจะลง {abs(price_increase)*100:.1f}%"
            else:
                reason = "ราคาคงที่ ควรเก็บเกี่ยวเลย"
        
        return {
            "success": True,
            "action": action,
            "reason": reason,
            "profits": {
                "now": profit_now,
                "wait_3d": profit_wait_3d,
                "wait_7d": profit_wait_7d
            },
            "details": {
                "now": {"profit": profit_now, "yield": yield_kg, "price": current_price, "storage_cost": 0},
                "wait_3d": {"profit": profit_wait_3d, "yield": yield_kg * 0.98, "price": forecast_price, "storage_cost": storage_cost_per_day * 3},
                "wait_7d": {"profit": profit_wait_7d, "yield": yield_kg * 0.95, "price": forecast_price, "storage_cost": storage_cost_per_day * 7}
            },
            "model_used": "fallback_rule_based",
            "model_confidence": 0.65
        }


# Global instance
model_d_wrapper = ModelDWrapper()

logger.info("📦 Model D Wrapper loaded")

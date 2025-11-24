"""
Model D - Harvest Decision (FIXED)
L4 Thompson Sampling Bandit - Replace L5 (DQN)

ปัญหา: DQN (L5) ต้องการ simulator, ข้อมูล leakage ร้ายแรง
วิธีแก้: Thompson Sampling (L4) - ใช้ historical data เรียนรู้ posterior distribution

ตัดสินใจ: Sell Now vs Wait 3 Days vs Wait 7 Days
Based on: Current Price, Market Forecast, Plant Health, Storage Condition
"""

import pandas as pd
import numpy as np
from scipy.stats import beta
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HarvestDecisionContext:
    """
    Context variables for harvest decision (NO leakage)
    
    ✅ CLEAN contexts:
    - Current price (observable now)
    - Price forecast (from Model C)
    - Plant health (observable now)
    - Storage condition (observable now)
    - Days since planting (time since action, not target!)
    - Seasonal factors (month, crop maturity stage)
    
    ❌ REMOVE:
    - days_since_planting = harvest_date - planting_date (TAUTOLOGICAL!)
    - future_price (unknown now)
    - actual_harvest_date (future)
    """
    
    def __init__(self):
        self.current_price = None
        self.price_forecast_median = None
        self.price_forecast_lower = None
        self.price_forecast_upper = None
        self.plant_health_score = None  # 0-1
        self.storage_cost_per_day = None
        self.spoilage_risk_per_day = None  # 0-1
        self.market_volatility = None
        self.days_to_full_maturity = None  # From crop characteristics

class ThompsonSamplingBandit:
    """
    Thompson Sampling for harvest timing decision
    
    Actions:
    - a0: Harvest now (sell today)
    - a1: Wait 3 days (storage cost = 3x daily cost)
    - a2: Wait 7 days (storage cost = 7x daily cost)
    
    Reward: Expected profit = Price * Yield - StorageCost - SpoilageLoss
    """
    
    def __init__(self, n_arms=3, alpha_init=1, beta_init=1):
        """
        Initialize Thompson Sampling
        
        Args:
            n_arms: Number of actions (3: now, wait3d, wait7d)
            alpha_init, beta_init: Beta distribution hyperparameters
        """
        self.n_arms = n_arms
        self.arm_names = ["Harvest Now", "Wait 3 Days", "Wait 7 Days"]
        
        # Beta distribution for each arm
        # α = successes, β = failures
        self.alpha = np.ones(n_arms) * alpha_init
        self.beta = np.ones(n_arms) * beta_init
        
        self.action_history = []
        self.reward_history = []
        
        logger.info(f"✅ Thompson Sampling initialized with {n_arms} arms")
        
    def update_beliefs(self, action_idx, reward):
        """
        Update posterior beliefs based on observed reward
        
        reward: [0, 1] normalized profit ratio
        """
        # Convert reward to success/failure
        if reward > 0.5:  # Good profit
            self.alpha[action_idx] += 1
        else:  # Poor profit
            self.beta[action_idx] += 1
        
        self.action_history.append(action_idx)
        self.reward_history.append(reward)
        
    def sample_and_select(self):
        """
        Thompson Sampling: Sample θ ~ Beta(α, β) for each arm, select max
        """
        # Sample from posterior
        theta_samples = np.array([
            np.random.beta(self.alpha[i], self.beta[i]) 
            for i in range(self.n_arms)
        ])
        
        # Select action with highest sample
        best_action = np.argmax(theta_samples)
        
        return best_action, theta_samples
    
    def get_arm_posteriors(self):
        """Get posterior distribution for each arm"""
        posteriors = {}
        for i in range(self.n_arms):
            posteriors[self.arm_names[i]] = {
                'alpha': self.alpha[i],
                'beta': self.beta[i],
                'mean': self.alpha[i] / (self.alpha[i] + self.beta[i]),
                'variance': (self.alpha[i] * self.beta[i]) / 
                           ((self.alpha[i] + self.beta[i])**2 * (self.alpha[i] + self.beta[i] + 1))
            }
        return posteriors

class HarvestProfitCalculator:
    """Calculate expected profit for each harvest action"""
    
    def __init__(self, yield_kg, storage_cost_per_day=10):
        """
        Args:
            yield_kg: Expected harvest yield
            storage_cost_per_day: Storage cost per day (baht/kg)
        """
        self.yield_kg = yield_kg
        self.storage_cost_per_day = storage_cost_per_day
    
    def calculate_profit(self, 
                        action_wait_days,
                        current_price,
                        forecast_price,
                        forecast_std,
                        spoilage_rate_per_day=0.02):
        """
        Calculate expected profit for given action
        
        Args:
            action_wait_days: 0 (now), 3, 7 (days to wait)
            current_price: Current market price (baht/kg)
            forecast_price: Model C forecast for future date
            forecast_std: Std deviation of forecast
            spoilage_rate_per_day: Loss rate per day storage
        
        Returns:
            expected_profit, profit_confidence (std)
        """
        
        # Expected yield after spoilage
        spoilage_loss = self.yield_kg * (spoilage_rate_per_day * action_wait_days)
        remaining_yield = self.yield_kg - spoilage_loss
        
        # Expected price
        if action_wait_days == 0:
            expected_price = current_price
            price_std = 0  # No uncertainty for current price
        else:
            expected_price = forecast_price
            price_std = forecast_std
        
        # Revenue
        expected_revenue = remaining_yield * expected_price
        revenue_std = remaining_yield * price_std
        
        # Costs
        storage_cost = self.storage_cost_per_day * action_wait_days
        
        # Profit
        expected_profit = expected_revenue - storage_cost
        profit_std = revenue_std
        
        return {
            'expected_profit': expected_profit,
            'profit_std': profit_std,
            'remaining_yield': remaining_yield,
            'expected_price': expected_price,
            'storage_cost': storage_cost,
            'revenue': expected_revenue,
        }

class HarvestDecisionEngine:
    """End-to-end harvest decision system"""
    
    def __init__(self):
        self.bandit = ThompsonSamplingBandit(n_arms=3)
        self.decision_history = []
        
    def decide(self, 
               current_price,
               forecast_price_median,
               forecast_price_std,
               yield_kg,
               plant_health_score=0.9,
               storage_cost_per_day=10,
               use_thompson=True):
        """
        Make harvest decision
        
        Args:
            current_price: Current market price
            forecast_price_median: Model C median forecast
            forecast_price_std: Model C std (from quantiles)
            yield_kg: Expected yield
            plant_health_score: 0-1 (higher = healthier)
            storage_cost_per_day: Storage cost
            use_thompson: Use Thompson Sampling (True) or greedy (False)
        
        Returns:
            decision_dict: Action, profits for each option, recommendation
        """
        
        profit_calc = HarvestProfitCalculator(yield_kg, storage_cost_per_day)
        
        # Calculate profits for each action
        profits = {}
        for wait_days in [0, 3, 7]:
            profits[f'wait_{wait_days}d'] = profit_calc.calculate_profit(
                wait_days,
                current_price,
                forecast_price_median,
                forecast_price_std,
                spoilage_rate_per_day=0.02 * (1 - plant_health_score)  # Healthier = less spoilage
            )
        
        # Make decision
        if use_thompson:
            # Thompson Sampling
            best_action, theta_samples = self.bandit.sample_and_select()
        else:
            # Greedy: pick highest expected profit
            profit_values = [
                profits['wait_0d']['expected_profit'],
                profits['wait_3d']['expected_profit'],
                profits['wait_7d']['expected_profit']
            ]
            best_action = np.argmax(profit_values)
        
        action_names = ["Harvest Now", "Wait 3 Days", "Wait 7 Days"]
        best_action_name = action_names[best_action]
        
        decision_dict = {
            'action': best_action_name,
            'action_idx': best_action,
            'profits': {
                'now': profits['wait_0d']['expected_profit'],
                'wait_3d': profits['wait_3d']['expected_profit'],
                'wait_7d': profits['wait_7d']['expected_profit'],
            },
            'details': profits,
            'confidence': self.bandit.get_arm_posteriors(),
        }
        
        self.decision_history.append(decision_dict)
        
        return decision_dict
    
    def get_stats(self):
        """Get bandit statistics"""
        return {
            'total_decisions': len(self.decision_history),
            'posteriors': self.bandit.get_arm_posteriors(),
        }

if __name__ == "__main__":
    print("✅ Model D (L4 Thompson Sampling) loaded successfully")
    print("Ready to make harvest decisions without data leakage")

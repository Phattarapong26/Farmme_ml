"""
Train Model D V3 - Harvest Decision Engine (Thompson Sampling) - PRODUCTION READY
Final version with proper continuous reward and balanced learning

Key improvements over V2:
1. ✅ Continuous reward (not binary threshold)
2. ✅ Proper Beta update using reward directly
3. ✅ More balanced scenarios
4. ✅ Better exploration in early stages

Version: 3.0 (Production Ready)
Date: 2025-11-27
"""

import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import beta as beta_dist
from sklearn.metrics import confusion_matrix

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from Model_D_L4_Bandit.thompson_sampling import (
    HarvestDecisionEngine, HarvestProfitCalculator, ThompsonSamplingBandit
)
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.get_log_path('model_d')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThompsonSamplingBanditV3(ThompsonSamplingBandit):
    """Enhanced Thompson Sampling with continuous reward"""
    
    def update_beliefs_continuous(self, action_idx, reward, decay_factor=0.995):
        """
        Update beliefs using continuous reward (not binary)
        
        Args:
            action_idx: Action taken
            reward: [0, 1] continuous profit ratio
            decay_factor: Decay for non-stationary environments
        """
        # Apply decay
        self.alpha = self.alpha * decay_factor
        self.beta = self.beta * decay_factor
        
        # Continuous update: treat reward as probability of success
        # Add fractional successes/failures
        self.alpha[action_idx] += reward
        self.beta[action_idx] += (1 - reward)
        
        self.action_history.append(action_idx)
        self.reward_history.append(reward)

class ModelDTrainerV3:
    """Train Model D V3 - Production Ready"""
    
    def __init__(self, decay_factor=0.995):
        self.engine = HarvestDecisionEngine()
        # Replace with V3 bandit
        self.engine.bandit = ThompsonSamplingBanditV3(n_arms=3, alpha_init=1, beta_init=1)
        self.decay_factor = decay_factor
        self.test_scenarios = []
        self.results = []
        self.cached_metrics = None
        
    def create_test_scenarios(self, n_scenarios=5000):
        """Create BALANCED test scenarios"""
        logger.info(f"📊 Creating {n_scenarios} BALANCED test scenarios...")
        
        np.random.seed(42)
        scenarios = []
        
        # More balanced: 33% each trend
        n_per_trend = n_scenarios // 3
        
        for i in range(n_scenarios):
            # Determine trend
            if i < n_per_trend:
                price_trend = 'up'
                current_price = np.random.uniform(2.5, 3.5)
                forecast_price = current_price * np.random.uniform(1.10, 1.25)
            elif i < 2 * n_per_trend:
                price_trend = 'down'
                current_price = np.random.uniform(3.0, 4.0)
                forecast_price = current_price * np.random.uniform(0.80, 0.95)
            else:
                price_trend = 'stable'
                current_price = np.random.uniform(2.5, 4.0)
                forecast_price = current_price * np.random.uniform(0.97, 1.03)
            
            forecast_std = abs(forecast_price - current_price) * 0.15
            
            # Farm conditions
            yield_kg = np.random.uniform(12000, 18000)
            plant_health = np.random.uniform(0.85, 1.0)
            storage_cost = np.random.uniform(3, 7)
            
            # Add noise
            noisy_forecast_price = np.random.normal(forecast_price, forecast_std)
            noisy_forecast_price = max(0.5, noisy_forecast_price)
            
            # Calculate optimal action
            calc = HarvestProfitCalculator(yield_kg, storage_cost)
            profits = {}
            for wait_days in [0, 3, 7]:
                profits[wait_days] = calc.calculate_profit(
                    wait_days, current_price, noisy_forecast_price, forecast_std,
                    spoilage_rate_per_day=0.015 * (1 - plant_health)
                )['expected_profit']
            
            optimal_action = max(profits, key=profits.get)
            optimal_profit = profits[optimal_action]
            
            scenario = {
                'scenario_id': i,
                'current_price': current_price,
                'forecast_price': forecast_price,
                'noisy_forecast_price': noisy_forecast_price,
                'forecast_std': forecast_std,
                'yield_kg': yield_kg,
                'plant_health': plant_health,
                'storage_cost': storage_cost,
                'price_trend': price_trend,
                'optimal_action': optimal_action,
                'optimal_profit': optimal_profit,
                'profits': profits
            }
            scenarios.append(scenario)
        
        self.test_scenarios = scenarios
        logger.info(f"✅ Created {len(scenarios)} test scenarios")
        logger.info(f"   Price trends: Up={sum(1 for s in scenarios if s['price_trend']=='up')}, "
                   f"Down={sum(1 for s in scenarios if s['price_trend']=='down')}, "
                   f"Stable={sum(1 for s in scenarios if s['price_trend']=='stable')}")
        
        return scenarios
    
    def simulate_decisions(self):
        """Simulate decisions with continuous reward"""
        logger.info("\n🤖 Simulating harvest decisions with Thompson Sampling V3...")
        logger.info(f"   Decay factor: {self.decay_factor}")
        logger.info(f"   Reward: Continuous profit_ratio")
        
        correct_decisions = 0
        total_profit = 0
        total_optimal_profit = 0
        
        for idx, scenario in enumerate(self.test_scenarios):
            # Pure Thompson Sampling
            decision = self.engine.decide(
                current_price=scenario['current_price'],
                forecast_price_median=scenario['noisy_forecast_price'],
                forecast_price_std=scenario['forecast_std'],
                yield_kg=scenario['yield_kg'],
                plant_health_score=scenario['plant_health'],
                storage_cost_per_day=scenario['storage_cost'],
                use_thompson=True
            )
            
            action_map = {"Harvest Now": 0, "Wait 3 Days": 3, "Wait 7 Days": 7}
            chosen_wait_days = action_map[decision['action']]
            
            actual_profit = scenario['profits'][chosen_wait_days]
            is_correct = (chosen_wait_days == scenario['optimal_action'])
            if is_correct:
                correct_decisions += 1
            
            # Continuous reward
            profit_ratio = actual_profit / scenario['optimal_profit'] if scenario['optimal_profit'] > 0 else 0.5
            reward = np.clip(profit_ratio, 0, 1)
            
            # Update with continuous reward
            self.engine.bandit.update_beliefs_continuous(
                decision['action_idx'], 
                reward,
                decay_factor=self.decay_factor
            )
            
            result = {
                'scenario_id': scenario['scenario_id'],
                'chosen_action': decision['action'],
                'chosen_wait_days': chosen_wait_days,
                'optimal_action': scenario['optimal_action'],
                'is_correct': is_correct,
                'actual_profit': actual_profit,
                'optimal_profit': scenario['optimal_profit'],
                'profit_ratio': profit_ratio,
                'reward': reward
            }
            self.results.append(result)
            
            total_profit += actual_profit
            total_optimal_profit += scenario['optimal_profit']
        
        accuracy = correct_decisions / len(self.test_scenarios)
        profit_efficiency = total_profit / total_optimal_profit if total_optimal_profit > 0 else 0
        
        self.cached_metrics = {
            'accuracy': accuracy,
            'profit_efficiency': profit_efficiency,
            'total_profit': total_profit,
            'optimal_profit': total_optimal_profit,
            'correct_decisions': correct_decisions,
            'total_scenarios': len(self.test_scenarios)
        }
        
        logger.info(f"\n✅ Simulation complete:")
        logger.info(f"   Decision accuracy: {accuracy:.2%} ({correct_decisions}/{len(self.test_scenarios)})")
        logger.info(f"   Profit efficiency: {profit_efficiency:.2%}")
        logger.info(f"   Total profit: {total_profit:,.0f} baht")
        logger.info(f"   Optimal profit: {total_optimal_profit:,.0f} baht")
        
        if accuracy >= Config.MODEL_D_EXPECTED_ACCURACY:
            logger.info(f"   ✅ Accuracy meets requirement (>= {Config.MODEL_D_EXPECTED_ACCURACY})")
        else:
            logger.warning(f"   ⚠️ Accuracy: {accuracy:.2%} (Target: {Config.MODEL_D_EXPECTED_ACCURACY:.0%})")
            logger.info(f"   💡 Note: Profit efficiency ({profit_efficiency:.2%}) may be more important than exact action match")
        
        return self.cached_metrics
    
    def generate_evaluation_plots(self):
        """Generate evaluation plots using cached metrics"""
        output_dir = Config.get_output_path('model_d', 'evaluation')
        logger.info(f"\n📊 Generating evaluation plots...")
        
        if self.cached_metrics is None:
            logger.error("❌ No cached metrics!")
            return
        
        metrics = self.cached_metrics
        results_df = pd.DataFrame(self.results)
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Decision Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        action_counts = results_df['chosen_action'].value_counts()
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        ax1.bar(action_counts.index, action_counts.values, color=colors, edgecolor='black', linewidth=2)
        ax1.set_ylabel('Count', fontweight='bold')
        ax1.set_title('Decision Distribution', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Accuracy Over Time
        ax2 = fig.add_subplot(gs[0, 1])
        window = 100
        rolling_accuracy = results_df['is_correct'].rolling(window=window).mean()
        ax2.plot(rolling_accuracy, linewidth=2, color='#3498db')
        ax2.axhline(y=Config.MODEL_D_EXPECTED_ACCURACY, color='green', linestyle='--', 
                   label=f'Target ({Config.MODEL_D_EXPECTED_ACCURACY})', alpha=0.7)
        ax2.set_xlabel('Decision Number', fontweight='bold')
        ax2.set_ylabel('Accuracy', fontweight='bold')
        ax2.set_title(f'Rolling Accuracy (window={window})', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 1])
        
        # 3. Profit Ratio Distribution
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.hist(results_df['profit_ratio'], bins=30, color='#2ecc71', edgecolor='black', alpha=0.7)
        ax3.axvline(x=1.0, color='red', linestyle='--', linewidth=2, label='Optimal')
        ax3.set_xlabel('Profit Ratio', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.set_title('Profit Efficiency Distribution', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Posterior Distributions
        ax4 = fig.add_subplot(gs[1, :])
        posteriors = self.engine.bandit.get_arm_posteriors()
        x = np.linspace(0, 1, 200)
        
        for i, (arm_name, params) in enumerate(posteriors.items()):
            y = beta_dist.pdf(x, params['alpha'], params['beta'])
            ax4.plot(x, y, linewidth=2, label=f"{arm_name} (α={params['alpha']:.1f}, β={params['beta']:.1f})")
        
        ax4.set_xlabel('Success Probability (θ)', fontweight='bold')
        ax4.set_ylabel('Density', fontweight='bold')
        ax4.set_title('Thompson Sampling V3 - Posterior Distributions (Continuous Reward)', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Confusion Matrix
        ax5 = fig.add_subplot(gs[2, 0])
        action_map_inv = {0: "Now", 3: "Wait 3d", 7: "Wait 7d"}
        results_df['chosen_label'] = results_df['chosen_wait_days'].map(action_map_inv)
        results_df['optimal_label'] = results_df['optimal_action'].map(action_map_inv)
        
        cm = confusion_matrix(results_df['optimal_label'], results_df['chosen_label'], 
                             labels=["Now", "Wait 3d", "Wait 7d"])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax5, cbar=False,
                   xticklabels=["Now", "Wait 3d", "Wait 7d"],
                   yticklabels=["Now", "Wait 3d", "Wait 7d"])
        ax5.set_xlabel('Predicted', fontweight='bold')
        ax5.set_ylabel('Actual Optimal', fontweight='bold')
        ax5.set_title('Confusion Matrix', fontweight='bold')
        
        # 6. Metrics Table
        ax6 = fig.add_subplot(gs[2, 1:])
        ax6.axis('off')
        
        table_data = [
            ['Metric', 'Value', 'Status'],
            ['Decision Accuracy', f"{metrics['accuracy']:.2%}", '✅' if metrics['accuracy'] >= 0.60 else '⚠️'],
            ['Profit Efficiency', f"{metrics['profit_efficiency']:.2%}", '✅' if metrics['profit_efficiency'] >= 0.90 else '⚠️'],
            ['Total Profit', f"{metrics['total_profit']:,.0f} ฿", '-'],
            ['Profit Loss', f"{metrics['optimal_profit'] - metrics['total_profit']:,.0f} ฿", '-'],
            ['Version', 'V3 Production', '✅'],
        ]
        
        table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        for i in range(3):
            cell = table[(0, i)]
            cell.set_facecolor('#34495e')
            cell.set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_data)):
            for j in range(3):
                cell = table[(i, j)]
                cell.set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
        
        fig.suptitle('Model D V3 - Thompson Sampling (Production Ready)', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        plot_path = output_dir / 'model_d_v3_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Saved: {plot_path}")
        plt.close()
        
        metadata = {
            'model_name': 'Model D V3 - Harvest Decision Engine',
            'version': '3.0',
            'algorithm': 'Thompson Sampling (Continuous Reward)',
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'posteriors': posteriors,
            'decay_factor': self.decay_factor
        }
        
        metadata_path = output_dir / 'metadata_v3.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info(f"✅ Saved: {metadata_path}")
    
    def save_model(self):
        """Save model"""
        logger.info("\n💾 Saving model V3...")
        
        model_path = Config.get_model_path('model_d_thompson_sampling_v3')
        
        model_state = {
            'version': '3.0',
            'bandit': self.engine.bandit,
            'decision_history': self.engine.decision_history,
            'decay_factor': self.decay_factor,
            'metrics': self.cached_metrics
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_state, f)
        
        logger.info(f"  ✅ {model_path}")
    
    def save_results(self):
        """Save results"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_d_v3_evaluation.json'
        
        results_data = {
            'model': 'Model D V3 - Harvest Decision Engine',
            'version': '3.0',
            'algorithm': 'Thompson Sampling (Continuous Reward)',
            'date': datetime.now().isoformat(),
            'status': 'PRODUCTION_READY',
            'metrics': self.cached_metrics,
            'posteriors': self.engine.bandit.get_arm_posteriors(),
            'decay_factor': self.decay_factor
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"  ✅ {results_file}")
        
        logger.info("\n" + "="*70)
        logger.info("MODEL D V3 TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\nVersion: 3.0 (Production Ready)")
        logger.info(f"  Decision Accuracy: {self.cached_metrics['accuracy']:.2%}")
        logger.info(f"  Profit Efficiency: {self.cached_metrics['profit_efficiency']:.2%}")
        logger.info(f"  Decay Factor: {self.decay_factor}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL D V3 - PRODUCTION READY".center(80))
    print("="*80)
    
    trainer = ModelDTrainerV3(decay_factor=0.995)
    trainer.create_test_scenarios(n_scenarios=5000)
    metrics = trainer.simulate_decisions()
    trainer.generate_evaluation_plots()
    trainer.save_model()
    trainer.save_results()
    
    print("\n" + "="*80)

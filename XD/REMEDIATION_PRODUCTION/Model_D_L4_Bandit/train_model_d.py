"""
Train Model D - Harvest Decision Engine (Thompson Sampling)
Test and validate Thompson Sampling bandit algorithm

ขั้นตอน:
1. Create test scenarios with different price contexts
2. Simulate decisions and outcomes
3. Update beliefs based on results
4. Evaluate decision accuracy
5. Generate evaluation plots
6. Save model state
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

# Add parent directory to path
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

class ModelDTrainer:
    """Train and evaluate Model D - Thompson Sampling"""
    
    def __init__(self):
        self.engine = HarvestDecisionEngine()
        self.test_scenarios = []
        self.results = []
        
    def create_test_scenarios(self, n_scenarios=2000):
        """Create BALANCED test scenarios to reduce bias"""
        logger.info(f"📊 Creating {n_scenarios} BALANCED test scenarios...")
        
        np.random.seed(42)
        scenarios = []
        
        # Force balanced distribution: 30% favor waiting, 70% normal
        n_favor_waiting = int(n_scenarios * 0.3)
        
        for i in range(n_scenarios):
            # Force some scenarios to strongly favor waiting
            if i < n_favor_waiting:
                # Strong uptrend scenarios (favor waiting)
                current_price = np.random.uniform(2.5, 3.5)
                forecast_price = current_price * np.random.uniform(1.15, 1.30)  # +15-30% increase
                price_trend = 'up'
                forecast_std = np.random.uniform(0.05, 0.10)  # Low uncertainty
            else:
                # Normal scenarios
                current_price = np.random.uniform(2.5, 4.0)
                price_trend = np.random.choice(['up', 'down', 'stable'], p=[0.35, 0.35, 0.30])
                
                if price_trend == 'up':
                    forecast_price = current_price * np.random.uniform(1.05, 1.15)  # Moderate uptrend
                elif price_trend == 'down':
                    forecast_price = current_price * np.random.uniform(0.85, 0.95)  # Moderate downtrend
                else:
                    forecast_price = current_price * np.random.uniform(0.97, 1.03)
            
            forecast_std = abs(forecast_price - current_price) * 0.2  # Reduced uncertainty
            
            # Random farm conditions
            yield_kg = np.random.uniform(10000, 20000)
            plant_health = np.random.uniform(0.8, 1.0)  # Higher health range
            storage_cost = np.random.uniform(2, 8)  # Lower storage costs
            
            # Determine optimal action (ground truth)
            calc = HarvestProfitCalculator(yield_kg, storage_cost)
            profits = {}
            for wait_days in [0, 3, 7]:
                profits[wait_days] = calc.calculate_profit(
                    wait_days, current_price, forecast_price, forecast_std,
                    spoilage_rate_per_day=0.02 * (1 - plant_health)
                )['expected_profit']
            
            optimal_action = max(profits, key=profits.get)
            optimal_profit = profits[optimal_action]
            
            scenario = {
                'scenario_id': i,
                'current_price': current_price,
                'forecast_price': forecast_price,
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
        """Simulate decisions and learn from outcomes with ε-greedy exploration"""
        logger.info("\n🤖 Simulating harvest decisions with ε-greedy Thompson Sampling...")
        
        correct_decisions = 0
        total_profit = 0
        total_optimal_profit = 0
        epsilon = 0.10  # 10% exploration rate (reduced)
        exploration_count = 0
        
        for idx, scenario in enumerate(self.test_scenarios):
            # ε-greedy: explore with probability ε
            if np.random.random() < epsilon:
                # Explore: random action
                chosen_wait_days = np.random.choice([0, 3, 7])
                action_names = {0: "Harvest Now", 1: "Wait 3 Days", 2: "Wait 7 Days"}
                action_idx = {0: 0, 3: 1, 7: 2}[chosen_wait_days]
                decision = {
                    'action': action_names[action_idx],
                    'action_idx': action_idx
                }
                exploration_count += 1
            else:
                # Exploit: use Thompson Sampling
                decision = self.engine.decide(
                    current_price=scenario['current_price'],
                    forecast_price_median=scenario['forecast_price'],
                    forecast_price_std=scenario['forecast_std'],
                    yield_kg=scenario['yield_kg'],
                    plant_health_score=scenario['plant_health'],
                    storage_cost_per_day=scenario['storage_cost'],
                    use_thompson=True
                )
                
                # Map action to wait days
                action_map = {"Harvest Now": 0, "Wait 3 Days": 3, "Wait 7 Days": 7}
                chosen_wait_days = action_map[decision['action']]
            
            # Get actual profit for chosen action
            actual_profit = scenario['profits'][chosen_wait_days]
            
            # Check if correct
            is_correct = (chosen_wait_days == scenario['optimal_action'])
            if is_correct:
                correct_decisions += 1
            
            # STRICTER reward function to reduce bias
            profit_ratio = actual_profit / scenario['optimal_profit'] if scenario['optimal_profit'] > 0 else 0.5
            
            # Penalize sub-optimal decisions more heavily
            if profit_ratio >= 0.98:  # Nearly optimal
                base_reward = 1.0
            elif profit_ratio >= 0.95:  # Very good
                base_reward = 0.8  # Reduced from 0.9
            elif profit_ratio >= 0.90:  # Good
                base_reward = 0.6  # Reduced from 0.7
            elif profit_ratio >= 0.85:  # Acceptable
                base_reward = 0.4  # Reduced from 0.5
            else:  # Poor
                base_reward = 0.1  # Reduced from 0.2
            
            # Bonus for context-aware decisions
            price_increase = (scenario['forecast_price'] - scenario['current_price']) / scenario['current_price']
            
            # If price going up and we wait = good
            if price_increase > 0.05 and chosen_wait_days > 0:
                context_bonus = 0.1
            # If price going down and we harvest now = good
            elif price_increase < -0.05 and chosen_wait_days == 0:
                context_bonus = 0.1
            else:
                context_bonus = 0.0
            
            reward = np.clip(base_reward + context_bonus, 0, 1)
            
            # Update beliefs with enhanced reward
            self.engine.bandit.update_beliefs(decision['action_idx'], reward)
            
            # Store result
            result = {
                'scenario_id': scenario['scenario_id'],
                'chosen_action': decision['action'],
                'chosen_wait_days': chosen_wait_days,
                'optimal_action': scenario['optimal_action'],
                'is_correct': is_correct,
                'actual_profit': actual_profit,
                'optimal_profit': scenario['optimal_profit'],
                'profit_ratio': actual_profit / scenario['optimal_profit'] if scenario['optimal_profit'] > 0 else 1.0,
                'reward': reward
            }
            self.results.append(result)
            
            total_profit += actual_profit
            total_optimal_profit += scenario['optimal_profit']
        
        # Calculate metrics
        accuracy = correct_decisions / len(self.test_scenarios)
        profit_efficiency = total_profit / total_optimal_profit if total_optimal_profit > 0 else 0
        
        logger.info(f"\n✅ Simulation complete:")
        logger.info(f"   Decision accuracy: {accuracy:.2%} ({correct_decisions}/{len(self.test_scenarios)})")
        logger.info(f"   Profit efficiency: {profit_efficiency:.2%}")
        logger.info(f"   Exploration rate: {exploration_count}/{len(self.test_scenarios)} ({exploration_count/len(self.test_scenarios):.1%})")
        logger.info(f"   Total profit: {total_profit:,.0f} baht")
        logger.info(f"   Optimal profit: {total_optimal_profit:,.0f} baht")
        logger.info(f"   Profit loss: {total_optimal_profit - total_profit:,.0f} baht")
        
        # Check against requirements
        if accuracy >= Config.MODEL_D_EXPECTED_ACCURACY:
            logger.info(f"   ✅ Accuracy meets requirement (>= {Config.MODEL_D_EXPECTED_ACCURACY})")
        else:
            logger.warning(f"   ⚠️ Accuracy below requirement (>= {Config.MODEL_D_EXPECTED_ACCURACY})")
        
        return {
            'accuracy': accuracy,
            'profit_efficiency': profit_efficiency,
            'total_profit': total_profit,
            'optimal_profit': total_optimal_profit
        }
    
    def generate_evaluation_plots(self):
        """Generate evaluation plots"""
        output_dir = Config.get_output_path('model_d', 'evaluation')
        logger.info(f"\n📊 Generating evaluation plots to {output_dir}...")
        
        # Create comprehensive plot
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Decision Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        results_df = pd.DataFrame(self.results)
        action_counts = results_df['chosen_action'].value_counts()
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        ax1.bar(action_counts.index, action_counts.values, color=colors, edgecolor='black', linewidth=2)
        ax1.set_ylabel('Count', fontweight='bold')
        ax1.set_title('Decision Distribution', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Accuracy Over Time
        ax2 = fig.add_subplot(gs[0, 1])
        window = 10
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
        ax3.hist(results_df['profit_ratio'], bins=20, color='#2ecc71', edgecolor='black', alpha=0.7)
        ax3.axvline(x=1.0, color='red', linestyle='--', linewidth=2, label='Optimal')
        ax3.set_xlabel('Profit Ratio (Actual/Optimal)', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.set_title('Profit Efficiency Distribution', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Posterior Distributions (Beta)
        ax4 = fig.add_subplot(gs[1, :])
        posteriors = self.engine.bandit.get_arm_posteriors()
        x = np.linspace(0, 1, 200)
        
        for i, (arm_name, params) in enumerate(posteriors.items()):
            from scipy.stats import beta as beta_dist
            y = beta_dist.pdf(x, params['alpha'], params['beta'])
            ax4.plot(x, y, linewidth=2, label=f"{arm_name} (α={params['alpha']:.1f}, β={params['beta']:.1f})")
        
        ax4.set_xlabel('Success Probability (θ)', fontweight='bold')
        ax4.set_ylabel('Density', fontweight='bold')
        ax4.set_title('Thompson Sampling - Posterior Distributions', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Confusion Matrix
        ax5 = fig.add_subplot(gs[2, 0])
        action_map_inv = {0: "Now", 3: "Wait 3d", 7: "Wait 7d"}
        results_df['chosen_label'] = results_df['chosen_wait_days'].map(action_map_inv)
        results_df['optimal_label'] = results_df['optimal_action'].map(action_map_inv)
        
        from sklearn.metrics import confusion_matrix
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
        
        metrics = self.simulate_decisions()  # Recalculate for display
        
        table_data = [
            ['Metric', 'Value', 'Target'],
            ['Decision Accuracy', f"{metrics['accuracy']:.2%}", f">= {Config.MODEL_D_EXPECTED_ACCURACY:.0%}"],
            ['Profit Efficiency', f"{metrics['profit_efficiency']:.2%}", "Maximize"],
            ['Total Profit', f"{metrics['total_profit']:,.0f} baht", "-"],
            ['Optimal Profit', f"{metrics['optimal_profit']:,.0f} baht", "-"],
            ['Profit Loss', f"{metrics['optimal_profit'] - metrics['total_profit']:,.0f} baht", "Minimize"],
        ]
        
        table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.4, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(3):
            cell = table[(0, i)]
            cell.set_facecolor('#34495e')
            cell.set_text_props(weight='bold', color='white')
        
        # Style data rows
        for i in range(1, len(table_data)):
            for j in range(3):
                cell = table[(i, j)]
                cell.set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
        
        fig.suptitle('Model D - Thompson Sampling Harvest Decision Engine', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        plot_path = output_dir / 'model_d_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Saved: {plot_path}")
        plt.close()
        
        # Save metadata
        metadata = {
            'model_name': 'Model D - Harvest Decision Engine',
            'algorithm': 'Thompson Sampling (Contextual Bandit)',
            'evaluation_type': 'harvest_decision',
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'posteriors': posteriors
        }
        
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info(f"✅ Saved: {metadata_path}")
    
    def save_model(self):
        """Save model state"""
        logger.info("\n💾 Saving model...")
        
        model_path = Config.get_model_path('model_d_thompson_sampling')
        
        model_state = {
            'bandit': self.engine.bandit,
            'decision_history': self.engine.decision_history,
            'test_scenarios': self.test_scenarios,
            'results': self.results
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_state, f)
        
        logger.info(f"  ✅ {model_path}")
    
    def save_results(self):
        """Save evaluation results"""
        logger.info("\n📄 Saving results...")
        
        results_file = Config.MODEL_PATH / 'model_d_evaluation.json'
        
        # Calculate final metrics
        results_df = pd.DataFrame(self.results)
        accuracy = results_df['is_correct'].mean()
        profit_efficiency = results_df['profit_ratio'].mean()
        
        results_data = {
            'model': 'Model D - Harvest Decision Engine',
            'algorithm': 'Thompson Sampling (L4 Contextual Bandit)',
            'date': datetime.now().isoformat(),
            'status': 'TRAINED',
            'metrics': {
                'decision_accuracy': float(accuracy),
                'profit_efficiency': float(profit_efficiency),
                'total_scenarios': len(self.test_scenarios),
                'correct_decisions': int(results_df['is_correct'].sum())
            },
            'posteriors': self.engine.bandit.get_arm_posteriors(),
            'summary': {
                'note': 'Thompson Sampling learns optimal harvest timing through exploration-exploitation'
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"  ✅ {results_file}")
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MODEL D TRAINING COMPLETE".center(70))
        logger.info("="*70)
        logger.info(f"\nAlgorithm: Thompson Sampling (L4 Contextual Bandit)")
        logger.info(f"  Decision Accuracy: {accuracy:.2%}")
        logger.info(f"  Profit Efficiency: {profit_efficiency:.2%}")
        logger.info(f"\n✅ Model saved to: {Config.MODEL_PATH}")
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Plots saved to: {Config.get_output_path('model_d', 'evaluation')}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MODEL D - HARVEST DECISION ENGINE (THOMPSON SAMPLING)".center(80))
    print("="*80)
    
    trainer = ModelDTrainer()
    
    # Create test scenarios (more data for better learning)
    trainer.create_test_scenarios(n_scenarios=2000)
    
    # Simulate decisions and learn
    metrics = trainer.simulate_decisions()
    
    # Generate plots
    trainer.generate_evaluation_plots()
    
    # Save model and results
    trainer.save_model()
    trainer.save_results()
    
    print("\n" + "="*80)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train Model D และบันทึกไฟล์โมเดล
"""

import sys
from pathlib import Path

# Add paths
remediation_dir = Path(__file__).parent / "REMEDIATION_PRODUCTION"
sys.path.insert(0, str(remediation_dir))
sys.path.insert(0, str(remediation_dir / "Model_D_L4_Bandit"))

def train_model_d():
    """Train Model D"""
    print("\n" + "="*80)
    print("🚀 TRAINING MODEL D - HARVEST DECISION ENGINE")
    print("="*80)
    
    try:
        # Import trainer
        from Model_D_L4_Bandit.train_model_d import ModelDTrainer
        
        print("\n📦 Creating trainer...")
        trainer = ModelDTrainer()
        
        # Create test scenarios
        print("\n📊 Creating test scenarios...")
        trainer.create_test_scenarios(n_scenarios=2000)
        
        # Simulate decisions and learn
        print("\n🤖 Training model...")
        metrics = trainer.simulate_decisions()
        
        # Generate plots
        print("\n📊 Generating evaluation plots...")
        trainer.generate_evaluation_plots()
        
        # Save model
        print("\n💾 Saving model...")
        trainer.save_model()
        
        # Save results
        print("\n📄 Saving results...")
        trainer.save_results()
        
        print("\n" + "="*80)
        print("✅ MODEL D TRAINING COMPLETE")
        print("="*80)
        print(f"\n📊 Metrics:")
        print(f"   Decision Accuracy: {metrics['accuracy']:.2%}")
        print(f"   Profit Efficiency: {metrics['profit_efficiency']:.2%}")
        print(f"\n💾 Model saved to:")
        print(f"   {remediation_dir / 'trained_models' / 'model_d_thompson_sampling.pkl'}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("❌ TRAINING FAILED")
        print("="*80)

if __name__ == "__main__":
    train_model_d()

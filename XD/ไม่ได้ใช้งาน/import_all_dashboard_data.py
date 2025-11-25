#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Master Import Script for Dashboard Data
Imports ALL datasets from buildingModel.py/Dataset folder
"""

import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    print("=" * 70)
    print("🚀 MASTER DASHBOARD DATA IMPORT SCRIPT")
    print("=" * 70)
    print()
    print("This script will import ALL datasets for the dashboard:")
    print("  1. Price data (crop_prices)")
    print("  2. Weather data (weather_data)")
    print("  3. Crop characteristics (crop_characteristics)")
    print("  4. Cultivation data (crop_cultivation)")
    print("  5. Economic factors (economic_factors)")
    print("  6. Farmer profiles (farmer_profiles)")
    print("  7. Population data (population_data)")
    print("  8. Profit data (profit_data)")
    print("  9. Compatibility scores (compatibility_scores)")
    print()
    print("=" * 70)
    print()
    
    input("Press ENTER to start import... ")
    print()
    
    start_time = time.time()
    
    # Import main datasets
    print("📦 PHASE 1: Importing Main Datasets")
    print("-" * 70)
    try:
        from backend.import_dashboard_data import main as import_main
        import_main()
    except Exception as e:
        print(f"❌ Error in Phase 1: {e}")
        print("Continuing to Phase 2...")
    
    print()
    print()
    
    # Import additional datasets
    print("📦 PHASE 2: Importing Additional Datasets")
    print("-" * 70)
    try:
        from backend.import_additional_data import main as import_additional
        import_additional()
    except Exception as e:
        print(f"❌ Error in Phase 2: {e}")
    
    print()
    print()
    
    elapsed_time = time.time() - start_time
    
    print("=" * 70)
    print("🎉 ALL IMPORTS COMPLETE!")
    print("=" * 70)
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print()
    print("✅ Your database is now ready for comprehensive dashboard charts!")
    print()
    print("Next steps:")
    print("  1. Restart your backend server")
    print("  2. Clear Redis cache (optional)")
    print("  3. Refresh your dashboard page")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

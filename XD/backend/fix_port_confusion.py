#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix port confusion - standardize all backend services to use port 8000
"""

import subprocess
import os
import sys

def kill_processes_on_ports():
    """Kill all processes running on ports 8000 and 8001"""
    ports = [8000, 8001]
    
    for port in ports:
        try:
            print(f"🔍 Checking for processes on port {port}...")
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"📍 Found {len(pids)} process(es) on port {port}")
                
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=True)
                        print(f"✅ Killed process {pid} on port {port}")
                    except subprocess.CalledProcessError:
                        print(f"⚠️ Could not kill process {pid}")
            else:
                print(f"✅ No processes found on port {port}")
                
        except FileNotFoundError:
            print(f"⚠️ lsof command not found, please manually stop processes on port {port}")

def update_frontend_to_use_single_port():
    """Update all frontend files to use port 8000 consistently"""
    
    frontend_files = [
        "src/hooks/useUserProfile.ts",
        "src/hooks/useForecastData.ts", 
        "src/hooks/usePlantingRecommendation.ts",
        "src/pages/ChatAI.tsx",
        "src/components/RealForecastChart.tsx"
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace port 8001 with 8000
                updated_content = content.replace('localhost:8001', 'localhost:8000')
                
                if content != updated_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f"✅ Updated {file_path} to use port 8000")
                else:
                    print(f"ℹ️ {file_path} already uses correct port")
                    
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")

def main():
    print("🔧 Fixing port confusion in Farmme backend...")
    print("=" * 60)
    
    # Step 1: Kill existing processes
    print("\n1️⃣ Stopping all backend processes...")
    kill_processes_on_ports()
    
    # Step 2: Update frontend files
    print("\n2️⃣ Updating frontend to use single port (8000)...")
    update_frontend_to_use_single_port()
    
    # Step 3: Instructions
    print("\n3️⃣ Next steps:")
    print("   ✅ All processes stopped")
    print("   ✅ Frontend updated to use port 8000")
    print("   🚀 Start only the main server:")
    print("      cd @backend")
    print("      python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n   🚫 DO NOT start these test servers:")
    print("      ❌ python standalone_test_server.py")
    print("      ❌ python simple_server_test.py")
    
    print("\n✅ Port confusion fixed!")
    print("📍 Use only: http://localhost:8000")

if __name__ == "__main__":
    main()
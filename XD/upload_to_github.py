#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload Project to GitHub using GitHub API
No Git installation required!
"""

import os
import base64
import requests
import json
from pathlib import Path

# GitHub Configuration
GITHUB_TOKEN = "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"
GITHUB_USERNAME = "Phattarapong26"
REPO_NAME = "app"
BRANCH = "main"

# API Base URL
API_BASE = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}"

# Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Files and directories to ignore (from .gitignore)
IGNORE_PATTERNS = [
    '.env',
    '.env.local',
    '.env.backup',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    '.git',
    '*.pyc',
    '*.db',
    '*.sqlite',
    '*.log',
    '.DS_Store',
    'Thumbs.db',
    '*.pkl',
    '*.h5',
    'Dataset',
    'exports',
]

def should_ignore(file_path):
    """Check if file should be ignored"""
    path_str = str(file_path)
    
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    
    # Ignore large files (>10MB)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 10:
            print(f"⚠️  Skipping large file ({size_mb:.1f}MB): {file_path}")
            return True
    
    return False

def create_or_update_file(file_path, content, message):
    """Create or update a file in GitHub repository"""
    
    # Convert to relative path
    rel_path = str(file_path).replace('\\', '/')
    
    # Encode content to base64
    content_encoded = base64.b64encode(content).decode('utf-8')
    
    # Check if file exists
    url = f"{API_BASE}/contents/{rel_path}"
    response = requests.get(url, headers=HEADERS)
    
    data = {
        "message": message,
        "content": content_encoded,
        "branch": BRANCH
    }
    
    # If file exists, include SHA for update
    if response.status_code == 200:
        file_data = response.json()
        data["sha"] = file_data["sha"]
        print(f"  📝 Updating: {rel_path}")
    else:
        print(f"  ✨ Creating: {rel_path}")
    
    # Create or update file
    response = requests.put(url, headers=HEADERS, json=data)
    
    if response.status_code in [200, 201]:
        return True
    else:
        print(f"  ❌ Failed: {rel_path} - {response.status_code}")
        print(f"     {response.json().get('message', 'Unknown error')}")
        return False

def upload_directory(directory, base_path=""):
    """Upload all files in directory recursively"""
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for item in Path(directory).rglob('*'):
        # Skip if should be ignored
        if should_ignore(item):
            skip_count += 1
            continue
        
        # Only process files
        if not item.is_file():
            continue
        
        try:
            # Read file content
            with open(item, 'rb') as f:
                content = f.read()
            
            # Get relative path
            try:
                rel_path = item.relative_to(Path.cwd())
            except ValueError:
                # If relative_to fails, try another approach
                rel_path = Path(str(item).replace(str(Path.cwd()) + os.sep, ''))
            
            # Upload file
            if create_or_update_file(rel_path, content, f"Add: {rel_path}"):
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            print(f"  ❌ Error with {item}: {e}")
            fail_count += 1
    
    return success_count, fail_count, skip_count

def check_repository():
    """Check if repository exists"""
    print("🔍 Checking repository...")
    
    response = requests.get(API_BASE, headers=HEADERS)
    
    if response.status_code == 200:
        print(f"✅ Repository exists: {GITHUB_USERNAME}/{REPO_NAME}")
        return True
    elif response.status_code == 404:
        print(f"❌ Repository not found: {GITHUB_USERNAME}/{REPO_NAME}")
        print(f"   Please create it first at: https://github.com/new")
        return False
    else:
        print(f"❌ Error checking repository: {response.status_code}")
        return False

def main():
    """Main upload function"""
    print("=" * 60)
    print("🚀 Upload to GitHub using API")
    print("=" * 60)
    print(f"Repository: {GITHUB_USERNAME}/{REPO_NAME}")
    print(f"Branch: {BRANCH}")
    print()
    
    # Check repository exists
    if not check_repository():
        return False
    
    print()
    print("📦 Starting upload...")
    print("⚠️  This may take a while for large projects")
    print()
    
    # Upload files
    success, fail, skip = upload_directory(".")
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Upload Summary")
    print("=" * 60)
    print(f"✅ Uploaded: {success} files")
    print(f"❌ Failed: {fail} files")
    print(f"⏭️  Skipped: {skip} files")
    print()
    
    if fail == 0:
        print("🎉 Upload completed successfully!")
        print(f"🌐 View at: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
    else:
        print("⚠️  Upload completed with some errors")
        print("   Check the messages above for details")
    
    print("=" * 60)
    
    return fail == 0

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

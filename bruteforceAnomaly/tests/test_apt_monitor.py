#!/usr/bin/env python3
"""
Test script for the APT monitoring functionality
"""

import os
import sys
import json

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config
from src.apt_monitor import APTMonitor

# Initialize configuration
config = Config()

def test_apt_monitor_initialization():
    """Test if the APT monitor can be initialized correctly"""
    print("🧪 Testing APT Monitor initialization")
    
    try:
        monitor = APTMonitor()
        print("✅ APT Monitor initialized successfully")
        print(f"  - Userlist path: {monitor.userlist_path}")
        print(f"  - APT log path: {monitor.apt_log_path}")
        print(f"  - Check interval: {monitor.check_interval} seconds")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize APT Monitor: {e}")
        return False

def test_userlist_access():
    """Test if the userlist file can be accessed and modified"""
    print("\n🧪 Testing userlist file access")
    
    userlist_path = config.get('paths.user_data.userlist')
    print(f"  - Userlist path: {userlist_path}")
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(userlist_path), exist_ok=True)
        
        # Create or load userlist file
        if not os.path.exists(userlist_path):
            test_data = {"suspicious_users": [
                {"username": "test_user", "ip": "192.168.1.100", "timestamp": "2025-07-05T12:00:00"}
            ]}
            with open(userlist_path, 'w') as f:
                json.dump(test_data, f, indent=2)
            print("✅ Created test userlist file")
        else:
            with open(userlist_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Loaded existing userlist with {len(data.get('suspicious_users', []))} users")
        
        return True
    except Exception as e:
        print(f"❌ Failed to access userlist file: {e}")
        return False

def run_tests():
    """Run all APT monitor tests"""
    print("=" * 50)
    print("🧪 RUNNING APT MONITOR TESTS")
    print("=" * 50)
    
    tests = [
        ("APT Monitor initialization", test_apt_monitor_initialization),
        ("Userlist file access", test_userlist_access)
    ]
    
    success_count = 0
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        if test_func():
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Test results: {success_count}/{len(tests)} tests passed")
    print("=" * 50)

if __name__ == "__main__":
    run_tests()

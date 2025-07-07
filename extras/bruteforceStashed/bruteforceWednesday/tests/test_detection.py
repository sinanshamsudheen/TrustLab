#!/usr/bin/env python3
"""
Test the SSH brute force detection system
"""

import os
import sys
import pandas as pd
import joblib

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config

# Initialize configuration
config = Config()

def test_model_loading():
    """Test if the model can be loaded correctly"""
    model_path = config.get('paths.models.bruteforce_model')
    print(f"🔍 Testing model loading from: {model_path}")
    
    try:
        model = joblib.load(model_path)
        print(f"✅ Model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def test_log_file_access():
    """Test if the log files can be accessed"""
    log_files = [
        ('Raw log', config.get('paths.logs.raw_log')),
        ('Recent log', config.get('paths.logs.recent_log')),
        ('Suspicious log', config.get('paths.logs.suspicious_log')),
        ('APT log', config.get('paths.logs.apt_log')),
        ('Monitor log', config.get('paths.logs.monitor_log'))
    ]
    
    all_success = True
    print("\n🔍 Testing log file access:")
    
    for name, path in log_files:
        log_dir = os.path.dirname(path)
        os.makedirs(log_dir, exist_ok=True)
        
        # Try creating or reading the file
        try:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(f"Test entry created at {path}\n")
                print(f"✅ {name} file created at {path}")
            else:
                print(f"✅ {name} file exists at {path}")
        except Exception as e:
            print(f"❌ Could not access {name} file at {path}: {e}")
            all_success = False
            
    return all_success

def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("🧪 RUNNING DETECTION SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        ("Model loading", test_model_loading),
        ("Log file access", test_log_file_access)
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

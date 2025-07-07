#!/usr/bin/env python3
"""
Tests the project structure by importing all key modules
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test all module imports to verify project structure"""
    print("🧪 Testing project structure and imports...")
    
    try:
        import pandas
        import joblib
        import yaml
        print("✅ External dependencies (pandas, joblib, yaml) successfully imported")
    except ImportError as e:
        print(f"❌ Missing external dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
    
    try:
        from src.config_loader import Config
        config = Config()
        print("✅ Configuration system successfully loaded")
        print(f"   - Config file path: {config.config_path}")
        print(f"   - Kafka broker: {config.get('kafka.broker')}")
    except ImportError as e:
        print(f"❌ Error loading configuration system: {e}")
    
    try:
        from src import apt_analyzer, apt_monitor, bruteforce_detector, bruteforce_parser
        print("✅ Core modules successfully imported")
    except ImportError as e:
        print(f"❌ Error importing core modules: {e}")
    
    # Check directory structure
    dirs = ['src', 'tests', 'config', 'logs', 'artifacts']
    all_found = True
    for directory in dirs:
        if os.path.isdir(os.path.join(project_root, directory)):
            print(f"✅ Directory '{directory}/' exists")
        else:
            print(f"❌ Directory '{directory}/' missing")
            all_found = False
    
    if all_found:
        print("✅ Project structure is correct")
    else:
        print("❌ Project structure has issues")

if __name__ == "__main__":
    test_imports()
    print("\n✅ Structure test complete")

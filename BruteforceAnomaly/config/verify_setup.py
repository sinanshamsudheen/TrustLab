#!/usr/bin/env python3
"""
Verification script to test all system dependencies and components
"""

import sys
import os
from datetime import datetime
import importlib

# Add project root to path to make imports work
if os.path.exists("/opt/BruteforceAnomaly"):
    project_root = "/opt/BruteforceAnomaly"
else:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Try to import the configuration
    from src.config_loader import Config
    config = Config()
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are available"""
    print("\n📦 Checking Python dependencies...")
    
    dependencies = [
        ('pandas', 'Core data processing'),
        ('sklearn', 'Machine learning'),
        ('joblib', 'Model serialization'),
        ('kafka', 'Kafka integration'),
        ('dateutil', 'Date/time processing'),
        ('yaml', 'Configuration file parsing')
    ]
    
    all_installed = True
    for package, purpose in dependencies:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - {purpose}")
        except ImportError:
            print(f"❌ {package} - {purpose} (MISSING)")
            all_installed = False
    
    return all_installed

def check_files():
    """Check if all required files are present"""
    print("\n📁 Checking required files...")
    
    required_files = [
        ('bruteforce_parser.py', 'Kafka log consumer'),
        ('tester2.py', 'Main analysis engine'),
        ('apt_analyzer.py', 'APT package monitoring'),
        ('test_log_parsing.py', 'Test utilities'),
        ('bruteforce_model.pkl', 'ML model'),
        ('requirements.txt', 'Dependencies list'),
        ('setup.sh', 'Setup script'),
        ('README.md', 'Documentation')
    ]
    
    missing_files = []
    
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} - {description} (MISSING)")
            missing_files.append(filename)
    
    return len(missing_files) == 0, missing_files

def check_directories():
    """Check if required directories can be created"""
    print("\n📂 Checking directory permissions...")
    
    test_dirs = [
        '/home/primum/logs',
        '/var/log/apt'
    ]
    
    for test_dir in test_dirs:
        try:
            os.makedirs(test_dir, exist_ok=True)
            if os.path.exists(test_dir):
                print(f"✅ {test_dir} - Accessible")
            else:
                print(f"⚠️  {test_dir} - Cannot create (permissions?)")
        except Exception as e:
            print(f"⚠️  {test_dir} - Error: {e}")

def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test ML model loading
        import joblib
        if os.path.exists('bruteforce_model.pkl'):
            model = joblib.load('bruteforce_model.pkl')
            print("✅ ML model loads successfully")
        else:
            print("⚠️  ML model file not found")
        
        # Test APT analyzer import
        from apt_analyzer import search_apt_history
        print("✅ APT analyzer imports successfully")
        
        # Test data processing
        import pandas as pd
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        print("✅ Data processing works")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def check_directory_structure():
    """Check if the project directory structure is valid"""
    print("\n📂 Checking directory structure...")
    
    required_dirs = [
        ('src', 'Core source code'),
        ('tests', 'Test scripts and utilities'),
        ('artifacts', 'Model files and data'),
        ('logs', 'Log files'),
        ('config', 'Configuration files')
    ]
    
    all_exist = True
    for directory, purpose in required_dirs:
        path = os.path.join(project_root, directory)
        if os.path.isdir(path):
            print(f"✅ {directory}/ - {purpose}")
        else:
            print(f"❌ {directory}/ - {purpose} (MISSING)")
            all_exist = False
    
    return all_exist

def check_configuration():
    """Check if the configuration system is working properly"""
    print("\n⚙️ Checking configuration...")
    
    if not CONFIG_AVAILABLE:
        print("❌ Configuration system not available")
        return False
    
    config_checks = [
        ('kafka.broker', 'Kafka broker address'),
        ('kafka.topics', 'Kafka topics list'),
        ('paths.logs.base_dir', 'Log directory'),
        ('paths.models.bruteforce_model', 'Bruteforce model path'),
        ('paths.user_data.userlist', 'User list path'),
        ('detection.time_window_seconds', 'Detection time window'),
        ('monitoring.check_interval', 'APT monitoring interval')
    ]
    
    all_configured = True
    for config_path, description in config_checks:
        value = config.get(config_path)
        if value is not None:
            print(f"✅ {config_path}: {value} - {description}")
        else:
            print(f"❌ {config_path} - {description} (MISSING)")
            all_configured = False
    
    return all_configured

def check_files():
    """Check if critical files exist"""
    print("\n📄 Checking critical files...")
    
    if not CONFIG_AVAILABLE:
        critical_files = [
            ('config/config.yaml', 'Main configuration file'),
            ('artifacts/bruteforce_model.pkl', 'Trained detection model'),
            ('config/userlist.json', 'User monitoring list'),
            ('src/bruteforce_detector.py', 'Bruteforce detection logic'),
            ('src/apt_monitor.py', 'APT monitoring service'),
            ('main.py', 'Main entry point')
        ]
    else:
        critical_files = [
            (config.config_path, 'Main configuration file'),
            (config.get('paths.models.bruteforce_model'), 'Trained detection model'),
            (config.get('paths.user_data.userlist'), 'User monitoring list'),
            (os.path.join(project_root, 'src/bruteforce_detector.py'), 'Bruteforce detection logic'),
            (os.path.join(project_root, 'src/apt_monitor.py'), 'APT monitoring service'),
            (os.path.join(project_root, 'main.py'), 'Main entry point')
        ]
    
    all_exist = True
    for file_path, description in critical_files:
        if os.path.isfile(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (MISSING)")
            all_exist = False
    
    return all_exist

def run_verification():
    """Run all verification checks"""
    print("=" * 60)
    print("🔍 TRUSTLAB SECURITY SYSTEM VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 60)
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directory structure", check_directory_structure),
        ("Configuration", check_configuration),
        ("Critical files", check_files)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("-" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("-" * 60)
    if all_passed:
        print("🎉 All checks passed! The system is properly configured.")
    else:
        print("⚠️ Some checks failed. Please address the issues above.")
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if run_verification() else 1)

#!/usr/bin/env python3
"""
Verification script to test all system dependencies and components
"""

import sys
import os
from datetime import datetime

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
        ('dateutil', 'Date/time processing')
    ]
    
    missing_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
        except ImportError:
            print(f"❌ {dep} - {description} (MISSING)")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0, missing_deps

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

def main():
    """Main verification function"""
    print("🔍 SSH BRUTE FORCE DETECTION SYSTEM VERIFICATION")
    print("=" * 55)
    print(f"Verification time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    python_ok = check_python_version()
    deps_ok, missing_deps = check_dependencies()
    files_ok, missing_files = check_files()
    check_directories()  # Non-critical
    func_ok = test_basic_functionality()
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 VERIFICATION SUMMARY:")
    
    if python_ok and deps_ok and files_ok and func_ok:
        print("🎉 ALL CHECKS PASSED - System is ready!")
        print("\n🚀 Next steps:")
        print("  1. Run: python3 test_log_parsing.py")
        print("  2. Run: python3 tester2.py")
        print("  3. For production: python3 bruteforce_parser.py")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues below:")
        
        if not python_ok:
            print("  • Upgrade Python to version 3.8 or higher")
        
        if not deps_ok:
            print("  • Install missing dependencies:")
            print("    pip install -r requirements.txt")
            for dep in missing_deps:
                print(f"    pip install {dep}")
        
        if not files_ok:
            print("  • Missing files:")
            for filename in missing_files:
                print(f"    {filename}")
        
        if not func_ok:
            print("  • System functionality issues detected")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

#!/bin/bash
"""
Setup script for the enhanced brute force detection system
"""

echo "🔧 Setting up Enhanced Brute Force Detection System..."

# Make Python scripts executable
chmod +x test_enhanced_detection.py
chmod +x db_manager.py

# Create necessary directories
mkdir -p /home/primum/logs

# Install required Python packages if not already installed
echo "📦 Checking Python dependencies..."

python3 -c "import pandas" 2>/dev/null || {
    echo "Installing pandas..."
    pip3 install pandas
}

python3 -c "import joblib" 2>/dev/null || {
    echo "Installing joblib..."
    pip3 install joblib
}

python3 -c "import dateutil" 2>/dev/null || {
    echo "Installing python-dateutil..."
    pip3 install python-dateutil
}

# Check if SQLite is available
python3 -c "import sqlite3" 2>/dev/null || {
    echo "❌ SQLite3 not available. Please install python3-sqlite3"
    exit 1
}

echo "✅ Setup completed!"
echo ""
echo "📚 Usage Examples:"
echo "  Run enhanced detection:     python3 tester2.py"
echo "  Test the system:           python3 test_enhanced_detection.py"
echo "  View database stats:       python3 db_manager.py --stats"
echo "  Show recent anomalies:     python3 db_manager.py --recent 24"
echo "  Show critical threats:     python3 db_manager.py --critical 24"
echo "  Export threat data:        python3 db_manager.py --export 24"
echo "  Cleanup old records:       python3 db_manager.py --cleanup 7"
echo ""
echo "🚀 System is ready to use!"

#!/bin/bash
"""
Setup script for SSH Brute Force Detection & APT Correlation System
"""

# Define project name and paths
PROJECT_NAME="BruteforceAnomaly"
SOURCE_DIR="$(dirname "$0")/.."
TARGET_DIR="/opt/$PROJECT_NAME"

echo "🔧 Setting up SSH Brute Force Detection & APT Correlation System..."

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "📁 Creating target directory at $TARGET_DIR..."
    sudo mkdir -p "$TARGET_DIR"
    sudo chown $(whoami):$(whoami) "$TARGET_DIR"
else
    echo "📁 Target directory $TARGET_DIR already exists."
fi

# Copy project files to target directory
echo "📋 Copying project files to $TARGET_DIR..."
sudo rsync -av --exclude="__pycache__" "$SOURCE_DIR/" "$TARGET_DIR/"
sudo chown -R $(whoami):$(whoami) "$TARGET_DIR"

# Move to project root at the target location
cd "$TARGET_DIR" || {
    echo "❌ Failed to change directory to $TARGET_DIR"
    exit 1
}

# Make Python scripts executable
echo "🔑 Setting executable permissions..."
chmod +x src/*.py
chmod +x tests/*.py
chmod +x config/*.py
chmod +x config/*.sh
chmod +x main.py

# Create necessary directories
echo "📁 Creating log directories..."
sudo mkdir -p /home/primum/logs
sudo mkdir -p /var/log/apt
mkdir -p "$TARGET_DIR/logs"

# Install required Python packages if not already installed
echo "📦 Installing Python dependencies from requirements.txt..."

if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
else
    echo "⚠️  requirements.txt not found, installing packages individually..."
    
    python3 -c "import pandas" 2>/dev/null || {
        echo "Installing pandas..."
        pip3 install pandas
    }

    # ...existing code...
fi

# Check if the ML model exists
if [ ! -f "$TARGET_DIR/artifacts/bruteforce_model.pkl" ]; then
    echo "⚠️  Warning: bruteforce_model.pkl not found!"
    echo "   The ML model is required for anomaly detection."
    echo "   Please ensure the model file is present before running the system."
fi

# Check Kafka connectivity (optional)
echo "🔗 Testing Kafka connectivity..."
python3 -c "
from kafka import KafkaConsumer
import socket
try:
    # Test connection to Kafka broker
    consumer = KafkaConsumer(bootstrap_servers=['10.130.171.246:9092'], consumer_timeout_ms=3000)
    consumer.close()
    print('✅ Kafka broker is reachable')
except Exception as e:
    print('⚠️  Warning: Cannot connect to Kafka broker (10.130.171.246:9092)')
    print('   This is normal if Kafka is not running or network is not available')
    print('   The system will work with test data')
" 2>/dev/null

# Create symbolic links for easy access
echo "🔗 Creating symbolic links for easy access..."
sudo ln -sf "$TARGET_DIR/main.py" /usr/local/bin/bruteforce-anomaly
sudo chmod +x /usr/local/bin/bruteforce-anomaly

# Install systemd service
echo "🔧 Installing systemd service..."
if [ -f "$TARGET_DIR/config/bruteforce-anomaly.service" ]; then
    sudo cp "$TARGET_DIR/config/bruteforce-anomaly.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Systemd service installed. You can start it with: sudo systemctl start bruteforce-anomaly"
    echo "   To enable it on boot: sudo systemctl enable bruteforce-anomaly"
else
    echo "⚠️ Service file not found. Skipping systemd service installation."
fi

echo "✅ Setup completed!"
echo ""
echo "📚 Usage Examples:"
echo "  Verify system setup:        $TARGET_DIR/config/verify_setup.py"
echo "  Start log collection:       $TARGET_DIR/src/bruteforce_parser.py"
echo "  Run anomaly detection:      $TARGET_DIR/main.py --detect"
echo "  Start monitoring:           $TARGET_DIR/main.py --monitor"
echo "  Test log parsing:           $TARGET_DIR/tests/test_log_parsing.py"
echo "  Or simply use:              bruteforce-anomaly --detect/--monitor"
echo ""
echo "🔍 System Components:"
echo "  bruteforce_parser.py  - Kafka log consumer (real-time)"
echo "  bruteforce_detector.py - ML-based anomaly detection"
echo "  apt_monitor.py        - APT monitoring service"
echo ""
echo "🚀 System is ready to use!"
echo ""
echo "💡 Quick Start:"
echo "  1. Verify setup: python3 $TARGET_DIR/config/verify_setup.py"
echo "  2. Start services: $TARGET_DIR/config/trustlab_service.sh"
echo "  3. Manual detection: $TARGET_DIR/main.py --detect"
echo "  4. Start monitoring: $TARGET_DIR/main.py --monitor"
echo "  5. For testing: python3 -m tests.test_log_parsing && python3 -m tests.create_suspicious_logs && python3 -m src.bruteforce_detector"
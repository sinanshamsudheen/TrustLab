#!/bin/bash
"""
Setup script for SSH Brute Force Detection & APT Correlation System
"""

# Define project name and paths
PROJECT_NAME="BruteforceAnomaly"
SOURCE_DIR="$(dirname "$0")/.."
TARGET_DIR="$SOURCE_DIR"  # Use the current directory instead of /opt/

echo "🔧 Setting up SSH Brute Force Detection & APT Correlation System..."

# We're already in the project directory, so no need to create or copy files
echo "� Using current project directory: $TARGET_DIR"

# Move to project root
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
mkdir -p "$TARGET_DIR/logs"
mkdir -p "$TARGET_DIR/logs/apt"

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

# Create executable wrapper script for easy access (optional but convenient)
echo "🔗 Creating wrapper script for easy CLI access..."
cat > /tmp/bruteforce-anomaly << EOF
#!/bin/bash
python3 "$TARGET_DIR/main.py" "\$@"
EOF
sudo mv /tmp/bruteforce-anomaly /usr/local/bin/bruteforce-anomaly
sudo chmod +x /usr/local/bin/bruteforce-anomaly

# Install systemd service
echo "🔧 Installing systemd service..."
if [ -f "$TARGET_DIR/config/bruteforce-anomaly.service" ]; then
    # Create a new service file with the correct paths
    cat > /tmp/bruteforce-anomaly.service << EOF
[Unit]
Description=TrustLab SSH Brute Force Detection & APT Correlation System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$TARGET_DIR
ExecStart=/usr/bin/python3 $TARGET_DIR/main.py --monitor
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    sudo cp /tmp/bruteforce-anomaly.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Systemd service installed."
    
    # Create log directories for the service
    echo "📁 Creating log directories for the service..."
    mkdir -p "$TARGET_DIR/logs"
    
    # Setting correct permissions for the service
    echo "🔑 Setting correct permissions..."
    sudo chown -R $(whoami):$(whoami) "$TARGET_DIR"
    
    echo "✅ System is ready to be started with: sudo systemctl start bruteforce-anomaly"
    echo "   Enable at boot with: sudo systemctl enable bruteforce-anomaly"
else
    echo "⚠️ Service file not found. Skipping systemd service installation."
fi

echo "✅ Setup completed!"
echo ""
echo "📚 Usage Examples:"
echo "  Verify system setup:        python3 $TARGET_DIR/config/verify_setup.py"
echo "  Run anomaly detection:      python3 $TARGET_DIR/main.py --detect"
echo "  Start monitoring:           python3 $TARGET_DIR/main.py --monitor"
echo "  Test log parsing:           python3 $TARGET_DIR/tests/test_log_parsing.py"
echo ""
echo "🔍 System Components:"
echo "  bruteforce_parser.py  - Kafka log consumer (real-time)"
echo "  bruteforce_detector.py - ML-based anomaly detection"
echo "  apt_monitor.py        - APT monitoring service"
echo ""
echo "🚀 System is ready to use!"
echo ""
echo "💡 Quick Start with Systemd Service (RECOMMENDED):"
echo "  1. Verify setup: python3 $TARGET_DIR/config/verify_setup.py"
echo "  2. Start the service: sudo systemctl start bruteforce-anomaly"
echo "  3. Enable service at boot: sudo systemctl enable bruteforce-anomaly"
echo "  4. Check service status: sudo systemctl status bruteforce-anomaly"
echo ""
echo "📋 Service Management Commands:"
echo "  Start:    sudo systemctl start bruteforce-anomaly"
echo "  Stop:     sudo systemctl stop bruteforce-anomaly"
echo "  Restart:  sudo systemctl restart bruteforce-anomaly"
echo "  Status:   sudo systemctl status bruteforce-anomaly"
echo "  Enable:   sudo systemctl enable bruteforce-anomaly"
echo "  Disable:  sudo systemctl disable bruteforce-anomaly"
echo "  View logs: sudo journalctl -u bruteforce-anomaly"
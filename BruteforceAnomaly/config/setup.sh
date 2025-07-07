#!/bin/bash
# Setup script for SSH Brute Force Detection & APT Correlation System

# Define project name and paths
PROJECT_NAME="BruteforceAnomaly"

# Using relative paths assuming script is run from project root
# or from config directory with proper navigation

echo "🔧 Setting up SSH Brute Force Detection & APT Correlation System..."

# Check if we're in the project root or config directory and adjust if needed
if [ -d "config" ]; then
    # We're already in project root
    echo "📍 Working from project root: $(pwd)"
else
    # We might be in the config directory
    if [ "$(basename $(pwd))" = "config" ]; then
        echo "📂 Moving to project root directory..."
        cd ..
        echo "📍 Working from project root: $(pwd)"
    else
        echo "❌ Please run this script from the BruteforceAnomaly project root or config directory."
        exit 1
    fi
}

# Make Python scripts executable
echo "🔑 Setting executable permissions..."
find src -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || echo "⚠️ No Python files found in src directory"
find tests -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || echo "⚠️ No Python files found in tests directory"
find config -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || echo "⚠️ No Python files found in config directory"
find config -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || echo "⚠️ No shell scripts found in config directory"
chmod +x main.py 2>/dev/null || echo "⚠️ main.py not found or not accessible"
chmod +x start.sh stop.sh 2>/dev/null || echo "⚠️ start.sh/stop.sh not found or not accessible"

# Create necessary directories
echo "📁 Creating log directories..."
mkdir -p logs
mkdir -p logs/apt

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
if [ ! -f "artifacts/bruteforce_model.pkl" ]; then
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
ABSOLUTE_PATH="$(cd "$(pwd)"; pwd)"
cat > /tmp/bruteforce-anomaly << EOF
#!/bin/bash
python3 "$ABSOLUTE_PATH/main.py" "\$@"
EOF
sudo mv /tmp/bruteforce-anomaly /usr/local/bin/bruteforce-anomaly
sudo chmod +x /usr/local/bin/bruteforce-anomaly

# Install systemd service
echo "🔧 Installing systemd service..."
if [ -f "config/bruteforce-anomaly.service" ]; then
    # Get absolute path for systemd (required by systemd)
    ABSOLUTE_PATH="$(cd "$(pwd)"; pwd)"
    echo "📂 Using absolute path for systemd service: $ABSOLUTE_PATH"
    
    # Create a new service file with absolute paths (required by systemd)
    cat > /tmp/bruteforce-anomaly.service << EOF
[Unit]
Description=TrustLab SSH Brute Force Detection & APT Correlation System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$ABSOLUTE_PATH
ExecStart=/usr/bin/python3 $ABSOLUTE_PATH/main.py --monitor
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    sudo cp /tmp/bruteforce-anomaly.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Systemd service installed with absolute paths (required by systemd)."
    
    # Create log directories for the service
    echo "📁 Creating log directories for the service..."
    mkdir -p logs
    
    # Setting correct permissions for the service
    echo "🔑 Setting correct permissions..."
    sudo chown -R $(whoami):$(whoami) "$(pwd)"
    
    echo "✅ System is ready to be started with: sudo systemctl start bruteforce-anomaly"
    echo "   Enable at boot with: sudo systemctl enable bruteforce-anomaly"
    
    # Ask user if they want to start the service now
    read -p "🚀 Do you want to start the service now? (y/n): " START_SERVICE
    if [[ "$START_SERVICE" =~ ^[Yy]$ ]]; then
        echo "📡 Starting bruteforce-anomaly service..."
        sudo systemctl start bruteforce-anomaly
        echo "📊 Checking service status..."
        sudo systemctl status bruteforce-anomaly --no-pager
    fi
    
    # Ask user if they want to enable the service at boot
    read -p "🔄 Do you want to enable the service to start on boot? (y/n): " ENABLE_SERVICE
    if [[ "$ENABLE_SERVICE" =~ ^[Yy]$ ]]; then
        echo "🔧 Enabling bruteforce-anomaly service to start on boot..."
        sudo systemctl enable bruteforce-anomaly
        echo "✅ Service enabled successfully!"
    fi
    
    echo ""
    echo "ℹ️  Note: If the systemd service fails to start, verify the path in:"
    echo "   /etc/systemd/system/bruteforce-anomaly.service"
    echo "   Systemd requires absolute paths in WorkingDirectory and ExecStart."
else
    echo "⚠️ Service file not found. Skipping systemd service installation."
fi

echo "✅ Setup completed!"
echo ""
echo "📚 Usage Examples:"
echo "  Verify system setup:        python3 config/verify_setup.py"
echo "  Start the system:           ./start.sh"
echo "  Stop the system:            ./stop.sh" 
echo "  Run anomaly detection:      python3 main.py --detect"
echo "  Start monitoring:           python3 main.py --monitor"
echo "  Test log parsing:           python3 tests/test_log_parsing.py"
echo ""
echo "🔍 System Components:"
echo "  bruteforce_parser.py  - Kafka log consumer (real-time)"
echo "  bruteforce_detector.py - ML-based anomaly detection"
echo "  apt_monitor.py        - APT monitoring service"
echo ""
echo "🚀 System is ready to use!"
echo ""
echo "💡 Quick Start with Systemd Service (RECOMMENDED):"
echo "  1. Verify setup: python3 config/verify_setup.py"
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
echo ""
echo "🚀 Starting the Service:"
echo "  To start the service immediately:"
echo "    sudo systemctl start bruteforce-anomaly"
echo ""
echo "  To enable automatic start on system boot:"
echo "    sudo systemctl enable bruteforce-anomaly"
echo ""
echo "  To check if the service is running correctly:"
echo "    sudo systemctl status bruteforce-anomaly"
echo ""
echo "  If you encounter any issues with the service, check the logs with:"
echo "    sudo journalctl -u bruteforce-anomaly -f"
echo ""
echo "📝 Note: If the service fails to start, make sure all dependencies are installed"
echo "   and that the model file exists at artifacts/bruteforce_model.pkl"
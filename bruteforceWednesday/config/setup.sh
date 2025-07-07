#!/bin/bash
"""
Setup script for SSH Brute Force Detection & APT Correlation System
"""

echo "🔧 echo "🚀 System is ready to use!"
echo ""
echo "💡 Quick Start:"
echo "  1. Verify setup: python3 -m config.verify_setup"
echo "  2. Start services: ./config/trustlab_service.sh"
echo "  3. Manual detection: python3 main.py --detect"
echo "  4. Start monitoring: python3 main.py --monitor"
echo "  5. For testing: python3 -m tests.test_log_parsing && python3 -m tests.create_suspicious_logs && python3 -m src.bruteforce_detector"g up SSH Brute Force Detection & APT Correlation System..."

# Move to project root
cd "$(dirname "$0")/.."

# Make Python scripts executable
chmod +x src/*.py
chmod +x tests/*.py
chmod +x config/*.py
chmod +x config/*.sh
chmod +x main.py

# Create necessary directories
echo "📁 Creating log directories..."
mkdir -p /home/primum/logs
mkdir -p /var/log/apt

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

    python3 -c "import joblib" 2>/dev/null || {
        echo "Installing joblib..."
        pip3 install joblib
    }

    python3 -c "import sklearn" 2>/dev/null || {
        echo "Installing scikit-learn..."
        pip3 install scikit-learn
    }

    python3 -c "import dateutil" 2>/dev/null || {
        echo "Installing python-dateutil..."
        pip3 install python-dateutil
    }

    python3 -c "import kafka" 2>/dev/null || {
        echo "Installing kafka-python..."
        pip3 install kafka-python
    }
fi

# Check if the ML model exists
if [ ! -f "bruteforce_model.pkl" ]; then
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

echo "✅ Setup completed!"
echo ""
echo "📚 Usage Examples:"
echo "  Verify system setup:        python3 verify_setup.py"
echo "  Start log collection:       python3 bruteforce_parser.py"
echo "  Run anomaly detection:      python3 tester2.py"
echo "  Test log parsing:           python3 test_log_parsing.py"
echo "  Test with custom data:      python3 test_log_parsing.py && python3 tester2.py"
echo ""
echo "🔍 System Components:"
echo "  bruteforce_parser.py  - Kafka log consumer (real-time)"
echo "  tester2.py           - ML-based anomaly detection"
echo "  apt_analyzer.py      - APT package monitoring"
echo "  test_log_parsing.py  - Test data generator"
echo ""
echo "📋 Configuration:"
echo "  Kafka Broker: 10.130.171.246:9092"
echo "  Kafka Topics: web_auth, webapt"
echo "  Log Output: /home/primum/logs/kafka_sixty.log"
echo "  APT Monitor: /var/log/apt/history.log"
echo ""
echo "🚀 System is ready to use!"
echo ""
echo "� Quick Start:"
echo "  1. Start log collection: python3 bruteforce_parser.py"
echo "  2. In another terminal, run: python3 tester2.py" 
echo "  3. For testing without Kafka: python3 test_log_parsing.py && python3 tester2.py"

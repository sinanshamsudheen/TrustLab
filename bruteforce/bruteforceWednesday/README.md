# SSH Brute Force Detection & APT Correlation System

A security monitoring system that detects SSH brute force attacks and correlates them with suspicious APT package installations.

## 📁 Project Structure

```
├── artifacts/             # Machine learning models and training data
│   ├── bruteforce_model.pkl
│   ├── bruteforce_training.ipynb
│   └── noisy_isolation_features_dataset.csv
├── config/                # Configuration and service files
│   ├── config.yaml        # Centralized configuration file
│   ├── setup.sh
│   ├── start_apt_monitor.sh
│   ├── stop_trustlab_service.sh
│   ├── trustlab_service.sh
│   ├── userlist.json
│   └── verify_setup.py
├── logs/                  # Log files
│   ├── apt_monitor.log
│   ├── apt_history_test.log
│   ├── kafka_logs_output.log
│   ├── kafka_sixty.log
│   └── kafka_suspicious.log
├── src/                   # Core source code
│   ├── __init__.py
│   ├── apt_analyzer.py
│   ├── apt_monitor.py
│   ├── bruteforce_detector.py
│   ├── bruteforce_parser.py
│   └── config_loader.py   # Configuration system
├── tests/                 # Testing utilities
│   ├── __init__.py
│   ├── create_apt_test.py
│   ├── create_suspicious_logs.py
│   ├── inspect_model.py
│   ├── test_apt_monitor.py
│   ├── test_detection.py
│   ├── test_log_parsing.py
│   └── test_structure.py
├── main.py                # Main entry point
└── requirements.txt       # Python dependencies
```

## 🔧 Quick Installation

```bash
# Clone the repository
cd trustlab-security

# Run the setup script (installs dependencies and creates required directories)
./config/setup.sh

# Alternative manual installation:
# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x config/*.py config/*.sh

# Verify installation
python3 config/verify_setup.py
```

## 🚀 Running the System

### Option 1: Using the Service Script

```bash
# Start both services with the full trustlab service script
./config/trustlab_service.sh

# To stop the services
./config/stop_trustlab_service.sh
```

### Option 2: Using the Main Entry Point

```bash
# Run SSH brute force detection only
python3 main.py --detect

# Run APT monitoring service only
python3 main.py --monitor
```

### Option 3: Individual Components

```bash
# Start the APT monitoring service (runs in background)
./config/start_apt_monitor.sh

# Run SSH brute force detection (runs once)
python3 -m src.bruteforce_detector
```

## 📋 System Components

### Core Components
- **src/bruteforce_parser.py**: Processes Kafka streams of SSH logs
- **src/bruteforce_detector.py**: ML-based anomaly detection for SSH brute force attacks
- **src/apt_analyzer.py**: Analyzes APT history for malicious package installations
- **src/apt_monitor.py**: Continuous monitoring of APT activities
- **src/config_loader.py**: Centralized configuration management system
- **config/config.yaml**: Configuration file with all system settings
- **config/userlist.json**: Correlation database linking suspicious IPs to usernames

### Service Scripts
- **config/trustlab_service.sh**: Starts all monitoring services
- **config/stop_trustlab_service.sh**: Stops all monitoring services
- **config/start_apt_monitor.sh**: Starts only the APT monitoring service

### Support Files
- **artifacts/bruteforce_model.pkl**: Pre-trained ML model (IsolationForest)
- **artifacts/bruteforce_training.ipynb**: Jupyter notebook for model training
- **requirements.txt**: Python package dependencies
- **setup.sh**: Setup script for dependencies
- **verify_setup.py**: System verification script

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Logs    │───▶│ bruteforce_parser│───▶│ kafka_sixty.log │
│ (SSH Auth Logs) │    │     .py          │    │ (60s window)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │bruteforce_detect│
                                               │    or.py        │◀────┐
                                               └────────┬────────┘     │
                                                        │              │
                                                        ▼              │
                   ┌─────────────────┐        ┌─────────────────┐     │
                   │   userlist.json │◀───────│  apt_analyzer.py│     │
                   │ (IP-User Map)   │        │                 │     │
                   └─────────────────┘        └────────┬────────┘     │
                            │                          │              │
                            │                          ▼              │
                            │                 ┌─────────────────┐     │
                            └────────────────▶│  apt_monitor.py │─────┘
                                              │ (Continuous     │
                                              │  Monitoring)    │
                                              └─────────────────┘
```

## 🔍 How It Works

1. **SSH Log Collection**:
   - `bruteforce_parser.py` captures SSH logs from Kafka
   - Logs are filtered and stored in a 60-second window file

2. **Anomaly Detection**:
   - `bruteforce_detector.py` analyzes logs using machine learning
   - Extracts features like login attempt patterns
   - Uses IsolationForest to identify anomalous behavior

3. **Username-IP Correlation**:
   - When an anomaly is detected, username and IP are extracted
   - Information is stored in `userlist.json` for continuous monitoring

4. **APT Activity Monitoring**:
   - `apt_analyzer.py` searches for suspicious package installations
   - `apt_monitor.py` continuously monitors APT logs for known suspicious users
   - Alerts are generated when suspicious activities are detected

## 📊 Output Example

```
Predictions (−1 = anomaly, 1 = normal): [-1]
192.168.1.100 → ⚠️ Anomaly
  - Attempts: 30
  - Unique users: 15
  - Invalid user attempts detected
  - Users attempted: admin, root, user, test
  - Selected username for monitoring: root

[!] Anomaly detected from IP: 192.168.1.100
[!] Associated username: root
[*] Searching for suspicious APT activity (±24h window)...
[+] Added/Updated root with IP 192.168.1.100 to monitoring list
[!!!] Suspicious activity found within 24h window:
    Time: 2025-06-25 14:30:15
    Action: Install: nmap:amd64 (7.80+dfsg1-2build1)
    User: root
    Command: apt install nmap
```

## ⚙️ Configuration

All configuration is centralized in a single YAML file at `config/config.yaml`:

```yaml
# Kafka Configuration
kafka:
  broker: "10.130.171.246:9092"
  topics:
    - "web_auth" 
    - "webapt"
  consumer_group: "auth-consumer-group"

# File Paths
paths:
  logs:
    base_dir: "${PROJECT_ROOT}/logs"
    raw_log: "${PROJECT_ROOT}/logs/kafka_logs_output.log"
    recent_log: "${PROJECT_ROOT}/logs/kafka_sixty.log"
    suspicious_log: "${PROJECT_ROOT}/logs/kafka_suspicious.log"
    apt_log: "${PROJECT_ROOT}/logs/apt_history_test.log"
    monitor_log: "${PROJECT_ROOT}/logs/apt_monitor.log"

  user_data:
    userlist: "${PROJECT_ROOT}/config/userlist.json"
  
  models:
    bruteforce_model: "${PROJECT_ROOT}/artifacts/bruteforce_model.pkl"

# Detection Configuration
detection:
  time_window_seconds: 60
  suspicious_keywords:
    - 'nmap'
    - 'masscan'
    - 'hydra'
    - 'john'
    - 'hashcat'
    - 'metasploit'
    - 'sqlmap'
    - 'nikto'
    - 'dirb'
    - 'gobuster'
    - 'burpsuite'
    - 'wireshark'
    - 'tcpdump'
    - 'netcat'
    - 'socat'
    - 'proxychains'
    - 'tor'
    - 'aircrack'
    - 'reaver'
    - 'ettercap'
    - 'beef'
    - 'armitage'
    - 'maltego'
    - 'backdoor'
    - 'rootkit'
    - 'keylogger'
```

### Configuration Loader

The system uses a singleton configuration loader class to access configuration values from anywhere in the codebase:

```python
from src.config_loader import Config

# Get configuration instance
config = Config()

# Access configuration values using dot notation
kafka_broker = config.get('kafka.broker')
log_file = config.get('paths.logs.recent_log')
time_window = config.get('detection.time_window_seconds')

# Configuration automatically resolves project paths
# ${PROJECT_ROOT} is replaced with the actual project directory
```

This centralized approach makes the system easy to configure without modifying code files.

## 🚨 Testing

The system includes utilities for testing:

```bash
# Generate test logs
python3 -m tests.test_log_parsing

# Create suspicious SSH logs
python3 -m tests.create_suspicious_logs

# Create APT test logs
python3 -m tests.create_apt_test

# Run analysis on test data
python3 -m src.bruteforce_detector
```

## 📝 Requirements

- Python 3.8+
- Required Python packages (see requirements.txt for exact versions):
  - joblib==1.4.2
  - kafka-python==2.2.10
  - numpy==1.24.3
  - pandas==1.5.3
  - python-dateutil==2.9.0.post0
  - scikit-learn==1.2.2
  - pyyaml>=6.0.0
- Linux system with APT package manager
- Kafka cluster (if using real-time log collection)

## 🤝 Support

For issues and questions:
1. Check log files for errors
2. Verify all dependencies are installed
3. Check file permissions and paths
4. Enable debug mode for detailed logging: `DEBUG = True` in Python files

---

**Version**: 2.0  
**Last Updated**: July 5, 2025

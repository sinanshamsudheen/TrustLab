# SSH Brute Force Detection & APT Correlation System

A comprehensive security monitoring system that uses machine learning to detect SSH brute force attacks and correlates them with suspicious APT (Advanced Package Tool) package installations. This system helps security teams identify potential advanced persistent threats by connecting unusual login patterns with subsequent suspicious software installations.

## 🔐 Project Overview

This project provides:

1. **SSH Brute Force Detection**: Uses machine learning (Isolation Forest) to identify anomalous login patterns in SSH logs
2. **APT Activity Monitoring**: Monitors package installations for potentially malicious software
3. **Threat Correlation**: Links suspicious IPs/users from brute force attempts to subsequent package installations
4. **Real-time Alerts**: Notifies security teams when correlated threats are detected
5. **Testing Framework**: Includes comprehensive test scripts to simulate attacks and validate system components

The system is designed to help security professionals detect post-exploitation activities where an attacker may gain access via brute force and then install tools for lateral movement or persistence.

## 📁 Project Structure

```
├── artifacts/             # Machine learning models and training data
│   ├── bruteforce_model.pkl
│   ├── bruteforce_training.ipynb
│   └── noisy_isolation_features_dataset.csv
├── config/                # Configuration and service files
│   ├── config.yaml        # Centralized configuration file
│   ├── setup.sh
│   ├── bruteforce-anomaly.service  # Systemd service file
│   ├── userlist.json      # User/IP correlation database
│   └── verify_setup.py    # System verification tool
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
git clone https://github.com/sinanshamsudheen/TrustLab.git

# Run the setup script which will configure the project in its current location
cd TrustLab/BruteforceAnomaly
sudo ./config/setup.sh

# The system is now ready to use from the current directory

# Start the service using systemd
sudo systemctl start bruteforce-anomaly

# If there's an error, check paths in the service file
# sudo nano /etc/systemd/system/bruteforce-anomaly.service
# Update WorkingDirectory and ExecStart paths if needed, then:
# sudo systemctl daemon-reload && sudo systemctl restart bruteforce-anomaly

# Enable the service to start at boot
sudo systemctl enable bruteforce-anomaly
```

## 🔍 Verification and Testing

### Initial System Verification

```bash
# Verify that all dependencies are correctly installed
python3 ./config/verify_setup.py
```

This command checks:
- If all required Python packages are installed
- If configuration files are accessible
- If the project structure is correct
- If core modules can be imported

### Testing Bruteforce Detection

```bash
# Step 1: Create test suspicious logs
python3 ./tests/create_suspicious_logs.py

# Step 2: Run detection on the generated logs
python3 ./tests/test_detection.py

# Step 3: Alternative: Run main detection system
python3 ./main.py --detect
```

The first command generates realistic SSH login failure patterns that simulate a brute-force attack. The second command runs the anomaly detection model against these logs and displays detailed results, showing how the system identifies suspicious patterns.

### Testing APT Analysis and Correlation

```bash
# Step 1: Create test suspicious user records
python3 ./tests/create_apt_test.py

# Step 2: Test the APT monitoring functionality
python3 ./tests/test_apt_monitor.py

# Step 3: Run the APT monitor service
python3 ./main.py --monitor
```

These commands:
1. Generate simulated APT (Advanced Package Tool) installation logs for suspicious users
2. Test if the APT monitor can correctly initialize and access the userlist
3. Start the monitoring service that watches for suspicious package installations from flagged users

### Advanced Testing with Log Parsing

```bash
# Test the log parsing functionality
python3 ./tests/test_log_parsing.py

# Inspect the machine learning model
python3 ./tests/inspect_model.py
```

These tools provide insights into how the system processes SSH logs and how the machine learning model works.

## 🚀 Running the System

### Option 1: Using Start and Stop Scripts (Recommended)

```bash
# Start the detection and monitoring services
./start.sh

# Stop the detection and monitoring services
./stop.sh
```

The start.sh script:
1. Sets up a cron job to run the bruteforce detector every minute
2. Asks if you want to start the APT monitoring service
3. Uses systemd if available, or runs the service directly otherwise

The stop.sh script:
1. Removes the cron job for bruteforce detection
2. Asks if you want to stop the APT monitoring service
3. Stops the service gracefully via systemd or direct process termination

This approach ensures that:
1. The APT monitoring service runs continuously 
2. The SSH brute force detection runs at regular intervals via cron
3. Both components operate independently but share information via the userlist.json file

### Option 2: Using Systemd Service Manually

```bash
# Start the APT monitoring service (runs in background even after logout)
sudo systemctl start bruteforce-anomaly

# Check service status
sudo systemctl status bruteforce-anomaly

# Stop the service
sudo systemctl stop bruteforce-anomaly

# Enable service to start automatically at boot
sudo systemctl enable bruteforce-anomaly
```

Note: When using systemd directly, you'll need to set up the cron job for bruteforce detection separately.

### Option 2: Using the Main Entry Point

```bash
# Run SSH brute force detection only
python3 main.py --detect

# Run APT monitoring service only
python3 main.py --monitor
```

### Option 3: Individual Components

```bash
# Start the APT monitoring service manually (runs in background)
python3 main.py --monitor &

# Run SSH brute force detection once
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

### Service Management
- **config/bruteforce-anomaly.service**: Systemd service configuration file
- **systemd**: Manages the service, handles auto-restart and boot persistence
- **cron job**: Automatically runs the bruteforce detector every 60 seconds (set up by setup.sh)
- **main.py --monitor**: Sets up and runs APT monitoring service
- **main.py --detect**: Runs one-time bruteforce detection scan

### Support Files
- **artifacts/bruteforce_model.pkl**: Pre-trained ML model (IsolationForest)
- **artifacts/bruteforce_training.ipynb**: Jupyter notebook for model training
- **requirements.txt**: Python package dependencies
- **config/setup.sh**: Installation and systemd service setup script
- **config/verify_setup.py**: System verification script

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Logs    │───▶│ bruteforce_parser│───▶│ kafka_sixty.log │
│ (SSH Auth Logs) │    │     .py          │    │ (60s window)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                               ┌─────────────────────────────────────┐
                               │       Systemd Service               │
                               │    (bruteforce-anomaly.service)     │
                               └─────────────┬───────────────────────┘
                                             │
                                             │ Controls
                                             ▼
                                ┌────────────────────────────┐
                                │         main.py            │
                                │  --monitor / --detect      │
                                └───────┬────────────────────┘
                                        │
                      ┌─────────────────┴─────────────────┐
                      │                                   │
                      ▼                                   ▼
┌──────────────────────────┐                  ┌─────────────────────────┐
│  bruteforce_detector.py  │◀────┐            │     apt_monitor.py      │
│  (Runs via cron job)     │     │            │ (Continuous monitoring) │
└───────────┬──────────────┘     │            └────────────┬────────────┘
            │                    │                         │
            ▼                    │                         │
┌─────────────────────┐          │            ┌────────────┴────────────┐
│    apt_analyzer.py  │──────────┘            │      userlist.json      │
│                     │                       │    (IP-User Map)        │
└─────────────────────┘                       └─────────────────────────┘
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

## 🚨 Testing and Troubleshooting

The system includes comprehensive testing utilities designed to validate each component of the system. Follow these testing workflows to understand how the system works or to debug issues.

### Testing Workflow for SSH Bruteforce Detection

1. **Generate Test Data:**
   ```bash
   # Create simulated SSH brute force logs
   python3 ./tests/create_suspicious_logs.py
   ```
   This creates log entries simulating SSH bruteforce attempts with various patterns:
   - Multiple failed logins for the same user from a single IP
   - Attempts to log in as different users from the same IP
   - Invalid username attempts
   - Password guessing patterns

2. **Run Detection and Analyze Results:**
   ```bash
   # Test the detection system on generated logs
   python3 ./tests/test_detection.py
   ```
   This will:
   - Load the ML model (IsolationForest)
   - Process the test logs
   - Extract features (login attempts, unique users, failure patterns)
   - Make anomaly predictions
   - Output detection results with confidence scores
   - Identify which IPs are flagged as suspicious

3. **Run Full Detection Pipeline:**
   ```bash
   # Run the complete detection system
   python3 ./main.py --detect
   ```
   This runs the full detection pipeline including:
   - Log parsing
   - Feature extraction
   - Anomaly detection
   - User-IP correlation
   - APT correlation for detected anomalies

### Testing Workflow for APT Correlation System

1. **Create Test APT Logs:**
   ```bash
   # Generate simulated APT history logs with suspicious packages
   python3 ./tests/create_apt_test.py
   ```
   This creates:
   - Simulated APT history with timestamps
   - Installation entries for potentially suspicious packages
   - Links between users and package installations

2. **Test the APT Monitoring System:**
   ```bash
   # Validate the APT monitoring functionality
   python3 ./tests/test_apt_monitor.py
   ```
   This tests:
   - Initialization of the APT monitor
   - Access to the userlist database
   - Correlation between flagged users and package installations
   - Detection of suspicious package installations

3. **Run the APT Monitor Service:**
   ```bash
   # Start the APT monitoring service
   python3 ./main.py --monitor
   ```
   This runs the continuous monitoring service that:
   - Watches the userlist.json file for flagged users
   - Monitors APT history logs
   - Alerts when suspicious users install suspicious packages

### Advanced Testing Options

```bash
# Test log parsing and formatting
python3 ./tests/test_log_parsing.py

# Inspect the machine learning model features and parameters
python3 ./tests/inspect_model.py

# Test the entire project structure and imports
python3 ./tests/test_structure.py
```

### Understanding Test Output

The test scripts output detailed information using these indicators:
- ✅ Success indicators for passed tests
- ❌ Failure indicators with error messages
- ⚠️ Warning indicators for potential issues
- 🔍 Detailed inspection results for model analysis
- 🧪 Test execution indicators

Review these outputs carefully to understand how the system is functioning or to identify issues.

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

### Troubleshooting Systemd Service

If the systemd service fails to start:

```bash
# Check the service status for detailed error messages
sudo systemctl status bruteforce-anomaly.service

# View service logs
sudo journalctl -u bruteforce-anomaly

# If there's an issue with paths in the service file:
sudo nano /etc/systemd/system/bruteforce-anomaly.service
# Ensure these have absolute paths (systemd requirement):
# WorkingDirectory=/home/username/path/to/BruteforceAnomaly
# ExecStart=/usr/bin/python3 /home/username/path/to/BruteforceAnomaly/main.py --monitor
# Then reload and restart:
sudo systemctl daemon-reload
sudo systemctl restart bruteforce-anomaly
```

**Note:** Systemd requires absolute paths in service files. The setup script automatically uses absolute paths, but you may need to adjust them if your installation location changes.

## 🧪 Complete Testing Guide

This section provides a step-by-step guide for testing the entire system using the provided test scripts.

### Step 1: Verify System Setup

```bash
# Check if all dependencies and paths are correctly set up
python3 ./config/verify_setup.py
```

Ensure you see green checkmarks (✅) for all tests. If there are any failures (❌), fix them before proceeding.

### Step 2: Test Project Structure and Core Imports

```bash
# Verify project structure and module imports
python3 ./tests/test_structure.py
```

This validates that all directories exist and all core modules can be imported successfully.

### Step 3: Generate Test Data

```bash
# Create suspicious SSH login logs
python3 ./tests/create_suspicious_logs.py

# Create simulated APT history logs
python3 ./tests/create_apt_test.py
```

These commands create the test data needed for running the detection and monitoring systems. They will generate:
- SSH logs with suspicious login patterns in `logs/kafka_sixty.log`
- APT history logs with package installations in `logs/apt_history_test.log`

### Step 4: Test Individual Components

```bash
# Test log parsing
python3 ./tests/test_log_parsing.py

# Test ML model analysis
python3 ./tests/inspect_model.py

# Test APT monitoring
python3 ./tests/test_apt_monitor.py
```

These tests validate each component individually, helping you understand how they work or identify issues.

### Step 5: Test Full Detection Pipeline

```bash
# Run full detection system on test data
python3 ./main.py --detect
```

This command processes the test logs and detects any suspicious SSH login patterns. It will:
1. Parse the SSH logs
2. Extract features for the ML model
3. Detect anomalies using the IsolationForest model
4. Update the userlist.json with flagged IPs and users
5. Check for suspicious APT activity correlated with flagged users

### Step 6: Test Monitoring System

```bash
# Run the APT monitoring service
python3 ./main.py --monitor
```

This starts the continuous monitoring service that watches for suspicious package installations by users who have been flagged from SSH brute force attempts.

### Interpreting Test Results

- **SSH Brute Force Detection**:
  - The system will output predictions for each IP address (`-1` = anomaly, `1` = normal)
  - For anomalies, it will show details like attempt counts, unique users tried, etc.
  - It will select a username to monitor based on the attack patterns

- **APT Correlation**:
  - For detected anomalies, the system will check APT logs for suspicious activities
  - If found, it will show details of suspicious package installations
  - These correlations help identify potential post-exploitation activities

### Testing Tips

- **Generate Custom Test Data**: Modify the test scripts to create different attack patterns
- **Adjust Detection Parameters**: Experiment with settings in `config.yaml`
- **Debug Issues**: Enable debug logging by setting `DEBUG = True` in the Python files
- **View Detailed Model Info**: Use `tests/inspect_model.py` to understand how the ML model works
- **Test in Isolation**: Test each component separately before testing the full pipeline
- **Simulate Real Attacks**: Create scenarios with increasing levels of sophistication

---

**Version**: 2.0  
**Last Updated**: July 8, 2025

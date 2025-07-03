# Enhanced Brute Force Detection System

A comprehensive security monitoring system that detects SSH brute force attacks and correlates them with suspicious package installations to identify advanced persistent threats (APTs).

## 🎯 Overview

This system provides multi-layered threat detection by:
1. **SSH Anomaly Detection** - Uses machine learning to identify brute force attacks
2. **APT Package Analysis** - Monitors system package installations for malicious tools
3. **Cross-Correlation** - Links SSH attacks with suspicious package activities
4. **Persistent Tracking** - Maintains a database of threats across time windows
5. **Real-time Processing** - Processes logs from Kafka streams in real-time

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Logs    │───▶│ bruteforce_parser│───▶│ kafka_sixty.log │
│ (SSH Auth Logs) │    │     .py          │    │ (60s window)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  APT Log Files  │    │    tester2.py    │◀───│ ML Model (.pkl) │
│ (/var/log/apt/) │───▶│ (Main Analyzer)  │    └─────────────────┘
└─────────────────┘    └──────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SQLite DB     │◀───│   ip_tracker.py  │    │ apt_analyzer.py │
│ (Threat Intel)  │    │ (Persistence)    │◀───│ (Package Mon.)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
bruteforce/
├── bruteforce_parser.py     # Kafka consumer & log processor
├── tester2.py              # Main analysis engine
├── apt_analyzer.py         # APT package monitoring
├── ip_tracker.py           # Persistent threat tracking
├── db_manager.py           # Database management utility
├── test_enhanced_detection.py # Test suite
├── setup.sh               # Setup script
├── bruteforce_model.pkl   # Pre-trained ML model
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or download the project files
cd bruteforce/

# Run setup script
chmod +x setup.sh
./setup.sh

# Ensure all dependencies are installed
pip3 install pandas joblib python-dateutil
```

### 2. Configuration

Edit the configuration in `tester2.py`:

```python
# CONFIG
LOG_FILE = "/home/primum/logs/kafka_sixty.log"
KNOWN_USERS = { "192.168.10.15": "primum" }  # Add your trusted IPs
```

Edit the Kafka configuration in `bruteforce_parser.py`:

```python
# CONFIG
BROKER = '10.130.171.246:9092'  # Your Kafka broker
TOPICS = ['web_auth', 'webapt']  # Your Kafka topics
```

### 3. Start the System

```bash
# Terminal 1: Start Kafka log consumer
python3 bruteforce_parser.py

# Terminal 2: Run detection (can be automated with cron)
python3 tester2.py
```

### 4. Test the System

```bash
# Run comprehensive test
python3 test_enhanced_detection.py
```

## 🔧 How It Works

### Phase 1: Log Collection
- `bruteforce_parser.py` consumes SSH authentication logs from Kafka
- Processes complex log formats with multiple timestamps
- Maintains a sliding 60-second window of recent logs
- Stores raw logs and cleaned logs separately

### Phase 2: SSH Anomaly Detection
- `tester2.py` analyzes logs using machine learning (Isolation Forest)
- Extracts features: attempt count, unique users, invalid users, etc.
- Detects patterns indicating brute force attacks
- Records anomalies in persistent SQLite database

### Phase 3: APT Package Analysis
- `apt_analyzer.py` monitors `/var/log/apt/` and `/var/log/dpkg.log`
- Searches for installation of suspicious packages (penetration testing tools, etc.)
- Correlates package installations with SSH anomalies
- Extends time window to catch delayed malicious activities

### Phase 4: Threat Correlation & Escalation
- Cross-correlates SSH attacks with package installations
- Escalates threat levels:
  - **Level 1**: SSH anomaly only
  - **Level 3**: SSH anomaly + suspicious package installations
- Generates comprehensive threat reports
- Maintains persistent tracking across detection cycles

## 📊 Usage Examples

### Basic Detection
```bash
# Run detection on current logs
python3 tester2.py
```

### Database Management
```bash
# View database statistics
python3 db_manager.py --stats

# Show recent anomalies (last 24 hours)
python3 db_manager.py --recent 24

# Show critical threats only
python3 db_manager.py --critical 24

# Export threat data to JSON
python3 db_manager.py --export 24 --output threats.json

# Cleanup old records (older than 7 days)
python3 db_manager.py --cleanup 7
```

### Monitoring & Automation
```bash
# Add to crontab for automated detection every minute
*/1 * * * * cd /path/to/bruteforce && python3 tester2.py >> /var/log/bruteforce_detection.log 2>&1

# Monitor critical threats every 5 minutes
*/5 * * * * cd /path/to/bruteforce && python3 db_manager.py --critical 1 >> /var/log/critical_threats.log 2>&1
```

## 🔍 Understanding Output

### Normal Detection Output
```
Predictions (−1 = anomaly, 1 = normal): [1, 1, -1]
192.168.1.100 → ✅ Normal
192.168.1.101 → ✅ Normal
10.129.6.192 → ⚠️ Anomaly
  - Attempts: 5
  - Unique users: 3
  - Invalid user attempts detected
  - Users attempted: admin, root, test
```

### Critical Threat Detection
```
🚨 CRITICAL: Suspicious package activities found for 10.129.6.192!

🔍 SUSPICIOUS PACKAGE ACTIVITIES DETECTED:
==================================================
⏰ Time: 2025-06-24 14:30:15
🎯 Action: Install
📦 Packages: nmap masscan hydra
📋 Source: apt-history
------------------------------
```

### Database Statistics
```
📈 DATABASE STATISTICS:
Total tracked IPs: 15
Recent activity (24h): 3
Threat levels: {1: 10, 3: 5}
```

## ⚙️ Configuration Options

### APT Analyzer Configuration
```python
# Customize suspicious package patterns
suspicious_patterns = [
    r'nmap', r'masscan', r'hydra', r'john', r'hashcat',
    r'metasploit', r'sqlmap', r'nikto', r'custom_pattern'
]

# Customize log paths
apt_log_paths = [
    '/var/log/apt/history.log',
    '/var/log/apt/history.log.1',
    '/custom/log/path.log'
]
```

### Time Window Settings
```python
# In tester2.py
recent_anomalous_ips = ip_tracker.get_recent_anomalous_ips(hours=6)  # SSH tracking window
apt_activities = apt_analyzer.analyze_ip_activity(ip, time_window_hours=8)  # APT analysis window

# In ip_tracker.py
ip_tracker.cleanup_old_records(days=7)  # Database retention
```

## 🚨 Alert Integration

### Email Alerts (Example)
```python
# Add to tester2.py after critical threat detection
if critical_threats:
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(f"Critical threats detected: {', '.join(critical_threats)}")
    msg['Subject'] = 'Security Alert: Critical Threats Detected'
    msg['From'] = 'security@company.com'
    msg['To'] = 'admin@company.com'
    
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
```

### Slack Integration (Example)
```python
# Add webhook notification
import requests
import json

webhook_url = "https://hooks.slack.com/your/webhook/url"
message = {
    "text": f"🚨 Critical Security Threat Detected",
    "attachments": [{
        "color": "danger",
        "fields": [{
            "title": "Affected IPs",
            "value": ", ".join(critical_threats),
            "short": True
        }]
    }]
}

requests.post(webhook_url, data=json.dumps(message))
```

## 🔧 Troubleshooting

### Common Issues

**1. "No module named 'apt_analyzer'"**
```bash
# Ensure all files are in the same directory
ls -la *.py
# Run from the correct directory
cd /path/to/bruteforce/
```

**2. "Log file not found"**
```bash
# Check log file paths
ls -la /home/primum/logs/
# Ensure bruteforce_parser.py is running and creating logs
```

**3. "Database locked"**
```bash
# Check if multiple processes are accessing the database
ps aux | grep python3
# Ensure proper file permissions
chmod 666 /home/primum/logs/ip_tracking.db
```

**4. "No suspicious activities found"**
```bash
# Check APT log paths exist
ls -la /var/log/apt/
# Verify suspicious package patterns match your environment
```

**5. "Kafka logs not being processed properly"**
```bash
# Test log parsing with your exact format
python3 test_log_parsing.py

# Enable debug mode in bruteforce_parser.py
DEBUG = True

# Check if logs are being written
tail -f /home/primum/logs/kafka_sixty.log
```

### Debug Mode
```python
# Enable debug mode in any script
DEBUG = True

# Or set debug for specific components
apt_analyzer = APTAnalyzer(debug=True)
```

## 📈 Performance Considerations

- **Memory Usage**: SQLite database with indexing for fast queries
- **CPU Usage**: ML model prediction is lightweight (Isolation Forest)
- **Disk Usage**: Automatic cleanup of old records (configurable retention)
- **Network**: Minimal impact, processes local log files

## 🔒 Security Considerations

- **File Permissions**: Ensure log files and database have appropriate permissions
- **Log Rotation**: Implement log rotation for long-term deployments
- **Access Control**: Restrict access to threat intelligence database
- **Data Retention**: Configure appropriate retention policies for compliance

## 📋 Dependencies

- Python 3.6+
- pandas
- joblib
- python-dateutil
- sqlite3 (built-in)
- Kafka Python client (for bruteforce_parser.py)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Enable debug mode for detailed logging
3. Review log files for error messages
4. Submit issues with complete error traces

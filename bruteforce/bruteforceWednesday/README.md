# SSH Brute Force Detection & APT Correlation System

A comprehensive security monitoring system that detects SSH brute force attacks and correlates them with suspicious package installations to identify potential system compromises.

## 🎯 Overview

This system provides intelligent threat detection by:
1. **SSH Anomaly Detection** - Uses machine learning to identify brute force attacks in real-time
2. **APT Package Analysis** - Monitors system package installations for malicious tools with timestamp correlation
3. **Simplified Architecture** - Streamlined design for efficiency and reliability
4. **Real-time Processing** - Processes logs from Kafka streams with 60-second windows

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Logs    │───▶│ bruteforce_parser│───▶│ kafka_sixty.log │
│ (SSH Auth Logs) │    │     .py          │    │ (60s window)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  APT Log Files  │    │    tester2.py    │◀───│ ML Model (.pkl) │
│ (/var/log/apt/) │───▶│ (Main Analyzer)  │    │ IsolationForest │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ apt_analyzer.py  │
                       │ (Package Mon.)   │
                       └──────────────────┘
```

## 📁 File Structure

```
bruteforce/
├── bruteforce_parser.py     # Kafka consumer & log processor
├── tester2.py              # Main ML-based analysis engine
├── apt_analyzer.py         # Timestamp-aware APT package monitoring
├── test_log_parsing.py     # Log parsing test utility
├── verify_setup.py         # System verification script
├── setup.sh               # Setup script for dependencies
├── requirements.txt       # Python package dependencies
├── bruteforce_model.pkl   # Pre-trained IsolationForest model
└── README.md              # This documentation
```

## 🔄 Data Flow

1. **Log Collection**: `bruteforce_parser.py` consumes SSH logs from Kafka topics
2. **Preprocessing**: Filters and processes logs into 60-second windows
3. **Feature Extraction**: `tester2.py` extracts behavioral features from SSH logs
4. **Anomaly Detection**: Machine learning model identifies suspicious patterns
5. **APT Analysis**: When anomaly detected, `apt_analyzer.py` searches for malicious packages
6. **Reporting**: System outputs detailed threat analysis and recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Kafka cluster running on `10.130.171.246:9092`
- SSH logs being published to Kafka topics: `web_auth`, `webapt`
- Linux system with APT package manager (for full functionality)

### Setup
```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# OR install individually
pip install pandas scikit-learn kafka-python joblib python-dateutil

# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh

# Verify installation
python3 verify_setup.py
```

### Running the System

1. **Verify Setup** (Recommended first step):
```bash
python3 verify_setup.py
```
This will check all dependencies, files, and basic functionality.

2. **Start Log Collection**:
```bash
python3 bruteforce_parser.py
```
This will:
- Connect to Kafka broker
- Listen to `web_auth` and `webapt` topics
- Process and save logs to `/home/primum/logs/kafka_sixty.log`

3. **Run Detection Analysis**:
```bash
python3 tester2.py
```
This will:
- Load the trained ML model
- Analyze recent logs for brute force patterns
- Trigger APT analysis for suspicious IPs
- Display detailed threat reports

### Testing

Create test logs and run analysis:
```bash
# Generate test logs
python3 test_log_parsing.py

# Run analysis on test data
python3 tester2.py
```

## 🧠 Machine Learning Model

### Model Details
- **Algorithm**: Isolation Forest (Unsupervised Anomaly Detection)
- **Features**: 
  - `attempts_in_60s`: Number of authentication attempts
  - `unique_users_in_60s`: Number of unique usernames tried
  - `invalid_user`: Boolean flag for invalid user attempts
  - `success_after_fail`: Boolean flag for successful login after failures
  - `true_user`: Boolean flag for expected user from known IP

### Model Performance
- **Anomaly Threshold**: -1 (anomaly), 1 (normal)
- **Training Data**: Historical SSH authentication patterns
- **False Positive Rate**: Optimized for security environments

## 🔍 APT Package Analysis

### Monitored Suspicious Keywords
The system monitors for installations of these potentially malicious packages:
- **Network Scanners**: nmap, masscan, nikto
- **Password Crackers**: hydra, john, hashcat
- **Exploitation Frameworks**: metasploit, sqlmap
- **Web Security Tools**: burpsuite, gobuster, dirb
- **Network Tools**: wireshark, tcpdump, netcat
- **Proxy/Anonymization**: proxychains, tor
- **Wireless Security**: aircrack, reaver
- **Social Engineering**: beef, maltego
- **Malware**: backdoor, rootkit, keylogger

### Timestamp Correlation
- **Default Window**: ±24 hours from anomaly detection
- **Configurable**: Time window can be adjusted per analysis
- **Smart Filtering**: Ignores old installations unrelated to current threats

## 📊 Output Examples

### Normal Traffic
```
Predictions (−1 = anomaly, 1 = normal): [1]
192.168.1.10 → ✅ Normal

📊 ANALYSIS SUMMARY:
SSH anomalies detected: 0
✅ No anomalies detected in this analysis.
```

### Detected Anomaly
```
Predictions (−1 = anomaly, 1 = normal): [-1]
192.168.1.100 → ⚠️ Anomaly
  - Attempts: 30
  - Unique users: 15
  - Invalid user attempts detected
  - Users attempted: admin, root, user, test, ...

[!] Anomaly detected from IP: 192.168.1.100
[*] Searching for suspicious APT activity (±24h window)...
[!!!] Suspicious activity found within 24h window:
    Time: 2025-06-25 14:30:15
    Action: Install: nmap:amd64 (7.80+dfsg1-2build1)

📊 ANALYSIS SUMMARY:
SSH anomalies detected: 1
🔥 Anomalous IPs: 192.168.1.100
```

## ⚙️ Configuration

### Kafka Settings
Edit `bruteforce_parser.py`:
```python
BROKER = '10.130.171.246:9092'
TOPICS = ['web_auth', 'webapt']
```

### Log Paths
Edit file paths as needed:
```python
RAW_LOG_FILE = '/home/primum/logs/kafka_logs_output.log'
RECENT_LOG_FILE = '/home/primum/logs/kafka_sixty.log'
APT_LOG_PATH = '/var/log/apt/history.log'
```

### APT Analysis Time Window
Modify `apt_analyzer.py`:
```python
search_apt_history(suspicious_ip, time_window_hours=24)  # Default: 24 hours
```

## 🔧 Advanced Usage

### Custom Suspicious Keywords
Add custom keywords to `apt_analyzer.py`:
```python
suspicious_keywords = [
    'nmap', 'hydra', 'metasploit',  # Default keywords
    'custom-tool', 'proprietary-scanner'  # Your additions
]
```

### Adjusting ML Sensitivity
The model sensitivity can be adjusted by modifying the anomaly threshold or retraining with different parameters.

## � Troubleshooting

### Common Issues

**1. Kafka Connection Failed**
   - Verify broker address and port
   - Check network connectivity
   - Ensure Kafka topics exist

**2. APT Log Not Found**
   - System might not be Debian/Ubuntu based
   - Check if `/var/log/apt/history.log` exists
   - Verify read permissions

**3. Model Loading Error**
   - Ensure `bruteforce_model.pkl` exists
   - Check Python version compatibility
   - Reinstall scikit-learn if needed

**4. No Logs in kafka_sixty.log**
   - Check if `bruteforce_parser.py` is running
   - Verify log directory permissions
   - Check Kafka topic has data

**5. "No module named 'apt_analyzer'"**
```bash
# Ensure all files are in the same directory
ls -la *.py
# Run from the correct directory
cd /path/to/bruteforce/
```

**6. "Log file not found"**
```bash
# Check log file paths
ls -la /home/primum/logs/
# Ensure bruteforce_parser.py is running and creating logs
```

**7. "Database locked"**
```bash
# Check if multiple processes are accessing the database
ps aux | grep python3
# Ensure proper file permissions
chmod 666 /home/primum/logs/ip_tracking.db
```

**8. "No suspicious activities found"**
```bash
# Check APT log paths exist
ls -la /var/log/apt/
# Verify suspicious package patterns match your environment
```

**9. "Kafka logs not being processed properly"**
```bash
# Test log parsing with your exact format
python3 test_log_parsing.py

# Enable debug mode in bruteforce_parser.py
DEBUG = True

# Check if logs are being written
tail -f /home/primum/logs/kafka_sixty.log
```

### Debug Mode
Enable debug output in `tester2.py`:
```python
DEBUG = True  # Set to True for verbose output

# Or set debug for specific components
apt_analyzer = APTAnalyzer(debug=True)
```

## 📈 Performance Considerations

- **Memory Usage**: ~50-100MB for typical workloads (SQLite database with indexing for fast queries)
- **CPU Usage**: Low, spikes during ML inference (ML model prediction is lightweight - Isolation Forest)
- **Disk I/O**: Minimal, mainly log file operations (automatic cleanup of old records - configurable retention)
- **Network**: Kafka connection bandwidth dependent (minimal impact, processes local log files)

## 🔒 Security Considerations

- **Permissions**: Run with appropriate user permissions
- **Log Retention**: Implement log rotation for disk space management (for long-term deployments)
- **Network Security**: Secure Kafka communications if needed
- **Alert Integration**: Consider integrating with SIEM systems
- **File Permissions**: Ensure log files and database have appropriate permissions
- **Access Control**: Restrict access to threat intelligence database
- **Data Retention**: Configure appropriate retention policies for compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes / Add tests for new functionality
4. Test thoroughly
5. Submit a pull request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages / Enable debug mode for detailed logging
3. Verify all dependencies are installed
4. Check file permissions and paths / Submit issues with complete error traces

## 📚 Technical Details

### Log Format Support
The system supports complex log formats like:
```
Jun 24 12:48:42 log-collector web_auth 2025-06-13T08:34:32+05:30 webserver webauth 2025-06-13T08:34:32.775864+05:30 webserver sshd[482432]: Failed password for invalid user hjames from 10.129.6.192 port 53655 ssh2
```

### Feature Engineering
The ML model uses behavioral features rather than signature-based detection:
- **Volume-based**: Number of attempts in time window
- **Diversity-based**: Variety of usernames attempted
- **Pattern-based**: Sequence of failed/successful attempts
- **Context-based**: Known vs unknown IP addresses

### APT Log Parsing
Supports standard APT history log format:
```
Start-Date: 2025-06-25  14:30:15
Commandline: apt install nmap
Install: nmap:amd64 (7.80+dfsg1-2build1)
End-Date: 2025-06-25  14:30:18
```

---

**Last Updated**: June 25, 2025  
**Version**: 2.0  
**Author**: Security Team

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

#!/usr/bin/env python3
"""
Script to create suspicious log patterns that should trigger anomaly detection
"""

import os
import sys
from datetime import datetime

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config

# Initialize configuration
config = Config()

def create_suspicious_logs():
    """Create log file with SSH brute force patterns"""
    
    # Get paths from configuration
    suspicious_log_file = config.get('paths.logs.suspicious_log')
    logs_dir = os.path.dirname(suspicious_log_file)
    os.makedirs(logs_dir, exist_ok=True)
    
    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')
    
    # Create log lines that show multiple failed login attempts
    # from the same IP with multiple usernames (classic brute force pattern)
    attacker_ip = "192.168.5.100"
    
    suspicious_logs = []
    
    # Add 15 failed login attempts with different usernames
    usernames = ["admin", "root", "user", "guest", "test", "oracle", "postgres", 
                "ubuntu", "administrator", "adm", "jenkins", "tomcat", 
                "webmaster", "support", "dev"]
    
    for username in usernames:
        suspicious_logs.append(
            f"{timestamp} webserver sshd: Failed password for invalid user {username} from {attacker_ip} port 45678 ssh2"
        )
    
    # Add a successful login after many failures (suspicious pattern)
    suspicious_logs.append(
        f"{timestamp} webserver sshd: Accepted password for sysadmin from {attacker_ip} port 45679 ssh2"
    )
    
    # Write to suspicious log file from config
    log_file = config.get('paths.logs.suspicious_log')
    with open(log_file, "w") as f:
        for log in suspicious_logs:
            f.write(log + "\n")
    
    print(f"\n✅ Created suspicious test logs at {log_file} with {len(suspicious_logs)} entries")
    print(f"This file contains a pattern of {len(usernames)} failed attempts from {attacker_ip}")
    print(f"To test: python3 main.py --detect")
    
    return log_file

if __name__ == "__main__":
    print("🔥 Generating suspicious SSH logs for testing anomaly detection")
    create_suspicious_logs()
    print("🚀 Ready to test the anomaly detection system!")

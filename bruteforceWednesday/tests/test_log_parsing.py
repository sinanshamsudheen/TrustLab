#!/usr/bin/env python3
"""
Test script to verify log parsing with your exact log format
"""

import re
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

# Same regex patterns as in bruteforce_parser.py
LOG_CONTENT_REGEX = re.compile(r'webserver\s+sshd\[\d+\]:\s*(.+)$')
SSHD_FALLBACK_REGEX = re.compile(r'sshd\[\d+\]:\s*(.+)$')

# Your actual log samples
test_logs = [
    "Jun 24 12:48:42 log-collector web_apt 2025-06-13T08:34:32+05:30 webserver webauth 2025-06-13T08:34:32.775864+05:30 webserver sshd[482432]: PAM 2 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost=10.129.6.192",
    "Jun 24 12:48:40 log-collector web_auth 2025-06-13T08:34:31+05:30 webserver webauth 2025-06-13T08:34:31.043484+05:30 webserver sshd[482432]: Failed password for invalid user hjames from 10.129.6.192 port 53655 ssh2",
    "Jun 24 12:48:42 log-collector web_auth 2025-06-13T08:34:32+05:30 webserver webauth 2025-06-13T08:34:32.775092+05:30 webserver sshd[482432]: Connection reset by invalid user hjames 10.129.6.192 port 53655 [preauth]"
]

def test_log_parsing():
    print("🧪 TESTING LOG PARSING WITH YOUR EXACT LOG FORMAT")
    print("=" * 60)
    
    for i, log_line in enumerate(test_logs, 1):
        print(f"\n📋 Test Log {i}:")
        print(f"Raw: {log_line}")
        
        # Test primary regex
        log_content_match = LOG_CONTENT_REGEX.search(log_line)
        if log_content_match:
            ssh_log_content = log_content_match.group(1)
            print(f"✅ Primary regex matched")
            print(f"📤 Extracted SSH content: {ssh_log_content}")
            
            # Create clean log line
            arrival_time = datetime.now()
            clean_log_line = f"{arrival_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: {ssh_log_content}"
            print(f"🔧 Clean log line: {clean_log_line}")
        else:
            # Test fallback
            fallback_match = SSHD_FALLBACK_REGEX.search(log_line)
            if fallback_match:
                ssh_log_content = fallback_match.group(1)
                print(f"⚠️ Fallback regex matched")
                print(f"📤 Extracted SSH content: {ssh_log_content}")
            else:
                print(f"❌ No regex matched - manual extraction needed")
                if 'webserver' in log_line:
                    parts = log_line.split('webserver')
                    ssh_content = parts[-1].strip()
                    print(f"🔧 Manual extraction: {ssh_content}")

def create_test_kafka_sixty_file():
    """Create a test kafka_sixty.log file with properly formatted logs"""
    
    # Use local logs directory we have permission for
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    current_time = datetime.now()
    
    # Create clean log lines from your raw logs
    clean_logs = [
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: PAM 2 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost=10.129.6.192",
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Failed password for invalid user hjames from 10.129.6.192 port 53655 ssh2",
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Connection reset by invalid user hjames 10.129.6.192 port 53655 [preauth]",
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Invalid user admin from 10.129.6.192 port 50106",
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Invalid user root from 10.129.6.192 port 50108"
    ]
    
    # Write to kafka_sixty.log
    log_file = os.path.join(logs_dir, "kafka_sixty.log")
    with open(log_file, "w") as f:
        for log in clean_logs:
            f.write(log + "\n")
    
    print(f"\n✅ Created test kafka_sixty.log at {log_file} with {len(clean_logs)} entries")
    print("Now you can run: python3 bruteforce_detector.py")
    # Return the log file path for convenience
    return log_file

if __name__ == "__main__":
    test_log_parsing()
    print("\n" + "=" * 60)
    create_test_kafka_sixty_file()
    print("\n🚀 Ready to test the full detection system!")

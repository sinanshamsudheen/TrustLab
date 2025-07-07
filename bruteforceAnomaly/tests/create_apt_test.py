#!/usr/bin/env python3
"""
Simulate APT activity for testing the APT monitoring service
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config

# Initialize configuration
config = Config()

def create_test_apt_history():
    """
    Create a mock APT history log entry in the logs directory
    for testing purposes. In production, this would be in /var/log/apt/history.log
    """
    
    # Get paths from configuration
    apt_log_file = config.get('paths.logs.apt_log')
    userlist_path = config.get('paths.user_data.userlist')
    suspicious_users = []
    
    try:
        with open(userlist_path, "r") as f:
            userlist = json.load(f)
            for user in userlist.get("suspicious_users", []):
                suspicious_users.append(user.get("username"))
    except Exception as e:
        print(f"Error reading userlist: {e}")
        suspicious_users = ["suspicious_user", "admin"]  # Fallback
    
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d  %H:%M:%S")
    
    # Create APT history entries - one for each suspicious user
    apt_entries = []
    
    for username in suspicious_users:
        # Create an entry that would trigger the APT monitor
        entry = (
            f"Start-Date: {date_str}\n"
            f"Commandline: apt install nmap\n"
            f"Requested-By: {username} (1000)\n"
            f"Install: nmap:amd64 (7.91-1)\n"
            f"End-Date: {date_str}\n"
            "\n"
        )
        apt_entries.append(entry)
    
    # Add an additional entry with a different suspicious tool
    entry = (
        f"Start-Date: {date_str}\n"
        f"Commandline: apt install metasploit-framework\n"
        f"Requested-By: {suspicious_users[0]} (1000)\n"
        f"Install: metasploit-framework:amd64 (6.1.27-1)\n"
        f"End-Date: {date_str}\n"
        "\n"
    )
    apt_entries.append(entry)
    
    # Write to file
    with open(apt_log_file, "w") as f:
        for entry in apt_entries:
            f.write(entry)
    
    print(f"\n✅ Created test APT history log at {apt_log_file}")
    print(f"Created {len(apt_entries)} suspicious APT entries for users: {', '.join(suspicious_users)}")
    print("Note: The APT monitor is looking at /var/log/apt/history.log by default")
    print("To test with this file, you would need to modify apt_monitor.py to point to this file")
    print(f"You can use: self.apt_log_path = '{apt_log_file}'")
    
    return apt_log_file

if __name__ == "__main__":
    print("🔥 Creating test APT history log entries to test monitoring")
    create_test_apt_history()

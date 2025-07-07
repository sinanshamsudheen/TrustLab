#!/usr/bin/env python3
"""
APT Monitor - Monitors APT history for suspicious package installations
by suspicious users identified by SSH brute force detection.
"""

import re
import os
import json
import sys
import time
import logging
from datetime import datetime, timedelta

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import Config

# Initialize configuration
config = Config()

# Configure logging
logging_file = config.get('paths.logs.monitor_log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logging_file),
        logging.StreamHandler()
    ]
)

class APTMonitor:
    def __init__(self):
        # Get file paths from configuration
        self.userlist_path = config.get('paths.user_data.userlist')
        self.apt_log_path = config.get('paths.logs.apt_log')
        self.check_interval = config.get('monitoring.check_interval', 60)
        
        logging.info(f"APT Monitor initialized. Using APT log: {self.apt_log_path}")
        logging.info(f"User list path: {self.userlist_path}")
        logging.info(f"Check interval: {self.check_interval} seconds")

        # For testing, reset the last check time to ensure we process all entries
        # In production, we'd use current time to avoid duplicate processing
        self.last_check_time = datetime.now() - timedelta(hours=1)
        
        self.suspicious_keywords = [
            'nmap', 'masscan', 'hydra', 'john', 'hashcat', 'metasploit', 'sqlmap',
            'nikto', 'dirb', 'gobuster', 'burpsuite', 'wireshark', 'tcpdump',
            'netcat', 'socat', 'proxychains', 'tor', 'aircrack', 'reaver',
            'ettercap', 'beef', 'armitage', 'maltego', 'backdoor', 'rootkit',
            'keylogger'
        ]

    def get_suspicious_users(self):
        """Get list of suspicious users from userlist.json"""
        try:
            if os.path.exists(self.userlist_path):
                with open(self.userlist_path, 'r') as f:
                    data = json.load(f)
                    return data.get("suspicious_users", [])
            return []
        except Exception as e:
            logging.error(f"Error reading user list: {e}")
            return []

    def extract_username_from_apt_entry(self, entry):
        """Extract username from APT log entry if available"""
        # Check direct user field
        if 'user' in entry:
            return entry['user']
            
        # Try to extract from commandline
        if 'commandline' in entry:
            cmd = entry['commandline'].lower()
            # Look for sudo user
            sudo_match = re.search(r'sudo -u (\S+)', cmd)
            if sudo_match:
                return sudo_match.group(1)
        
        return None
                
    def check_apt_history(self):
        """Check APT history for suspicious activities"""
        if not os.path.exists(self.apt_log_path):
            logging.warning(f"APT log file not found: {self.apt_log_path}")
            return []

        suspicious_users = self.get_suspicious_users()
        # Extract just usernames for easier matching
        suspicious_usernames = [entry.get("username") for entry in suspicious_users if "username" in entry]
        
        try:
            # Check for new activities since last run
            check_time = datetime.now()
            new_activities = []
            
            with open(self.apt_log_path, 'r') as f:
                current_entry = {}
                
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('Start-Date:'):
                        date_str = line.replace('Start-Date:', '').strip()
                        try:
                            entry_time = datetime.strptime(date_str, '%Y-%m-%d  %H:%M:%S')
                            current_entry = {'time': entry_time, 'actions': []}
                        except ValueError:
                            continue
                            
                    elif line.startswith(('Install:', 'Remove:', 'Upgrade:')):
                        if 'time' in current_entry:
                            current_entry['actions'].append(line)
                    
                    elif line.startswith('Commandline:'):
                        if 'time' in current_entry:
                            current_entry['commandline'] = line.replace('Commandline:', '').strip()
                    
                    elif line.startswith('Requested-By:'):
                        if 'time' in current_entry:
                            current_entry['user'] = line.replace('Requested-By:', '').strip()
                            
                    elif line.startswith('End-Date:'):
                        # Process completed entry
                        if 'time' in current_entry and current_entry['time'] > self.last_check_time:
                            # Extract username
                            username = self.extract_username_from_apt_entry(current_entry)
                            
                            # Flag for suspicious package
                            is_suspicious_package = False
                            suspicious_action = ""
                            
                            # Check for suspicious keywords in actions
                            for action in current_entry.get('actions', []):
                                for keyword in self.suspicious_keywords:
                                    if keyword.lower() in action.lower():
                                        is_suspicious_package = True
                                        suspicious_action = action
                                        break
                                if is_suspicious_package:
                                    break
                                    
                            # Two scenarios to alert:
                            # 1. Suspicious user performs ANY package operation
                            # 2. ANY user installs suspicious package
                            
                            alert_level = logging.INFO
                            alert_data = None
                            
                            if username and username in suspicious_usernames:
                                # Suspicious user detected
                                alert_level = logging.WARNING
                                alert_data = {
                                    'time': current_entry['time'].isoformat(),
                                    'user': username,
                                    'action': current_entry.get('actions', ['Unknown action'])[0],
                                    'commandline': current_entry.get('commandline', 'Unknown'),
                                    'reason': 'Suspicious user activity',
                                    'severity': 'WARNING'
                                }
                                
                                # Upgrade severity if installing suspicious package
                                if is_suspicious_package:
                                    alert_level = logging.CRITICAL
                                    alert_data['action'] = suspicious_action
                                    alert_data['reason'] = 'Suspicious user installing malicious package'
                                    alert_data['severity'] = 'CRITICAL'
                            
                            elif is_suspicious_package:
                                # Suspicious package detected
                                alert_level = logging.WARNING
                                alert_data = {
                                    'time': current_entry['time'].isoformat(),
                                    'user': username or 'Unknown',
                                    'action': suspicious_action,
                                    'commandline': current_entry.get('commandline', 'Unknown'),
                                    'reason': 'Malicious package installation',
                                    'severity': 'WARNING'
                                }
                            
                            # Add to alerts if needed
                            if alert_data:
                                new_activities.append(alert_data)
                                
                                # Find associated IPs for this user
                                associated_ips = []
                                for user_entry in suspicious_users:
                                    if user_entry.get("username") == username:
                                        associated_ips = user_entry.get("ips", [])
                                        break
                                        
                                # Log with appropriate severity
                                ip_info = f" (associated IPs: {', '.join(associated_ips)})" if associated_ips else ""
                                logging.log(
                                    alert_level,
                                    f"{alert_data['reason']} by {alert_data['user']}{ip_info}: {alert_data['action']}"
                                )
                                    
                        # Reset for next entry
                        current_entry = {}
                        
            # Update last check time
            self.last_check_time = check_time
            
            return new_activities
            
        except Exception as e:
            logging.error(f"Error checking APT history: {e}")
            return []
            
    def run_monitoring(self, interval=60):
        """Run continuous monitoring with the specified interval (seconds)"""
        logging.info("Starting APT activity monitoring...")
        
        try:
            while True:
                activities = self.check_apt_history()
                if activities:
                    logging.info(f"Found {len(activities)} suspicious activities")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            

if __name__ == "__main__":
    monitor = APTMonitor()
    monitor.run_monitoring()

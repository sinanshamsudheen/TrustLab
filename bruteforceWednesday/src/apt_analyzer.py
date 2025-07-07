import re
import os
import json
import sys
from datetime import datetime, timedelta

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_loader import config

def search_apt_history(suspicious_ip, username=None, time_window_hours=None):
    """
    Search apt history for malicious packages within a time window.
    Also stores suspicious IP and username to userlist.json for continuous monitoring.
    """
    # Use configured time window hours if not explicitly provided
    if time_window_hours is None:
        time_window_hours = config.get('monitoring.apt_time_window_hours', 24)
        
    print(f"\n[!] Anomaly detected from IP: {suspicious_ip}")
    if username:
        print(f"[!] Associated username: {username}")
    print(f"[*] Searching for suspicious APT activity (±{time_window_hours}h window)...")

    # Store username-IP mapping in userlist.json for continuous monitoring
    if username:
        userlist_path = config.get('paths.user_data.userlist')
        try:
            if os.path.exists(userlist_path):
                with open(userlist_path, 'r') as f:
                    user_data = json.load(f)
            else:
                user_data = {"suspicious_users": []}
            
            # Check if user already exists
            user_found = False
            for entry in user_data["suspicious_users"]:
                if entry.get("username") == username:
                    # Update existing entry
                    user_found = True
                    if suspicious_ip not in entry.get("ips", []):
                        entry["ips"].append(suspicious_ip)
                    entry["last_seen"] = datetime.now().isoformat()
                    break
            
            # Add new user entry if not found
            if not user_found:
                user_data["suspicious_users"].append({
                    "username": username,
                    "ips": [suspicious_ip],
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat()
                })
                
            user_data["last_updated"] = datetime.now().isoformat()
            
            with open(userlist_path, 'w') as f:
                json.dump(user_data, f, indent=2)
                
            print(f"[+] Added/Updated {username} with IP {suspicious_ip} to monitoring list")
        except Exception as e:
            print(f"[!] Error updating user list: {e}")

    # Check for test APT log file first
    test_apt_log = config.get('paths.logs.apt_log')
    production_apt_log = config.get('paths.production.apt_history')
    
    if os.path.exists(test_apt_log):
        apt_log_path = test_apt_log
        print(f"[*] Using test APT log: {test_apt_log}")
    else:
        apt_log_path = production_apt_log
    
    # Get suspicious keywords from config
    suspicious_keywords = config.get('detection.suspicious_keywords', [
        'nmap', 'masscan', 'hydra', 'metasploit'  # Fallback defaults
    ])
    
    found_suspicious_activity = False
    current_time = datetime.now()
    time_window = timedelta(hours=time_window_hours)

    if not os.path.exists(apt_log_path):
        print(f"[!] Log file not found: {apt_log_path}")
        return

    try:
        with open(apt_log_path, 'r') as f:
            current_entry = {}
            
            for line in f:
                line = line.strip()
                
                # Parse APT log entries (Start-Date, Install, Remove, etc.)
                if line.startswith('Start-Date:'):
                    # Extract timestamp: "Start-Date: 2025-06-25  14:30:15"
                    date_str = line.replace('Start-Date:', '').strip()
                    try:
                        entry_time = datetime.strptime(date_str, '%Y-%m-%d  %H:%M:%S')
                        current_entry = {'time': entry_time, 'actions': []}
                    except ValueError:
                        continue
                        
                elif line.startswith(('Install:', 'Remove:', 'Upgrade:')):
                    if 'time' in current_entry:
                        current_entry['actions'].append(line)
                
                # Capture command line to extract username if possible
                elif line.startswith('Commandline:'):
                    if 'time' in current_entry:
                        current_entry['commandline'] = line.replace('Commandline:', '').strip()
                
                # Try to capture requesting user if available
                elif line.startswith('Requested-By:'):
                    if 'time' in current_entry:
                        current_entry['user'] = line.replace('Requested-By:', '').strip()
                        
                elif line.startswith('End-Date:'):
                    # Process completed entry
                    if 'time' in current_entry:
                        # Check if within time window
                        time_diff = abs(current_time - current_entry['time'])
                        if time_diff <= time_window:
                            # Check for suspicious keywords
                            for action in current_entry['actions']:
                                for keyword in suspicious_keywords:
                                    if keyword in action.lower():
                                        print(f"[!!!] Suspicious activity found within {time_window_hours}h window:")
                                        print(f"    Time: {current_entry['time']}")
                                        print(f"    Action: {action}")
                                        if 'user' in current_entry:
                                            print(f"    User: {current_entry['user']}")
                                        if 'commandline' in current_entry:
                                            print(f"    Command: {current_entry['commandline']}")
                                        found_suspicious_activity = True
                    current_entry = {}
                    
    except Exception as e:
        print(f"[!] Error reading {apt_log_path}: {e}")

    if not found_suspicious_activity:
        print(f"[*] No suspicious APT activities found within ±{time_window_hours}h window.")

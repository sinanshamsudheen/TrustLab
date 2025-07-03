import re
import os
from datetime import datetime, timedelta

def search_apt_history(suspicious_ip, time_window_hours=24):
    """
    Search apt history for malicious packages within a time window.
    """
    print(f"\n[!] Anomaly detected from IP: {suspicious_ip}")
    print(f"[*] Searching for suspicious APT activity (±{time_window_hours}h window)...")

    apt_log_path = '/var/log/apt/history.log'
    suspicious_keywords = [
        'nmap', 'masscan', 'hydra', 'john', 'hashcat', 'metasploit', 'sqlmap',
        'nikto', 'dirb', 'gobuster', 'burpsuite', 'wireshark', 'tcpdump',
        'netcat', 'socat', 'proxychains', 'tor', 'aircrack', 'reaver',
        'ettercap', 'beef', 'armitage', 'maltego', 'backdoor', 'rootkit',
        'keylogger'
    ]
    
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
                                        found_suspicious_activity = True
                    current_entry = {}
                    
    except Exception as e:
        print(f"[!] Error reading {apt_log_path}: {e}")

    if not found_suspicious_activity:
        print(f"[*] No suspicious APT activities found within ±{time_window_hours}h window.")

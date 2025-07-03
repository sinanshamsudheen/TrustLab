import re
import os
from datetime import datetime, timedelta
from collections import defaultdict

class APTAnalyzer:
    def __init__(self, apt_log_paths=None, debug=False):
        self.debug = debug
        # Common APT log locations
        self.apt_log_paths = apt_log_paths or [
            '/var/log/apt/history.log',
            '/var/log/apt/history.log.1',
            '/var/log/dpkg.log',
            '/var/log/dpkg.log.1'
        ]
        
        # Suspicious package patterns
        self.suspicious_patterns = [
            r'nmap',
            r'masscan',
            r'hydra',
            r'john',
            r'hashcat',
            r'metasploit',
            r'sqlmap',
            r'nikto',
            r'dirb',
            r'gobuster',
            r'burpsuite',
            r'wireshark',
            r'tcpdump',
            r'netcat',
            r'socat',
            r'proxychains',
            r'tor',
            r'aircrack',
            r'reaver',
            r'ettercap',
            r'beef',
            r'armitage',
            r'maltego',
            r'reconnaissance',
            r'exploit',
            r'payload',
            r'backdoor',
            r'rootkit',
            r'keylogger',
            r'steghide',
            r'binwalk',
            r'foremost',
            r'volatility',
            r'yara',
            r'clamav',
            r'chkrootkit',
            r'rkhunter'
        ]
        
        # Compile regex patterns for efficiency
        self.suspicious_regex = re.compile('|'.join(self.suspicious_patterns), re.IGNORECASE)
        
        # Regex patterns for parsing APT logs
        self.apt_install_regex = re.compile(r'Install:\s*(.+)')
        self.apt_upgrade_regex = re.compile(r'Upgrade:\s*(.+)')
        self.apt_remove_regex = re.compile(r'Remove:\s*(.+)')
        self.apt_timestamp_regex = re.compile(r'Start-Date:\s*(.+)')
        self.apt_end_regex = re.compile(r'End-Date:\s*(.+)')
        
        # For dpkg logs
        self.dpkg_regex = re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+?)\s+(.+)')

    def analyze_ip_activity(self, suspicious_ip, time_window_hours=24):
        """
        Analyze APT activity for a specific IP within a time window
        """
        if self.debug:
            print(f"[DEBUG] Analyzing APT activity for IP: {suspicious_ip}")
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=time_window_hours)
        
        suspicious_activities = []
        
        # Check each log file
        for log_path in self.apt_log_paths:
            if os.path.exists(log_path):
                try:
                    activities = self._parse_apt_log(log_path, cutoff_time, suspicious_ip)
                    suspicious_activities.extend(activities)
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Error reading {log_path}: {e}")
        
        return suspicious_activities
    
    def _parse_apt_log(self, log_path, cutoff_time, suspicious_ip):
        """
        Parse APT history log for suspicious activities
        """
        suspicious_activities = []
        
        try:
            with open(log_path, 'r') as f:
                content = f.read()
            
            if 'history.log' in log_path:
                activities = self._parse_history_log(content, cutoff_time, suspicious_ip)
            elif 'dpkg.log' in log_path:
                activities = self._parse_dpkg_log(content, cutoff_time, suspicious_ip)
            else:
                activities = []
                
            suspicious_activities.extend(activities)
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error parsing {log_path}: {e}")
        
        return suspicious_activities
    
    def _parse_history_log(self, content, cutoff_time, suspicious_ip):
        """
        Parse /var/log/apt/history.log format
        """
        suspicious_activities = []
        
        # Split into individual transactions
        transactions = content.split('\n\n')
        
        for transaction in transactions:
            if not transaction.strip():
                continue
                
            lines = transaction.strip().split('\n')
            transaction_data = {}
            
            for line in lines:
                if line.startswith('Start-Date:'):
                    try:
                        date_str = line.replace('Start-Date: ', '').strip()
                        transaction_data['timestamp'] = datetime.strptime(date_str, '%Y-%m-%d  %H:%M:%S')
                    except:
                        continue
                elif line.startswith('Install:'):
                    transaction_data['action'] = 'Install'
                    transaction_data['packages'] = line.replace('Install: ', '').strip()
                elif line.startswith('Upgrade:'):
                    transaction_data['action'] = 'Upgrade'
                    transaction_data['packages'] = line.replace('Upgrade: ', '').strip()
                elif line.startswith('Remove:'):
                    transaction_data['action'] = 'Remove'
                    transaction_data['packages'] = line.replace('Remove: ', '').strip()
            
            # Check if transaction is within time window and has suspicious packages
            if 'timestamp' in transaction_data and transaction_data['timestamp'] >= cutoff_time:
                if 'packages' in transaction_data:
                    if self.suspicious_regex.search(transaction_data['packages']):
                        suspicious_activities.append({
                            'timestamp': transaction_data['timestamp'],
                            'action': transaction_data.get('action', 'Unknown'),
                            'packages': transaction_data['packages'],
                            'source': 'apt-history',
                            'suspicious_ip': suspicious_ip
                        })
        
        return suspicious_activities
    
    def _parse_dpkg_log(self, content, cutoff_time, suspicious_ip):
        """
        Parse /var/log/dpkg.log format
        """
        suspicious_activities = []
        
        for line in content.split('\n'):
            match = self.dpkg_regex.match(line)
            if match:
                timestamp_str, action, package, details = match.groups()
                
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if timestamp >= cutoff_time:
                        if self.suspicious_regex.search(package) or self.suspicious_regex.search(details):
                            suspicious_activities.append({
                                'timestamp': timestamp,
                                'action': action,
                                'packages': f"{package} - {details}",
                                'source': 'dpkg',
                                'suspicious_ip': suspicious_ip
                            })
                except:
                    continue
        
        return suspicious_activities
    
    def generate_report(self, activities):
        """
        Generate a formatted report of suspicious activities
        """
        if not activities:
            return "No suspicious package activities found."
        
        report = "\n🔍 SUSPICIOUS PACKAGE ACTIVITIES DETECTED:\n"
        report += "=" * 50 + "\n"
        
        for activity in activities:
            report += f"⏰ Time: {activity['timestamp']}\n"
            report += f"🎯 Action: {activity['action']}\n"
            report += f"📦 Packages: {activity['packages']}\n"
            report += f"📋 Source: {activity['source']}\n"
            report += "-" * 30 + "\n"
        
        return report

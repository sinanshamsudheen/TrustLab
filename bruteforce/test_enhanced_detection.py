#!/usr/bin/env python3
"""
Test script to simulate APT activities and verify the enhanced detection system
"""

import os
import subprocess
from datetime import datetime, timedelta
import tempfile

def create_test_apt_logs():
    """Create test APT log files with suspicious activities"""
    
    # Create test directory
    test_log_dir = "/tmp/test_apt_logs"
    os.makedirs(test_log_dir, exist_ok=True)
    
    # Create fake apt history.log with suspicious packages
    current_time = datetime.now()
    suspicious_time = current_time - timedelta(minutes=30)  # 30 minutes ago
    
    apt_history_content = f"""Start-Date: {suspicious_time.strftime('%Y-%m-%d  %H:%M:%S')}
Commandline: apt install nmap
Install: nmap:amd64 (7.80+dfsg1-2build1, automatic)
End-Date: {suspicious_time.strftime('%Y-%m-%d  %H:%M:%S')}

Start-Date: {(suspicious_time + timedelta(minutes=5)).strftime('%Y-%m-%d  %H:%M:%S')}
Commandline: apt install hydra
Install: hydra:amd64 (9.0-1, automatic), hydra-gtk:amd64 (9.0-1, automatic)
End-Date: {(suspicious_time + timedelta(minutes=5)).strftime('%Y-%m-%d  %H:%M:%S')}

Start-Date: {(suspicious_time + timedelta(minutes=10)).strftime('%Y-%m-%d  %H:%M:%S')}
Commandline: apt install metasploit-framework
Install: metasploit-framework:amd64 (6.1.14+dfsg-1, automatic)
End-Date: {(suspicious_time + timedelta(minutes=10)).strftime('%Y-%m-%d  %H:%M:%S')}
"""
    
    apt_history_path = os.path.join(test_log_dir, "history.log")
    with open(apt_history_path, 'w') as f:
        f.write(apt_history_content)
    
    # Create fake dpkg.log with more suspicious activities
    dpkg_content = f"""{suspicious_time.strftime('%Y-%m-%d %H:%M:%S')} install nmap:amd64 <none> 7.80+dfsg1-2build1
{(suspicious_time + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')} configure nmap:amd64 7.80+dfsg1-2build1 <none>
{(suspicious_time + timedelta(minutes=6)).strftime('%Y-%m-%d %H:%M:%S')} install hydra:amd64 <none> 9.0-1
{(suspicious_time + timedelta(minutes=8)).strftime('%Y-%m-%d %H:%M:%S')} configure hydra:amd64 9.0-1 <none>
{(suspicious_time + timedelta(minutes=12)).strftime('%Y-%m-%d %H:%M:%S')} install sqlmap:amd64 <none> 1.4.7+dfsg-1
{(suspicious_time + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')} configure sqlmap:amd64 1.4.7+dfsg-1 <none>
"""
    
    dpkg_path = os.path.join(test_log_dir, "dpkg.log")
    with open(dpkg_path, 'w') as f:
        f.write(dpkg_content)
    
    print(f"✅ Created test APT logs in: {test_log_dir}")
    return test_log_dir

def create_test_ssh_logs():
    """Create test SSH logs that will trigger anomalies"""
    
    current_time = datetime.now()
    
    # Test logs with brute force attempts
    test_ssh_logs = [
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Invalid user admin from 10.129.6.192 port 50106",
        f"{(current_time - timedelta(seconds=10)).strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Invalid user root from 10.129.6.192 port 50108",
        f"{(current_time - timedelta(seconds=20)).strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Invalid user test from 10.129.6.192 port 50110",
        f"{(current_time - timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Failed password for invalid user hacker from 10.129.6.192 port 50112",
        f"{(current_time - timedelta(seconds=40)).strftime('%Y-%m-%dT%H:%M:%S+05:30')} webserver sshd: Accepted password for primum from 192.168.10.15 port 50114"
    ]
    
    # Ensure log directory exists
    os.makedirs("/home/primum/logs", exist_ok=True)
    
    # Write test logs
    with open("/home/primum/logs/kafka_sixty.log", "w") as f:
        for log in test_ssh_logs:
            f.write(log + "\n")
    
    print("✅ Created test SSH logs")

def run_enhanced_test():
    """Run the complete enhanced detection test"""
    
    print("🧪 RUNNING ENHANCED BRUTE FORCE DETECTION TEST")
    print("=" * 60)
    
    # Step 1: Create test APT logs
    test_apt_dir = create_test_apt_logs()
    
    # Step 2: Create test SSH logs
    create_test_ssh_logs()
    
    # Step 3: Modify APT analyzer to use test logs
    print("\n📝 Updating APT analyzer to use test logs...")
    
    # Create a test version of the analyzer
    test_analyzer_code = f"""
# Temporary test configuration
from apt_analyzer import APTAnalyzer

# Create analyzer with test log paths
apt_analyzer = APTAnalyzer(
    apt_log_paths=[
        '{test_apt_dir}/history.log',
        '{test_apt_dir}/dpkg.log'
    ],
    debug=True
)

# Test the analyzer
print("Testing APT analyzer with suspicious IP 10.129.6.192...")
activities = apt_analyzer.analyze_ip_activity("10.129.6.192", time_window_hours=2)

if activities:
    print("🚨 FOUND SUSPICIOUS ACTIVITIES:")
    report = apt_analyzer.generate_report(activities)
    print(report)
else:    print("❌ No suspicious activities found")
"""
    
    # Get absolute path for the test script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_analyzer_path = os.path.join(script_dir, "test_apt_analyzer.py")
    
    with open(test_analyzer_path, "w") as f:
        f.write(test_analyzer_code)
    
    # Step 4: Run the test
    print("\n🔍 Testing APT analyzer...")
    try:
        result = subprocess.run(["python3", test_analyzer_path], 
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"Error running APT test: {e}")
    
    # Step 5: Run the main detection system
    print("\n🎯 Running main detection system...")
    try:
        # Update tester2.py to use test APT logs temporarily
        result = subprocess.run(["python3", "tester2.py"], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"Error running main detection: {e}")
    
    # Step 6: Check database contents
    print("\n📊 Checking tracking database...")
    try:
        from ip_tracker import IPTracker
        tracker = IPTracker()
        stats = tracker.get_stats()
        print(f"Database stats: {stats}")
        
        recent_ips = tracker.get_recent_anomalous_ips(hours=1)
        print(f"Recent anomalous IPs: {recent_ips}")
        
        critical_threats = tracker.get_critical_threats(hours=1)
        print(f"Critical threats: {critical_threats}")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    try:
        os.remove("test_apt_analyzer.py")
        subprocess.run(["rm", "-rf", test_apt_dir], check=True)
    except:
        pass
    
    print("\n✅ Enhanced detection test completed!")

if __name__ == "__main__":
    run_enhanced_test()

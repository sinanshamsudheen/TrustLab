import pandas as pd
import joblib
import re
import os
from datetime import datetime
from dateutil.parser import isoparse
from apt_analyzer import APTAnalyzer
from ip_tracker import IPTracker

# Set debug flag
DEBUG = False  # Set to True for verbose output

# Initialize components
apt_analyzer = APTAnalyzer(debug=DEBUG)
ip_tracker = IPTracker()

# Load trained model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "bruteforce_model.pkl")

try:
    model = joblib.load(model_path)  # IsolationForest model
    if DEBUG:
        print(f"[DEBUG] Model loaded successfully from {model_path}")
except Exception as e:
    print(f"[ERROR] Failed to load model from {model_path}: {e}")
    model = None

# CONFIG
LOG_FILE = "/home/primum/logs/kafka_sixty.log"
KNOWN_USERS = { "192.168.10.15": "primum" }  # IP to expected user mapping

# Improved regex patterns - updated for raw log format
IP_REGEX = re.compile(r'rhost=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
USER_REGEX = re.compile(r'invalid user\s+([a-zA-Z0-9_\-]+)|user\s+([a-zA-Z0-9_\-]+)')

# Read logs with error handling
lines = []
try:
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    if DEBUG:
        print(f"[DEBUG] Successfully read {len(lines)} log lines")
except FileNotFoundError:
    print(f"[ERROR] Log file {LOG_FILE} not found")
except Exception as e:
    print(f"[ERROR] Failed to read logs: {e}")

if DEBUG:
    print(f"[DEBUG] Loaded logs: {lines}")

# Group by source IP
ip_log_dict = {}
for line in lines:
    try:
        ip_match = IP_REGEX.search(line)
        user_match = USER_REGEX.search(line)
        if ip_match:
            # Extract IP from either capture group
            ip = ip_match.group(1) if ip_match.group(1) else ip_match.group(2)
            # Extract username from either capture group
            user = None
            if user_match:
                user = user_match.group(1) if user_match.group(1) else user_match.group(2)
            
            ip_log_dict.setdefault(ip, []).append((line, user))
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Error processing log line: {e}")
            print(f"[DEBUG] Line: {line}")

# Extract features per IP
feature_rows = []
for ip, logs in ip_log_dict.items():
    attempts = len(logs)
    users = [u for _, u in logs if u]
    unique_users = len(set(users))
    invalid_user = any("Invalid user" in l for l, _ in logs)
    success_after_fail = any("Failed password" in l for l, _ in logs) and any("Accepted password" in l for l, _ in logs)

    true_user_flag = 0
    if ip in KNOWN_USERS:
        expected_user = KNOWN_USERS[ip]
        true_user_flag = int(expected_user in users)

    feature_rows.append({
        'attempts_in_60s': attempts,
        'unique_users_in_60s': unique_users,
        'invalid_user': int(invalid_user),
        'success_after_fail': int(success_after_fail),
        'true_user': true_user_flag
    })

# Predict
df_features = pd.DataFrame(feature_rows)

if df_features.empty:
    print("⛔ No valid log entries to analyze.")
elif model is None:
    print("⛔ Cannot analyze logs - model loading failed.")
else:
    try:
        preds = model.predict(df_features)
        print(f"\nPredictions (−1 = anomaly, 1 = normal): {preds}")

        current_anomalies = []
        
        for i, ip in enumerate(ip_log_dict.keys()):
            if preds[i] == -1:  # New anomaly detected
                print(f"{ip} → ⚠️ Anomaly")
                
                # Prepare SSH details for tracking
                users = [u for _, u in ip_log_dict[ip] if u]
                ssh_details = {
                    'attempts': feature_rows[i]['attempts_in_60s'],
                    'unique_users': feature_rows[i]['unique_users_in_60s'],
                    'invalid_user': bool(feature_rows[i]['invalid_user']),
                    'success_after_fail': bool(feature_rows[i]['success_after_fail']),
                    'users': list(set(users))
                }
                
                # Record this anomaly in the tracking database
                ip_tracker.record_anomaly(ip, ssh_details)
                current_anomalies.append(ip)
                
                # Display anomaly details
                print(f"  - Attempts: {ssh_details['attempts']}")
                print(f"  - Unique users: {ssh_details['unique_users']}")
                if ssh_details['invalid_user']:
                    print("  - Invalid user attempts detected")
                if ssh_details['success_after_fail']:
                    print("  - Success after failure detected")
                print(f"  - Users attempted: {', '.join(ssh_details['users'])}")
                
            else:  # Normal behavior
                print(f"{ip} → ✅ Normal")
        
        # 🔍 NOW CHECK APT ACTIVITIES FOR ALL RECENT ANOMALOUS IPs
        print(f"\n🔍 Checking APT activities for recently anomalous IPs...")
        recent_anomalous_ips = ip_tracker.get_recent_anomalous_ips(hours=6)  # Check last 6 hours
        
        critical_threats = []
        
        for ip, last_seen, current_threat_level in recent_anomalous_ips:
            print(f"\n📋 Analyzing APT activity for {ip} (last anomaly: {last_seen}, threat level: {current_threat_level})...")
            
            # Check APT activities in the time window around the anomaly
            apt_activities = apt_analyzer.analyze_ip_activity(ip, time_window_hours=8)
            
            if apt_activities:
                print(f"🚨 CRITICAL: Suspicious package activities found for {ip}!")
                apt_report = apt_analyzer.generate_report(apt_activities)
                print(apt_report)
                
                # Update the tracking database
                ip_tracker.update_apt_analysis(ip, apt_activities)
                critical_threats.append(ip)
                
                # Log to critical threats file
                try:
                    with open("/home/primum/logs/critical_threats.log", "a") as threat_file:
                        threat_file.write(f"\n{'-'*60}\n")
                        threat_file.write(f"CRITICAL THREAT DETECTED: {ip}\n")
                        threat_file.write(f"Detection Time: {datetime.now()}\n")
                        threat_file.write(f"Last SSH Anomaly: {last_seen}\n")
                        threat_file.write(f"Threat Level: CRITICAL (SSH + APT)\n")
                        threat_file.write(apt_report)
                        threat_file.write(f"\n{'-'*60}\n")
                except Exception as e:
                    print(f"[ERROR] Failed to write to critical threats log: {e}")
                    
            else:
                print(f"✅ No suspicious package activities found for {ip}")
                # Update tracking to mark APT as checked
                ip_tracker.update_apt_analysis(ip, [])
        
        # Get and display current critical threats
        critical_threat_records = ip_tracker.get_critical_threats(hours=24)
        
        # Summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"New SSH anomalies detected: {len(current_anomalies)}")
        print(f"Recently anomalous IPs checked: {len(recent_anomalous_ips)}")
        print(f"IPs with APT activities: {len(critical_threats)}")
        print(f"Total critical threats (24h): {len(critical_threat_records)}")
        
        if current_anomalies:
            print(f"🔥 New anomalous IPs: {', '.join(current_anomalies)}")
        
        if critical_threats:
            print(f"🚨 CRITICAL IPs (SSH + APT): {', '.join(critical_threats)}")
        
        if critical_threat_records:
            print(f"\n🚨 ALL CRITICAL THREATS (Last 24h):")
            for record in critical_threat_records:
                ip, detection_time, ssh_details, apt_activities, threat_level = record
                print(f"  {ip} - Level {threat_level} - Last seen: {detection_time}")
        
        # Display database statistics
        stats = ip_tracker.get_stats()
        print(f"\n📈 DATABASE STATISTICS:")
        print(f"Total tracked IPs: {stats['total_records']}")
        print(f"Recent activity (24h): {stats['recent_records_24h']}")
        print(f"Threat levels: {stats['threat_level_stats']}")
        
        # Cleanup old records
        ip_tracker.cleanup_old_records(days=7)
        
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")


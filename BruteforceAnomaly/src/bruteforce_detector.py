import pandas as pd
import joblib
import re
import os
import sys
from datetime import datetime
from dateutil.parser import isoparse

# Add project root to path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.apt_analyzer import search_apt_history
from src.config_loader import config

# Set debug flag
DEBUG = True  # Set to True for verbose output

# Load trained model
model_path = config.get('paths.models.bruteforce_model')

try:
    model = joblib.load(model_path)  # IsolationForest model
    if DEBUG:
        print(f"[DEBUG] Model loaded successfully from {model_path}")
except Exception as e:
    print(f"[ERROR] Failed to load model from {model_path}: {e}")
    model = None

# CONFIG
# Check for suspicious test log file first, then regular test log, then production path
suspicious_log_file = config.get('paths.logs.suspicious_log')
local_log_file = config.get('paths.logs.recent_log')
production_log_file = config.get('paths.production.kafka_log')

if os.path.exists(suspicious_log_file):
    LOG_FILE = suspicious_log_file
    print(f"[INFO] Using suspicious test log file: {suspicious_log_file}")
elif os.path.exists(local_log_file):
    LOG_FILE = local_log_file
    print(f"[INFO] Using local test log file: {local_log_file}")
else:
    LOG_FILE = production_log_file
    
# IP to expected user mapping - Add your known legitimate users here
# Example format: KNOWN_USERS = { "192.168.1.100": "username", "10.0.0.5": "admin" }
KNOWN_USERS = {}  # Empty by default - populate with your legitimate IP-to-user mappings

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
    print("⚠️ Model loading failed - proceeding with simulated detection for testing")
    # Simulate detection for testing purposes
    simulated_preds = [-1] * len(df_features)  # Treat all as anomalies for testing
    try:
        preds = simulated_preds
        print(f"\nSimulated Predictions (−1 = anomaly, 1 = normal): {preds}")

        current_anomalies = []
        
        for i, ip in enumerate(ip_log_dict.keys()):
            if preds[i] == -1:  # Simulated anomaly detected
                print(f"{ip} → ⚠️ Anomaly")
                
                # Display anomaly details
                users = [u for _, u in ip_log_dict[ip] if u]
                print(f"  - Attempts: {feature_rows[i]['attempts_in_60s']}")
                print(f"  - Unique users: {feature_rows[i]['unique_users_in_60s']}")
                if feature_rows[i]['invalid_user']:
                    print("  - Invalid user attempts detected")
                if feature_rows[i]['success_after_fail']:
                    print("  - Success after failure detected")
                print(f"  - Users attempted: {', '.join(set(users))}")
                
                # Call APT analysis with username and IP
                # Select the most relevant username for the alert
                suspicious_user = None
                if users and len(users) > 0:
                    suspicious_user = users[0]  # Use first user by default
                    # Prefer successful logins if available
                    successful_users = [u for u, l in zip([u for _, u in ip_log_dict[ip] if u], 
                                              [l for l, _ in ip_log_dict[ip]]) 
                                        if "Accepted password" in l]
                    if successful_users:
                        suspicious_user = successful_users[0]
                
                # Call with username if available
                if suspicious_user:
                    print(f"  - Selected username for monitoring: {suspicious_user}")
                    search_apt_history(ip, username=suspicious_user)
                else:
                    search_apt_history(ip)
                    
                current_anomalies.append(ip)
                
            else:  # Normal behavior
                print(f"{ip} → ✅ Normal")
        
        # Summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"SSH anomalies detected: {len(current_anomalies)}")
        
        if current_anomalies:
            print(f"🔥 Anomalous IPs: {', '.join(current_anomalies)}")
        else:
            print("✅ No anomalies detected in this analysis.")
            
    except Exception as e:
        print(f"[ERROR] Simulation failed: {e}")
else:
    try:
        preds = model.predict(df_features)
        print(f"\nPredictions (−1 = anomaly, 1 = normal): {preds}")

        current_anomalies = []
        
        for i, ip in enumerate(ip_log_dict.keys()):
            if preds[i] == -1:  # New anomaly detected
                print(f"{ip} → ⚠️ Anomaly")
                
                # Display anomaly details
                users = [u for _, u in ip_log_dict[ip] if u]
                print(f"  - Attempts: {feature_rows[i]['attempts_in_60s']}")
                print(f"  - Unique users: {feature_rows[i]['unique_users_in_60s']}")
                if feature_rows[i]['invalid_user']:
                    print("  - Invalid user attempts detected")
                if feature_rows[i]['success_after_fail']:
                    print("  - Success after failure detected")
                print(f"  - Users attempted: {', '.join(set(users))}")
                
                # Call APT analysis with username and IP
                # Select the most relevant username for the alert
                suspicious_user = None
                if users and len(users) > 0:
                    suspicious_user = users[0]  # Use first user by default
                    # Prefer successful logins if available
                    successful_users = [u for u, l in zip([u for _, u in ip_log_dict[ip] if u], 
                                              [l for l, _ in ip_log_dict[ip]]) 
                                        if "Accepted password" in l]
                    if successful_users:
                        suspicious_user = successful_users[0]
                
                # Call with username if available
                if suspicious_user:
                    print(f"  - Selected username for monitoring: {suspicious_user}")
                    search_apt_history(ip, username=suspicious_user)
                else:
                    search_apt_history(ip)
                    
                current_anomalies.append(ip)
                
            else:  # Normal behavior
                print(f"{ip} → ✅ Normal")
        
        # Summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"SSH anomalies detected: {len(current_anomalies)}")
        
        if current_anomalies:
            print(f"🔥 Anomalous IPs: {', '.join(current_anomalies)}")
        else:
            print("✅ No anomalies detected in this analysis.")
        
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")

def main():
    """Main function for running the detector when imported as a module"""
    # All detection logic is already at the module level, just need this function
    # as an entry point when imported
    print("Running SSH brute force detection...")
    # The detection code will execute when the module is imported

if __name__ == "__main__":
    # This allows the script to be run as a standalone program
    main()


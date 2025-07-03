import pandas as pd
import joblib
import re
import os
from datetime import datetime
from dateutil.parser import isoparse
from apt_analyzer import search_apt_history

# Set debug flag
DEBUG = False  # Set to True for verbose output

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
                
                # Display anomaly details
                users = [u for _, u in ip_log_dict[ip] if u]
                print(f"  - Attempts: {feature_rows[i]['attempts_in_60s']}")
                print(f"  - Unique users: {feature_rows[i]['unique_users_in_60s']}")
                if feature_rows[i]['invalid_user']:
                    print("  - Invalid user attempts detected")
                if feature_rows[i]['success_after_fail']:
                    print("  - Success after failure detected")
                print(f"  - Users attempted: {', '.join(set(users))}")
                
                # Call simplified APT analysis
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


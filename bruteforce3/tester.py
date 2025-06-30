import pandas as pd
from datetime import datetime, timedelta
import joblib
import re

# Load trained model
model = joblib.load("bruteforce_model.pkl")  # Make sure this is IsolationForest

# CONFIG
LOG_FILE = "/etc/parser_service/core/kafka_logs_output.log"
KNOWN_USERS = { "192.168.10.15": "primum",
               "192.168.10.17" : "bytesentinel"
                }  # Dictionary of known users per IP
time_window_seconds = 60

# Regex patterns
IP_REGEX = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})')
USER_REGEX = re.compile(r'user\s+([a-zA-Z0-9_\-]+)')

# Read and filter logs
with open(LOG_FILE, "r") as f:
    lines = f.readlines()

# Get current time and filter recent 60 seconds logs
now = datetime.now()
recent_logs = []
for line in lines:
    parts = line.split()
    from dateutil.parser import isoparse

for line in lines:
    match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line)
    if match:
        try:
            log_time = isoparse(match.group())
            if now - log_time <= timedelta(seconds=time_window_seconds):
                recent_logs.append(line)
        except:
            continue


# Group by source IP
ip_log_dict = {}
for line in recent_logs:
    ip_match = IP_REGEX.search(line)
    user_match = USER_REGEX.search(line)
    if ip_match:
        ip = ip_match.group(1)
        user = user_match.group(1) if user_match else None
        ip_log_dict.setdefault(ip, []).append((line, user))

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

# Convert to DataFrame
df_features = pd.DataFrame(feature_rows)

if df_features.empty:
    print("⛔ No recent logs in the past 60 seconds.")
else:
    preds = model.predict(df_features)
    print(f"\nPredictions (−1 = anomaly, 1 = normal): {preds}")

    for i, ip in enumerate(ip_log_dict.keys()):
        print(f"{ip} → {'⚠️ Anomaly' if preds[i] == -1 else '✅ Normal'}")

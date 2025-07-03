import joblib
import pandas as pd
from datetime import datetime, timedelta
import re
import os

# Load the model
model = joblib.load("bruteforce_model.pkl")

# Feature extraction from raw log lines
def extract_features(log_lines):
    now = datetime.now()
    time_window = timedelta(seconds=60)

    timestamps = []
    users = []
    invalid_users = 0
    success_after_fail = 0
    source_ips = []

    last_event_by_ip = {}

    for line in log_lines:
        # Match datetime from log
        match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line)
        if not match:
            continue
        timestamp = datetime.strptime(match.group(), "%Y-%m-%dT%H:%M:%S")

        if now - timestamp > time_window:
            continue  # Skip logs outside the 30-second window

        timestamps.append(timestamp)

        # Extract IP
        ip_match = re.search(r'from ([\d\.]+)', line)
        if ip_match:
            source_ips.append(ip_match.group(1))

        # Extract user
        user_match = re.search(r'user (\w+)', line)
        if user_match:
            users.append(user_match.group(1))

        # Invalid user check
        if "Invalid user" in line or "user unknown" in line:
            invalid_users += 1

        # Success after fail detection
        ip = ip_match.group(1) if ip_match else None
        if ip:
            if "Failed password" in line:
                last_event_by_ip[ip] = "fail"
            elif "Accepted password" in line and last_event_by_ip.get(ip) == "fail":
                success_after_fail += 1

    # If no relevant logs, return None
    if not timestamps:
        return None

    # Calculate features
    attempts_in_30s = len(timestamps)
    unique_users_in_30s = len(set(users))
    invalid_user_flag = 1 if invalid_users > 0 else 0
    success_flag = 1 if success_after_fail > 0 else 0

    features = pd.DataFrame([{
        'attempts_in_30s': attempts_in_30s,
        'unique_users_in_30s': unique_users_in_30s,
        'invalid_user': invalid_user_flag,
        'success_after_fail': success_flag
    }])

    return features

# Read recent logs from file
def read_logs_from_file(log_file='kafka_logs.log'):
    if not os.path.exists(log_file):
        return []
    with open(log_file, 'r') as f:
        return f.readlines()

# Main prediction logic
def predict_bruteforce():
    logs = read_logs_from_file()
    features = extract_features(logs)

    if features is None:
        print("❌ No logs in the last 30 seconds.")
        return False

    prediction = model.predict(features)[0]
    print("✅ Prediction:", "Brute-force detected!" if prediction else "Normal activity")
    return bool(prediction)

# Run the prediction
if __name__ == "__main__":
    predict_bruteforce()

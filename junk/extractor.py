import pandas as pd
import json
from datetime import datetime, timedelta

LOG_FILE = 'latest_logs.jsonl'

def load_logs():
    logs = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                log = json.loads(line.strip())
                logs.append(log)
            except json.JSONDecodeError:
                continue
    return logs

def preprocess_logs(logs):
    df = pd.DataFrame(logs)
    
    # Convert timestamps to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Add required fields if not present
    if 'source_ip' not in df.columns:
        df['source_ip'] = '0.0.0.0'
    if 'event_type' not in df.columns:
        df['event_type'] = 'unknown'
    if 'user' not in df.columns:
        df['user'] = 'unknown'
    if 'raw_message' not in df.columns:
        df['raw_message'] = ''

    return df

def extract_features(df):
    feature_rows = []

    for i in range(len(df)):
        row = df.iloc[i]
        current_time = row['timestamp']
        source_ip = row['source_ip']

        # Filter logs within 30 seconds from same IP
        time_window = df[
            (df['source_ip'] == source_ip) &
            (df['timestamp'] >= current_time - timedelta(seconds=30)) &
            (df['timestamp'] <= current_time)
        ]

        # Feature 1: Number of attempts in 30s
        attempts_in_30s = len(time_window)

        # Feature 2: Unique users in 30s
        unique_users_in_30s = time_window['user'].nunique()

        # Feature 3: invalid user
        invalid_user = int('invalid user' in row['raw_message'].lower())

        # Feature 4: success after fail
        success_after_fail = 0
        past_events = df[
            (df['source_ip'] == source_ip) &
            (df['timestamp'] < current_time)
        ]
        if not past_events.empty:
            last_failed = past_events[past_events['event_type'] == 'failed']
            if not last_failed.empty and row['event_type'] == 'success':
                success_after_fail = 1

        feature_rows.append({
            'source_ip': source_ip,
            'user': row['user'],
            'timestamp': row['timestamp'],
            'attempts_in_30s': attempts_in_30s,
            'unique_users_in_30s': unique_users_in_30s,
            'invalid_user': invalid_user,
            'success_after_fail': success_after_fail
        })

    return pd.DataFrame(feature_rows)

if __name__ == "__main__":
    logs = load_logs()
    if not logs:
        print("❌ No logs found.")
    else:
        df_logs = preprocess_logs(logs)
        features_df = extract_features(df_logs)
        features_df.to_csv("features_latest.csv", index=False)
        print("✅ Features extracted and saved to features_latest.csv")
        print(features_df.head(3))

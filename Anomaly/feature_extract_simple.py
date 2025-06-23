import pandas as pd
import json
import re
from datetime import datetime

def load_logs(log_data):
    """Load logs from JSON data or file path"""
    if isinstance(log_data, str) and log_data.endswith('.json'):
        with open(log_data, 'r') as f:
            data = json.load(f)
    elif isinstance(log_data, str):
        data = json.loads(log_data)
    else:
        data = log_data

    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} log entries")
    return df

def extract_features_for_log(log):
    """Extract features for a single log entry"""
    features = {}

    process = log.get('process', 'unknown')
    user = log.get('user', 'unknown')
    host = log.get('host', {})
    message = str(log.get('message', ''))
    queue_status = log.get('queue_status', 'unknown')
    timestamp = log.get('timestamp', '')
    qid = log.get('qid', 'unknown')

    # BASIC FEATURES
    features['process'] = process
    features['user'] = user
    features['queue_status'] = queue_status
    features['host_name'] = host.get('hostname', 'unknown') if isinstance(host, dict) else str(host)
    features['qid'] = qid

    # PROCESS ONE-HOT
    features['is_pickup'] = 1 if 'pickup' in process else 0
    features['is_cleanup'] = 1 if 'cleanup' in process else 0
    features['is_qmgr'] = 1 if 'qmgr' in process else 0
    features['is_bounce'] = 1 if 'bounce' in process else 0
    features['is_postsuper'] = 1 if 'postsuper' in process else 0

    # QUEUE STATUS ONE-HOT
    features['queue_active'] = 1 if 'queue active' == queue_status else 0
    features['queue_unknown'] = 1 if 'unknown' == queue_status else 0
    features['queue_deferred'] = 1 if 'deferred' == queue_status else 0
    features['queue_bounced'] = 1 if 'bounced' == queue_status else 0

    # MESSAGE FEATURES
    size_match = re.search(r'size=(\d+)', message)
    features['size'] = int(size_match.group(1)) if size_match else 0

    nrcpt_match = re.search(r'nrcpt=(\d+)', message)
    features['nrcpt'] = int(nrcpt_match.group(1)) if nrcpt_match else 0

    features['has_from_email'] = 1 if 'from=<' in message else 0
    features['has_to_email'] = 1 if 'to=<' in message else 0
    features['has_message_id'] = 1 if 'message-id=' in message else 0
    features['has_removed'] = 1 if 'removed' in message else 0
    features['has_error'] = 1 if any(word in message.lower() for word in ['error', 'fail', 'timeout', 'reject']) else 0

    # TIME FEATURES
    try:
        dt = datetime.strptime(timestamp + f" {datetime.now().year}", '%b %d %H:%M:%S %Y')
        features['log_hour'] = dt.hour
        features['not_working_hour'] = 1 if (dt.hour < 8 or dt.hour >= 20) else 0
        features['is_weekend'] = 1 if dt.weekday() >= 5 else 0
    except:
        features['log_hour'] = -1
        features['not_working_hour'] = 0
        features['is_weekend'] = 0

    # TEXT FEATURES
    features['message_length'] = len(message)
    features['unique_words'] = len(set(message.lower().split()))
    features['contains_warning'] = 1 if 'warning' in message.lower() else 0
    features['contains_connection'] = 1 if any(w in message.lower() for w in ['connection', 'connect', 'disconnect']) else 0
    features['contains_status'] = 1 if 'status' in message.lower() else 0
    features['contains_relay'] = 1 if 'relay' in message.lower() else 0
    features['contains_delivered'] = 1 if 'delivered' in message.lower() else 0
    features['contains_held'] = 1 if 'held' in message.lower() else 0

    numeric_patterns = re.findall(r'\b\d+\b', message)
    features['numeric_pattern_count'] = len(numeric_patterns)

    return features

def extract_all_features(df):
    """Extract features for all log entries"""
    print("Extracting features for each log entry...")
    feature_list = [extract_features_for_log(row) for _, row in df.iterrows()]
    features_df = pd.DataFrame(feature_list).fillna(0)

    # USER-DERIVED FEATURES
    features_df['user_is_unknown'] = (features_df['user'] == 'unknown').astype(int)
    user_counts = features_df['user'].value_counts()
    features_df['user_frequency'] = features_df['user'].map(user_counts)

    # ONE-HOT ENCODE PROCESS
    process_one_hot = pd.get_dummies(features_df['process'], prefix='process')
    features_df = pd.concat([features_df, process_one_hot], axis=1)

    # DROP raw columns except qid
    features_df = features_df.drop(columns=['user', 'host_name', 'queue_status', 'process'])

    print(f"Extracted {len(features_df.columns)} features for {len(features_df)} logs")
    print(f"Features: {list(features_df.columns)}")
    return features_df

def save_to_csv(features_df, filename="realtime_extracted_features.csv"):
    features_df.to_csv(filename, index=False)
    print(f"Features saved to '{filename}'")

def show_summary(features_df):
    print("\n=== FEATURE SUMMARY ===")
    print(features_df.head())
    print(features_df.describe())

def main(input_file=None, output_file=None):
    if input_file is None:
        input_file = "filtered_logs.json"
    if output_file is None:
        output_file = "realtime_extracted_features.csv"

    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    try:
        df = load_logs(input_file)
        features_df = extract_all_features(df)
        show_summary(features_df)
        save_to_csv(features_df, output_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main('filtered_logs.json', 'realtime_extracted_features.csv')

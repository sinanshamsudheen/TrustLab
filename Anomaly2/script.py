#this is the script to extract features from auth.log for SSH brute force detection
import re
import pandas as pd
from datetime import datetime

# Read file
with open('attack_auth.log') as f:
    lines = f.readlines()

# Parse lines
records = []
for line in lines:
    # Extract ISO timestamp
    ts_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+00:00)', line)
    if not ts_match:
        continue
    ts = datetime.strptime(ts_match.group(1), '%Y-%m-%dT%H:%M:%S.%f+00:00')

    # Match failed login
    if 'Failed password' in line:
        m = re.search(r'Failed password for (?:invalid user )?(\S+) from (\S+)', line)
        if m:
            records.append({'timestamp': ts, 'ip': m.group(2), 'user': m.group(1), 'event': 'failed'})
    
    # Match invalid user
    elif 'Invalid user' in line:
        m = re.search(r'Invalid user (\S+) from (\S+)', line)
        if m:
            records.append({'timestamp': ts, 'ip': m.group(2), 'user': m.group(1), 'event': 'invalid_user'})

    # Match successful login
    elif 'Accepted password' in line:
        m = re.search(r'Accepted password for (\S+) from (\S+)', line)
        if m:
            records.append({'timestamp': ts, 'ip': m.group(2), 'user': m.group(1), 'event': 'success'})

# If no records, exit
if not records:
    print("No relevant SSH events found in auth.log.")
else:
    df = pd.DataFrame(records)
    df = df.sort_values('timestamp')
    df = df.set_index('timestamp')

    # Group by window + IP + user
    resampled = df.groupby(['ip', 'user']).resample('1min')

    # Aggregations
    def compute_features(x):
        failed_count = (x['event'] == 'failed').sum()
        invalid_count = (x['event'] == 'invalid_user').sum()
        success_count = (x['event'] == 'success').sum()

        unique_users = x['user'].nunique()
        unique_ips = x['ip'].nunique()

        fail_times = x[x['event'] == 'failed'].index
        if len(fail_times) >= 2:
            intervals = (fail_times[1:] - fail_times[:-1]).total_seconds()
            avg_interval = intervals.mean()
            max_gap = intervals.max()
        else:
            avg_interval = 0
            max_gap = 0

        success_after_fails = int((failed_count > 0) and (success_count > 0))

        return pd.Series({
            'failed_login_count': failed_count,
            'invalid_user_count': invalid_count,
            'success_after_fails': success_after_fails,
            'unique_users_targeted': unique_users,
            'unique_ips_failed_this_user': unique_ips,
            'avg_interval_between_fails': avg_interval,
            'max_attempt_gap': max_gap,
            'fail_success_ratio': failed_count / (success_count + 1e-5),
            'login_hour': x.index[0].hour if len(x) > 0 else -1
        })

    features = resampled.apply(compute_features).reset_index()

    # Save output
    features.to_csv('attack_features_full.csv', index=False)
    print("Features extracted and saved to /mnt/data/bruteforce_features_full.csv")
 
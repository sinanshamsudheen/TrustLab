import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Basic setup
random.seed(42)
np.random.seed(42)

# Define parameters
n_samples = 2000
class_balance = 0.5  # 50% of each class
feature_cols = ['attempts_in_30s', 'unique_users_in_30s', 'invalid_user', 'success_after_fail']

# 1. Generate data for normal traffic (class 0)
n_normal = int(n_samples * class_balance)
print(f"Generating {n_normal} normal records...")

normal_data = []
for _ in range(n_normal):
    # Normal behavior has few attempts in time window (1-3)
    attempts_in_30s = random.randint(1, 3)
    
    # Usually 1-2 unique users
    unique_users_in_30s = min(attempts_in_30s, random.randint(1, 2))
    
    # Very rarely invalid users
    invalid_user = 1 if random.random() < 0.05 else 0
    
    # Often successful
    success_after_fail = 1 if random.random() < 0.8 else 0
    
    normal_data.append({
        'source_ip': f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
        'user': random.choice(['alice', 'bob', 'charlie', 'admin']),
        'event_type': 'success' if success_after_fail else 'failed',
        'timestamp': datetime.now() + timedelta(seconds=random.randint(0, 3600)),
        'attempts_in_30s': attempts_in_30s,
        'unique_users_in_30s': unique_users_in_30s,
        'invalid_user': invalid_user,
        'success_after_fail': success_after_fail,
        'bruteforce': 0  # Class label
    })

# 2. Generate data for brute force traffic (class 1)
n_brute = n_samples - n_normal
print(f"Generating {n_brute} brute force records...")

brute_data = []
for _ in range(n_brute):
    # High number of attempts (5-15)
    attempts_in_30s = random.randint(5, 15)
    
    # Multiple unique users tried
    unique_users_in_30s = random.randint(2, min(5, attempts_in_30s))
    
    # Often invalid users
    invalid_user = 1 if random.random() < 0.7 else 0
    
    # Rarely successful
    success_after_fail = 1 if random.random() < 0.1 else 0
    
    brute_data.append({
        'source_ip': f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
        'user': random.choice(['root', 'admin', 'test', 'user', 'guest']),
        'event_type': 'success' if success_after_fail else 'failed',
        'timestamp': datetime.now() + timedelta(seconds=random.randint(0, 3600)),
        'attempts_in_30s': attempts_in_30s,
        'unique_users_in_30s': unique_users_in_30s,
        'invalid_user': invalid_user,
        'success_after_fail': success_after_fail,
        'bruteforce': 1  # Class label
    })

# 3. Combine data
all_data = normal_data + brute_data
df = pd.DataFrame(all_data)

# 4. Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. Save to CSV
output_file = 'balanced_synthetic_auth_dataset.csv'

if os.path.exists(output_file):
    os.remove(output_file)

df.to_csv(output_file, index=False)

# 6. Print statistics
print("\nDataset statistics:")
print(f"Total records: {len(df)}")
print(f"Bruteforce distribution:\n{df['bruteforce'].value_counts()}")
print(f"\nFeature summary:")
print(df[feature_cols].describe())

print(f"\nSample of normal traffic (class 0):")
print(df[df['bruteforce'] == 0].head(3)[['attempts_in_30s', 'unique_users_in_30s', 'event_type', 'bruteforce']])

print(f"\nSample of brute force traffic (class 1):")
print(df[df['bruteforce'] == 1].head(3)[['attempts_in_30s', 'unique_users_in_30s', 'event_type', 'bruteforce']])

print(f"\n✅ Balanced dataset saved as {output_file}")

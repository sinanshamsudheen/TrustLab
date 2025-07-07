import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Basic setup
random.seed(42)
np.random.seed(42)

n_samples = 2000
class_balance = 0.5
feature_cols = ['attempts_in_30s', 'unique_users_in_30s', 'invalid_user', 'success_after_fail']

n_normal = int(n_samples * class_balance)
n_brute = n_samples - n_normal

print(f"Generating {n_normal} normal records and {n_brute} brute-force records...")

normal_data = []
for _ in range(n_normal):
    base_attempts = random.randint(1, 4)
    attempts_in_30s = int(np.clip(np.random.normal(loc=base_attempts, scale=1.2), 1, 8))

    base_unique = min(base_attempts, random.randint(1, 3))
    unique_users_in_30s = int(np.clip(np.random.normal(loc=base_unique, scale=1.0), 1, attempts_in_30s))

    invalid_user = np.random.choice([0, 1], p=[0.95, 0.05])
    success_after_fail = np.random.choice([0, 1], p=[0.2, 0.8])

    normal_data.append({
        'source_ip': f"192.168.{random.randint(0, 254)}.{random.randint(0, 254)}",
        'user': random.choice(['alice', 'bob', 'charlie', 'admin']),
        'event_type': 'success' if success_after_fail else 'failed',
        'timestamp': datetime.now() + timedelta(seconds=random.randint(0, 3600)),
        'attempts_in_30s': attempts_in_30s,
        'unique_users_in_30s': unique_users_in_30s,
        'invalid_user': invalid_user,
        'success_after_fail': success_after_fail,
        'bruteforce': 0
    })

brute_data = []
for _ in range(n_brute):
    base_attempts = random.randint(5, 15)
    attempts_in_30s = int(np.clip(np.random.normal(loc=base_attempts, scale=2.5), 3, 20))

    base_unique = random.randint(2, 6)
    unique_users_in_30s = int(np.clip(np.random.normal(loc=base_unique, scale=1.5), 2, attempts_in_30s))

    invalid_user = np.random.choice([0, 1], p=[0.3, 0.7])
    success_after_fail = np.random.choice([0, 1], p=[0.9, 0.1])

    brute_data.append({
        'source_ip': f"10.0.{random.randint(0, 254)}.{random.randint(0, 254)}",
        'user': random.choice(['root', 'admin', 'test', 'user', 'guest']),
        'event_type': 'success' if success_after_fail else 'failed',
        'timestamp': datetime.now() + timedelta(seconds=random.randint(0, 3600)),
        'attempts_in_30s': attempts_in_30s,
        'unique_users_in_30s': unique_users_in_30s,
        'invalid_user': invalid_user,
        'success_after_fail': success_after_fail,
        'bruteforce': 1
    })

# Combine and shuffle
df = pd.DataFrame(normal_data + brute_data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save CSV
output_file = 'noisy_balanced_synthetic_auth_dataset.csv'
if os.path.exists(output_file):
    os.remove(output_file)

df.to_csv(output_file, index=False)

# Print stats
print("\n✅ Dataset with added noise saved as:", output_file)
print("Class Distribution:\n", df['bruteforce'].value_counts())
print("\nFeature Summary:")
print(df[feature_cols].describe())

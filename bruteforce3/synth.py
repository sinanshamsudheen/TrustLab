import pandas as pd
import numpy as np
import random
import os

# Config
n_samples = 2000
anomaly_ratio = 0.3  # 30% anomalies
known_users = {
    '192.168.10.15': 'primum',
    '192.168.5.20': 'admin',
    '192.168.100.25': 'service',
}
user_pool = ['primum', 'admin', 'guest', 'test', 'root', 'service', 'unknown']
ip_pool = list(known_users.keys()) + [f'10.0.0.{i}' for i in range(1, 20)]

# Set seed
random.seed(42)
np.random.seed(42)

data = []

for i in range(n_samples):
    is_anomaly = i < int(n_samples * anomaly_ratio)

    # Choose IP and user
    ip = random.choice(ip_pool)
    if is_anomaly:
        # Use wrong user or noise
        user = random.choice([u for u in user_pool if known_users.get(ip, None) != u])
    else:
        user = known_users[ip] if ip in known_users else random.choice(user_pool)

    # Generate features
    attempts = random.randint(20, 35) if is_anomaly else random.randint(6, 7)
    unique_users = random.randint(3, 6) if is_anomaly else random.randint(1, 2)
    invalid_user = 1 if is_anomaly else (1 if random.random() < 0.05 else 0)
    success_after_fail = 1 if (not is_anomaly and random.random() < 0.7) else 0
    true_user = int(user == known_users.get(ip, ''))

    # Optional feature noise
    if random.random() < 0.1:
        attempts += random.randint(-2, 2)
    if random.random() < 0.1:
        unique_users += random.choice([-1, 0, 1])

    # Ensure no negatives
    attempts = max(1, attempts)
    unique_users = max(1, unique_users)

    data.append({
        'attempts_in_60s': attempts,
        'unique_users_in_60s': unique_users,
        'invalid_user': invalid_user,
        'success_after_fail': success_after_fail,
        'true_user': true_user,
        'anomaly': int(is_anomaly)
    })

# Create DataFrame and save
df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

output_file = 'noisy_isolation_features_dataset.csv'
df.to_csv(output_file, index=False)

print(f"✅ Dataset saved as '{output_file}'")
print(df['anomaly'].value_counts())
print(df.head())

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import os

# For reproducibility
random.seed(42)
np.random.seed(42)

fake = Faker()
Faker.seed(42)

# Configuration for balanced labels
NORMAL_IP_COUNT = 100
ENTRIES_PER_NORMAL_IP = 10

ATTACKER_IP_COUNT = 80
ENTRIES_PER_ATTACKER_IP = 30

USERS = ["alice", "bob", "charlie", "dan", "emma"]
INVALID_USERS = ["admin1", "test", "root", "user123", "sanket"]

# Ensure clean output
output_file = "balanced_synthetic_auth_dataset.csv"
if os.path.exists(output_file):
    os.remove(output_file)
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)

# Configuration
NORMAL_IP_COUNT = 100
ENTRIES_PER_NORMAL_IP = 10

ATTACKER_IP_COUNT = 80
ENTRIES_PER_ATTACKER_IP = 30

USERS = ["alice", "bob", "charlie", "dan", "emma"]
INVALID_USERS = ["admin", "test", "root", "guest", "sanket"]

def generate_log_entry(ts, ip, user, event_type, invalid_user, success_after_fail):
    return {
        "timestamp": ts,
        "source_ip": ip,
        "user": user,
        "event_type": event_type,
        "invalid_user": int(invalid_user),
        "success_after_fail": int(success_after_fail)
    }

logs = []
current_time = datetime.now().replace(microsecond=0)

# ✅ Normal IPs
for _ in range(NORMAL_IP_COUNT):
    ip = fake.ipv4()
    ts = current_time
    for i in range(ENTRIES_PER_NORMAL_IP):
        event_type = "success" if random.random() > 0.2 else "failed"
        user = random.choice(USERS)
        logs.append(generate_log_entry(ts, ip, user, event_type, False, event_type == "success"))
        ts += timedelta(seconds=random.randint(5, 30))

# ❌ Attacker IPs
for _ in range(ATTACKER_IP_COUNT):
    ip = fake.ipv4()
    ts = current_time
    fail_users = set()
    for i in range(ENTRIES_PER_ATTACKER_IP):
        if i < 15:
            user = random.choice(INVALID_USERS + USERS)
            is_invalid = user in INVALID_USERS
            fail_users.add(user)
            logs.append(generate_log_entry(ts, ip, user, "failed", is_invalid, False))
        else:
            user = random.choice(list(fail_users)) if fail_users else random.choice(USERS)
            logs.append(generate_log_entry(ts, ip, user, "success", False, True))
        ts += timedelta(seconds=random.randint(1, 6))

# Convert to DataFrame
df = pd.DataFrame(logs)
df = df.sort_values(by="timestamp").reset_index(drop=True)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# Feature 1: attempts_in_30s
def rolling_fail_count(group):
    return (group["event_type"] == "failed").rolling("30s").sum()

df["attempts_in_30s"] = df.groupby("source_ip", group_keys=False).apply(rolling_fail_count)

# Feature 2: unique_users_in_30s
def rolling_unique_users(group):
    return group["user"].rolling("30s").apply(lambda x: len(set(x)), raw=False)

df["unique_users_in_30s"] = df.groupby("source_ip", group_keys=False).apply(rolling_unique_users)

# Fill NaNs
df.fillna(0, inplace=True)
df.reset_index(inplace=True)

# Label: Brute-force if >=5 failed attempts in 30s
df["bruteforce"] = ((df["event_type"] == "failed") & (df["attempts_in_30s"] >= 5)).astype(int)

# Balance the dataset
min_count = df["bruteforce"].value_counts().min()
balanced_df = df.groupby("bruteforce").apply(lambda x: x.sample(min_count)).reset_index(drop=True)

# Save to CSV
balanced_df.to_csv("train_data.csv", index=False)
print("✅ Training data saved as 'train_data.csv'")
print("Label counts:\n", balanced_df["bruteforce"].value_counts())

import pandas as pd
import numpy as np
import random
import os

# Config based on real log analysis
n_samples = 3000
anomaly_ratio = 0.25  # 25% anomalies (more realistic)

# Real user mappings from your environment
known_users = {
    '10.51.1.77': 'primum',        # Your legitimate internal IP
    '192.168.10.15': 'primum',     # Known good IP from config
    '192.168.5.20': 'admin',
    '192.168.100.25': 'service',
}

# Common usernames (legitimate + brute force targets)
user_pool = ['primum', 'admin', 'root', 'guest', 'test', 'service', 'ahmed', 'john', 'oracle', 'mysql', 'postgres', 'ftp']

# IP pools based on your real environment
legitimate_ips = list(known_users.keys())
suspicious_ips = [f'10.129.6.{i}' for i in range(190, 200)]  # Your suspicious IP range
external_ips = [f'103.45.67.{i}' for i in range(1, 10)]     # External attackers

ip_pool = legitimate_ips + suspicious_ips + external_ips

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

data = []

for i in range(n_samples):
    is_anomaly = i < int(n_samples * anomaly_ratio)
    
    if is_anomaly:
        # ANOMALOUS PATTERNS - Based on brute force attacks
        scenario = random.choices([
            'brute_force_invalid_user',     # Like ahmed@10.129.6.192
            'brute_force_valid_user',       # Attacking known users  
            'password_spray',               # Many users, few passwords
            'systematic_attack'             # Automated high-volume
        ], weights=[40, 30, 20, 10])[0]
        
        if scenario == 'brute_force_invalid_user':
            ip = random.choice(suspicious_ips + external_ips)
            user = random.choice(['ahmed', 'john', 'oracle', 'mysql', 'postgres', 'ftp', 'mail'])
            attempts = random.randint(8, 25)        # High attempts like your real logs
            unique_users = random.randint(1, 3)     # Focus on few invalid users
            invalid_user = 1                       # Always invalid
            success_after_fail = 0                 # Never succeed
            
        elif scenario == 'brute_force_valid_user':
            ip = random.choice(suspicious_ips + external_ips)
            user = random.choice(['primum', 'admin', 'root'])  # Target valid users
            attempts = random.randint(10, 30)       # Many attempts
            unique_users = 1                       # Single user focus
            invalid_user = 0                       # Valid username
            success_after_fail = 0                 # Don't succeed (they're attackers)
            
        elif scenario == 'password_spray':
            ip = random.choice(suspicious_ips + external_ips)
            user = random.choice(user_pool)
            attempts = random.randint(15, 40)       # Many attempts
            unique_users = random.randint(8, 15)    # Many different users
            invalid_user = random.choice([0, 1])   # Mix of valid/invalid
            success_after_fail = 0                 # Spray attacks don't succeed
            
        else:  # systematic_attack
            ip = random.choice(suspicious_ips + external_ips)
            user = random.choice(user_pool)
            attempts = random.randint(20, 50)       # Very high attempts
            unique_users = random.randint(10, 20)   # Many users
            invalid_user = random.choice([0, 1])
            success_after_fail = 0
        
    else:
        # NORMAL PATTERNS - Based on your real legitimate usage
        scenario = random.choices([
            'successful_single_login',      # 1 attempt, success (like your scenario 3)
            'user_typo_then_success',      # 2 attempts, success (like your scenario 1)  
            'forgot_password_retry',       # 3-5 attempts, eventual success
            'forgot_password_gave_up',     # 3-5 attempts, gave up (like your scenario 2)
            'admin_maintenance'            # Legitimate admin work
        ], weights=[40, 25, 15, 15, 5])[0]
        
        ip = random.choice(legitimate_ips)  # Normal users come from known IPs
        user = known_users.get(ip, 'primum')  # Use correct user for IP
        
        if scenario == 'successful_single_login':
            # Like your successful login: 1 attempt, immediate success
            attempts = 1
            unique_users = 1
            invalid_user = 0
            success_after_fail = 1           # Success without failures
            
        elif scenario == 'user_typo_then_success':
            # Like your "one wrong password" scenario: ~2 attempts
            attempts = 2
            unique_users = 1
            invalid_user = 0
            success_after_fail = 1           # Success after initial failure
            
        elif scenario == 'forgot_password_retry':
            # User trying multiple times, eventually succeeds
            attempts = random.randint(3, 5)  # Similar to your 3-password scenario
            unique_users = 1
            invalid_user = 0
            success_after_fail = 1           # Eventually succeeds
            
        elif scenario == 'forgot_password_gave_up':
            # Like your "denied after 3 passwords" scenario: 5 attempts, gave up
            attempts = 5                     # Similar to your real 5-attempt pattern
            unique_users = 1
            invalid_user = 0
            success_after_fail = 0           # Gave up, connection closed
            
        else:  # admin_maintenance
            # Legitimate admin doing routine work
            attempts = random.randint(1, 3)
            unique_users = 1
            invalid_user = 0
            success_after_fail = 1
    
    # Calculate true_user flag (whether user matches expected user for IP)
    true_user = int(user == known_users.get(ip, ''))
    
    # Add realistic noise (5% chance of slight variation)
    if random.random() < 0.05:
        attempts += random.choice([-1, 0, 1])
        attempts = max(1, attempts)
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

output_file = 'realistic_ssh_dataset.csv'
df.to_csv(output_file, index=False)

# Also save training-only features (without metadata)
training_features = ['attempts_in_60s', 'unique_users_in_60s', 'invalid_user', 'success_after_fail', 'true_user', 'anomaly']
df_training = df[training_features]
df_training.to_csv('training_features.csv', index=False)

print(f"✅ Realistic dataset saved as '{output_file}'")
print(f"✅ Training features saved as 'training_features.csv'")

print(f"\n📊 Dataset Statistics:")
print(f"Total samples: {len(df)}")
print(f"Normal samples: {len(df[df['anomaly'] == 0])}")
print(f"Anomalous samples: {len(df[df['anomaly'] == 1])}")
print(f"Anomaly ratio: {df['anomaly'].mean():.2%}")

print(f"\n🎯 Scenario Distribution:")
scenario_counts = df.groupby(['anomaly', 'scenario']).size().unstack(fill_value=0)
print(scenario_counts)

print(f"\n📋 Attempts Distribution by Class:")
print("NORMAL (should be 1-5 attempts):")
normal_attempts = df[df['anomaly'] == 0]['attempts_in_60s']
print(f"  Min: {normal_attempts.min()}, Max: {normal_attempts.max()}, Avg: {normal_attempts.mean():.1f}")

print("ANOMALOUS (should be 8+ attempts):")
anomaly_attempts = df[df['anomaly'] == 1]['attempts_in_60s']
print(f"  Min: {anomaly_attempts.min()}, Max: {anomaly_attempts.max()}, Avg: {anomaly_attempts.mean():.1f}")

print(f"\n✅ Training Data Samples:")
print("Normal samples:")
print(df[df['anomaly'] == 0][['attempts_in_60s', 'unique_users_in_60s', 'scenario']].head(3))
print("\nAnomalous samples:")
print(df[df['anomaly'] == 1][['attempts_in_60s', 'unique_users_in_60s', 'scenario']].head(3))

from datetime import datetime, timedelta
import random

base_time = datetime(2025, 6, 16, 1, 45)
lines = []
pid = 3001

# 30 fake users
attack_users = [f"user{i}" for i in range(1, 31)]
attack_ips = [f"192.168.1.{i}" for i in range(10, 20)]

for _ in range(300):
    ip = random.choice(attack_ips)
    user = random.choice(attack_users)
    event_type = 'fail' if random.random() < 0.97 else 'success'

    if event_type == 'fail':
        if random.random() < 0.5:
            line = f"{base_time.isoformat()}+00:00 vm1 sshd[{pid}]: Failed password for invalid user {user} from {ip} port {40000 + pid} ssh2"
        else:
            line = f"{base_time.isoformat()}+00:00 vm1 sshd[{pid}]: Failed password for {user} from {ip} port {40000 + pid} ssh2"
    else:
        line = f"{base_time.isoformat()}+00:00 vm1 sshd[{pid}]: Accepted password for {user} from {ip} port {40000 + pid} ssh2"

    lines.append(line)
    base_time += timedelta(seconds=random.randint(1, 5))
    pid += 1

with open('attack_auth.log', 'w') as f:
    for l in lines:
        f.write(l + "\n")

print("Generated large synthetic attack log: /mnt/data/large_synthetic_attack_auth.log")


base_time = datetime(2025, 6, 16, 3, 0)
lines = []
pid = 4001

# 30 legit users
auth_users = [f"dev{i}" for i in range(1, 31)]
auth_ips = [f"192.168.2.{i}" for i in range(100, 110)]

for _ in range(300):
    ip = random.choice(auth_ips)
    user = random.choice(auth_users)

    line = f"{base_time.isoformat()}+00:00 vm1 sshd[{pid}]: Accepted password for {user} from {ip} port {50000 + pid} ssh2"

    lines.append(line)
    base_time += timedelta(seconds=random.randint(10, 60))
    pid += 1

with open('authentic_auth.log', 'w') as f:
    for l in lines:
        f.write(l + "\n")

print("Generated large synthetic authentic log: /mnt/data/large_synthetic_authentic_auth.log")

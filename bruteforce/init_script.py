import subprocess
import re
from datetime import datetime

# CONFIG
VM_USER = 'primum'  
VM_IP = '192.168.10.15'
LOG_FILE = '/etc/parser_service/core/kafka_logs_output.log'

# IP regex
IP_REGEX = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})')

def parse_line(line):
    parts = line.split()
    if len(parts) < 7:
        return None

    
    outer_ts_str = ' '.join(parts[:3])
    try:
        outer_ts = datetime.strptime(f"{datetime.now().year} {outer_ts_str}", "%Y %b %d %H:%M:%S")
    except Exception:
        outer_ts = None

   
    inner_ts = None
    for part in parts:
        if part.startswith('2025-'):
            try:
                inner_ts = datetime.fromisoformat(part)
                break
            except Exception:
                continue

    # IP
    ip_match = IP_REGEX.search(line)
    ip = ip_match.group(1) if ip_match else None

    # Action + user
    action = None
    user = None
    if 'Failed password' in line:
        action = 'Failed password'
        match = re.search(r'for (invalid user )?(\S+)', line)
        if match:
            user = match.group(2)
    elif 'Accepted password' in line:
        action = 'Accepted password'
        match = re.search(r'for (\S+)', line)
        if match:
            user = match.group(1)

    return {
        'outer_ts': outer_ts,
        'inner_ts': inner_ts,
        'ip': ip,
        'user': user,
        'action': action
    }

def main():
    # Build SSH command
    ssh_cmd = [
        'ssh',
        f'{VM_USER}@{VM_IP}',
        f'tail -Fp {LOG_FILE}'
    ]

    print(f"Connecting to {VM_IP}, following log file {LOG_FILE}...")
    proc = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        for line in proc.stdout:
            line = line.strip()
            if line:
                result = parse_line(line)
                if result:
                    print(result)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        proc.terminate()

if __name__ == "__main__":
    main()

from kafka import KafkaConsumer
from collections import deque
from datetime import datetime, timedelta
import re
import os

# CONFIG
BROKER = '10.130.171.246:9092'
TOPICS = ['web_auth', 'webapt']
RAW_LOG_FILE = '/home/primum/logs/kafka_logs_output.log'
RECENT_LOG_FILE = '/home/primum/logs/kafka_sixty.log'
TIME_WINDOW_SECONDS = 60

# Ensure log directory exists
os.makedirs(os.path.dirname(RAW_LOG_FILE), exist_ok=True)

# Store recent logs in memory
recent_logs = deque()  # List of (arrival_time, log_line)

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=BROKER,
    value_deserializer=lambda m: m.decode('utf-8'),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='auth-consumer-group'
)

print("[*] Listening to Kafka logs...")

with open(RAW_LOG_FILE, 'a') as raw_file:
    for msg in consumer:
        log_line = msg.value.strip()

        # ðŸš« Skip CRON logs
        if 'CRON' in log_line.upper():
            continue

        # Capture current system time as reliable timestamp
        arrival_time = datetime.now()

        # Print and append to raw log
        print(f"[+] Log: {log_line}")
        raw_file.write(log_line + "\n")
        raw_file.flush()

        # Add to deque
        recent_logs.append((arrival_time, log_line))

        # Remove entries older than 60 seconds
        cutoff = arrival_time - timedelta(seconds=TIME_WINDOW_SECONDS)
        while recent_logs and recent_logs[0][0] < cutoff:
            recent_logs.popleft()

        # Save to kafka_sixty.log
        with open(RECENT_LOG_FILE, 'w') as recent_file:
            for _, log in recent_logs:
                recent_file.write(log + "\n")


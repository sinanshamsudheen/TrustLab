from kafka import KafkaConsumer
from collections import deque
from datetime import datetime, timedelta
import re
import os
from .config_loader import Config

# Load configuration
config = Config()

# Get configuration values
BROKER = config.get('kafka.broker')
TOPICS = config.get('kafka.topics')
RAW_LOG_FILE = config.get('paths.logs.raw_log')
RECENT_LOG_FILE = config.get('paths.logs.recent_log')
TIME_WINDOW_SECONDS = config.get('detection.time_window_seconds')
CONSUMER_GROUP = config.get('kafka.consumer_group')

# Ensure log directory exists
os.makedirs(os.path.dirname(RAW_LOG_FILE), exist_ok=True)

# Store recent logs in memory
recent_logs = deque()  # List of (arrival_time, log_line)

# Initialize Kafka Consumer only when run as script
def initialize_kafka():
    print("[*] Initializing Kafka consumer...")
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=BROKER,
        value_deserializer=lambda m: m.decode('utf-8'),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=CONSUMER_GROUP
    )
    print("[*] Listening to Kafka logs...")
    return consumer

# Function to process Kafka logs
def process_kafka_logs():
    consumer = initialize_kafka()
    
    with open(RAW_LOG_FILE, 'a') as raw_file:
        for msg in consumer:
            log_line = msg.value.strip()

            # Skip CRON logs
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

            # Remove entries older than configured time window
            cutoff = arrival_time - timedelta(seconds=TIME_WINDOW_SECONDS)
            while recent_logs and recent_logs[0][0] < cutoff:
                recent_logs.popleft()

            # Save to recent log file
            with open(RECENT_LOG_FILE, 'w') as recent_file:
                for _, log in recent_logs:
                    recent_file.write(log + "\n")
                    
# Only process logs when run as script, not when imported
if __name__ == "__main__":
    process_kafka_logs()


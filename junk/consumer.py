from kafka import KafkaConsumer
import json
import os
from collections import deque

# Settings
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'auth_logs'
LOG_FILE = 'latest_logs.jsonl'
MAX_LOGS = 100  # Keep only last 100 logs

# Create a Kafka consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='log-consumer-group'
)

# Use deque to hold last MAX_LOGS entries
log_buffer = deque(maxlen=MAX_LOGS)

# Load existing logs (optional, if app restarted)
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r') as f:
        for line in f:
            log_buffer.append(json.loads(line.strip()))

print(f"✅ Listening to Kafka topic: {TOPIC_NAME}")

try:
    for msg in consumer:
        log_entry = msg.value
        log_buffer.append(log_entry)

        # Write updated buffer to file
        with open(LOG_FILE, 'w') as f:
            for log in log_buffer:
                f.write(json.dumps(log) + '\n')

        print(f"➕ Log received and written: {log_entry}")
except KeyboardInterrupt:
    print("🛑 Stopped consuming.")

# kafka_producer.py
from kafka import KafkaProducer
import time
import pandas as pd
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

df = pd.read_csv('dataset_phishing.csv')
for i, row in df.iterrows():
    message = {'url': row['url'], 'status': row['status']}
    producer.send('phishing-url-topic', message)
    print(f"Sent: {message}")
    time.sleep(1)  # simulate stream
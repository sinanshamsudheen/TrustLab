# kafka_consumer_predict.py
from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
# import kafka
import numpy as np
import joblib
from urllib.parse import urlparse
import re
import psutil
import os

model = joblib.load('phishing_modelv1.pkl')

consumer = KafkaConsumer(
    'phishing-url-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def extract_url_features(url):
    parsed = urlparse(url)
    return {
        "url_length": len(url),
        "hostname_length": len(parsed.hostname) if parsed.hostname else 0,
        "path_length": len(parsed.path),
        "has_ip": bool(re.match(r"\d{1,3}(\.\d{1,3}){3}", parsed.hostname or '')),
        "has_at_symbol": "@" in url,
        "count_dots": url.count('.'),
        "count_hyphens": url.count('-'),
        "uses_https": parsed.scheme == "https",
        "suspicious_words": sum([kw in url.lower() for kw in ["login", "secure", "account", "bank", "verify"]]),
    }

for message in consumer:
    try:
        data = message.value
        url = data['url']
        
        features = extract_url_features(url)
        features = {
            "url_length": np.int16(features["url_length"]),
            "hostname_length": np.int16(features["hostname_length"]),
            "path_length": np.int16(features["path_length"]),
            "has_ip": bool(features["has_ip"]),
            "has_at_symbol": bool(features["has_at_symbol"]),
            "count_dots": np.int8(features["count_dots"]),
            "count_hyphens": np.int8(features["count_hyphens"]),
            "uses_https": bool(features["uses_https"]),
            "suspicious_words": np.int8(features["suspicious_words"]),
        }

        features_df = pd.DataFrame([features])
        result = 'Phishing' if model.predict(features_df)[0] == 1 else 'Legitimate'
        print(f"URL: {url} --> {result}")

    except Exception as e:
        print(f"Error processing message: {e}")

# import kafka
import numpy as np
import pandas as pd
import joblib
from urllib.parse import urlparse
import re
import psutil
import os

url = input("Enter the URL to check: ")

def print_memory(stage=''):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)
    print(f"RAM Usage [{stage}]: {mem:.2f} MB")

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
print_memory('After Extraction..')

model = joblib.load('phishing_modelv1.pkl')

features_df = pd.DataFrame([features])
result = 'Phishing' if model.predict(features_df)[0] == 1 else 'Legitimate'
print_memory('After Prediction')
print(result)


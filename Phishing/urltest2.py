import numpy as np
import pandas as pd
import joblib
from urllib.parse import urlparse
import re
import psutil
import os
import shap

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

def format_features(raw_features):
    return {
        "url_length": np.int16(raw_features["url_length"]),
        "hostname_length": np.int16(raw_features["hostname_length"]),
        "path_length": np.int16(raw_features["path_length"]),
        "has_ip": bool(raw_features["has_ip"]),
        "has_at_symbol": bool(raw_features["has_at_symbol"]),
        "count_dots": np.int8(raw_features["count_dots"]),
        "count_hyphens": np.int8(raw_features["count_hyphens"]),
        "uses_https": bool(raw_features["uses_https"]),
        "suspicious_words": np.int8(raw_features["suspicious_words"]),
    }

# Load model
model = joblib.load('phishing_modelv1.pkl')

# Load background dataset for SHAP (should match training data format)
background_data = pd.read_csv("shap_background.csv")

# Ensure correct dtypes for SHAP background
background_data = background_data.astype({
    "url_length": np.int16,
    "hostname_length": np.int16,
    "path_length": np.int16,
    "has_ip": bool,
    "has_at_symbol": bool,
    "count_dots": np.int8,
    "count_hyphens": np.int8,
    "uses_https": bool,
    "suspicious_words": np.int8
})

# Create SHAP explainer
explainer = shap.LinearExplainer(model, background_data, feature_perturbation="interventional")

# Extract and format features from input URL
raw_features = extract_url_features(url)
features = format_features(raw_features)
features_df = pd.DataFrame([features])

print_memory('After Feature Extraction')


prediction = model.predict(features_df)[0]
result = 'Phishing' if prediction == 1 else 'Legitimate'

print_memory('After Prediction')


shap_values = explainer(features_df)

top_features = sorted(zip(features_df.columns, shap_values.values[0]), key=lambda x: abs(x[1]), reverse=True)[:3]
print(shap_values)

print(f"\nURL: {url} --> {result}")
print("Top SHAP Contributions:")
for feat, val in top_features:
    direction = "↑" if val > 0 else "↓"
    print(f"  {feat}: {val:.4f} ({direction} risk)")

print(result)

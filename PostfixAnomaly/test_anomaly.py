#!/usr/bin/env python3
"""
Test script for AnomalyPostfix V2
Tests the anomaly detection functionality without requiring Kafka
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path
import yaml
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load configuration
base_dir = Path(__file__).parent.absolute()
config_path = base_dir / "config/config.yaml"

with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)

# Setup paths
MODEL_FILE = str(base_dir / CONFIG['paths']['model'])
SCALER_FILE = str(base_dir / CONFIG['paths']['scaler'])

# Sample test logs
test_logs = [
    # Normal logs
    "Jun 15 08:25:12 mailserver postfix/smtpd[1234]: connect from client.example.com[192.168.1.10]",
    "Jun 15 08:26:33 mailserver postfix/smtp[2345]: 8F3B9ED68: to=<user@example.com>, relay=mail.example.com[10.0.0.1]:25, delay=0.57, status=sent (250 2.0.0 Ok: queued as 7B4D9E7A1)",
    "Jun 15 08:30:01 mailserver postfix/qmgr[3456]: 8F3B9ED68: removed",
    # Potentially anomalous logs
    "Jun 15 03:12:45 mailserver postfix/smtpd[9999]: warning: hostname client-suspicious.com[10.11.12.13] mismatch",
    "Jun 15 03:15:22 mailserver postfix/smtpd[8888]: disconnect from unknown[10.20.30.40] ehlo=1 auth=0/1 quit=1 commands=2/3",
]

class TestAnomalyDetector:
    def __init__(self):
        """Initialize the anomaly detection system"""
        self.load_model()
        print("✅ Test harness initialized")
    
    def load_model(self):
        """Load the trained anomaly detection model"""
        try:
            self.model = joblib.load(MODEL_FILE)
            self.scaler = joblib.load(SCALER_FILE)
            
            # Get feature names from config
            self.selected_features = CONFIG['anomaly']['features']
            
            print(f"✅ Model loaded: {len(self.selected_features)} features")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)
    
    def parse_log(self, raw_log):
        """Extract fields from raw log using basic parsing"""
        parsed_data = {}
        
        # Extract timestamp
        timestamp_match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', raw_log)
        timestamp = timestamp_match.group(1) if timestamp_match else ''
        
        # Extract process
        process_match = re.search(r'postfix/(\w+)', raw_log)
        process = f"postfix/{process_match.group(1)}" if process_match else 'unknown'
        
        # Extract event
        if ':' in raw_log:
            parts = raw_log.split(':')
            if len(parts) > 1:
                event = parts[1].strip().split()[0]
            else:
                event = 'unknown'
        else:
            event = 'unknown'
        
        return {
            "timestamp": timestamp,
            "process": process,
            "event": event,
            "message": raw_log
        }
    
    def extract_features(self, log):
        """Extract features to match those used in anomaly_new.ipynb"""
        features = {}
        service = log.get('process', 'unknown')
        message = str(log.get('message', ''))
        timestamp = log.get('timestamp', '')
        
        # Get mappings from config
        service_map = CONFIG['anomaly']['service_mappings']
        event_map = CONFIG['anomaly']['event_mappings']
        
        # 1. service_encoded
        features['service_encoded'] = service_map.get(service, service_map.get('unknown', 6))
        
        # 2. event_encoded
        event = log.get('event', 'unknown')
        features['event_encoded'] = event_map.get(event.lower(), event_map.get('unknown', 9))
        
        # 3-5. Time-based features
        try:
            dt = datetime.strptime(timestamp + f" {datetime.now().year}", '%b %d %H:%M:%S %Y')
            features['hour'] = dt.hour
            features['minute'] = dt.minute
            features['dayofweek'] = dt.weekday()
        except:
            # Default values if timestamp parsing fails
            features['hour'] = 0
            features['minute'] = 0
            features['dayofweek'] = 0
        
        # 6. msg_len
        features['msg_len'] = len(message)

        return features
    
    def predict_anomaly(self, log):
        """Predict if log is anomalous"""
        try:
            # Extract features
            features = self.extract_features(log)
            
            # Create DataFrame with only the features used by the model
            feature_names = self.selected_features
            df_features = pd.DataFrame([features])
            
            # Ensure the order matches what was used during training
            df_features = df_features[feature_names]
            
            # Scale features
            X_scaled = self.scaler.transform(df_features)
            
            # Predict
            pred = self.model.predict(X_scaled)[0]
            score = self.model.decision_function(X_scaled)[0]
            
            # Get thresholds from config
            high_threshold = CONFIG['anomaly']['threshold']['high']
            medium_threshold = CONFIG['anomaly']['threshold']['medium']
            
            result = {
                "is_anomaly": 1 if pred == -1 else 0,
                "anomaly_score": float(score),
                "extracted_features": features
            }
            
            # Add confidence level for anomalies
            if pred == -1:
                result["confidence"] = "HIGH" if score < high_threshold else "MEDIUM" if score < medium_threshold else "LOW"
                
            return result
        
        except Exception as e:
            return {
                "is_anomaly": 0,
                "error": str(e),
                "extracted_features": features if 'features' in locals() else {}
            }
    
    def run_tests(self):
        """Run tests on sample logs"""
        print("\n🧪 Running tests on sample logs...\n")
        
        for i, log in enumerate(test_logs):
            print(f"Test log #{i+1}:")
            print(f"  {log}")
            
            parsed = self.parse_log(log)
            result = self.predict_anomaly(parsed)
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                if result["is_anomaly"] == 1:
                    confidence = result.get("confidence", "UNKNOWN")
                    print(f"  ❗ ANOMALY DETECTED - Confidence: {confidence}, Score: {result['anomaly_score']:.6f}")
                else:
                    print(f"  ✅ Normal log - Score: {result['anomaly_score']:.6f}")
                
                print(f"  Features: {result['extracted_features']}")
            print()

if __name__ == "__main__":
    detector = TestAnomalyDetector()
    detector.run_tests()

#!/usr/bin/env python3
"""
Test suite for Postfix Anomaly Detection

This script contains tests to verify the functionality of the anomaly detection system.
It tests both the model training and anomaly detection processes.
"""

import os
import sys
import unittest
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.retrain import process_logs, train_model

class TestAnomalyDetection(unittest.TestCase):
    """Test cases for anomaly detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample log files
        self.postfix_log = os.path.join(self.test_dir, "sample_mail.log")
        self.roundcube_log = os.path.join(self.test_dir, "sample_roundcube.log")
        
        # Create sample output directory
        self.output_dir = os.path.join(self.test_dir, "models")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create sample logs
        self._create_sample_logs()
        
    def _create_sample_logs(self):
        """Create sample log files for testing"""
        # Sample Postfix logs
        postfix_entries = [
            "Jul 10 12:34:56 host1 postfix/smtpd[1234]: connect from client.example.com[192.168.1.1]",
            "Jul 10 12:35:01 host1 postfix/smtpd[1234]: disconnect from client.example.com[192.168.1.1]",
            "Jul 10 12:36:12 host1 postfix/cleanup[1235]: message-id=<20210710123612.GA1234@example.com>",
            "Jul 10 12:36:15 host1 postfix/qmgr[1236]: from=<user@example.com>, size=2048, nrcpt=1",
            "Jul 10 12:37:22 host1 postfix/smtp[1237]: to=<recipient@example.org>, relay=mail.example.org[192.168.2.2]:25, status=sent (250 OK)",
        ]
        
        # Sample Roundcube logs
        roundcube_entries = [
            "[10-Jul-2025 13:45:22 +0200]: <s1ab2c3d> Successful login for user@example.com (ID: 123) from 192.168.1.100(X-Real-IP: 203.0.113.1,X-Forwarded-For: 203.0.113.1) in session s1ab2c3d",
            "[10-Jul-2025 13:46:35 +0200]: <e4fg5h6i> Failed login for wrong@example.com from 192.168.1.101 in session e4fg5h6i (error: 401)",
            "[10-Jul-2025 13:47:18 +0200]: <j7kl8m9n> Successful login for admin@example.com (ID: 1) from 192.168.1.102(X-Real-IP: 203.0.113.2,X-Forwarded-For: 203.0.113.2) in session j7kl8m9n",
            "[10-Jul-2025 13:48:42 +0200]: [roundcube] FAILED login for hacker@evil.com from 192.168.1.103",
            "[10-Jul-2025 13:49:55 +0200]: <o0pq1r2s> Successful login for user2@example.com from 192.168.1.104 in session o0pq1r2s",
        ]
        
        # Write to files
        with open(self.postfix_log, 'w') as f:
            f.write('\n'.join(postfix_entries))
            
        with open(self.roundcube_log, 'w') as f:
            f.write('\n'.join(roundcube_entries))
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Clean up files
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.test_dir)
    
    def test_process_logs(self):
        """Test log processing functionality"""
        temp_dir = os.path.join(self.test_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process the sample logs
        features_path = process_logs(self.postfix_log, self.roundcube_log, temp_dir, max_lines=100)
        
        # Check if features file was created
        self.assertTrue(os.path.exists(features_path), "Features file not created")
        
        # Check if the content is valid
        df = pd.read_csv(features_path)
        self.assertGreater(len(df), 0, "No features extracted from logs")
        
        # Check required columns
        required_columns = ["timestamp", "service", "pid", "event", "message"]
        for col in required_columns:
            self.assertIn(col, df.columns, f"Column {col} missing from extracted features")
    
    def test_train_model(self):
        """Test model training functionality"""
        # First process logs to get features
        temp_dir = os.path.join(self.test_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        features_path = process_logs(self.postfix_log, self.roundcube_log, temp_dir, max_lines=100)
        
        # Train a model
        model_paths = train_model(features_path, contamination=0.05, n_estimators=10, output_dir=self.output_dir)
        
        # Check if model files were created
        self.assertTrue(os.path.exists(model_paths["model"]), "Model file not created")
        self.assertTrue(os.path.exists(model_paths["scaler"]), "Scaler file not created")
        
        # Check if the models can be loaded
        model = joblib.load(model_paths["model"])
        scaler = joblib.load(model_paths["scaler"])
        
        # Test if the model is an Isolation Forest
        from sklearn.ensemble import IsolationForest
        self.assertIsInstance(model, IsolationForest, "Model is not an Isolation Forest")
        
        # Test if the scaler is a StandardScaler
        from sklearn.preprocessing import StandardScaler
        self.assertIsInstance(scaler, StandardScaler, "Scaler is not a StandardScaler")
        
        # Check if metrics were returned
        self.assertIn("metrics", model_paths, "Metrics not returned from model training")
        
    def test_anomaly_detection(self):
        """Test actual anomaly detection functionality"""
        # Train a model first
        temp_dir = os.path.join(self.test_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        features_path = process_logs(self.postfix_log, self.roundcube_log, temp_dir, max_lines=100)
        model_paths = train_model(features_path, contamination=0.05, n_estimators=10, output_dir=self.output_dir)
        
        # Load the model and scaler
        model = joblib.load(model_paths["model"])
        scaler = joblib.load(model_paths["scaler"])
        
        # Create a sample feature vector for testing
        # This represents a normal log entry
        normal_features = np.array([[0, 0, 12, 30, 2, 100]])  # service, event, hour, minute, day, msg_len
        
        # Scale the features
        normal_features_scaled = scaler.transform(normal_features)
        
        # Get prediction
        normal_prediction = model.predict(normal_features_scaled)[0]
        normal_score = model.decision_function(normal_features_scaled)[0]
        
        # Create an anomalous feature vector (extreme values)
        anomaly_features = np.array([[100, 100, 3, 59, 6, 9999]])
        
        # Scale the features
        anomaly_features_scaled = scaler.transform(anomaly_features)
        
        # Get prediction
        anomaly_prediction = model.predict(anomaly_features_scaled)[0]
        anomaly_score = model.decision_function(anomaly_features_scaled)[0]
        
        # Check if the predictions make sense (anomaly should have lower score)
        self.assertGreater(normal_score, anomaly_score, 
                          "Anomaly detection failed: normal entry has lower score than anomalous entry")
        
        # Print results for debugging
        print(f"Normal entry prediction: {normal_prediction}, score: {normal_score}")
        print(f"Anomaly entry prediction: {anomaly_prediction}, score: {anomaly_score}")

# Main execution
if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Integration tests for Postfix Anomaly Detection System

This script performs integration testing of the complete anomaly detection pipeline,
from log processing to anomaly detection and service management.
"""

import os
import sys
import unittest
import subprocess
import tempfile
import time
import signal
from datetime import datetime

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.kafka_anomaly_detector import AnomalyDetector  # If available

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete anomaly detection pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample log files
        self.postfix_log = os.path.join(self.test_dir, "sample_mail.log")
        self.roundcube_log = os.path.join(self.test_dir, "sample_roundcube.log")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.models_dir = os.path.join(self.test_dir, "models")
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Create sample logs with normal and anomalous patterns
        self._create_sample_logs()
        
        # Get project root directory
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    def _create_sample_logs(self):
        """Create sample log files for testing, including anomalous entries"""
        # Sample Postfix logs with mostly normal entries and some anomalies
        postfix_entries = [
            # Normal entries
            "Jul 10 12:34:56 host1 postfix/smtpd[1234]: connect from client.example.com[192.168.1.1]",
            "Jul 10 12:35:01 host1 postfix/smtpd[1234]: disconnect from client.example.com[192.168.1.1]",
            "Jul 10 12:36:12 host1 postfix/cleanup[1235]: message-id=<20210710123612.GA1234@example.com>",
            "Jul 10 12:36:15 host1 postfix/qmgr[1236]: from=<user@example.com>, size=2048, nrcpt=1",
            "Jul 10 12:37:22 host1 postfix/smtp[1237]: to=<recipient@example.org>, relay=mail.example.org[192.168.2.2]:25, status=sent (250 OK)",
            
            # Repeat some normal patterns to make dataset larger
            "Jul 10 13:34:56 host1 postfix/smtpd[2234]: connect from client2.example.com[192.168.1.2]",
            "Jul 10 13:35:01 host1 postfix/smtpd[2234]: disconnect from client2.example.com[192.168.1.2]",
            "Jul 10 13:36:12 host1 postfix/cleanup[2235]: message-id=<20210710133612.GA2234@example.com>",
            "Jul 10 13:36:15 host1 postfix/qmgr[2236]: from=<user2@example.com>, size=3048, nrcpt=1",
            "Jul 10 13:37:22 host1 postfix/smtp[2237]: to=<recipient2@example.org>, relay=mail.example.org[192.168.2.2]:25, status=sent (250 OK)",
            
            # Anomalous entries
            "Jul 10 03:14:15 host1 postfix/smtpd[9999]: NOQUEUE: reject: RCPT from unknown[10.0.0.1]: 554 5.7.1 Service unavailable; Client host [10.0.0.1] blocked using zen.spamhaus.org; Blocked - see https://www.spamhaus.org/query/ip/10.0.0.1; from=<spammer@evil.com> to=<victim@example.com> proto=ESMTP helo=<evil.com>",
            "Jul 10 03:15:27 host1 postfix/smtpd[9998]: warning: hostname evil.example.com does not resolve to address 192.168.99.99: Name or service not known",
            "Jul 10 03:16:42 host1 postfix/smtpd[9997]: connect from unknown[192.168.99.99]",
            "Jul 10 03:17:58 host1 postfix/smtpd[9997]: lost connection after AUTH from unknown[192.168.99.99]",
            "Jul 10 03:19:01 host1 postfix/smtpd[9996]: too many errors after AUTH from unknown[192.168.99.98]",
        ]
        
        # Sample Roundcube logs with mostly normal entries and some anomalies
        roundcube_entries = [
            # Normal entries
            "[10-Jul-2025 13:45:22 +0200]: <s1ab2c3d> Successful login for user@example.com (ID: 123) from 192.168.1.100(X-Real-IP: 203.0.113.1,X-Forwarded-For: 203.0.113.1) in session s1ab2c3d",
            "[10-Jul-2025 13:46:35 +0200]: <e4fg5h6i> Failed login for wrong@example.com from 192.168.1.101 in session e4fg5h6i (error: 401)",
            "[10-Jul-2025 13:47:18 +0200]: <j7kl8m9n> Successful login for admin@example.com (ID: 1) from 192.168.1.102(X-Real-IP: 203.0.113.2,X-Forwarded-For: 203.0.113.2) in session j7kl8m9n",
            "[10-Jul-2025 13:49:55 +0200]: <o0pq1r2s> Successful login for user2@example.com from 192.168.1.104 in session o0pq1r2s",
            
            # Repeat some normal patterns
            "[10-Jul-2025 14:45:22 +0200]: <t3uv4w5x> Successful login for user3@example.com (ID: 124) from 192.168.1.105(X-Real-IP: 203.0.113.3,X-Forwarded-For: 203.0.113.3) in session t3uv4w5x",
            "[10-Jul-2025 14:46:35 +0200]: <y6za7b8c> Failed login for wrong2@example.com from 192.168.1.106 in session y6za7b8c (error: 401)",
            "[10-Jul-2025 14:47:18 +0200]: <d9ef0g1h> Successful login for admin@example.com (ID: 1) from 192.168.1.102(X-Real-IP: 203.0.113.2,X-Forwarded-For: 203.0.113.2) in session d9ef0g1h",
            "[10-Jul-2025 14:49:55 +0200]: <i2jk3l4m> Successful login for user2@example.com from 192.168.1.104 in session i2jk3l4m",
            
            # Anomalous entries
            "[10-Jul-2025 03:12:34 +0200]: [roundcube] FAILED login for admin@example.com from 192.168.99.200",
            "[10-Jul-2025 03:13:35 +0200]: [roundcube] FAILED login for admin@example.com from 192.168.99.200",
            "[10-Jul-2025 03:14:36 +0200]: [roundcube] FAILED login for admin@example.com from 192.168.99.200",
            "[10-Jul-2025 03:15:37 +0200]: [roundcube] FAILED login for admin@example.com from 192.168.99.200",
            "[10-Jul-2025 03:16:38 +0200]: [roundcube] FAILED login for admin@example.com from 192.168.99.200",
            "[10-Jul-2025 03:17:39 +0200]: <x9yz0a1b> Failed login for admin@example.com from 192.168.99.201 in session x9yz0a1b (error: 401)",
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
    
    def test_retrain_script(self):
        """Test the retrain.py script with sample logs"""
        # Build the command to run retrain.py
        retrain_script = os.path.join(self.project_root, "src", "retrain.py")
        cmd = [
            "python3", retrain_script,
            f"--postfix-logs={self.postfix_log}",
            f"--roundcube-logs={self.roundcube_log}",
            f"--output-dir={self.models_dir}",
            "--contamination=0.1",  # Higher contamination for our small test set
            "--n-estimators=10",
            f"--temp-dir={self.test_dir}/temp",
            "--max-lines=100"
        ]
        
        # Run the retrain script
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check if the script ran successfully
        self.assertEqual(result.returncode, 0, 
                         f"Retrain script failed with:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        
        # Check if model files were created
        model_file = os.path.join(self.models_dir, "anomaly_det.pkl")
        scaler_file = os.path.join(self.models_dir, "scaler.pkl")
        
        self.assertTrue(os.path.exists(model_file), "Model file not created")
        self.assertTrue(os.path.exists(scaler_file), "Scaler file not created")
        
        print(f"Retrain script output:\n{result.stdout}")
    
    def test_end_to_end_pipeline(self):
        """Test the full pipeline from retraining to detection"""
        # Skip this test in CI environments without full dependencies
        if os.environ.get('CI') == 'true':
            self.skipTest("Skipping end-to-end test in CI environment")
        
        try:
            # First, train a model with our sample data
            self.test_retrain_script()
            
            # Now test if we can load the model and detect anomalies
            # This is simplified since we can't easily test the full service
            # In a real test, you might want to use mock Kafka producers/consumers
            model_file = os.path.join(self.models_dir, "anomaly_det.pkl")
            scaler_file = os.path.join(self.models_dir, "scaler.pkl")
            
            # Try to import required modules
            try:
                import joblib
                from sklearn.ensemble import IsolationForest
                
                # Load the model and scaler
                model = joblib.load(model_file)
                scaler = joblib.load(scaler_file)
                
                # Create a test log entry (similar to what might come from Kafka)
                test_log = "Jul 10 15:34:56 host1 postfix/smtpd[3234]: connect from normal.example.com[192.168.1.10]"
                anomaly_log = "Jul 10 04:14:15 host1 postfix/smtpd[8888]: NOQUEUE: reject: RCPT from unknown[10.0.0.99]: 554 5.7.1 Service unavailable"
                
                # Extract features (simplified, in real code you'd use the full pipeline)
                import re
                service_pattern = re.compile(
                    r"(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+(?P<service>\S+?)\[(?P<pid>\d+)\]:\s+(?P<message>.+)"
                )
                
                # Process normal log
                match = service_pattern.search(test_log)
                if match:
                    msg = match.group("message")
                    event = msg.split(":")[0]
                    hour = int(match.group("time").split(":")[0])
                    minute = int(match.group("time").split(":")[1])
                    dayofweek = 5  # Assuming it's a Friday
                    msg_len = len(msg)
                    
                    # For simplicity, we'll use dummy values for service/event encoding
                    # In a real scenario, you'd use the same encoders used during training
                    features = [[0, 0, hour, minute, dayofweek, msg_len]]
                    
                    # Scale features and get prediction
                    features_scaled = scaler.transform(features)
                    prediction = model.predict(features_scaled)[0]
                    score = model.decision_function(features_scaled)[0]
                    
                    print(f"Normal log prediction: {prediction}, score: {score}")
                    
                # Process anomaly log
                match = service_pattern.search(anomaly_log)
                if match:
                    msg = match.group("message")
                    event = msg.split(":")[0]
                    hour = int(match.group("time").split(":")[0])
                    minute = int(match.group("time").split(":")[1])
                    dayofweek = 5  # Assuming it's a Friday
                    msg_len = len(msg)
                    
                    # Again, using dummy values for encoding
                    features = [[0, 1, hour, minute, dayofweek, msg_len]]
                    
                    # Scale features and get prediction
                    features_scaled = scaler.transform(features)
                    prediction = model.predict(features_scaled)[0]
                    score = model.decision_function(features_scaled)[0]
                    
                    print(f"Anomalous log prediction: {prediction}, score: {score}")
                
                # This is a simplification. In a real test, you'd verify more aspects
                # of the pipeline, possibly by injecting test messages into Kafka.
                
            except ImportError as e:
                self.skipTest(f"Skipping full pipeline test due to missing dependency: {e}")
                
        except Exception as e:
            self.fail(f"End-to-end test failed with error: {str(e)}")

# Main execution
if __name__ == "__main__":
    unittest.main()

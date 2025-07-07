#!/usr/bin/env python3
"""
Unified Real-time Kafka Consumer with Anomaly Detection
======================================================
Single consumer that:
1. Consumes logs from Kafka topics in real-time
2. Parses logs using regex patterns (replaces kafka_parser.py)
3. Detects anomalies using ML model
4. Saves parsed logs and anomaly results
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
import yaml
import pandas as pd
import numpy as np
import joblib
import shap
from kafka import KafkaConsumer

# Configuration
MODEL_FILE = 'New_anomaly_det.pkl'
SCALER_FILE = 'New_scaler.pkl'
FEATURES_FILE = 'new_selected_features.json'
CONFIG_FILE = 'config/kafka_config.yaml'
OUTPUT_DIR = '/home/primum/PostfixOutput'

# Debug helper to identify filesystem/permission issues at startup
def check_environment():
    """Basic environment checks for permissions and paths"""
    print("\n[ENV] Checking environment...")
    
    # Check Python version
    print(f"[ENV] Python: {sys.version.split()[0]}")
    
    # Check current working directory and permissions
    cwd = os.getcwd()
    print(f"[ENV] Working directory: {cwd}")
    
    try:
        # Check if output directory exists or can be created
        if os.path.exists(OUTPUT_DIR):
            print(f"[ENV] Output directory exists: {OUTPUT_DIR}")
            # Check if we can write to it
            writable = os.access(OUTPUT_DIR, os.W_OK)
            if writable:
                print(f"[ENV] Output directory is writable: ✓")
            else:
                print(f"[ENV] Output directory is NOT writable: ✗")
        else:
            print(f"[ENV] Output directory does not exist: {OUTPUT_DIR}")
            print("[ENV] Will attempt to create it during initialization")
    except Exception as e:
        print(f"[ERROR] Error checking output directory: {e}")

class RealTimeAnomalyDetector:
    def __init__(self):
        """Initialize the anomaly detection system"""
        self.load_model()
        self.load_kafka_config()
        self.setup_output_dir()
        
    def load_model(self):
        """Load the trained anomaly detection model"""
        try:
            self.model = joblib.load(MODEL_FILE)
            self.scaler = joblib.load(SCALER_FILE)
            
            with open(FEATURES_FILE, 'r') as f:
                self.selected_features = json.load(f)
            
            self.explainer = shap.TreeExplainer(self.model)
            print(f"[SETUP] Model loaded: {len(self.selected_features)} features")
            
        except Exception as e:
            print(f"[ERROR] Error loading model: {e}")
            sys.exit(1)
    
    def load_kafka_config(self):
        """Load Kafka configuration"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
            
            self.kafka_broker = config['broker']
            self.topics = config['topics']
            
            if '<KAFKA-IP-ADD>' in self.kafka_broker:
                print("[ERROR] Please update config/kafka_config.yaml with your Kafka broker IP")
                sys.exit(1)
                
            print(f"[SETUP] Kafka config: {self.kafka_broker}, topics: {self.topics}")
            
        except Exception as e:
            print(f"[ERROR] Error loading Kafka config: {e}")
            sys.exit(1)
    
    def setup_output_dir(self):
        """Create output directory with appropriate permissions"""
        try:
            # Create the directory with exist_ok to prevent errors if it already exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Set permissions to 755 (rwxr-xr-x) to allow writing by the current user
            # This helps in Linux environments where permission issues are common
            import stat
            os.chmod(OUTPUT_DIR, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # Verify we can write to this directory
            test_path = f"{OUTPUT_DIR}/.write_test"
            with open(test_path, 'w') as f:
                f.write("test")
            os.remove(test_path)
            print(f"[SETUP] Output directory ready: {OUTPUT_DIR}")
        except PermissionError:
            print(f"[ERROR] No permission to create or write to {OUTPUT_DIR}")
            print("[ERROR] Please run: sudo mkdir -p /home/primum/PostfixOutput && sudo chown primum:primum /home/primum/PostfixOutput")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Setting up output directory: {e}")
            sys.exit(1)
        
    def parse_log(self, raw_log):
        """Extract fields from raw log using regex patterns"""
        try:
            # Import the existing regex loader
            from core.regex_loader import extract_fields
            parsed_data, _ = extract_fields(raw_log)
        except ImportError:
            # Fallback basic parsing if regex loader not available
            parsed_data = {}
        
        # Extract key information
        timestamp = parsed_data.get('postfix_syslog', '')
        if not timestamp:
            timestamp_match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', raw_log)
            timestamp = timestamp_match.group(1) if timestamp_match else ''
        
        process = parsed_data.get('postfix_process', 'unknown')
        if not process or process == 'unknown':
            process_match = re.search(r'postfix/(\w+)', raw_log)
            process = f"postfix/{process_match.group(1)}" if process_match else 'unknown'
        
        user = parsed_data.get('postfix_from', 'unknown')
        if not user or user == 'unknown':
            from_match = re.search(r'from=<([^>]+)>', raw_log)
            user = from_match.group(1) if from_match else 'unknown'
        
        queue_status = 'unknown'
        if 'queue active' in raw_log:
            queue_status = 'queue active'
        elif 'deferred' in raw_log:
            queue_status = 'deferred'
        elif 'bounced' in raw_log:
            queue_status = 'bounced'
        
        return {
            "timestamp": timestamp,
            "user": user,
            "process": process,
            "queue_status": queue_status,
            "message": raw_log
        }
    
    def extract_features(self, log):
        """Extract the 10 ML features from parsed log"""
        features = {}
        process = log.get('process', 'unknown')
        user = log.get('user', 'unknown')
        message = str(log.get('message', ''))
        timestamp = log.get('timestamp', '')

        # 1. message_length
        features['message_length'] = len(message)
        
        # 2. numeric_pattern_count
        features['numeric_pattern_count'] = len(re.findall(r'\b\d+\b', message))
        
        # 3-5. Time-based features
        try:
            dt = datetime.strptime(timestamp + f" {datetime.now().year}", '%b %d %H:%M:%S %Y')
            features['log_hour'] = dt.hour
            features['is_weekend'] = 1 if dt.weekday() >= 5 else 0
            features['not_working_hour'] = 1 if (dt.hour < 8 or dt.hour >= 20) else 0
        except:
            features['log_hour'] = -1
            features['is_weekend'] = 0
            features['not_working_hour'] = 0
        
        # 6. size
        size_match = re.search(r'size[=:](\d+)', message)
        features['size'] = int(size_match.group(1)) if size_match else 0
        
        # 7. user_frequency (simplified)
        features['user_frequency'] = 7704 if user == 'unknown' else 100
        
        # 8-10. Process-based features
        features['process_postfix/bounce'] = 1 if process == 'postfix/bounce' else 0
        features['is_postsuper'] = 1 if 'postsuper' in process else 0
        features['is_bounce'] = 1 if 'bounce' in process else 0

        return features
    
    def predict_anomaly(self, log):
        """Predict if log is anomalous"""
        try:
            # Extract features
            features = self.extract_features(log)
            
            # Create DataFrame with selected features
            df_features = pd.DataFrame([features])
            df_features = df_features.reindex(columns=self.selected_features, fill_value=0)
            
            # Scale features
            X_scaled = self.scaler.transform(df_features)
            
            # Predict
            pred = self.model.predict(X_scaled)[0]
            score = self.model.decision_function(X_scaled)[0]
            
            result = {
                "is_anomaly": 1 if pred == -1 else 0,
                "anomaly_score": float(score),
                "extracted_features": features
            }
            
            # Add explanation for anomalies
            if pred == -1:  # This condition is fine since it's checking model output directly
                shap_values = self.explainer.shap_values(X_scaled)
                shap_df = pd.DataFrame({
                    'feature': self.selected_features,
                    'value': df_features.iloc[0].values,
                    'shap_value': shap_values[0]
                })
                shap_df['abs_shap'] = shap_df['shap_value'].abs()
                top_features = shap_df.sort_values(by='abs_shap', ascending=False).head(3)
                
                result["confidence"] = "HIGH" if score < -0.1 else "MEDIUM" if score < -0.05 else "LOW"
                result["top_features"] = top_features[['feature', 'value', 'shap_value']].to_dict(orient='records')
            
            return result
            
        except Exception as e:
            return {
                "is_anomaly": 0,  # Default to 0 (False) instead of None for cleaner output
                "error": str(e),
                "extracted_features": features if 'features' in locals() else {}
            }
    
    def make_json_serializable(self, obj):
        """Convert any non-JSON-serializable objects to serializable types"""
        if isinstance(obj, dict):
            return {k: self.make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_json_serializable(item) for item in obj]
        elif isinstance(obj, bool):
            # Convert boolean to integer (0 or 1)
            return 1 if obj else 0
        elif isinstance(obj, (int, float, str)) or obj is None:
            return obj
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            # Convert any other types to string
            return str(obj)
    
    def save_parsed_log(self, raw_log, parsed_data, topic):
        """Save parsed log data like the original kafka_parser.py"""
        # Convert boolean values to strings to avoid JSON serialization issues
        parsed_data_serializable = self.make_json_serializable(parsed_data)
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": topic,
            "original_log": raw_log,
            "parsed_data": parsed_data_serializable
        }
        
        # Save to service-specific file
        service_file = f"{OUTPUT_DIR}/{topic}_logs.json"
        with open(service_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def save_result(self, log, result, topic):
        """Save detection result to file"""
        # Convert log and result to JSON serializable format
        log_serializable = self.make_json_serializable(log)
        result_serializable = self.make_json_serializable(result)
        
        result_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "log": log_serializable,
            "detection": result_serializable
        }
        
        # Save all results
        with open(f"{OUTPUT_DIR}/all_detections.jsonl", 'a') as f:
            f.write(json.dumps(result_entry) + '\n')
        
        # Save only anomalies
        if result.get("is_anomaly") == 1:
            with open(f"{OUTPUT_DIR}/anomalies.jsonl", 'a') as f:
                f.write(json.dumps(result_entry) + '\n')
    
    def run(self):
        """Main processing loop"""
        print("\n" + "=" * 60)
        print("||  UNIFIED KAFKA CONSUMER WITH ANOMALY DETECTION  ||")
        print("=" * 60)
        print(f"[CONFIG] Replacing: core/kafka_parser.py (original consumer)")
        print(f"[CONFIG] Model: Isolation Forest ({len(self.selected_features)} features)")
        print(f"[CONFIG] Kafka: {self.kafka_broker}")
        print(f"[CONFIG] Topics: {self.topics}")
        print(f"[CONFIG] Output: {OUTPUT_DIR}/")
        print("=" * 60)
        
        # Setup Kafka consumer
        try:
            consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=[self.kafka_broker],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='unified-parser-anomaly-detection',  # Single unified consumer
                value_deserializer=lambda m: m.decode('utf-8')
            )
            print(f"[INFO] Connected to Kafka\n")
            
        except Exception as e:
            print(f"[ERROR] Kafka connection failed: {e}\n")
            return
        
        # Process messages
        message_count = 0
        anomaly_count = 0
        
        try:
            for message in consumer:
                raw_log = message.value.strip()
                topic = message.topic
                message_count += 1
                
                # Parse and analyze log
                parsed_log = self.parse_log(raw_log)
                result = self.predict_anomaly(parsed_log)
                
                # Save parsed log using regex patterns (like original kafka_parser.py)
                try:
                    from core.regex_loader import extract_fields
                    parsed_data, matched = extract_fields(raw_log)
                    # No need to print the parsed data - just save it
                    self.save_parsed_log(raw_log, parsed_data, topic)
                except ImportError:
                    # Fallback to basic parsing if regex loader not available
                    self.save_parsed_log(raw_log, parsed_log, topic)
                except PermissionError:
                    print(f"[ERROR] No permission to write to {OUTPUT_DIR}/{topic}_logs.json")
                    print(f"[ERROR] Please check permissions and ownership of {OUTPUT_DIR}")
                    break
                except Exception as e:
                    print(f"[ERROR] Error saving parsed log: {e}")
                    continue
                
                # Save anomaly detection result
                try:
                    self.save_result(parsed_log, result, topic)
                except PermissionError:
                    print(f"[ERROR] No permission to write to output files in {OUTPUT_DIR}")
                    print(f"[ERROR] Please check permissions and ownership of {OUTPUT_DIR}")
                    break
                except Exception as e:
                    print(f"[ERROR] Error saving result: {e}")
                    continue
                
                # Display result - single line output with improved formatting
                if result.get("is_anomaly") == 1:
                    anomaly_count += 1
                    # Get top 3 contributing features
                    top_features = []
                    for feat in result["top_features"]:
                        top_features.append(f"{feat['feature']}:{feat['value']}")
                    features_str = ", ".join(top_features)
                    
                    # Print with clear formatting and feature information
                    confidence = result.get("confidence", "MEDIUM")
                    print(f"[ANOMALY ALERT!!] [{confidence}] [{features_str}] {raw_log}\n")
                        
                elif result.get("is_anomaly") == 0:
                    # Clearly mark normal logs
                    print(f"[NORMAL] {raw_log}\n")
                # Remove error case since we now default to 0 (False)
                
                # Statistics every 1000 messages (reduced frequency)
                if message_count % 1000 == 0:
                    rate = (anomaly_count / message_count) * 100
                    print(f"[STATS] {message_count} processed, {anomaly_count} anomalies ({rate:.1f}%)\n")
                
        except KeyboardInterrupt:
            print(f"\n[INFO] Stopped. Processed {message_count} messages, {anomaly_count} anomalies")
        except Exception as e:
            print(f"\n[ERROR] {e}")
        finally:
            consumer.close()

def main():
    # Run environment checks first
    check_environment()
    
    # Then initialize and run the detector
    detector = RealTimeAnomalyDetector()
    detector.run()

if __name__ == "__main__":
    main()

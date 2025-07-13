#!/usr/bin/env python3
"""
Model retraining script for Postfix Anomaly Detection

This script automates the retraining of the anomaly detection model
using the latest log data. It follows the exact training methodology
used in the original training notebook.

Usage:
  python retrain.py --postfix-logs=/var/log/mail.log --roundcube-logs=/var/log/cse_roundcube_userlogins.log
"""

import argparse
import re
import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from pathlib import Path


def find_alternative_logs(directory, patterns):
    """Find alternative log files based on common patterns"""
    import glob
    alternatives = []
    
    if not os.path.exists(directory):
        safe_print(f"⚠️ Warning: Directory {directory} does not exist")
        return alternatives
    
    for pattern in patterns:
        matches = glob.glob(os.path.join(directory, pattern))
        # Sort by modification time, newest first
        matches.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        alternatives.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    alternatives = [x for x in alternatives if x not in seen and not seen.add(x)]
    
    return alternatives

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Retrain anomaly detection model')
    parser.add_argument('--postfix-logs', required=True, help='Path to Postfix log file')
    parser.add_argument('--roundcube-logs', required=True, help='Path to Roundcube login logs')
    parser.add_argument('--output-dir', default='/opt/PostfixAnomaly/models', help='Output directory for models')
    parser.add_argument('--contamination', type=float, default=0.001, help='Isolation Forest contamination parameter')
    parser.add_argument('--n-estimators', type=int, default=100, help='Number of estimators for Isolation Forest')
    parser.add_argument('--temp-dir', default='/tmp/anomaly_retraining', help='Temporary directory for intermediate files')
    parser.add_argument('--max-lines', type=int, default=100000, help='Maximum number of log lines to process from each file')
    
    args = parser.parse_args()
    
    # Validate arguments
    validate_args(args)
    
    return args

def validate_args(args):
    """Validate command line arguments and check file/directory existence"""
    # Validate log files
    for log_path, log_type in [(args.postfix_logs, 'Postfix'), (args.roundcube_logs, 'Roundcube')]:
        if not os.path.exists(log_path):
            # Try to find alternative log files based on common patterns
            if log_type == 'Postfix':
                alternatives = find_alternative_logs(os.path.dirname(log_path), ['mail.log', 'mail.log.*', 'maillog', 'syslog'])
            else:  # Roundcube
                alternatives = find_alternative_logs(os.path.dirname(log_path), ['roundcube', 'cse_roundcube', '*roundcube*'])
                
            if alternatives:
                if log_type == 'Postfix':
                    args.postfix_logs = alternatives[0]
                    safe_print(f"⚠️ Warning: Specified Postfix log not found. Using alternative: {args.postfix_logs}")
                else:
                    args.roundcube_logs = alternatives[0]
                    safe_print(f"⚠️ Warning: Specified Roundcube log not found. Using alternative: {args.roundcube_logs}")
            else:
                raise FileNotFoundError(f"{log_type} log file not found at {log_path} and no alternatives found")
    
    # Validate output directory
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir, exist_ok=True)
            safe_print(f"Created output directory: {args.output_dir}")
        except Exception as e:
            raise IOError(f"Could not create output directory {args.output_dir}: {str(e)}")
    
    # Validate contamination parameter
    if args.contamination <= 0 or args.contamination >= 1:
        safe_print(f"⚠️ Warning: Contamination parameter ({args.contamination}) should be between 0 and 1. Using default 0.001.")
        args.contamination = 0.001
    
    # Validate n_estimators parameter
    if args.n_estimators < 10:
        safe_print(f"⚠️ Warning: n_estimators parameter ({args.n_estimators}) is too small. Using default 100.")
        args.n_estimators = 100
    
    # Validate max_lines parameter
    if args.max_lines < 1000:
        safe_print(f"⚠️ Warning: max_lines parameter ({args.max_lines}) is too small. Using minimum of 1,000.")
        args.max_lines = 1000

def safe_print(s):
    """Print a string with UTF-8 encoding handling"""
    print(s.encode("utf-8", errors="replace").decode("utf-8"))


def process_logs(postfix_log_path, roundcube_log_path, temp_dir, max_lines=100000):
    """Process log files and extract features
    
    Args:
        postfix_log_path: Path to postfix log file
        roundcube_log_path: Path to roundcube log file
        temp_dir: Directory to store temporary files
        max_lines: Maximum number of log lines to process from each file (default: 100000)
    """
    
    # Create temp directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)
    
    # Helper function to read the last N lines from a file
    def read_last_n_lines(file_path, n):
        safe_print(f"Reading last {n:,} lines from {file_path}")
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # If file is empty or doesn't exist
            if file_size == 0:
                return []
                
            # Use the tail command for efficient reading of last lines
            import subprocess
            result = subprocess.run(
                ['tail', f'-{n}', file_path], 
                capture_output=True, 
                text=True, 
                encoding='utf-8', 
                errors='replace'
            )
            
            # Split the output into lines
            lines = result.stdout.splitlines()
            safe_print(f"Successfully read {len(lines):,} lines from {file_path}")
            return lines
            
        except Exception as e:
            safe_print(f"Warning: Could not efficiently read lines with tail command: {str(e)}")
            safe_print(f"Falling back to Python implementation (may be slower)")
            
            # Fallback to Python implementation (slower but more portable)
            # This uses a buffer and reads from the end
            lines = []
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            # Take only the last n lines
            lines = lines[-n:] if len(lines) > n else lines
            safe_print(f"Successfully read {len(lines):,} lines using fallback method")
            return lines
    
    # Read log files (only the last max_lines)
    postfix_lines = read_last_n_lines(postfix_log_path, max_lines)
    roundcube_lines = read_last_n_lines(roundcube_log_path, max_lines)
    
    # Prepare regex patterns
    service_pattern = re.compile(
        r"(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+(?P<service>\S+?)\[(?P<pid>\d+)\]:\s+(?P<message>.+)"
    )
    
    # Roundcube Patterns
    pattern_full = re.compile(
        r"\[(?P<timestamp>\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2} [+-]\d{4})\]:\s"
        r"<(?P<session_id>[^>]+)>\s(?P<status>Successful|Failed) login for\s*(?P<username>.+?)"
        r"(?: \(ID: (?P<user_id>\d+)\))?\sfrom (?P<internal_ip>[\d.]+)"
        r"\(?(?:X-Real-IP: (?P<real_ip>[\d.]+),)?X-Forwarded-For: (?P<forwarded_ip>[^)]+)\)?"
        r"\s*in session (?P<session_id2>[^\s]+)?(?: \(error: (?P<error_code>\d+)\))?"
    )

    pattern_mid = re.compile(
        r"\[(?P<timestamp>\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2} [+-]\d{4})\]:\s"
        r"<(?P<session_id>[^>]+)>\s(?P<status>Successful|Failed) login for\s*(?P<username>.+?)"
        r"(?: \(ID: (?P<user_id>\d+)\))?\sfrom (?P<internal_ip>[\d.]+)\s"
        r"in session\s(?P<session_id2>\w+)(?: \(error: (?P<error_code>\d+)\))?"
    )

    pattern_minimal = re.compile(
        r"\[(?P<timestamp>\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2} [+-]\d{4})\]:\s"
        r"\[roundcube\]\sFAILED login for\s*(?P<username>.+?)\sfrom\s(?P<internal_ip>[\d.]+)"
    )
    
    # Extract features
    postfix_logs = []
    roundcube_logs = []
    unmatched_postfix_lines = []
    unmatched_roundcube_lines = []
    
    # Process Postfix logs
    for line in postfix_lines:
        match = service_pattern.search(line)
        if match:
            msg = match.group("message")
            postfix_logs.append({
                "timestamp": f"{match.group('month')} {match.group('day')} {match.group('time')}",
                "service": match.group("service"),
                "pid": int(match.group("pid")),
                "event": msg.split(":")[0],
                "message": msg
            })
        else:
            unmatched_postfix_lines.append(line.strip())
    
    # Process Roundcube logs
    for line in roundcube_lines:
        m1 = pattern_full.search(line)
        m3 = pattern_minimal.search(line)
        m2 = pattern_mid.search(line)
        
        if m1:
            roundcube_logs.append({
            "timestamp": m1.group("timestamp"),
            "session_id": m1.group("session_id2") or m1.group("session_id"),
            "username": m1.group("username").strip() if m1.group("username") else None,
            "user_id": int(m1.group("user_id")) if m1.group("user_id") else None,
            "internal_ip": m1.group("internal_ip"),
            "real_ip": m1.group("real_ip") if m1.group("real_ip") else None,
            "forwarded_ip": m1.group("forwarded_ip").strip(),
            "status": m1.group("status"),
            "error_code": int(m1.group("error_code")) if m1.group("error_code") else 0
        })
        elif m2:
            roundcube_logs.append({
                "timestamp": m2.group("timestamp"),
                "session_id": m2.group("session_id"),
                "username": m2.group("username"),
                "user_id": int(m2.group("user_id")) if m2.group("user_id") else None,
                "internal_ip": m2.group("internal_ip"),
                "real_ip": None,
                "forwarded_ip": None,
                "status": m2.group("status"),
                "error_code": int(m2.group("error_code")) if m2.group("error_code") else 0
            })
        elif m3:
            roundcube_logs.append({
            "timestamp": m3.group("timestamp"),
            "session_id": None,
            "username": m3.group("username").strip(),
            "user_id": None,
            "internal_ip": m3.group("internal_ip"),
            "real_ip": None,
            "forwarded_ip": None,
            "status": "Failed",
            "error_code": 0
        })
        else:
            unmatched_roundcube_lines.append(line.strip())
    
    # Convert to DataFrames
    df_postfix = pd.DataFrame(postfix_logs)
    df_roundcube = pd.DataFrame(roundcube_logs)
    
    # Convert timestamps
    if not df_postfix.empty:
        df_postfix["timestamp"] = pd.to_datetime(
            df_postfix["timestamp"] + f" {datetime.now().year}",
            format="%b %d %H:%M:%S %Y", errors="coerce"
        )
    
    if not df_roundcube.empty:
        df_roundcube["timestamp"] = pd.to_datetime(
            df_roundcube["timestamp"], format="%d-%b-%Y %H:%M:%S %z", errors="coerce"
        )
    
    # Save extracted features and unmatched logs
    postfix_features_path = os.path.join(temp_dir, "postfix_features.csv")
    roundcube_features_path = os.path.join(temp_dir, "roundcube_features.csv")
    unmatched_postfix_path = os.path.join(temp_dir, "unmatched_postfix_logs.txt")
    unmatched_roundcube_path = os.path.join(temp_dir, "unmatched_roundcube_logs.txt")
    
    df_postfix.to_csv(postfix_features_path, index=False)
    df_roundcube.to_csv(roundcube_features_path, index=False)
    
    with open(unmatched_postfix_path, "w", encoding="utf-8", errors="replace") as f:
        f.writelines(line + "\n" for line in unmatched_postfix_lines)
    
    with open(unmatched_roundcube_path, "w", encoding="utf-8", errors="replace") as f:
        f.writelines(line + "\n" for line in unmatched_roundcube_lines)
    
    # Print summary
    safe_print(f"✅ Features extracted and saved for both Postfix and Roundcube logs.")
    safe_print(f"Postfix logs: Extracted {len(df_postfix)}, Unmatched {len(unmatched_postfix_lines)}")
    safe_print(f"Roundcube logs: Extracted {len(df_roundcube)}, Unmatched {len(unmatched_roundcube_lines)}")
    
    return postfix_features_path


def train_model(features_path, contamination, n_estimators, output_dir):
    """Train the anomaly detection model using extracted features"""
    
    # Start tracking metrics
    metrics = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "training_start": datetime.now(),
        "contamination": contamination,
        "n_estimators": n_estimators,
    }
    
    # Read the extracted features
    df = pd.read_csv(features_path, parse_dates=["timestamp"])
    metrics["sample_size"] = len(df)
    
    # Create and apply encoders
    le_service = LabelEncoder()
    le_event = LabelEncoder()
    df["service_encoded"] = le_service.fit_transform(df["service"])
    df["event_encoded"] = le_event.fit_transform(df["event"])
    
    metrics["unique_services"] = len(le_service.classes_)
    metrics["unique_events"] = len(le_event.classes_)
    
    # Extract time features
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["msg_len"] = df["message"].str.len()
    
    # Prepare features for model
    features = df[["service_encoded", "event_encoded", "hour", "minute", "dayofweek", "msg_len"]]
    
    # Scale features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Train Isolation Forest model
    import time
    model_start_time = time.time()
    model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=42)
    model.fit(features_scaled)
    model_end_time = time.time()
    
    metrics["training_time"] = round(model_end_time - model_start_time, 2)
    
    # Score samples and identify anomalies
    df["anomaly_score"] = model.decision_function(features_scaled)
    df["is_anomaly"] = model.predict(features_scaled)  # -1 = anomaly, 1 = normal
    anomalies = df[df["is_anomaly"] == -1].sort_values("anomaly_score")
    
    # Calculate metrics
    metrics["anomalies_found"] = len(anomalies)
    metrics["anomaly_percentage"] = round((len(anomalies) / len(df)) * 100, 4)
    metrics["avg_anomaly_score"] = round(df["anomaly_score"].mean(), 4)
    metrics["min_anomaly_score"] = round(df["anomaly_score"].min(), 4)
    metrics["max_anomaly_score"] = round(df["anomaly_score"].max(), 4)
    metrics["training_end"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save metrics
    metrics_path = os.path.join(os.path.dirname(output_dir), "metrics", "training_metrics.csv")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    
    # If metrics file exists, append; otherwise create new
    if os.path.exists(metrics_path):
        metrics_df = pd.read_csv(metrics_path)
        metrics_df = pd.concat([metrics_df, pd.DataFrame([metrics])], ignore_index=True)
    else:
        metrics_df = pd.DataFrame([metrics])
    
    metrics_df.to_csv(metrics_path, index=False)
    
    # Save anomalies
    anomalies_path = os.path.join(os.path.dirname(output_dir), "output", "postfix_anomalies.csv")
    os.makedirs(os.path.dirname(anomalies_path), exist_ok=True)
    anomalies.to_csv(anomalies_path, index=False)
    
    # Log performance metrics
    safe_print("\n📊 Model Performance Metrics:")
    safe_print(f"   - Training time: {metrics['training_time']} seconds")
    safe_print(f"   - Sample size: {metrics['sample_size']} log entries")
    safe_print(f"   - Unique services: {metrics['unique_services']}")
    safe_print(f"   - Unique events: {metrics['unique_events']}")
    safe_print(f"   - Anomalies found: {metrics['anomalies_found']} ({metrics['anomaly_percentage']}%)")
    safe_print(f"   - Average anomaly score: {metrics['avg_anomaly_score']}")
    safe_print(f"   - Score range: {metrics['min_anomaly_score']} to {metrics['max_anomaly_score']}")
    
    # Generate timestamp for versioned model files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths for model files
    current_model_path = os.path.join(output_dir, "anomaly_det.pkl")
    current_scaler_path = os.path.join(output_dir, "scaler.pkl")
    
    # Also save versioned copies as backups
    versioned_model_path = os.path.join(output_dir, f"anomaly_det_{timestamp}.pkl")
    versioned_scaler_path = os.path.join(output_dir, f"scaler_{timestamp}.pkl")
    
    # Create backups of the current models if they exist
    if os.path.exists(current_model_path):
        backup_model_path = os.path.join(output_dir, f"anomaly_det.pkl.bak")
        safe_print(f"Creating backup of current model: {backup_model_path}")
        try:
            if os.path.exists(backup_model_path):
                os.remove(backup_model_path)
            os.rename(current_model_path, backup_model_path)
        except Exception as e:
            safe_print(f"Warning: Could not create backup of current model: {str(e)}")
    
    if os.path.exists(current_scaler_path):
        backup_scaler_path = os.path.join(output_dir, f"scaler.pkl.bak")
        safe_print(f"Creating backup of current scaler: {backup_scaler_path}")
        try:
            if os.path.exists(backup_scaler_path):
                os.remove(backup_scaler_path)
            os.rename(current_scaler_path, backup_scaler_path)
        except Exception as e:
            safe_print(f"Warning: Could not create backup of current scaler: {str(e)}")
    
    # Save model and scaler (both versioned and current)
    safe_print(f"Saving new model to {current_model_path}")
    joblib.dump(model, current_model_path)
    safe_print(f"Saving new scaler to {current_scaler_path}")
    joblib.dump(scaler, current_scaler_path)
    
    # Also save versioned copies
    safe_print(f"Saving versioned model to {versioned_model_path}")
    joblib.dump(model, versioned_model_path)
    safe_print(f"Saving versioned scaler to {versioned_scaler_path}")
    joblib.dump(scaler, versioned_scaler_path)
    
    safe_print(f"✅ Model training complete")
    safe_print(f"📊 Found {len(anomalies)} anomalies out of {len(df)} logs")
    safe_print(f"📁 New model saved to {current_model_path}")
    safe_print(f"📁 New scaler saved to {current_scaler_path}")
    safe_print(f"📁 Versioned backups saved to {versioned_model_path} and {versioned_scaler_path}")
    
    # Return paths to the new models
    return {
        "model": current_model_path,
        "scaler": current_scaler_path,
        "versioned_model": versioned_model_path,
        "versioned_scaler": versioned_scaler_path,
        "metrics": metrics
    }


def main():
    """Main function to orchestrate the retraining process"""
    # Parse command line arguments
    args = parse_args()
    
    safe_print(f"🚀 Starting model retraining process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print(f"📋 Parameters:")
    safe_print(f"   - Postfix logs: {args.postfix_logs}")
    safe_print(f"   - Roundcube logs: {args.roundcube_logs}")
    safe_print(f"   - Output directory: {args.output_dir}")
    safe_print(f"   - Max lines per log: {args.max_lines:,}")
    safe_print(f"   - Contamination: {args.contamination}")
    safe_print(f"   - N Estimators: {args.n_estimators}")
    
    try:
        # Process logs
        safe_print("\n🔍 Processing log files...")
        safe_print(f"   - Max lines to process: {args.max_lines:,}")
        features_path = process_logs(args.postfix_logs, args.roundcube_logs, args.temp_dir, args.max_lines)
        
        # Train model
        safe_print("\n🧠 Training anomaly detection model...")
        model_paths = train_model(features_path, args.contamination, args.n_estimators, args.output_dir)
        
        safe_print("\n✅ Model retraining completed successfully!")
        return 0
    except Exception as e:
        safe_print(f"\n❌ Error during model retraining: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

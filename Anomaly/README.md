# Unified Kafka Consumer with Anomaly Detection (v2)

## Overview
An improved version of the unified Kafka consumer with real-time anomaly detection, featuring better organization and configuration.

## Improvements in v2
- ✅ **Improved folder structure**: Better organization with separate directories for components
- ✅ **Centralized configuration**: All settings in a single config file
- ✅ **Platform independence**: Works on both Windows and Linux
- ✅ **Enhanced error handling**: Better error messages and handling
- ✅ **Same detection performance**: Same ML model with 6 key features

## Directory Structure
```
v2/
├── config/              # Configuration files
│   └── config.yaml      # Central configuration
├── core/                # Core functionality
│   └── regex_loader.py  # Log parsing patterns
├── features/            # Feature definitions
│   └── selected_features.json  
├── logs/                # Log output directory
├── models/              # ML models
│   ├── anomaly_det.pkl  # Anomaly detection model
│   └── scaler.pkl       # Feature scaler
├── output/              # Results output directory
├── src/                 # Source code
│   └── kafka_anomaly_detector.py  # Main application
├── run.bat              # Run script
└── setup.bat            # Setup script
```

## Setup

1. **Run setup script:**
   ```
   setup.bat
   ```

2. **Check configuration:**
   Edit `config/config.yaml` to update:
   - Kafka broker address
   - Output directory paths
   - Anomaly detection thresholds

3. **Run the detector:**
   ```
   run.bat
   ```

## Configuration (config.yaml)

The configuration file controls all aspects of the detector:

```yaml
# System paths
paths:
  model: models/anomaly_det.pkl
  scaler: models/scaler.pkl
  features: features/selected_features.json
  output_dir: output

# Kafka configuration
kafka:
  broker: "kafka-server:9092" 
  consumer_group: unified-parser-anomaly-detection
  topics:
    - postfix
    - mail_login

# Anomaly detection settings
anomaly:
  threshold:
    high: -0.1
    medium: -0.05
    low: 0
```

## Output Files

- **`output/postfix_logs.json`** - All parsed postfix logs
- **`output/mail_login_logs.json`** - All parsed mail_login logs
- **`output/all_detections.jsonl`** - Every log with anomaly analysis
- **`output/anomalies.jsonl`** - Only detected anomalies with explanations

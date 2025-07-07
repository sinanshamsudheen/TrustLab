# Unified Kafka Consumer with Anomaly Detection (v2)

## Overview
An improved version of the unified Kafka consumer with real-time anomaly detection, featuring better organization and configuration.

## Improvements in v2
- ✅ **Improved folder structure**: Better organization with separate directories for components
- ✅ **Centralized configuration**: All settings in a single config file
- ✅ **Linux optimized**: Fully optimized for Linux environments
- ✅ **Enhanced error handling**: Better error messages and handling
- ✅ **Same detection performance**: Same ML model with 6 key features

## Directory Structure
```
/
├── config/              # Configuration files
│   └── config.yaml      # Central configuration
├── core/                # Core functionality
│   └── regex_loader.py  # Log parsing patterns
├── features/            # Feature definitions
│   └── selected_features.json  
├── linux/               # Linux service files
│   ├── anomalypostfix.service    # Systemd service definition
│   ├── service_manager.sh        # Service management script
│   └── service_status.sh         # Service status checker
├── logs/                # Log output directory
├── models/              # ML models
│   ├── anomaly_det.pkl  # Anomaly detection model
│   └── scaler.pkl       # Feature scaler
├── output/              # Results output directory
├── src/                 # Source code
│   └── kafka_anomaly_detector.py  # Main application
├── run.sh               # Run script
└── setup.sh             # Main setup script
```

## Setup

1. **Run setup script as root (installs to /opt/PostfixAnomaly):**
   ```bash
   sudo ./setup.sh
   ```

2. **Check configuration:**
   Edit `/opt/PostfixAnomaly/config/config.yaml` to update:
   - Kafka broker address
   - Output directory paths
   - Anomaly detection thresholds

3. **Run the detector:**
   ```bash
   # From any directory
   anomalypostfix
   
   # Or from the installation directory
   /opt/PostfixAnomaly/run.sh
   ```

4. **Run as a service (optional):**
   ```bash
   sudo /opt/PostfixAnomaly/linux/service_manager.sh install
   sudo systemctl start anomalypostfix
   ```

5. **Check service status:**
   ```bash
   sudo /opt/PostfixAnomaly/linux/service_status.sh
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

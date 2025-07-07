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

1. **Clone the repository and navigate to the project directory:**
   ```bash
   # Clone the repository
   git clone https://github.com/sinanshamsudheen/TrustLab.git
   
   # Navigate to the PostfixAnomaly directory
   cd TrustLab/PostfixAnomaly
   ```

2. **Install Miniconda and set up Python environment:**
   ```bash
   # Download the Miniconda installer
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   
   # Run the installer (say yes at the last question to initialize Miniconda)
   bash Miniconda3-latest-Linux-x86_64.sh
   
   # Update your current shell session to use Miniconda
   source ~/.bashrc
   
   # Create a Python 3.10.10 environment
   conda create -n py31010 python=3.10.10
   
   # Activate the environment
   conda activate py31010
   ```

3. **Install required packages:**
   ```bash
   # Install Python dependencies from requirements.txt
   pip install -r requirements.txt
   ```

4. **Run setup script:**
   ```bash
   ./setup.sh
   ```

5. **Check configuration:**
   Edit `config/config.yaml` to update:
   - Kafka broker address
   - Output directory paths
   - Anomaly detection thresholds

6. **Run the detector:**
   ```bash
   # Ensure you're in the project directory and your conda environment is activated
   conda activate py31010
   
   # Run the application
   ./run.sh
   ```

7. **Run as a service (optional):**
   ```bash
   # Install the service
   sudo ./linux/service_manager.sh install
   
   # Start the service
   sudo systemctl start anomalypostfix
   ```

8. **Check service status:**
   ```bash
   sudo ./linux/service_status.sh
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
    high: -0.1    # High severity anomaly
    medium: -0.05 # Medium severity anomaly
    low: 0        # Low severity anomaly
```

## Adjusting Model Sensitivity

You can adjust the model's sensitivity without retraining by modifying the threshold values in `config.yaml`. The thresholds determine how the model classifies anomalies based on the anomaly score:

### Threshold Guide

- **Lower values** (more negative) = **Less sensitive**:
  - Fewer events will be flagged as anomalies
  - Reduces false positives
  - Only extremely unusual events will be detected
  - Example: Change `high: -0.1` to `high: -0.2`

- **Higher values** (less negative or positive) = **More sensitive**:
  - More events will be flagged as anomalies
  - May increase false positives
  - Catches more borderline unusual events
  - Example: Change `high: -0.1` to `high: -0.05`

### Recommended Adjustments

1. **For high-traffic environments** with many false positives:
   - Decrease sensitivity by lowering threshold values
   - Example: `high: -0.15, medium: -0.1, low: -0.05`

2. **For critical security environments** where missing anomalies is a concern:
   - Increase sensitivity by raising threshold values
   - Example: `high: -0.05, medium: 0, low: 0.05`

3. **For initial tuning**, make small adjustments (±0.02) and observe the detection rate for a few days before making further changes.

## Output Files

- **`output/postfix_logs.json`** - All parsed postfix logs
- **`output/mail_login_logs.json`** - All parsed mail_login logs
- **`output/all_detections.jsonl`** - Every log with anomaly analysis
- **`output/anomalies.jsonl`** - Only detected anomalies with explanations

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

## Model Retraining

The system includes automated model retraining capabilities to keep the anomaly detection model up-to-date:

1. **Automatic Retraining**:
   ```bash
   # Set up weekly automatic retraining (runs every Sunday at 2:00 AM)
   sudo ./setup_cron.sh
   
   # Change retraining frequency (options: daily, weekly, monthly)
   sudo ./setup_cron.sh monthly
   ```

2. **Manual Retraining**:
   ```bash
   # Manually retrain the model using current log files (default: last 100,000 lines)
   sudo ./retrain_model.sh
   
   # Specify a custom number of lines to process from each log file
   sudo ./retrain_model.sh 50000  # Process last 50,000 lines
   ```

3. **Versioned Models**:
   - Each retraining creates a timestamped model version
   - Models are stored in `/opt/PostfixAnomaly/models/`
   - The system automatically uses the latest model version
   - Previous models are preserved for comparison/rollback

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

3. **Prepare for production use:**
   ```bash
   # Run the make_ready.sh script to prepare the repository
   ./make_ready.sh
   ```
   This script will:
   - Create required directories
   - Remove unnecessary files
   - Set correct file permissions
   - Check for dependencies
   - Validate essential files

4. **Install required packages:**
   ```bash
   # Install Python dependencies from requirements.txt
   pip install -r requirements.txt
   ```

5. **Run setup script:**
   ```bash
   ./setup.sh
   ```

6. **Check configuration:**
   Edit `config/config.yaml` to update:
   - Kafka broker address
   - Output directory paths
   - Anomaly detection thresholds

7. **Run the detector:**
   ```bash
   # Ensure you're in the project directory and your conda environment is activated
   conda activate py31010
   
   # Run the application
   ./run.sh
   ```

8. **Run as a service (optional):**
   ```bash
   # Install the service
   sudo ./linux/service_manager.sh install
   
   # Start the service
   sudo systemctl start anomalypostfix
   ```

9. **Check service status:**
   ```bash
   sudo ./linux/service_status.sh
   ```
   
10. **Set up automatic model retraining (optional):**
   ```bash
   # Set up weekly retraining (default)
   sudo ./setup_cron.sh
   
   # For monthly retraining instead
   sudo ./setup_cron.sh monthly
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

## Advanced Features

### Input Validation
The system now includes robust input validation:

- Automatic detection of alternate log file locations if specified paths are not found
- Validation of configuration parameters with sensible defaults
- Graceful handling of malformed log entries
- Error messages with helpful suggestions for resolution

### Performance Metrics Tracking
The system now tracks and stores model performance metrics:

- Training time and sample size statistics
- Anomaly detection rates and distributions
- Historical performance comparison
- All metrics are stored in `/opt/PostfixAnomaly/metrics/training_metrics.csv`

These metrics can be used to:
- Monitor model quality over time
- Identify when retraining is beneficial
- Compare different parameter configurations
- Detect changes in system behavior

### Backup and Recovery

The system includes a backup and recovery utility for models and configuration:

```bash
# Create a backup
sudo ./backup_restore.sh backup [optional_destination_dir]

# List available backups
sudo ./backup_restore.sh list

# Restore from a backup
sudo ./backup_restore.sh restore /path/to/backup_file.tar.gz
```

Regular backups are recommended before:
- Retraining models
- Updating configuration
- System upgrades

### Testing Suite

A comprehensive testing suite is available in the `tests/` directory:

```bash
# Run all tests
cd /opt/PostfixAnomaly/tests
./run_tests.sh all

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration
```

See the [test documentation](/tests/README.md) for more details on the testing framework.

### Production Deployment

For production deployment, please refer to the [Production Checklist](production_checklist.md) to ensure your system is properly configured and secured for production use.

The checklist covers important aspects such as:
- Pre-installation requirements
- Configuration validation
- Service setup
- Scheduled retraining
- Monitoring
- Backup & recovery
- Security considerations
- Documentation

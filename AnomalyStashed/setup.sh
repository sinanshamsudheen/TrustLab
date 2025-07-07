#!/bin/bash
# Linux setup script for Unified Kafka Anomaly Detection
set -e

# Check directory
if [ ! -f core/regex_loader.py ]; then
  echo "❌ Error: Run this from the parser_service_primum directory"
  exit 1
fi

echo "🔧 Kafka Anomaly Detection Setup"
echo "================================"

# Install Python dependencies
pip install --upgrade pip
pip install kafka-python PyYAML pandas scikit-learn shap joblib numpy

echo "📁 Creating output directory..."
OUTPUT_DIR="/home/primum/PostfixOutput"
echo "Setting up output directory: $OUTPUT_DIR"

# Try creating the directory
mkdir -p $OUTPUT_DIR 2>/dev/null || true

# If failed or if we don't have write permissions, try with sudo
if [ ! -d "$OUTPUT_DIR" ] || [ ! -w "$OUTPUT_DIR" ]; then
    echo "Using sudo to create and set permissions on output directory..."
    sudo mkdir -p $OUTPUT_DIR
    sudo chown $(whoami):$(whoami) $OUTPUT_DIR
    sudo chmod 755 $OUTPUT_DIR
fi

# Verify output directory is writable
if [ -w "$OUTPUT_DIR" ]; then
    echo "✅ Output directory is writable"
else
    echo "❌ ERROR: Output directory is not writable!"
    echo "Please run the following command manually:"
    echo "sudo mkdir -p $OUTPUT_DIR && sudo chown $(whoami):$(whoami) $OUTPUT_DIR && sudo chmod 755 $OUTPUT_DIR"
    exit 1
fi

echo "🔍 Checking model files..."
if [ ! -f New_anomaly_det.pkl ]; then
  echo "❌ Missing New_anomaly_det.pkl"
  echo "Please copy model files from parent directory"
  exit 1
fi
if [ ! -f New_scaler.pkl ]; then
  echo "❌ Missing New_scaler.pkl"
  echo "Please copy model files from parent directory"
  exit 1
fi
if [ ! -f new_selected_features.json ]; then
  echo "❌ Missing new_selected_features.json"
  echo "Please copy model files from parent directory"
  exit 1
fi

echo "✅ Model files found"

# Check Kafka config
if [ ! -f config/kafka_config.yaml ]; then
  echo "❌ Kafka config missing"
  exit 1
fi
if grep -q '<KAFKA-IP-ADD>' config/kafka_config.yaml; then
  echo "⚠️ Please update config/kafka_config.yaml with your Kafka IP"
else
  echo "✅ Kafka config looks good"
fi

echo
echo "🎉 Setup Complete!"
echo "=================="
echo
cat <<EOF
📋 Next Steps:
1. Update config/kafka_config.yaml with your Kafka broker IP
2. Run: python kafka_anomaly_detector.py

📁 Results will be saved to:
   - output/all_detections.jsonl (all logs)
   - output/anomalies.jsonl (only anomalies)
EOF

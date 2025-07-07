#!/bin/bash
# Enhanced run script for Kafka Anomaly Detector
# Ensures proper setup of output directory and permissions
set -e

# Output directory
OUTPUT_DIR="/home/primum/PostfixOutput"

echo "========================================="
echo "Kafka Anomaly Detector - Setup Script"
echo "========================================="

# Verify Kafka config
if grep -q '<KAFKA-IP-ADD>' config/kafka_config.yaml; then
  echo "ERROR: Please update config/kafka_config.yaml with your Kafka IP."
  exit 1
fi

# Make sure output directory exists with proper permissions
echo "Setting up output directory: $OUTPUT_DIR"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory..."
    # Try creating the directory
    mkdir -p $OUTPUT_DIR 2>/dev/null || true
    
    # If failed, try with sudo
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "Directory creation failed, trying with sudo..."
        sudo mkdir -p $OUTPUT_DIR
        sudo chown $(whoami):$(whoami) $OUTPUT_DIR
        sudo chmod 755 $OUTPUT_DIR
    fi
else
    echo "Output directory already exists."
    # Check if we can write to it
    if [ ! -w "$OUTPUT_DIR" ]; then
        echo "WARNING: Cannot write to output directory, fixing permissions..."
        sudo chown $(whoami):$(whoami) $OUTPUT_DIR
        sudo chmod 755 $OUTPUT_DIR
    fi
fi

# Verify output directory is writable
if [ -w "$OUTPUT_DIR" ]; then
    echo "Output directory is writable ✓"
else
    echo "ERROR: Output directory is not writable!"
    echo "Please run the following command manually:"
    echo "sudo mkdir -p $OUTPUT_DIR && sudo chown $(whoami):$(whoami) $OUTPUT_DIR && sudo chmod 755 $OUTPUT_DIR"
    exit 1
fi

# Run the Python script
echo "Starting Kafka Anomaly Detector..."
echo "========================================="
python kafka_anomaly_detector.py

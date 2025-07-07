#!/bin/bash
# AnomalyPostfix V2 Run Script for Linux
echo "Starting AnomalyPostfix V2 Anomaly Detector..."
echo "============================================="
echo

# Define the installation directory
INSTALL_DIR="/opt/PostfixAnomaly"

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "⚠️ Installation directory $INSTALL_DIR not found!"
    echo "Please run setup.sh first to complete the installation."
    exit 1
fi

# Go to the installation directory
cd "$INSTALL_DIR"

echo "Working directory: $(pwd)"
echo

# Go to the src directory
cd "$INSTALL_DIR/src"

echo "Launching Kafka Anomaly Detector..."
echo "Press Ctrl+C to stop the detector"
echo

# Run the detector
python3 kafka_anomaly_detector.py

# Check the exit status
if [ $? -ne 0 ]; then
    echo
    echo "⚠️ Error encountered while running the detector."
    echo "Please check the logs for more information in $INSTALL_DIR/logs"
    exit 1
fi

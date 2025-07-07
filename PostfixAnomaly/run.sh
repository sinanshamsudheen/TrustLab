#!/bin/bash
# AnomalyPostfix V2 Run Script for Linux
echo "Starting AnomalyPostfix V2 Anomaly Detector..."
echo "============================================="
echo

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$SCRIPT_DIR"

# Go to the installation directory
cd "$INSTALL_DIR"

echo "Working directory: $(pwd)"
echo

# Ensure we have proper permissions for output and logs directories
mkdir -p "$INSTALL_DIR/output" "$INSTALL_DIR/logs"
chmod -R 755 "$INSTALL_DIR/output" "$INSTALL_DIR/logs"

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

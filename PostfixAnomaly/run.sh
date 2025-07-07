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

# Activate conda environment
echo "Activating conda environment py31010..."
# Try to find conda.sh in common locations
if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
else
    # If conda.sh not found, try to use conda directly if it's in PATH
    echo "Warning: conda.sh not found in standard locations, trying to use conda directly"
fi
conda activate py31010

# Run the detector
python kafka_anomaly_detector.py

# Check the exit status
if [ $? -ne 0 ]; then
    echo
    echo "⚠️ Error encountered while running the detector."
    echo "Please check the logs for more information in $INSTALL_DIR/logs"
    exit 1
fi

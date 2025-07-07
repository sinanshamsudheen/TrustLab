#!/bin/bash
# AnomalyPostfix V2 Detector Runner Script for Linux

# Get the directory where this script is located and navigate to parent
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"

# Go to the installation directory
cd "$INSTALL_DIR"

echo "Working directory: $(pwd)"
echo

# Activate the conda environment
echo "Activating conda environment py31010..."
source ~/anaconda3/etc/profile.d/conda.sh || source ~/miniconda3/etc/profile.d/conda.sh
conda activate py31010

# Run the detector script
echo "Starting Postfix Anomaly Detector..."
python "$INSTALL_DIR/src/kafka_anomaly_detector.py"

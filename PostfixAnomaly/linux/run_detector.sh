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

# Run the detector script
echo "Starting Postfix Anomaly Detector..."
python "$INSTALL_DIR/src/kafka_anomaly_detector.py"

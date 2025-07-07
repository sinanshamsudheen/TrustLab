#!/bin/bash

# Start the APT monitoring service
PROJECT_NAME="BruteforceAnomaly"
PROJECT_ROOT="/opt/$PROJECT_NAME"

cd "$PROJECT_ROOT"
python3 main.py --monitor >> logs/apt_monitor.log 2>&1 &
echo "APT Monitor started with PID $!"
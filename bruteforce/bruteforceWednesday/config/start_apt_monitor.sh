#!/bin/bash

# Start the APT monitoring service
cd "$(dirname "$0")/.."
python3 main.py --monitor >> logs/apt_monitor.log 2>&1 &
echo "APT Monitor started with PID $!"

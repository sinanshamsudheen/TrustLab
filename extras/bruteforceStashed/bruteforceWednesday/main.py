#!/usr/bin/env python3
"""
Main entry point for the TrustLab SSH Brute Force Detection & APT Correlation System
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_detection():
    """Run the SSH brute force detection"""
    from src.bruteforce_detector import main
    main()

def run_apt_monitor():
    """Run the APT monitoring service"""
    from src.apt_monitor import APTMonitor
    monitor = APTMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TrustLab SSH Brute Force Detection & APT Correlation System")
    parser.add_argument("--monitor", action="store_true", help="Run APT monitoring service")
    parser.add_argument("--detect", action="store_true", help="Run SSH brute force detection")
    
    args = parser.parse_args()
    
    if args.monitor:
        run_apt_monitor()
    elif args.detect:
        run_detection()
    else:
        # Default: run detection
        run_detection()

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
    # When running as a service, set up the cron job for bruteforce detection
    import subprocess
    import os
    from src.apt_monitor import APTMonitor
    
    # Set up cron job for bruteforce detector if not already set up
    try:
        log_dir = os.path.join(project_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Check if cron job already exists
        cron_check = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        
        if "bruteforce_detector" not in cron_check.stdout:
            print("[+] Setting up cron job for bruteforce detector (runs every minute)")
            cron_content = cron_check.stdout.strip()
            
            # Create new cron job
            cron_job = f"* * * * * cd {project_root} && /usr/bin/python3 {project_root}/src/bruteforce_detector.py >> {log_dir}/bruteforce_detector.log 2>&1"
            
            # Add the new cron job to the existing crontab
            if cron_content:
                cron_content = cron_content + "\n" + cron_job
            else:
                cron_content = cron_job
                
            # Write back to crontab
            with open("/tmp/trustlab_cron", "w") as f:
                f.write(cron_content + "\n")
                
            subprocess.run(["crontab", "/tmp/trustlab_cron"])
            print("[+] Cron job added: bruteforce detector will run every minute")
    except Exception as e:
        print(f"[!] Warning: Could not set up cron job: {e}")
        
    # Start the APT monitor
    monitor = APTMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TrustLab SSH Brute Force Detection & APT Correlation System")
    parser.add_argument("--monitor", action="store_true", help="Run APT monitoring service")
    parser.add_argument("--detect", action="store_true", help="Run SSH brute force detection")
    
    args = parser.parse_args()
    
    if args.monitor:
        print("[*] Starting APT monitoring service...")
        print("[*] Setting up cron job for bruteforce detection...")
        run_apt_monitor()
    elif args.detect:
        print("[*] Running SSH bruteforce detection...")
        run_detection()
    else:
        print("[*] No action specified. Use --monitor or --detect")
        print("[*] For production use, run with --monitor and enable systemd service")
        parser.print_help()

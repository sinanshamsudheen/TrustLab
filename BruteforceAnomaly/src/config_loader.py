#!/usr/bin/env python3
"""
Configuration loader for the TrustLab Security System
"""

import os
import yaml
import re

class Config:
    """Configuration manager for the TrustLab Security System"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of Config exists"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration if not already done"""
        if self._initialized:
            return
        
        # Check if the code is running from the installed location
        if os.path.exists("/opt/BruteforceAnomaly"):
            self.project_root = "/opt/BruteforceAnomaly"
        else:
            # Fallback to the development location
            self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.config_path = os.path.join(self.project_root, "config", "config.yaml")
        self.config = {}
        
        self.load_config()
        self._initialized = True
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                
            # Replace ${PROJECT_ROOT} with actual path
            config_str = yaml.dump(config_data)
            config_str = config_str.replace('${PROJECT_ROOT}', self.project_root)
            self.config = yaml.safe_load(config_str)
                
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            # Set some default values if config loading fails
            self.config = {
                "kafka": {
                    "broker": "10.130.171.246:9092",
                    "topics": ["web_auth", "webapt"],
                    "consumer_group": "auth-consumer-group"
                },
                "paths": {
                    "logs": {
                        "base_dir": os.path.join(self.project_root, "logs"),
                        "raw_log": os.path.join(self.project_root, "logs", "kafka_logs_output.log"),
                        "recent_log": os.path.join(self.project_root, "logs", "kafka_sixty.log"),
                        "suspicious_log": os.path.join(self.project_root, "logs", "kafka_suspicious.log"),
                        "apt_log": os.path.join(self.project_root, "logs", "apt_history_test.log"),
                        "monitor_log": os.path.join(self.project_root, "logs", "apt_monitor.log")
                    },
                    "user_data": {
                        "userlist": os.path.join(self.project_root, "config", "userlist.json")
                    },
                    "models": {
                        "bruteforce_model": os.path.join(self.project_root, "artifacts", "bruteforce_model.pkl")
                    }
                },
                "detection": {
                    "time_window_seconds": 60,
                    "suspicious_keywords": [
                        "nmap", "masscan", "hydra", "metasploit"
                    ]
                },
                "monitoring": {
                    "check_interval": 60,
                    "apt_time_window_hours": 24
                }
            }
    
    def get(self, key_path, default=None):
        """
        Get a configuration value using dot notation
        Example: config.get('kafka.broker') returns the broker address
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def __getitem__(self, key):
        """Allow dictionary-like access to top level config items"""
        return self.config.get(key, None)

# Create a global instance
config = Config()

# For testing
if __name__ == "__main__":
    print("Configuration Test:")
    print(f"Kafka Broker: {config.get('kafka.broker')}")
    print(f"Recent Log Path: {config.get('paths.logs.recent_log')}")
    print(f"Monitoring Interval: {config.get('monitoring.check_interval')} seconds")
    print(f"Model Path: {config.get('paths.models.bruteforce_model')}")

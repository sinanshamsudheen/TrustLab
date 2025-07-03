def filter_known_process_logs(logs):
    """
    Remove log entries where 'process' == 'unknown'.
    
    Args:
        logs (list): List of log entries (each is a dict)
        
    Returns:
        list: Filtered list with only known process logs
    """
    filtered_logs = [entry for entry in logs if entry.get("process") != "unknown"]
    return filtered_logs

import json

# Load your logs from file
with open('kafka_logs_cleaned.json', 'r') as f:
    data = json.load(f)

# Apply the filter
cleaned_logs = filter_known_process_logs(data)

# Optionally save to a new file
with open('filtered_logs.json', 'w') as f:
    json.dump(cleaned_logs, f, indent=4)

print(f"Filtered logs count: {len(cleaned_logs)}")

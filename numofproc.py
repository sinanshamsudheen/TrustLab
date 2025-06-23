import json

# Load the JSON logs file
with open('kafka_logs_cleaned.json', 'r') as f:
    data = json.load(f)

# Assuming data is a list of log entries
process_values = set()

for entry in data:
    process = entry.get('process')
    if process is not None:
        process_values.add(process)

# Print unique 'process' values
print(process_values)

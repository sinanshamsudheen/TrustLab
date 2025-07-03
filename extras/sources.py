import json

def extract_sources(filename, source_field):
    sources = set()
    with open(filename, 'r') as file:
        for line in file:
            try:
                log = json.loads(line)
                # Adjust this line based on actual log structure
                source = log.get(source_field)
                if source:
                    sources.add(source)
            except json.JSONDecodeError:
                continue  # skip invalid JSON lines
    return sources

# Example usage
filename = 'kafka_logs_cleaned.json'
source_field = 'service'  # change this based on actual field in your log

unique_sources = extract_sources(filename, source_field)
print("Unique sources sending logs:")
for src in unique_sources:
    print(src)

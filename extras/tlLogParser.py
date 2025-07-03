import json

def clean_logs(raw_log_file, output_file):
    formatted_logs = []
    with open(raw_log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                # Unescape and parse the nested 'message' and 'event.original'
                message_json = json.loads(log_entry.get("message", "{}"))
                event_json = json.loads(log_entry.get("event", {}).get("original", "{}"))

                # Merge and flatten
                clean_log = {
                    "timestamp": message_json.get("timestamp") or event_json.get("timestamp"),
                    "user": message_json.get("from", "unknown"),
                    "host": message_json.get("host", "unknown"),
                    "qid": message_json.get("qid") or event_json.get("qid"),
                    "queue_status": message_json.get("queuestatus", "unknown"),
                    "message": message_json.get("message", ""),
                    "process": message_json.get("process", {}).get("name", "unknown"),
                }
                formatted_logs.append(clean_log)

            except Exception as e:
                print(f"Error parsing line: {e}")

    # Save as new JSON or CSV
    with open(output_file, "w") as out:
        json.dump(formatted_logs, out, indent=4)

    print(f"Saved {len(formatted_logs)} cleaned logs to {output_file}")

clean_logs('kafka_logs.json','kafka_logs_cleaned.json')
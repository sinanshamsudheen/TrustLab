# remove_cron_logs.py

LOG_FILE = "C:/Users/sinan/Documents/kafka_logs_output.log"

def remove_cron_lines(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Keep only lines that do not contain 'CRON' (case-insensitive)
    filtered_lines = [line for line in lines if 'cron' not in line.lower()]

    # Overwrite the file with filtered content
    with open(file_path, 'w') as f:
        f.writelines(filtered_lines)

    print(f"✅ Removed {len(lines) - len(filtered_lines)} CRON log(s).")

if __name__ == "__main__":
    remove_cron_lines(LOG_FILE)

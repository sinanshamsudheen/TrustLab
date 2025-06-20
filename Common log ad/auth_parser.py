
import re
import csv

import re

pattern = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+\d{2}:\d{2})\s+'  # Timestamp
    r'(?P<host>\S+)\s+'
    r'(?:\((?P<process_paren>[\w\-.]+)\)|(?P<process>[\w\-.]+))'                    # Process (with or without parentheses)
    r'(?:\[(?P<pid>\d+)\])?:\s*'                                                   # Optional [PID]
    r'(?P<message>.+)'                                                             # Message
)

tcount=0
count=0
import csv

with open("authuse.txt", "r") as infile, open("parsed_auth.csv", "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Timestamp", "Host", "Process", "PID", "Message"])

    for line in infile:
        match = pattern.match(line)
        tcount+=1
        if match:
            process = match.group("process_paren") or match.group("process")
            writer.writerow([
                match.group("timestamp"),
                match.group("host"),
                process,
                match.group("pid") or "-",
                match.group("message")
            ])
        else:
            print("Unmatched line:", line.strip())
            count+=1

        
print(count)
print(tcount)
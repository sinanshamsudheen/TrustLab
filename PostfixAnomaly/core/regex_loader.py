import os
import yaml
import re

def load_all_patterns():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'regexes'))
    all_patterns = {}

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == 'patterns.yaml':
                with open(os.path.join(root, file), 'r') as f:
                    patterns = yaml.safe_load(f)
                    for category, pats in patterns.items():
                        if category not in all_patterns:
                            all_patterns[category] = []
                        all_patterns[category].extend(pats)
    
    return all_patterns
# This function runs all regex patterns and extracts data
def extract_fields(log_line):
    extracted = {}
    matched_patterns = []
    all_patterns = load_all_patterns() 

    for category, patterns in all_patterns.items():
        for pat in patterns:
            match = re.search(pat['pattern'], log_line)
            if match:
                if match.groupdict():
                    extracted.update(match.groupdict())
                else:
                    extracted[pat['name']] = match.group(1) if match.groups() else match.group(0)
                matched_patterns.append(pat['name'])
                break
   
    # No debug prints needed in production
    return extracted, matched_patterns

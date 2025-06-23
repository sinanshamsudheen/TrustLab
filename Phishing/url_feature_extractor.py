import pandas as pd
import re
import tldextract
import math
from urllib.parse import urlparse
from collections import Counter

def calculate_url_entropy(url):
    """Calculate the entropy of characters in a URL"""
    # Count frequency of each character
    char_counts = Counter(url.lower())
    url_length = len(url)
    
    # Calculate entropy
    entropy = 0
    for count in char_counts.values():
        probability = count / url_length
        entropy -= probability * math.log2(probability)
    
    return entropy

def extract_url_features(url):
    parsed = urlparse(url)
    domain_info = tldextract.extract(url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    
    # Helper function for consecutive character patterns
    def max_consecutive_chars(text, char_type='digit'):
        max_count = 0
        current_count = 0
        for c in text:
            if (char_type == 'digit' and c.isdigit()) or \
               (char_type == 'alpha' and c.isalpha()) or \
               (char_type == 'same' and len(text) > 0 and c == text[0]):
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
                if char_type == 'same':
                    current_count = 1 if c == text[0] else 0
        return max_count
    
    # Count different types of brackets and special chars
    brackets_count = url.count('(') + url.count(')') + url.count('[') + url.count(']') + url.count('{') + url.count('}')
    
    return {
        # Original features
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "has_ip": bool(re.match(r"\d{1,3}(\.\d{1,3}){3}", hostname)),
        "has_at_symbol": "@" in url,
        "count_dots": url.count('.'),
        "count_hyphens": url.count('-'),
        "count_slashes": url.count('/'),
        "count_underscores": url.count('_'),
        "count_question_marks": url.count('?'),
        "count_equals": url.count('='),
        "count_ampersands": url.count('&'),
        "count_digits": sum(c.isdigit() for c in url),
        "count_uppercase": sum(c.isupper() for c in url),
        "count_lowercase": sum(c.islower() for c in url),
        "digit_ratio": sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0,
        "uppercase_ratio": sum(c.isupper() for c in url) / len(url) if len(url) > 0 else 0,
        "special_char_count": sum(not c.isalnum() and c not in './-_:?' for c in url),
        "subdomain_count": len(hostname.split('.')) - 2 if len(hostname.split('.')) > 2 else 0,
        "max_segment_length": max([len(segment) for segment in hostname.split('.')] + [0]),
        "avg_segment_length": sum(len(segment) for segment in hostname.split('.')) / len(hostname.split('.')) if hostname else 0,
        "url_entropy": calculate_url_entropy(url),
        "hostname_entropy": calculate_url_entropy(hostname) if hostname else 0,
        "path_entropy": calculate_url_entropy(path) if path else 0,
        "uses_https": parsed.scheme == "https",
        "suspicious_words": sum([kw in url.lower() for kw in ["login", "secure", "account", "bank", "verify"]]),
        
        # 15 NEW NUMERICAL FEATURES
        "count_percent": url.count('%'),  # URL encoding indicator
        "count_semicolons": url.count(';'),
        "count_colons": url.count(':'),
        "count_brackets": brackets_count,
        "count_plus": url.count('+'),
        "count_asterisk": url.count('*'),
        "path_depth": len([p for p in path.split('/') if p]),  # Directory depth
        "query_params": len([p for p in query.split('&') if p]) if query else 0,
        "max_consecutive_digits": max_consecutive_chars(url, 'digit'),
        "max_consecutive_letters": max_consecutive_chars(url, 'alpha'),
        "hostname_digit_ratio": sum(c.isdigit() for c in hostname) / len(hostname) if hostname else 0,
        "path_digit_ratio": sum(c.isdigit() for c in path) / len(path) if path else 0,
        "domain_length": len(domain_info.domain) if domain_info.domain else 0,
        "tld_length": len(domain_info.suffix) if domain_info.suffix else 0,
        "vowel_consonant_ratio": sum(c.lower() in 'aeiou' for c in url) / sum(c.isalpha() for c in url) if sum(c.isalpha() for c in url) > 0 else 0,
        "unique_char_ratio": len(set(url.lower())) / len(url) if len(url) > 0 else 0,
        "numeric_domain_ratio": sum(c.isdigit() for c in hostname.replace('.', '')) / len(hostname.replace('.', '')) if hostname.replace('.', '') else 0,
        "shortening_service": int(any(service in hostname.lower() for service in ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly'])),
        "suspicious_tld": int(domain_info.suffix.lower() in ['tk', 'ml', 'ga', 'cf', 'click', 'download', 'zip'] if domain_info.suffix else 0),
        
        # Keep original non-numerical features
        # "domain": domain_info.domain,
        # "suffix": domain_info.suffix
    }

def process_csv_and_extract_features(csv_path, url_column="url"):
    df = pd.read_csv(csv_path)
    feature_rows = df[url_column].apply(lambda x: extract_url_features(str(x)))
    feature_df = pd.DataFrame(feature_rows.tolist())
    combined_df = pd.concat([df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    return combined_df

df = process_csv_and_extract_features("URLdataset.csv", url_column="url")
# df2 = df.drop('Unnamed: 0', axis=1)
print(df.head(5))
df.to_csv("phishing_with_features_final.csv", index=False)
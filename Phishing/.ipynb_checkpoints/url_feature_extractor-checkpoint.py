import pandas as pd
import re
import tldextract
from urllib.parse import urlparse

def extract_url_features(url):
    parsed = urlparse(url)
    domain_info = tldextract.extract(url)

    return {
        "url_length": len(url),
        "hostname_length": len(parsed.hostname) if parsed.hostname else 0,
        "path_length": len(parsed.path),
        "has_ip": bool(re.match(r"\d{1,3}(\.\d{1,3}){3}", parsed.hostname or '')),
        "has_at_symbol": "@" in url,
        "count_dots": url.count('.'),
        "count_hyphens": url.count('-'),
        "count_slashes": url.count('/'),
        "uses_https": parsed.scheme == "https",
        "suspicious_words": sum([kw in url.lower() for kw in ["login", "secure", "account", "bank", "verify"]]),
        "domain": domain_info.domain,
        "suffix": domain_info.suffix
    }

def process_csv_and_extract_features(csv_path, url_column="url"):
    df = pd.read_csv(csv_path)
    feature_rows = df[url_column].apply(lambda x: extract_url_features(str(x)))
    feature_df = pd.DataFrame(feature_rows.tolist())
    combined_df = pd.concat([df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    return combined_df

# Example usage:
df = process_csv_and_extract_features("URLdataset.csv", url_column="url")
df.to_csv("phishing_with_features.csv", index=False)

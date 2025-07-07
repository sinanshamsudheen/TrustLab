import numpy as np
import pandas as pd
import joblib
from urllib.parse import urlparse
import re
import shap
import math
import tldextract
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# Define the exact column order from training
EXPECTED_COLUMNS = [
    'url_length', 'hostname_length', 'path_length', 'query_length',
    'has_ip', 'has_at_symbol', 'count_dots', 'count_hyphens',
    'count_slashes', 'count_underscores', 'count_question_marks',
    'count_equals', 'count_ampersands', 'count_digits', 'count_uppercase',
    'count_lowercase', 'digit_ratio', 'uppercase_ratio',
    'special_char_count', 'subdomain_count', 'max_segment_length',
    'avg_segment_length', 'url_entropy', 'hostname_entropy', 'path_entropy',
    'uses_https', 'suspicious_words', 'count_percent', 'count_semicolons',
    'count_colons', 'count_brackets', 'count_plus', 'count_asterisk',
    'path_depth', 'query_params', 'max_consecutive_digits',
    'max_consecutive_letters', 'hostname_digit_ratio', 'path_digit_ratio',
    'domain_length', 'tld_length', 'vowel_consonant_ratio',
    'unique_char_ratio', 'numeric_domain_ratio', 'shortening_service',
    'suspicious_tld'
]

def calculate_url_entropy(url):
    """Calculate the entropy of characters in a URL"""
    if not url:
        return 0
    char_counts = Counter(url.lower())
    url_length = len(url)
    
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
        if not text:
            return 0
        max_count = 0
        current_count = 0
        for c in text:
            if (char_type == 'digit' and c.isdigit()) or (char_type == 'alpha' and c.isalpha()):
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        return max_count
    
    # Count different types of brackets and special chars
    brackets_count = url.count('(') + url.count(')') + url.count('[') + url.count(']') + url.count('{') + url.count('}')
    
    return {
        # Length features
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "domain_length": len(domain_info.domain) if domain_info.domain else 0,
        "tld_length": len(domain_info.suffix) if domain_info.suffix else 0,
        
        # Count features
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
        "special_char_count": sum(not c.isalnum() and c not in './-_:?' for c in url),
        "count_percent": url.count('%'),
        "count_semicolons": url.count(';'),
        "count_colons": url.count(':'),
        "count_brackets": brackets_count,
        "count_plus": url.count('+'),
        "count_asterisk": url.count('*'),
        "suspicious_words": sum([kw in url.lower() for kw in ["login", "secure", "account", "bank", "verify"]]),
        
        # Ratio features
        "digit_ratio": sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0,
        "uppercase_ratio": sum(c.isupper() for c in url) / len(url) if len(url) > 0 else 0,
        "hostname_digit_ratio": sum(c.isdigit() for c in hostname) / len(hostname) if hostname else 0,
        "path_digit_ratio": sum(c.isdigit() for c in path) / len(path) if path else 0,
        "vowel_consonant_ratio": sum(c.lower() in 'aeiou' for c in url) / sum(c.isalpha() for c in url) if sum(c.isalpha() for c in url) > 0 else 0,
        "unique_char_ratio": len(set(url.lower())) / len(url) if len(url) > 0 else 0,
        "numeric_domain_ratio": sum(c.isdigit() for c in hostname.replace('.', '')) / len(hostname.replace('.', '')) if hostname.replace('.', '') else 0,
        
        # Structure features
        "subdomain_count": len(hostname.split('.')) - 2 if len(hostname.split('.')) > 2 else 0,
        "max_segment_length": max([len(segment) for segment in hostname.split('.')] + [0]),
        "avg_segment_length": sum(len(segment) for segment in hostname.split('.')) / len(hostname.split('.')) if hostname else 0,
        "path_depth": len([p for p in path.split('/') if p]),
        "query_params": len([p for p in query.split('&') if p]) if query else 0,
        "max_consecutive_digits": max_consecutive_chars(url, 'digit'),
        "max_consecutive_letters": max_consecutive_chars(url, 'alpha'),
        
        # Entropy features
        "url_entropy": calculate_url_entropy(url),
        "hostname_entropy": calculate_url_entropy(hostname),
        "path_entropy": calculate_url_entropy(path),
        
        # Boolean features (convert to int for consistency)
        "has_ip": int(bool(re.match(r"\d{1,3}(\.\d{1,3}){3}", hostname))),
        "has_at_symbol": int("@" in url),
        "uses_https": int(parsed.scheme == "https"),
        "shortening_service": int(any(service in hostname.lower() for service in ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly'])),
        "suspicious_tld": int(domain_info.suffix.lower() in ['tk', 'ml', 'ga', 'cf', 'click', 'download', 'zip'] if domain_info.suffix else 0),
    }

def format_features(raw_features):
    formatted = {}
    
    # Integer features
    int_cols = ['url_length', 'hostname_length', 'path_length', 'query_length',
                'count_dots', 'count_hyphens', 'count_slashes', 'count_underscores',
                'count_question_marks', 'count_equals', 'count_ampersands', 
                'count_digits', 'count_uppercase', 'count_lowercase',
                'special_char_count', 'subdomain_count', 'max_segment_length',
                'suspicious_words', 'count_percent', 'count_semicolons', 
                'count_colons', 'count_brackets', 'count_plus', 'count_asterisk',
                'path_depth', 'query_params', 'max_consecutive_digits',
                'max_consecutive_letters', 'domain_length', 'tld_length',
                'has_ip', 'has_at_symbol', 'uses_https', 'shortening_service', 'suspicious_tld']
    
    for col in int_cols:
        if col in raw_features:
            formatted[col] = int(raw_features[col])
    
    # Float features
    float_cols = ['digit_ratio', 'uppercase_ratio', 'avg_segment_length',
                  'url_entropy', 'hostname_entropy', 'path_entropy',
                  'hostname_digit_ratio', 'path_digit_ratio', 
                  'vowel_consonant_ratio', 'unique_char_ratio', 'numeric_domain_ratio']
    
    for col in float_cols:
        if col in raw_features:
            formatted[col] = float(raw_features[col])
    
    return formatted

def sanity_check_prediction(url, features_df, probability):
    """Perform basic sanity checks on the prediction"""
    warnings = []
    
    # Check for obviously legitimate domains
    legitimate_domains = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 
                         'facebook.com', 'youtube.com', 'wikipedia.org', 'github.com']
    
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    
    for domain in legitimate_domains:
        if domain in hostname.lower():
            if probability[1] > 0.5:  # Phishing probability > 50%
                warnings.append(f"WARNING: {hostname} contains '{domain}' but predicted as phishing ({probability[1]:.2%})")
    
    # Check for basic legitimacy indicators
    if parsed.scheme == 'https' and len(hostname) < 50 and '.' in hostname:
        if probability[1] > 0.8:  # Very high phishing probability
            warnings.append(f"WARNING: URL appears legitimate but high phishing score ({probability[1]:.2%})")
    
    return warnings

def validate_features(features_df):
    """Validate extracted features for sanity"""
    issues = []
    
    # Check for impossible values
    for col in features_df.columns:
        val = features_df[col].iloc[0]
        
        # Check for negative values where they shouldn't exist
        if col.startswith('count_') or col.endswith('_length') or col in ['subdomain_count', 'path_depth']:
            if val < 0:
                issues.append(f"Negative value for {col}: {val}")
        
        # Check for ratio values outside [0, 1]
        if col.endswith('_ratio') and col != 'vowel_consonant_ratio':
            if val < 0 or val > 1:
                issues.append(f"Invalid ratio for {col}: {val}")
    
    return issues

def analyze_url(url):
    """Analyze a single URL and return the prediction results"""
    # Load model and scaler
    model = joblib.load('models/logistic_model.pkl')
    scaler = joblib.load('models/scaler.pkl')
    
    # Extract and format features from input URL
    raw_features = extract_url_features(url)
    features = format_features(raw_features)
    
    # Create DataFrame with features in the exact order expected by the model
    features_df = pd.DataFrame([features])
    
    # Ensure all expected columns are present
    missing_cols = set(EXPECTED_COLUMNS) - set(features_df.columns)
    if missing_cols:
        print(f"Warning: Missing columns: {missing_cols}")
        for col in missing_cols:
            features_df[col] = 0
    
    # Reorder columns to match training data
    features_df = features_df.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
    
    # Validate features
    validation_issues = validate_features(features_df)
    if validation_issues:
        print(f"\n=== FEATURE VALIDATION ISSUES ===")
        for issue in validation_issues:
            print(f"  {issue}")
    
    # Scale features for prediction
    features_scaled = scaler.transform(features_df)
    features_scaled_df = pd.DataFrame(features_scaled, columns=EXPECTED_COLUMNS)
    
    # Make prediction
    probability = model.predict_proba(features_scaled)[0]
    phishing_prob = probability[1]  # Probability of being phishing
    
    # Perform sanity check
    warnings = sanity_check_prediction(url, features_df, probability)
    if warnings:
        print(f"\n=== SANITY CHECK WARNINGS ===")
        for warning in warnings:
            print(f"  {warning}")
    
    # Apply threshold
    prediction = 1 if phishing_prob >= 0.5 else 0
    result = 'Phishing' if prediction == 1 else 'Legitimate'
    
    # SHAP explanation
    background_data = pd.read_csv("data/shap_background.csv", index_col=0)
    explainer = shap.LinearExplainer(model, background_data)
    shap_values = explainer(features_scaled_df)
    shap_explanation = sorted(zip(features_scaled_df.columns, shap_values.values[0]), 
                          key=lambda x: abs(x[1]), reverse=True)[:3]
    
    return {
        'url': url,
        'prediction': result,
        'probability': phishing_prob,
        'confidence': max(phishing_prob, 1-phishing_prob),
        'shap_explanation': shap_explanation
    }

def display_results(result):
    """Display the analysis results for a single URL"""
    print(f"\n{'='*50}")
    print(f"URL: {result['url']}")
    print(f"Prediction: {result['prediction']}")
    print(f"Phishing Probability: {result['probability']:.4f}")
    print(f"Confidence: {result['confidence']:.2%}")
    
    print(f"\nTop 3 Feature Contributions (SHAP):")
    for feat, val in result['shap_explanation']:
        direction = "↑ Phishing" if val > 0 else "↓ Legitimate"
        print(f"  {feat}: {val:.4f} ({direction})")

if __name__ == "__main__":
    print("Phishing URL Detection Tool")
    print("==========================")
    print("Enter URLs (separate multiple URLs by commas):")
    
    user_input = input("> ")
    
    if not user_input.strip():
        print("No URLs entered. Exiting.")
        exit()
    
    # Split the input by commas and strip whitespace
    urls = [url.strip() for url in user_input.split(',') if url.strip()]
    
    if not urls:
        print("No valid URLs entered. Exiting.")
        exit()
    
    # Single URL case
    if len(urls) == 1:
        print("\nAnalyzing URL...")
        result = analyze_url(urls[0])
        display_results(result)
    
    # Multiple URLs case
    else:
        print(f"\nAnalyzing {len(urls)} URLs...")
        
        # Load models only once for efficiency
        print("Loading model and scaler...")
        model = joblib.load('models/logistic_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        background_data = pd.read_csv("data/shap_background.csv", index_col=0)
        
        results = []
        for i, url in enumerate(urls):
            print(f"Processing URL {i+1}/{len(urls)}: {url}")
            try:
                result = analyze_url(url)
                results.append(result)
                display_results(result)
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
        
        # Summary
        phishing_count = sum(1 for r in results if r['prediction'] == 'Phishing')
        legitimate_count = len(results) - phishing_count
        
        print(f"\n{'='*50}")
        print(f"SUMMARY: Analyzed {len(results)} URLs")
        print(f"Phishing: {phishing_count} ({phishing_count/len(results):.1%})")
        print(f"Legitimate: {legitimate_count} ({legitimate_count/len(results):.1%})")
import numpy as np
import pandas as pd
import joblib
import shap
import os
import re
import string
from sklearn.preprocessing import StandardScaler

# Load the model and preprocessors
try:
    model = joblib.load("models/spam_model.pkl")
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    scaler = joblib.load("models/extra_features_scaler.pkl")
    extra_feature_names = joblib.load("models/extra_feature_names.pkl")
    background_data = np.load("models/shap_background_data.npy")
    print("All model artifacts loaded successfully!")
except FileNotFoundError as e:
    print(f"Error loading model artifacts: {e}")
    print("Please run the training notebook first to generate all required files.")
    exit(1)

# Memory tracking removed

# Define the same stopwords used in training
manual_stopwords = set("""
a about above after again against all am an and any are aren't as at be because been before being below between 
both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further 
had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i 
i'd i'll i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on 
once only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some 
such than that that's the their theirs them themselves then there there's these they they'd they'll they're they've 
this those through to too under until up very was wasn't we we'd we'll we re we've were weren't what what's when when's 
where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours 
yourself yourselves
""".split())

def clean_text(text):
    """Clean text exactly as done in training"""
    text = str(text).lower()                               # Lowercase
    text = re.sub(r'\n', ' ', text)                        # Remove newlines
    text = re.sub(r'http\S+|www.\S+', '', text)            # Remove URLs
    text = re.sub(r'<.*?>', '', text)                      # Remove HTML tags
    text = re.sub(r'\d+', '', text)                        # Remove numbers
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()               # Remove extra whitespace
    return text

def extract_features(text):
    """Extract the same features used in training"""
    words = text.lower().split()
    total_words = len(words)
    stopword_count = sum(1 for word in words if word in manual_stopwords)
    
    return pd.Series({
        'text_length': len(text),
        'word_count': total_words,
        'sentence_count': text.count('.') + text.count('!') + text.count('?'),
        'punctuation_count': sum([1 for char in text if char in '.,!?;:']),
        'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0,
        'unique_word_count': len(set(words)),
        'stopword_ratio': stopword_count / total_words if total_words > 0 else 0,
        'avg_word_len': np.mean([len(word) for word in words]) if words else 0,
    })

def test_email(email_text):
    # Process the email exactly as in training
    # Step 1: Extract features from ORIGINAL text (before cleaning)
    original_text_features = extract_features(email_text)
    extra_features_df = pd.DataFrame([original_text_features])

    # Step 2: Clean the text for TF-IDF
    cleaned_text = clean_text(email_text)

    # Step 3: Extract TF-IDF features
    X_tfidf = vectorizer.transform([cleaned_text])

    # Step 4: Scale the extra features
    extra_features_scaled = scaler.transform(extra_features_df)

    # Step 5: Combine features exactly as in training
    X_combined = np.hstack([X_tfidf.toarray(), extra_features_scaled])

    # Make prediction
    prediction = model.predict(X_combined)[0]
    probabilities = model.predict_proba(X_combined)[0]
    result = "Spam" if prediction == 1 else "Ham"

    # Display results
    print(f"\nEmail Analysis Results:")
    print(f"Text: \"{email_text[:100]}{'...' if len(email_text) > 100 else ''}\"")
    print(f"Prediction: {result}")
    print(f"Confidence: Ham={probabilities[0]:.3f}, Spam={probabilities[1]:.3f}")

    # Feature breakdown
    # print(f"\nFeature Analysis:")
    # print(f"Text Features (extracted from original text):")
    # for feature_name, value in original_text_features.items():
    #     scaled_value = extra_features_scaled[0][list(original_text_features.index).index(feature_name)]
    #     print(f"  {feature_name}: {value} (scaled: {scaled_value:.4f})")

    # Top TF-IDF features
    print(f"\nTop TF-IDF Features:")
    tfidf_features = X_tfidf.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    non_zero_indices = np.where(tfidf_features > 0)[0]

    if len(non_zero_indices) > 0:
        top_tfidf = sorted([(feature_names[i], tfidf_features[i]) for i in non_zero_indices], 
                          key=lambda x: x[1], reverse=True)[:10]
        for feat, val in top_tfidf:
            print(f"  '{feat}': {val:.4f}")
    else:
        print("  No significant TF-IDF features found")

    # SHAP explanation
    print(f"\nSHAP Explanation:")
    try:
        explainer = shap.Explainer(model, background_data)
        shap_values = explainer(X_combined)
        
        # Get all feature names
        tfidf_names = list(vectorizer.get_feature_names_out())
        all_feature_names = tfidf_names + extra_feature_names
        
        # Get top contributing features
        feature_importance = np.abs(shap_values.values[0])
        top_indices = np.argsort(feature_importance)[-5:][::-1]
        
        print("Top 5 SHAP Contributions:")
        for idx in top_indices:
            if idx < len(all_feature_names):
                feat_name = all_feature_names[idx]
                shap_val = shap_values.values[0][idx]
                direction = "→ Spam" if shap_val > 0 else "→ Ham"
                print(f"  {feat_name}: {shap_val:.4f} {direction}")
                
    except Exception as e:
        print(f"SHAP analysis failed: {e}")

# Test with different email examples
if __name__ == "__main__":
    message = input("Enter an email: ")
    test_email(message)
    # print("=== Testing Spam Email ===")
    # spam_email = "Congratulations! You have won $1000! Click here to claim your prize: http://fake-lottery.com. Act now, limited time offer!"
    # test_email(spam_email)
    
    # print("\n" + "="*50)
    # print("=== Testing Ham Email ===")
    # ham_email = "Hi John, I hope you're doing well. Could we schedule a meeting for next Tuesday to discuss the project timeline? Let me know what works for you. Best regards, Sarah"
    # test_email(ham_email)

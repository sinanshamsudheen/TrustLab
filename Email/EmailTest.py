import numpy as np
import pandas as pd
import joblib
import re
import string

# Load model artifacts
print("Loading model...")
model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")
scaler = joblib.load("extra_features_scaler.pkl")
print("Model loaded successfully!")

# Define stopwords used in training
manual_stopwords = set("""
a about above after again against all am an and any are aren't as at be because been before being below between 
both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further 
had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i 
i'd i'll i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on 
once only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some 
such than that that's the their theirs them themselves then there there's these they they'd they'll they're they've 
this those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's 
where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours 
yourself yourselves
""".split())

def clean_text(text):
    """Clean text for TF-IDF vectorization"""
    text = str(text).lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_features(text):
    """Extract extra features from text"""
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

def predict_email(email_text):
    """Predict if email is spam or ham"""
    # Extract features from original text
    original_features = extract_features(email_text)
    extra_features_df = pd.DataFrame([original_features])
    
    # Clean text for TF-IDF
    cleaned_text = clean_text(email_text)
    X_tfidf = vectorizer.transform([cleaned_text])
    
    # Scale extra features
    extra_features_scaled = scaler.transform(extra_features_df)
    
    # Combine features
    X_combined = np.hstack([X_tfidf.toarray(), extra_features_scaled])
    
    # Make prediction
    prediction = model.predict(X_combined)[0]
    probabilities = model.predict_proba(X_combined)[0]
    
    return prediction, probabilities

# Test examples
test_examples = [
    "Congratulations! You have won $1000000! Click here to claim your prize now!",
    "Hi John, can you please send me the report by Friday? Thanks, Sarah",
    "URGENT: Your account will be suspended unless you update your payment information immediately!",
    "Meeting reminder: We have our weekly team meeting tomorrow at 2 PM in conference room B."
]

print("\nTesting with example emails:")
print("=" * 50)

for i, email in enumerate(test_examples, 1):
    prediction, probabilities = predict_email(email)
    result = "SPAM" if prediction == 1 else "HAM"
    
    print(f"\nExample {i}:")
    print(f"Email: {email[:50]}...")
    print(f"Prediction: {result}")
    print(f"Confidence - Ham: {probabilities[0]:.3f}, Spam: {probabilities[1]:.3f}")

# Interactive mode
while True:
    print("\n" + "=" * 50)
    email_input = input("\nEnter email text to classify (or 'quit' to exit): ")
    
    if email_input.lower() == 'quit':
        break
    
    try:
        prediction, probabilities = predict_email(email_input)
        result = "SPAM" if prediction == 1 else "HAM"
        
        print(f"\nPrediction: {result}")
        print(f"Confidence - Ham: {probabilities[0]:.3f}, Spam: {probabilities[1]:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")

print("Thanks for using the spam detector!")


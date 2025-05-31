import numpy as np
import pandas as pd
import joblib
import shap
import psutil
import os
import re
import string

# Load the model and vectorizer
model = joblib.load("email_spam_model.pkl")
vectorizer = joblib.load("email_vectorizer.pkl")

def print_memory(stage=''):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)
    print(f"RAM Usage [{stage}]: {mem:.2f} MB")

email_input = input("Enter the email text to check: ")

def clean_text(text):
    text = str(text).lower()                               # Lowercase
    text = re.sub(r'\n', ' ', text)                        # Remove newlines
    text = re.sub(r'http\S+|www.\S+', '', text)            # Remove URLs
    text = re.sub(r'<.*?>', '', text)                      # Remove HTML tags
    text = re.sub(r'\d+', '', text)                        # Remove numbers
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()               # Remove extra whitespace
    return text

email_text = clean_text(email_input)

print_memory("Before Vectorization")
X_input_vec = vectorizer.transform([email_text])
X_input_df = pd.DataFrame(X_input_vec.toarray(), columns=vectorizer.get_feature_names_out())
print_memory("After Vectorization")

prediction = model.predict(X_input_vec)[0]
result = "Spam" if prediction == 1 else "Ham"
print_memory("After Prediction")

background_data = pd.read_csv("email_shap_background.csv")

explainer = shap.Explainer(model, background_data, algorithm="linear")

shap_values = explainer(X_input_df)

top_features = sorted(zip(X_input_df.columns, shap_values.values[0]), key=lambda x: abs(x[1]), reverse=True)[:5]

print(f"\nEmail: \"{email_text[:100]}...\" --> {result}")
print("\nTop SHAP Contributions:")

for feat, val in top_features:
    direction = "↑" if val > 0 else "↓"
    print(f"  {feat}: {val:.4f} ({direction} spam likelihood)")


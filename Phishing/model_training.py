import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

# Load and label the dataset
df = pd.read_csv("dataset_phishing.csv")
df['label'] = df['status'].apply(lambda x: 1 if x == "phishing" else 0)

# Prepare features and labels
urls = df['url'].tolist()
y = df['label'].values

# TF-IDF Vectorizer (char-level)
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=1000)
X = vectorizer.fit_transform(urls).toarray()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Handle class imbalance
scale_pos_weight = (len(y_train) - sum(y_train)) / max(sum(y_train), 1)

# Initialize XGBoost model
model = xgb.XGBClassifier(
    scale_pos_weight=scale_pos_weight,
    eval_metric='logloss',
    objective='binary:logistic',
    max_depth=6,
    learning_rate=0.1,
    n_estimators=100,
    use_label_encoder=False
)

# Train the model
model.fit(X_train_scaled, y_train)

# Predict
y_pred = model.predict(X_test_scaled)
y_score = model.predict_proba(X_test_scaled)[:, 1]

# Precision-Recall Curve
precision, recall, thresholds = precision_recall_curve(y_test, y_score)
idx = np.argmax(recall >= 0.99) if any(recall >= 0.99) else len(recall) - 1
high_recall_precision = precision[idx]

# Report
print(f"Precision at {recall[idx]:.2%} recall: {high_recall_precision:.4f}")
print(classification_report(y_test, y_pred))

import joblib
joblib.dump(model, 'phishing_lr_model.pkl')
joblib.dump(vectorizer, 'phishing_vectorizer.pkl')

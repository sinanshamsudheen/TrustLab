# kafka_consumer_predict.py
from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load model + vectorizer
model = joblib.load('phishing_lr_model.pkl')
vectorizer = joblib.load('phishing_vectorizer.pkl')

consumer = KafkaConsumer(
    'phishing-url-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    data = message.value
    url = data['url']
    features = vectorizer.transform([url])
    prediction = model.predict(features)[0]
    print(f"URL: {url} | Prediction: {'Phishing' if prediction == 1 else 'Legit'}")

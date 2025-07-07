# Phishing Detection System

A machine learning-based system to detect phishing URLs.

## Project Structure

```
├── data/                  # Dataset files
│   ├── phishing_with_features_final.csv
│   ├── shap_background.csv
│   └── URLdataset.csv
│
├── models/                # Trained model artifacts
│   ├── logistic_model.pkl
│   ├── phishing_modelv1.pkl
│   └── scaler.pkl
│
├── notebooks/             # Jupyter notebooks
│   ├── final_training.ipynb
│   └── junk.ipynb
│
├── utils/                 # Utility scripts
│   └── url_feature_extractor.py
│
├── main.py                # Main application script
└── requirements.txt       # Project dependencies
```

## Usage

Run the main script:

```bash
python main.py
```

When prompted, enter a URL to check if it's legitimate or a phishing attempt.

## Features

The system extracts various features from URLs including:
- Length-based features
- Character distribution
- Domain properties
- Path structure
- Special character counts
- And more

## Dependencies

See `requirements.txt` for the list of dependencies.

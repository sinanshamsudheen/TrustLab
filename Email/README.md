# Email Spam Detection Project

This project implements a machine learning model to classify emails as spam or ham (non-spam). It uses text features and additional engineered features to achieve high accuracy and provides explainable predictions using SHAP values.

## Features

- **Text Classification**: Uses TF-IDF vectorization to analyze email content
- **Feature Engineering**: Extracts additional features like text length, word count, etc.
- **Explainability**: Utilizes SHAP values to explain model decisions
- **Interactive Analysis**: Command-line interface to analyze any email message
- **Model Metrics**: Provides confidence scores and key feature analysis

## Project Structure

- **Main.py**: The main application file for analyzing and classifying emails
- **requirements.txt**: Lists all required Python dependencies with specific versions
- **data/**: Contains datasets used for training and testing
  - `spam_Emails_data.csv`: Main dataset containing labeled emails
  - `email_shap_background.csv`: Background data for SHAP explanations
- **models/**: Contains all trained model artifacts
  - `spam_model.pkl`: The trained classifier model
  - `tfidf_vectorizer.pkl`: TF-IDF vectorizer for text processing
  - `extra_features_scaler.pkl`: Scaler for additional email features
  - `extra_feature_names.pkl`: Names of the additional features
  - `shap_background_data.npy`: Background data for SHAP explainability
- **notebooks/**: Contains Jupyter notebooks for model training and experimentation
  - `final_training.ipynb`: The notebook used to train the final spam detection model

## Installation

1. Clone this repository or download the project files
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the main application:
   ```
   python Main.py
   ```

2. Enter an email message when prompted to analyze it.

3. Review the analysis results:
   - Classification (Spam or Ham)
   - Confidence scores
   - Top TF-IDF features that influenced the prediction
   - SHAP explanation highlighting the most important features

Example output:
```
Email Analysis Results:
Text: "Hi John, I hope you're doing well. Could we schedule a meeting for next Tuesday..."
Prediction: Ham
Confidence: Ham=0.982, Spam=0.018

Top TF-IDF Features:
  'schedule': 0.3421
  'meeting': 0.2987
  'tuesday': 0.2654
  'hope': 0.2143
  'well': 0.1998

SHAP Explanation:
Top 5 SHAP Contributions:
  stopword_ratio: -0.1243 → Ham
  text_length: -0.0987 → Ham
  tuesday: -0.0876 → Ham
  meeting: -0.0654 → Ham
  schedule: -0.0432 → Ham
```

## Retraining the Model

To retrain the model with new data or different parameters:

1. Ensure your training data is in the correct format and placed in the `data/` directory
2. Open the notebook in Jupyter:
   ```
   jupyter notebook notebooks/final_training.ipynb
   ```
3. Adjust hyperparameters or feature engineering steps as needed
4. Run all cells in the notebook to:
   - Train the model
   - Evaluate performance
   - Save model artifacts to the `models/` directory

## Model Details

- **Algorithm**: The primary model is a Logistic Regression classifier
- **Feature Processing**:
  - Text features: TF-IDF vectorization (max 5000 features)
  - Additional features: 8 engineered features (scaled with StandardScaler)
- **Performance**: Achieves high accuracy and F1-score on the test dataset
- **Explainability**: Uses SHAP (SHapley Additive exPlanations) for transparent predictions

## Requirements

All dependencies are listed in `requirements.txt` with their specific versions:
- joblib (1.4.2)
- numpy (1.24.3)
- pandas (1.5.3)
- scikit-learn (1.2.2)
- shap (0.47.2)

## License

This project is provided for educational and research purposes.

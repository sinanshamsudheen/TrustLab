import pandas as pd
import json
import re
from datetime import datetime
import joblib
from sklearn.preprocessing import StandardScaler
import shap

# Load model & scaler
model = joblib.load('anomaly_model.pkl')
scaler = joblib.load('anomaly_scaler.pkl')
# SHAP explainer
explainer = shap.TreeExplainer(model)

def extract_features_from_log(log):
    features = {}
    process = log.get('process', 'unknown')
    user = log.get('user', 'unknown')
    message = str(log.get('message', ''))
    queue_status = log.get('queue_status', 'unknown')
    qid = log.get('qid', 'unknown')
    timestamp = log.get('timestamp', '')

    features['qid'] = qid
    features['is_pickup'] = 1 if 'pickup' in process else 0
    features['is_cleanup'] = 1 if 'cleanup' in process else 0
    features['is_qmgr'] = 1 if 'qmgr' in process else 0
    features['is_bounce'] = 1 if 'bounce' in process else 0
    features['is_postsuper'] = 1 if 'postsuper' in process else 0

    features['queue_active'] = 1 if queue_status == 'queue active' else 0
    features['queue_unknown'] = 1 if queue_status == 'unknown' else 0
    features['queue_deferred'] = 1 if queue_status == 'deferred' else 0
    features['queue_bounced'] = 1 if queue_status == 'bounced' else 0

    features['size'] = int(re.search(r'size=(\d+)', message).group(1)) if re.search(r'size=(\d+)', message) else 0
    features['nrcpt'] = int(re.search(r'nrcpt=(\d+)', message).group(1)) if re.search(r'nrcpt=(\d+)', message) else 0
    features['has_from_email'] = 1 if 'from=<' in message else 0
    features['has_to_email'] = 1 if 'to=<' in message else 0
    features['has_message_id'] = 1 if 'message-id=' in message else 0
    features['has_removed'] = 1 if 'removed' in message else 0
    features['has_error'] = 1 if any(w in message.lower() for w in ['error', 'fail', 'timeout', 'reject']) else 0

    try:
        dt = datetime.strptime(timestamp + f" {datetime.now().year}", '%b %d %H:%M:%S %Y')
        features['log_hour'] = dt.hour
        features['not_working_hour'] = 1 if (dt.hour < 8 or dt.hour >= 20) else 0
        features['is_weekend'] = 1 if dt.weekday() >= 5 else 0
    except:
        features['log_hour'] = -1
        features['not_working_hour'] = 0
        features['is_weekend'] = 0

    features['message_length'] = len(message)
    features['unique_words'] = len(set(message.lower().split()))
    features['contains_warning'] = 1 if 'warning' in message.lower() else 0
    features['contains_connection'] = 1 if any(w in message.lower() for w in ['connection', 'connect', 'disconnect']) else 0
    features['contains_status'] = 1 if 'status' in message.lower() else 0
    features['contains_relay'] = 1 if 'relay' in message.lower() else 0
    features['contains_delivered'] = 1 if 'delivered' in message.lower() else 0
    features['contains_held'] = 1 if 'held' in message.lower() else 0
    features['numeric_pattern_count'] = len(re.findall(r'\b\d+\b', message))

    features['user_is_unknown'] = 1 if user == 'unknown' else 0
    features['user_frequency'] = 1  # Placeholder

    features['process_postfix/bounce'] = 1 if process == 'postfix/bounce' else 0
    features['process_postfix/cleanup'] = 1 if process == 'postfix/cleanup' else 0
    features['process_postfix/pickup'] = 1 if process == 'postfix/pickup' else 0
    features['process_postfix/postsuper'] = 1 if process == 'postfix/postsuper' else 0
    features['process_postfix/qmgr'] = 1 if process == 'postfix/qmgr' else 0

    return features

def predict_anomaly_with_explain(log_json):
    if isinstance(log_json, str):
        log = json.loads(log_json)
    else:
        log = log_json

    features = extract_features_from_log(log)
    df_features = pd.DataFrame([features])
    df_features_no_qid = df_features.drop(columns=['qid'], errors='ignore')
    X_scaled = scaler.transform(df_features_no_qid)

    pred = model.predict(X_scaled)[0]

    if pred == -1:
        # SHAP explain
        shap_values = explainer.shap_values(X_scaled)
        shap_df = pd.DataFrame({
            'feature': df_features_no_qid.columns,
            'shap_value': shap_values[0]
        })
        shap_df['abs_shap'] = shap_df['shap_value'].abs()
        top_features = shap_df.sort_values(by='abs_shap', ascending=False).head(10)

        return {
            "anomaly": True,
            "log": log,
            "top_features": top_features[['feature', 'shap_value']].to_dict(orient='records')
        }
    else:
        return {"anomaly": False}

# Example usage
if __name__ == "__main__":
    # log_str = '{"process":"postfix/pickup","user":"unknown","host":{},"message":"from=<user@example.com>, size=1234, nrcpt=1","queue_status":"queue active","qid":"ABC123","timestamp":"Jun 14 05:30:00"}'
    log_str = input("Enter log JSON string: ")
    result = predict_anomaly_with_explain(log_str)

    if result["anomaly"]:
        print("Anomaly detected!")
        print(json.dumps(result, indent=2))
    else:
        print("No anomaly.")

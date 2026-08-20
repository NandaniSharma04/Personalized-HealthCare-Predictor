import sys
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

PROJECT_ROOT = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

csv_path = PROJECT_ROOT / "data" / "raw_dataset" / "Diseases_and_Symptoms_dataset.csv"
model_path = PROJECT_ROOT / "backend" / "ml" / "best_model.pkl"

df = pd.read_csv(csv_path)
symptom_cols = [c for c in df.columns if c != 'diseases']
model = joblib.load(model_path)

print("="*60, flush=True)
print("1. SECTION 10: EXPLICIT TEST FOR ['fever', 'chills', 'sweating', 'headache']", flush=True)
print("="*60, flush=True)

test_syms = ['fever', 'chills', 'sweating', 'headache']
row_dict = {col: 1 if col in test_syms else 0 for col in symptom_cols}
X_single = pd.DataFrame([row_dict], columns=symptom_cols)

direct_pred = model.predict(X_single)[0]
probs = model.predict_proba(X_single)[0] if hasattr(model, 'predict_proba') else []
top_prob = float(max(probs)) * 100.0 if len(probs) > 0 else 0.0

print(f"Input Symptoms: {test_syms}", flush=True)
print(f"Direct Saved Model Prediction: '{direct_pred}'", flush=True)
print(f"Model Confidence Estimate: {top_prob:.2f}%", flush=True)

# Test Flask API call via predict_symptoms
from backend.ml.predictor import predict_symptoms
api_res = predict_symptoms(test_syms)

print(f"Flask API Prediction: '{api_res['predicted_disease']}'", flush=True)
print(f"Flask API Confidence: {api_res['confidence']}%", flush=True)
print(f"Direct Model vs Flask API Match: {direct_pred == api_res['predicted_disease']}", flush=True)

print("\n" + "="*60, flush=True)
print("2. SECTION 11 & 12: 30-TEST CASE ACCURACY & PER-CLASS REPORT", flush=True)
print("="*60, flush=True)

# Sample 30 random rows from dataset
np.random.seed(42)
sample_indices = np.random.choice(df.index, size=30, replace=False)
sample_df = df.iloc[sample_indices]

X_samp = sample_df[symptom_cols]
y_samp_true = sample_df['diseases'].values
y_samp_pred = model.predict(X_samp)

correct_count = 0
incorrect_count = 0

print(f"{'Index':<6} | {'True Disease':<32} | {'Predicted Disease':<32} | {'Result':<8}", flush=True)
print("-" * 80, flush=True)

for idx in range(30):
    t = y_samp_true[idx]
    p = y_samp_pred[idx]
    match = (t == p)
    if match:
        correct_count += 1
    else:
        incorrect_count += 1
    print(f"{idx+1:<6} | {t[:30]:<32} | {p[:30]:<32} | {'CORRECT' if match else 'FAIL'}", flush=True)

print("-" * 80, flush=True)
print(f"30 Test Cases Summary: {correct_count}/30 Correct ({(correct_count/30)*100:.2f}%)", flush=True)

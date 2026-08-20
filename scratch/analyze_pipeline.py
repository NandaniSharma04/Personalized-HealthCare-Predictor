import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main")
csv_path = PROJECT_ROOT / "data" / "raw_dataset" / "Diseases_and_Symptoms_dataset.csv"
model_path = PROJECT_ROOT / "backend" / "ml" / "best_model.pkl"

df = pd.read_csv(csv_path)
symptom_cols = [c for c in df.columns if c != 'diseases']

print("="*60)
print("FEATURE VECTOR & SYMPTOM ALIGNMENT AUDIT")
print("="*60)
print(f"Total Features in Dataset: {len(symptom_cols)}")
print(f"First 10 Features in Dataset: {symptom_cols[:10]}")

# Test feature vector construction for ['fever', 'chills', 'sweating', 'headache']
test_syms = ['fever', 'chills', 'sweating', 'headache']

# Check how feature vector is constructed
vector_dict = {col: 1 if col in test_syms else 0 for col in symptom_cols}
X_test = pd.DataFrame([vector_dict], columns=symptom_cols)

print(f"\nConstructed 230-feature vector sum (number of 1s): {X_test.sum(axis=1).values[0]}")
print(f"Indices of 1s in feature vector:")
for col in test_syms:
    idx = symptom_cols.index(col) if col in symptom_cols else -1
    print(f"  Feature '{col}' -> Index {idx}")

# Load model if exists
if model_path.exists():
    model = joblib.load(model_path)
    print("\nModel loaded successfully:", type(model).__name__)
    
    # Check model features
    if hasattr(model, 'feature_names_in_'):
        model_feats = list(model.feature_names_in_)
        print(f"Model feature count: {len(model_feats)}")
        print(f"Dataset features == Model features: {symptom_cols == model_feats}")
    
    # Run prediction
    pred = model.predict(X_test)
    probs = model.predict_proba(X_test)[0] if hasattr(model, 'predict_proba') else []
    
    print(f"\nModel Prediction for ['fever', 'chills', 'sweating', 'headache']:")
    print(f"Predicted Class: '{pred[0]}'")
    
    if len(probs) > 0:
        top5_idx = np.argsort(probs)[::-1][:5]
        print("\nTop 5 Model Probabilities:")
        for idx in top5_idx:
            cls_name = model.classes_[idx]
            print(f"  {cls_name}: {probs[idx]*100:.2f}%")

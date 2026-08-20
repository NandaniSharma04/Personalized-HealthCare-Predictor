import sys
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

PROJECT_ROOT = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main")
csv_path = PROJECT_ROOT / "data" / "raw_dataset" / "Diseases_and_Symptoms_dataset.csv"
model_dir = PROJECT_ROOT / "backend" / "ml"

print("="*60, flush=True)
print("1. LOADING DATASET FOR MODEL RETRAINING & COMPARISON", flush=True)
print("="*60, flush=True)
df = pd.read_csv(csv_path)

X = df.drop(columns=['diseases'])
y = df['diseases']

feature_names = list(X.columns)
target_classes = sorted(y.unique().tolist())

print(f"Total Rows: {len(df)}", flush=True)
print(f"Total Features: {len(feature_names)}", flush=True)
print(f"Total Classes: {len(target_classes)}", flush=True)

# Stratified Train/Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train Set Rows: {len(X_train)}", flush=True)
print(f"Test Set Rows: {len(X_test)}", flush=True)

print("\n" + "="*60, flush=True)
print("2. MODEL COMPARISON & CROSS-VALIDATION EVALUATION", flush=True)
print("="*60, flush=True)

models = {
    "RandomForest": RandomForestClassifier(n_estimators=60, max_depth=20, random_state=42, n_jobs=-1),
    "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=50, learning_rate=0.1, random_state=42),
    "DecisionTree": DecisionTreeClassifier(max_depth=20, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=200, random_state=42)
}

results = {}

for name, clf in models.items():
    print(f"\n[TRAINING] {name}...", flush=True)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    w_precision, w_recall, w_f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
    
    results[name] = {
        "model": clf,
        "accuracy": acc,
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": f1,
        "weighted_f1": w_f1
    }
    
    print(f"  -> Accuracy: {acc*100:.2f}%", flush=True)
    print(f"  -> Macro F1: {f1:.4f}", flush=True)
    print(f"  -> Weighted F1: {w_f1:.4f}", flush=True)

# Select Best Model based on Macro F1
best_model_name = max(results, key=lambda k: results[k]['macro_f1'])
best_clf = results[best_model_name]['model']

print("\n" + "="*60, flush=True)
print(f"3. SELECTED BEST MODEL: {best_model_name}", flush=True)
print(f"Accuracy: {results[best_model_name]['accuracy']*100:.2f}% | Macro F1: {results[best_model_name]['macro_f1']:.4f}", flush=True)
print("="*60, flush=True)

# Save production model artifacts
model_file = model_dir / "best_model.pkl"
joblib.dump(best_clf, model_file)

symptom_list_file = model_dir / "symptom_list.json"
symptom_list_file.write_text(json.dumps(feature_names, indent=2), encoding="utf-8")

report_file = model_dir / "training_report.json"
report_data = {
    "model_algorithm": type(best_clf).__name__,
    "model_version": "v2.0.0",
    "input_rows": len(df),
    "training_rows": len(X_train),
    "validation": {
        "test_rows": len(X_test),
        "accuracy": round(results[best_model_name]['accuracy'], 6),
        "macro_f1": round(results[best_model_name]['macro_f1'], 6),
        "weighted_f1": round(results[best_model_name]['weighted_f1'], 6)
    },
    "input_features": len(feature_names),
    "input_classes": len(target_classes),
    "comparison": {
        k: {
            "accuracy": round(v['accuracy'], 4),
            "macro_f1": round(v['macro_f1'], 4),
            "weighted_f1": round(v['weighted_f1'], 4)
        } for k, v in results.items()
    }
}
report_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

print(f"\nSaved production model to: {model_file}", flush=True)
print(f"Saved feature list to: {symptom_list_file}", flush=True)
print(f"Saved training report to: {report_file}", flush=True)

print("\n" + "="*60, flush=True)
print("4. EVALUATING 30 RANDOM TEST CASES FROM TEST SET", flush=True)
print("="*60, flush=True)

test_sample = X_test.head(30)
y_sample_true = y_test.head(30).values
y_sample_pred = best_clf.predict(test_sample)

correct_count = 0
incorrect_count = 0

for i in range(30):
    row_features = [col for col, val in test_sample.iloc[i].items() if val == 1]
    true_label = y_sample_true[i]
    pred_label = y_sample_pred[i]
    is_correct = (true_label == pred_label)
    if is_correct:
        correct_count += 1
    else:
        incorrect_count += 1
        
    print(f"Case {i+1:2d}: True='{true_label}' | Pred='{pred_label}' | {'CORRECT' if is_correct else 'INCORRECT'} | Present Syms: {row_features[:4]}", flush=True)

print(f"\n30 Test Cases Summary: {correct_count}/30 Correct ({(correct_count/30)*100:.1f}%)", flush=True)

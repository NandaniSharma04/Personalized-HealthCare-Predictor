from pathlib import Path
import pandas as pd
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report
from typing import Dict, Any
import datetime
try:
    from .mlflow_utils import log_model_run
except Exception:
    log_model_run = None


def train_model(csv_path: str = None, model_output: str = None) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    if csv_path is None:
        csv_path = repo_root / "data" / "raw_dataset" / "Diseases_and_Symptoms_dataset.csv"
    else:
        csv_path = Path(csv_path)
    if model_output is None:
        model_output = Path(__file__).resolve().parent / "best_model.pkl"
    else:
        model_output = Path(model_output)

    df = pd.read_csv(csv_path)
    if "diseases" not in df.columns:
        raise ValueError("Expected 'diseases' column in CSV")
    y = df["diseases"].astype(str)
    X = df.drop(columns=["diseases"])
    # Convert symptom columns to int
    X = X.applymap(lambda v: int(v) if pd.notnull(v) else 0)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, stratify=y_enc, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="macro"))
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)

    # Save model and label encoder into timestamped folder
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    models_dir = model_output.parent / f"model_{ts}"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_file = models_dir / model_output.name
    joblib.dump(clf, model_file)
    le_file = models_dir / "label_encoder.pkl"
    joblib.dump(le, str(le_file))

    # also write a copy at requested model_output path (for backward compatibility)
    joblib.dump(clf, model_output)
    joblib.dump(le, str(model_output.with_name("label_encoder.pkl")))

    # Build training report
    feature_importances = None
    if hasattr(clf, "feature_importances_"):
        feature_importances = clf.feature_importances_.tolist()
        # attach symptom names if present
        sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
        if sym_file.exists():
            syms = json.loads(sym_file.read_text(encoding="utf-8"))
            feature_importances = dict(zip(syms, clf.feature_importances_.tolist()))

    training_report = {
        "input_rows": int(df.shape[0]),
        "input_features": int(X.shape[1]),
        "input_classes": int(len(le.classes_)),
        "metrics": {"accuracy": acc, "f1_macro": f1},
        "classification_report": report,
        "feature_importances": feature_importances,
    }

    # attach model folder path to report
    training_report["model_folder"] = str(models_dir)

    tr_path = model_output.parent / "training_report.json"
    tr_path.write_text(json.dumps(training_report, indent=2), encoding="utf-8")

    # attempt to log run to MLflow
    try:
        if log_model_run is not None:
            run_id = log_model_run("disease_prediction", str(models_dir), training_report.get("metrics"))
            training_report["mlflow_run_id"] = run_id
    except Exception:
        # don't fail training if MLflow logging fails
        pass

    return training_report


if __name__ == "__main__":
    out = train_model()
    print(json.dumps(out, indent=2))

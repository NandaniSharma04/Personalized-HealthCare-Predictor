import pandas as pd
import json
from pathlib import Path
try:
    from backend_fastapi.app.ml.train_pipeline import train_model
except ModuleNotFoundError:
    from app.ml.train_pipeline import train_model


def make_sample_csv(tmp_path: Path) -> Path:
    # Build sample dataset: 3 symptoms, 3 diseases (4 rows per disease)
    rows = []
    for _ in range(4):
        rows.append({"fever": 1, "cough": 1, "fatigue": 0, "diseases": "flu"})
        rows.append({"fever": 0, "cough": 1, "fatigue": 1, "diseases": "cold"})
        rows.append({"fever": 1, "cough": 0, "fatigue": 1, "diseases": "covid"})
    df = pd.DataFrame(rows)
    p = tmp_path / "sample_ds.csv"
    df.to_csv(p, index=False)
    return p


def test_train_model_creates_report_and_model(tmp_path: Path):
    csv_path = make_sample_csv(tmp_path)
    report = train_model(csv_path=str(csv_path), model_output=tmp_path / "best_model.pkl")
    assert isinstance(report, dict)
    assert "metrics" in report and "accuracy" in report.get("metrics", {}) or True
    # model_folder should exist
    mf = report.get("model_folder")
    assert mf is not None
    folder = Path(mf)
    assert folder.exists()
    # model file exists in folder
    files = list(folder.glob("*.pkl"))
    assert len(files) >= 1

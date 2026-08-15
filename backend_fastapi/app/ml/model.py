import joblib
from pathlib import Path
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def load_model() -> Any:
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / "backend" / "ml" / "best_model.pkl"
    if not candidate.exists():
        raise FileNotFoundError(f"Model file not found at {candidate}")
    model = joblib.load(candidate)
    return model

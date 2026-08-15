from pathlib import Path
import json
from typing import List, Tuple, Optional
import joblib
from functools import lru_cache

from . import cf as cf_impl


INTERACTIONS_FILE = Path(__file__).resolve().parents[3] / "backend" / "ml" / "interactions.json"
MODEL_FILE = Path(__file__).resolve().parents[3] / "backend" / "ml" / "cf_model.pkl"


def _ensure_interactions_file():
    if not INTERACTIONS_FILE.exists():
        INTERACTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        INTERACTIONS_FILE.write_text("[]", encoding="utf-8")


def append_interaction(user: str, item: str, rating: float = 1.0):
    _ensure_interactions_file()
    data = json.loads(INTERACTIONS_FILE.read_text(encoding="utf-8"))
    data.append({"user": str(user), "item": str(item), "rating": float(rating)})
    INTERACTIONS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_interactions() -> List[Tuple[str, str, float]]:
    _ensure_interactions_file()
    data = json.loads(INTERACTIONS_FILE.read_text(encoding="utf-8"))
    return [(d["user"], d["item"], float(d.get("rating", 1.0))) for d in data]


def train_cf_model(n_factors: int = 50):
    interactions = load_interactions()
    if not interactions:
        raise RuntimeError("No interactions available to train CF model")
    algo = cf_impl.train_cf(interactions, n_factors=n_factors)
    # save model
    joblib.dump(algo, MODEL_FILE)
    # clear cached loader
    try:
        load_cf_model.cache_clear()
    except Exception:
        pass
    return algo


@lru_cache(maxsize=1)
def load_cf_model():
    if not MODEL_FILE.exists():
        return None
    return joblib.load(MODEL_FILE)

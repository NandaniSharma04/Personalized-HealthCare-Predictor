from pathlib import Path
import pandas as pd
import math
import json
from collections import Counter, defaultdict
from typing import Dict, Any, List
from ..models import Prediction
from ..db.session import get_db
from sqlalchemy.orm import Session


def _safe_prob_dist(arr: List[float], eps: float = 1e-9) -> List[float]:
    # convert counts to probability distribution with smoothing
    total = sum(arr) + eps * len(arr)
    return [(x + eps) / total for x in arr]


def kl_divergence(p: List[float], q: List[float]) -> float:
    # KL(P||Q)
    p_s = _safe_prob_dist(p)
    q_s = _safe_prob_dist(q)
    kl = 0.0
    for pi, qi in zip(p_s, q_s):
        kl += pi * math.log(pi / qi)
    return float(kl)


def baseline_symptom_distribution() -> Dict[str, float]:
    """Compute baseline symptom prevalence from raw dataset.

    Returns mapping symptom -> prevalence (0..1)
    """
    repo_root = Path(__file__).resolve().parents[3]
    csv_path = repo_root / "data" / "raw_dataset" / "Diseases_and_Symptoms_dataset.csv"
    sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
    if not csv_path.exists() or not sym_file.exists():
        return {}
    df = pd.read_csv(csv_path)
    symptoms = json.loads(sym_file.read_text(encoding="utf-8"))
    # assume symptom columns exist in df
    dist = {}
    for s in symptoms:
        if s in df.columns:
            vals = pd.to_numeric(df[s], errors="coerce").fillna(0)
            dist[s] = float((vals > 0).sum() / len(vals))
    return dist


def current_symptom_distribution_from_predictions(db: Session, limit: int = 1000) -> Dict[str, float]:
    """Estimate current symptom prevalence from recent Prediction.input_vector values.

    Supports input_vector form {"vector": [0,1,0,...]} or mapping of symptom->value.
    """
    repo_root = Path(__file__).resolve().parents[3]
    sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
    if not sym_file.exists():
        return {}
    symptoms = json.loads(sym_file.read_text(encoding="utf-8"))
    n = len(symptoms)
    counts = [0] * n
    total = 0
    qs = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    for p in qs:
        iv = p.input_vector or {}
        vec = None
        if isinstance(iv, dict) and "vector" in iv:
            vec = iv.get("vector")
        elif isinstance(iv, dict) and all(k in symptoms for k in iv.keys()):
            # mapping symptom->value
            vec = [int(iv.get(s, 0)) for s in symptoms]
        if vec and len(vec) == n:
            for i, v in enumerate(vec):
                try:
                    counts[i] += 1 if int(v) > 0 else 0
                except Exception:
                    continue
            total += 1
    if total == 0:
        return {s: 0.0 for s in symptoms}
    return {symptoms[i]: float(counts[i] / total) for i in range(n)}


def prediction_metrics(db: Session, days: int = 7) -> Dict[str, Any]:
    # basic metrics: counts per disease, average confidence for top prediction
    qs = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(5000).all()
    total = len(qs)
    counter = Counter()
    confidences = []
    for p in qs:
        if p.predicted_disease:
            counter[p.predicted_disease] += 1
        # try to get top probability
        probs = p.probabilities or {}
        if isinstance(probs, dict) and len(probs) > 0:
            top = max(probs.values())
            confidences.append(float(top))
    top_diseases = counter.most_common(10)
    avg_conf = float(sum(confidences) / len(confidences)) if confidences else None
    return {"total_predictions": total, "top_diseases": top_diseases, "avg_confidence": avg_conf}

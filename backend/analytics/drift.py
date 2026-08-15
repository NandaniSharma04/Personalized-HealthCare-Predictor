"""
Kullback-Leibler (KL) Divergence Data Drift Detection for ML Symptoms Vector.
"""
import numpy as np

def calculate_kl_divergence(p: list[float], q: list[float], epsilon: float = 1e-10) -> float:
    p_arr = np.asarray(p, dtype=np.float64) + epsilon
    q_arr = np.asarray(q, dtype=np.float64) + epsilon
    p_norm = p_arr / np.sum(p_arr)
    q_norm = q_arr / np.sum(q_arr)
    kl_score = np.sum(p_norm * np.log(p_norm / q_norm))
    return float(round(kl_score, 4))

def evaluate_symptom_drift(current_counts: dict[str, int], baseline_counts: dict[str, int]) -> dict:
    all_keys = sorted(list(set(current_counts.keys()).union(set(baseline_counts.keys()))))
    if not all_keys:
        return {"kl_divergence": 0.0, "status": "No data"}
    p = [baseline_counts.get(k, 1) for k in all_keys]
    q = [current_counts.get(k, 1) for k in all_keys]
    score = calculate_kl_divergence(p, q)
    status = "Stable" if score < 0.1 else ("Moderate Drift" if score < 0.3 else "High Drift")
    return {
        "kl_divergence": score,
        "status": status,
        "evaluated_features": len(all_keys)
    }

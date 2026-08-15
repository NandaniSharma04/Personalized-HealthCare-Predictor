from pathlib import Path
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from functools import lru_cache
from typing import List, Tuple


@lru_cache(maxsize=1)
def _build_corpus():
    repo_root = Path(__file__).resolve().parents[3]
    disease_file = repo_root / "backend" / "ml" / "disease_info.json"
    if not disease_file.exists():
        return [], None, None
    data = json.loads(disease_file.read_text(encoding="utf-8"))
    names = []
    docs = []
    for name, info in data.items():
        names.append(name)
        desc = info.get("Description") or ""
        meds = " ".join(info.get("Medication") or []) if isinstance(info.get("Medication"), list) else (info.get("Medication") or "")
        workouts = " ".join(info.get("Workouts") or []) if isinstance(info.get("Workouts"), list) else (info.get("Workouts") or "")
        doc = " ".join([desc, meds, workouts])
        docs.append(doc)
    vect = TfidfVectorizer(stop_words="english", max_features=10000)
    tfidf = vect.fit_transform(docs)
    return names, tfidf, vect


def recommend_by_disease(disease_name: str, top_k: int = 5) -> List[Tuple[str, float]]:
    names, tfidf, vect = _build_corpus()
    if not names:
        return []
    try:
        idx = names.index(disease_name)
    except ValueError:
        return []
    cosine_similarities = linear_kernel(tfidf[idx:idx+1], tfidf).flatten()
    related_docs_indices = cosine_similarities.argsort()[::-1]
    results = []
    for i in related_docs_indices[1: top_k+1]:
        results.append((names[i], float(cosine_similarities[i])))
    return results


def recommend_by_text(text: str, top_k: int = 5) -> List[Tuple[str, float]]:
    names, tfidf, vect = _build_corpus()
    if not names:
        return []
    vec = vect.transform([text])
    cosine_similarities = linear_kernel(vec, tfidf).flatten()
    related_docs_indices = cosine_similarities.argsort()[::-1]
    results = []
    for i in related_docs_indices[:top_k]:
        results.append((names[i], float(cosine_similarities[i])))
    return results

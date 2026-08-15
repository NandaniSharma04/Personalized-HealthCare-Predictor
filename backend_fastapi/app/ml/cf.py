"""Collaborative filtering scaffold using Surprise.
If Surprise is not installed, functions will raise informative errors.
"""
try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import train_test_split
except Exception:
    Dataset = None

from pathlib import Path
import json


def train_cf(interactions: list[tuple], n_factors=50):
    if Dataset is None:
        raise RuntimeError("Surprise library not available. Install scikit-surprise to use CF.")
    # interactions: list of (user, item, rating)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(
        __import__("pandas").DataFrame(interactions, columns=["user", "item", "rating"]), reader
    )
    trainset, testset = train_test_split(data, test_size=0.2)
    algo = SVD(n_factors=n_factors)
    algo.fit(trainset)
    return algo


def recommend_cf(algo, user_id, items, k=10):
    # items: iterable of item ids to score
    results = []
    for item in items:
        try:
            pred = algo.predict(str(user_id), str(item))
            results.append((item, pred.est))
        except Exception:
            continue
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]

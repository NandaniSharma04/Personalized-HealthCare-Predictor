try:
    from backend_fastapi.app.ml.sentiment import analyze_sentiment
except ModuleNotFoundError:
    from app.ml.sentiment import analyze_sentiment


def test_analyze_sentiment_positive():
    res = analyze_sentiment("I love this healthcare recommendation, it helped me a lot")
    assert isinstance(res, dict)
    assert "label" in res and "score" in res


def test_analyze_sentiment_neutral():
    res = analyze_sentiment("")
    assert res["label"] == "neutral"

from typing import Dict, Any
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except Exception:
        nltk.download("vader_lexicon")
    _SID = SentimentIntensityAnalyzer()
except Exception:
    _SID = None


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Return sentiment label and score for input text.

    Uses NLTK VADER when available; falls back to a simple heuristic.
    """
    if not text or not isinstance(text, str):
        return {"label": "neutral", "score": 0.0, "raw": {}}

    if _SID is not None:
        s = _SID.polarity_scores(text)
        compound = float(s.get("compound", 0.0))
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return {"label": label, "score": compound, "raw": s}

    # fallback simple heuristic
    text_l = text.lower()
    pos = ["good", "great", "happy", "love", "excellent", "best", "awesome", "improved"]
    neg = ["bad", "sad", "terrible", "hate", "awful", "worst", "pain", "worse"]
    score = sum(1 for w in pos if w in text_l) - sum(1 for w in neg if w in text_l)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"label": label, "score": float(score), "raw": {}}

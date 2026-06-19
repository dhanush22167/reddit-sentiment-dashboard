"""
Text cleaning and sentiment analysis (BERT via transformers, with a
TextBlob fallback if the transformer model can't load).
"""
import re
from collections import Counter

import streamlit as st
from textblob import TextBlob


def clean_text(text: str) -> str:
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower().strip()


@st.cache_resource
def get_sentiment_pipeline():
    """Lazily load and cache the HuggingFace sentiment pipeline."""
    from transformers import pipeline
    return pipeline("sentiment-analysis")


def analyze_sentiment(text: str, use_bert: bool = True) -> str:
    """Return one of POSITIVE / NEGATIVE / NEUTRAL for the given text."""
    if use_bert:
        try:
            analyzer = get_sentiment_pipeline()
            return analyzer(text[:512])[0]["label"]
        except Exception:
            use_bert = False  # fall back silently if model fails to load

    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.05:
        return "POSITIVE"
    elif polarity < -0.05:
        return "NEGATIVE"
    return "NEUTRAL"


def get_reddit_sentiment(posts, use_bert: bool = True) -> list[dict]:
    """Run sentiment analysis over a list of PRAW submissions."""
    results = []
    for post in posts:
        text = clean_text(post.title + " " + post.selftext)
        if not text:
            continue
        sentiment = analyze_sentiment(text, use_bert=use_bert)
        results.append({
            "title": post.title,
            "sentiment": sentiment,
            "url": post.url,
            "text": text,
            "score": post.score,
            "num_comments": post.num_comments,
        })
    return results


def get_overall_sentiment(results: list[dict]) -> dict:
    """Percentage breakdown of sentiments across all analyzed posts."""
    if not results:
        return {}
    counts = Counter(r["sentiment"] for r in results)
    total = len(results)
    return {sent: round((count / total) * 100, 1) for sent, count in counts.items()}

# Reddit Sentiment Analysis Dashboard

An interactive dashboard that pulls live posts from any subreddit and analyzes their sentiment in real time, visualizing the results through KPIs, charts, and a word cloud.

[project live application](https://reddit-sentiment-dashboard-kzcqufqgf6chsra8tjkmew.streamlit.app/)

## What It Does

The dashboard answers a simple question for any subreddit: **"what's the overall mood here right now?"** It fetches the current "hot" posts from a chosen subreddit, runs each post's text through a sentiment classification model, and aggregates the results into an at-a-glance view — percentage breakdown, visual charts, common terms, and a browsable feed of individual posts tagged with their detected sentiment.

##  Architecture

The project is split into four focused modules, each responsible for one stage of the pipeline:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌─────────────┐
│  config.py  │────▶│ reddit_client.py │────▶│ sentiment.py │────▶│   app.py    │
│  (secrets)  │     │  (data fetch)    │     │  (analysis)  │     │    (UI)     │
└─────────────┘     └──────────────────┘     └─────────────┘     └─────────────┘
```

- **`config.py`** — Loads Reddit API credentials from environment variables rather than hardcoding them in source, and exposes a `credentials_present()` check so the UI can fail gracefully instead of crashing.
- **`reddit_client.py`** — Wraps the Reddit API connection (via PRAW). The client is created once and cached for the session (`st.cache_resource`), then used to pull a configurable number of "hot" posts from any subreddit.
- **`sentiment.py`** — Cleans raw post text (strips URLs and punctuation), then classifies each post using a transformer-based sentiment model, falling back to a lightweight rule-based method if the model is unavailable. Also aggregates individual results into an overall percentage breakdown.
- **`app.py`** — The Streamlit interface. Takes the analyzed results and renders them as metric cards, interactive charts, a word cloud, and per-post cards.

This separation means each piece can be tested, swapped, or extended independently — e.g. plugging in a different sentiment model only touches `sentiment.py`, and switching from Reddit to another data source would only touch `reddit_client.py`.

##  Data Flow

1. **Input** — user specifies a subreddit name and how many posts to analyze.
2. **Fetch** — `reddit_client.py` retrieves that many "hot" posts (title + body text) via the Reddit API.
3. **Clean** — each post's combined title and body text has URLs and punctuation stripped, then is lowercased.
4. **Classify** — cleaned text is passed to the sentiment model, returning one of `POSITIVE`, `NEGATIVE`, or `NEUTRAL` per post.
5. **Aggregate** — individual sentiments are tallied into percentages across the whole batch.
6. **Visualize** — results are rendered as KPI metrics, a bar chart, a donut chart, a word cloud built from all analyzed text, and a scrollable list of color-coded post cards linking back to Reddit.

##  Sentiment Analysis Approach

Two methods are supported, with automatic fallback:

- **Primary — Transformer model (BERT/DistilBERT via 🤗 Transformers):** a pretrained model fine-tuned for binary sentiment classification. It captures context and word order far better than simple keyword/polarity scoring, making it more reliable on short, informally written Reddit posts.
- **Fallback — TextBlob:** a lightweight, rule-based polarity scorer. It's used automatically if the transformer model fails to load (for example, on a resource-constrained hosting environment), trading some accuracy for speed and reliability.

##  Visualizations

| Component | Purpose |
|---|---|
| KPI metric cards | Quick read on overall Positive / Neutral / Negative percentages |
| Bar chart | Raw count of posts per sentiment category |
| Donut chart | Proportional sentiment breakdown |
| Word cloud | Most frequent terms across all analyzed post text, sized by frequency |
| Post cards | Individual posts with title, score, comment count, sentiment tag, and a link to the original Reddit thread |

##  Performance Characteristics

- **Caching:** the Reddit client connection and the sentiment model are both cached for the session, so only the first run pays the cost of initializing them — subsequent analyses in the same session are noticeably faster.
- **Latency:** for a typical batch of 10–20 posts, sentiment classification with the transformer model completes in a few seconds on CPU; the dominant cost is model inference rather than the Reddit API call itself.
- **Accuracy trade-off:** the transformer model is more accurate on nuanced or context-dependent text, while the TextBlob fallback is faster and dependency-light but more prone to misclassifying sarcasm or mixed-sentiment posts.
- **Resource sensitivity:** because transformer models are memory-hungry, behavior may vary on constrained free-tier hosting — the automatic fallback exists specifically to keep the dashboard usable even when the full model can't be loaded.

## Security Design Note

The original prototype had live API credentials and an account password hardcoded directly in the script. This version loads all credentials from environment variables instead, keeping secrets out of source control entirely — a deliberate architectural choice, not just a config detail.

##  Tech Stack

- **Streamlit** — UI framework and app server
- **PRAW** — Reddit API client
- **Transformers (Hugging Face)** — BERT-based sentiment classification
- **TextBlob** — fallback sentiment analysis
- **Plotly** — interactive bar/donut charts
- **WordCloud + Matplotlib** — word frequency visualization
- **Pandas** — result aggregation and tabular handling

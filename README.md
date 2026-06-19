# 📊 Reddit Sentiment Analysis Dashboard

An interactive Streamlit dashboard that pulls hot posts from any subreddit and analyzes their sentiment using a **BERT transformer model** (with a TextBlob fallback), then visualizes the results with charts, KPIs, and a word cloud.

## ✨ Features

- 🔍 Analyze sentiment for any public subreddit's hot posts
- 🤖 BERT-based sentiment classification (`distilbert-base-uncased-finetuned-sst-2-english` via 🤗 Transformers), with a lightweight TextBlob fallback
- 📈 Interactive bar and pie charts (Plotly)
- ☁️ Auto-generated word cloud from post text
- 🗂️ Per-post sentiment cards with score, comment count, and direct links
- 🎨 Custom dark theme with a polished, card-based UI

## 📁 Project Structure

This was split from a single monolithic script into focused modules:

```
.
├── app.py              # Streamlit UI — layout, charts, post cards
├── config.py            # Loads secrets from environment (.env), never hardcoded
├── reddit_client.py      # PRAW Reddit API wrapper (cached client + fetch)
├── sentiment.py          # Text cleaning + BERT/TextBlob sentiment analysis
├── requirements.txt       # Python dependencies
├── .env.example          # Template for your local credentials (safe to commit)
├── .gitignore            # Excludes .env and other local-only files
├── .streamlit/config.toml # Custom dark theme
└── README.md
```

**⚠️ Security note:** the original script had a live Reddit API client secret and account password hardcoded directly in the source. That has been removed — all credentials are now loaded from environment variables via a local `.env` file, which is excluded from git by `.gitignore`. Never commit real secrets to a public repo.

## 🛠️ Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
pip install -r requirements.txt
```

### 2. Create a Reddit API app

1. Go to https://www.reddit.com/prefs/apps
2. Click **"create another app..."**
3. Choose type **script**
4. Note the **client ID** (under the app name) and **client secret**

### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=windows:reddit-sentiment-dashboard:1.0 (by /u/your_username)
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

> Username/password are only required if your Reddit app needs authenticated access; for read-only public subreddit data they can usually be left blank.

### 4. Run locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 🆓 Deploy for Free — Streamlit Community Cloud

This is a Python/Streamlit server app, so it needs a Python host — **GitHub Pages won't work** (it only serves static files). The free option built for exactly this is **Streamlit Community Cloud**:

1. Push this project to a public GitHub repository (see below).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, select your repo, branch `main`, and main file `app.py`.
4. Under **Advanced settings → Secrets**, paste your credentials in TOML format:
   ```toml
   REDDIT_CLIENT_ID = "your_client_id_here"
   REDDIT_CLIENT_SECRET = "your_client_secret_here"
   REDDIT_USER_AGENT = "windows:reddit-sentiment-dashboard:1.0 (by /u/your_username)"
   REDDIT_USERNAME = "your_reddit_username"
   REDDIT_PASSWORD = "your_reddit_password"
   ```
5. Click **Deploy**. Your app will be live at `https://<your-app-name>.streamlit.app` within a few minutes, and free for personal/small projects.

### Pushing to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Reddit sentiment dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

(Your `.env` will **not** be pushed — it's gitignored. Only `.env.example`, with placeholder values, goes to GitHub.)

## 🚀 Performance & Output

- **Latency:** fetching `N` hot posts plus BERT sentiment scoring typically takes a few seconds for `N ≤ 20` on CPU; the model and Reddit client are cached (`st.cache_resource`) so repeat runs in the same session are much faster.
- **Accuracy:** the BERT model (DistilBERT fine-tuned on SST-2) gives strong binary positive/negative sentiment classification; for short, informal Reddit text it generally outperforms TextBlob's rule-based polarity scoring, especially on sarcasm-free, opinionated posts. TextBlob remains as an instant, dependency-light fallback if the transformer model fails to load (e.g. on constrained free hosting tiers).
- **Output:** for a given subreddit and post count, the dashboard shows:
  - Overall sentiment split as percentages (Positive / Neutral / Negative)
  - A bar chart and donut chart of sentiment counts
  - A word cloud of the most frequent terms across analyzed posts
  - A scrollable list of individual posts, each tagged with its sentiment, score, comment count, and a link back to Reddit

## ⚠️ Limitations

- Subject to Reddit API rate limits — keep post counts modest (≤ 50) for smooth performance.
- BERT sentiment models are general-purpose and not fine-tuned specifically for Reddit slang, sarcasm, or memes — treat results as directional, not definitive.
- Free hosting tiers (e.g. Streamlit Community Cloud) have limited CPU/RAM, so very large post counts or repeated rapid runs may be slow or throttled.

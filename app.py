"""
Reddit Sentiment Analysis Dashboard
Analyzes the sentiment of hot posts in any subreddit using a BERT
transformer model (with a TextBlob fallback), and visualizes results
with interactive charts and a word cloud.
"""
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud

from config import credentials_present
from reddit_client import fetch_posts
from sentiment import get_overall_sentiment, get_reddit_sentiment

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Reddit Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- THEME / STYLES -----------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #0f1117 0%, #161922 100%); }

    .big-title {
        font-size: 2.4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FF4500, #FF8717);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #9aa3b2;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 1.8rem;
        margin-bottom: 0.6rem;
        color: #5fb4ff;
        border-left: 4px solid #5fb4ff;
        padding-left: 10px;
    }
    div[data-testid="stMetric"] {
        background-color: #1b1f2a;
        border: 1px solid #2a2f3d;
        border-radius: 12px;
        padding: 14px 10px;
    }
    .post-card {
        padding: 16px 18px;
        margin-bottom: 12px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.25);
    }
    .post-card h4 { margin: 0 0 6px 0; color: #f1f1f1; }
    .post-meta { color: #c7ccd6; font-size: 0.82rem; margin: 4px 0; }
    .post-link { text-decoration: none; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

SENTIMENT_COLORS = {"POSITIVE": "#1c3a2a", "NEGATIVE": "#3a1c22", "NEUTRAL": "#2a2d36"}
SENTIMENT_BORDER = {"POSITIVE": "#2ecc71", "NEGATIVE": "#ff5d6c", "NEUTRAL": "#8a93a6"}
SENTIMENT_EMOJI = {"POSITIVE": "😊", "NEGATIVE": "😡", "NEUTRAL": "😐"}

# ----------------- HEADER -----------------
st.markdown("<div class='big-title'>📊 Reddit Sentiment Analysis Dashboard</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Analyze the mood of any subreddit using BERT + TextBlob, "
    "with interactive charts and a live word cloud.</div>",
    unsafe_allow_html=True,
)

if not credentials_present():
    st.warning(
        "⚠️ Reddit API credentials are not configured. Copy **.env.example** to **.env** "
        "and fill in your Reddit app credentials before running an analysis. "
        "See the README for setup instructions."
    )

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.header("⚙️ Settings")
    subreddit_name = st.text_input("Subreddit", "technology", help="Enter a subreddit name without r/")
    num_posts = st.slider("Number of posts", 5, 50, 15)
    use_bert = st.toggle("Use BERT model (slower, more accurate)", value=True)
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
    st.divider()
    st.caption("Built with Streamlit, PRAW, Transformers & Plotly.")

# ----------------- RUN ANALYSIS -----------------
if run_btn:
    if not credentials_present():
        st.error("Cannot fetch data — Reddit API credentials are missing. See the README.")
        st.stop()

    try:
        with st.spinner(f"Fetching r/{subreddit_name} posts & analyzing sentiment..."):
            posts = fetch_posts(subreddit_name, num_posts)
            results = get_reddit_sentiment(posts, use_bert=use_bert)
    except Exception as e:
        st.error(f"Something went wrong while fetching/analyzing posts: {e}")
        st.stop()

    if results:
        df = pd.DataFrame(results)
        sentiment_summary = get_overall_sentiment(results)

        # ----------------- KPIs -----------------
        st.markdown("<div class='section-header'>📌 Sentiment Overview</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive", f"{sentiment_summary.get('POSITIVE', 0)}%")
        with col2:
            st.metric("😐 Neutral", f"{sentiment_summary.get('NEUTRAL', 0)}%")
        with col3:
            st.metric("😡 Negative", f"{sentiment_summary.get('NEGATIVE', 0)}%")

        # ----------------- VISUALIZATIONS -----------------
        st.markdown("<div class='section-header'>📊 Sentiment Distribution</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        sentiment_counts = df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]

        color_map = {"POSITIVE": "#2ecc71", "NEGATIVE": "#ff5d6c", "NEUTRAL": "#8a93a6"}

        with c1:
            fig_bar = px.bar(
                sentiment_counts, x="Sentiment", y="Count", color="Sentiment",
                color_discrete_map=color_map, title="Sentiment Count",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e6e6e6", showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            fig_pie = px.pie(
                sentiment_counts, names="Sentiment", values="Count", hole=0.45,
                color="Sentiment", color_discrete_map=color_map, title="Sentiment Breakdown",
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e6e6e6")
            st.plotly_chart(fig_pie, use_container_width=True)

        # ----------------- WORD CLOUD -----------------
        st.markdown("<div class='section-header'>☁️ Word Cloud</div>", unsafe_allow_html=True)
        all_text = " ".join(df["text"])
        if all_text.strip():
            wordcloud = WordCloud(
                width=1200, height=400, background_color="#161922",
                colormap="Oranges",
            ).generate(all_text)
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            fig.patch.set_alpha(0)
            st.pyplot(fig)

        # ----------------- INDIVIDUAL POSTS -----------------
        st.markdown("<div class='section-header'>📰 Individual Posts</div>", unsafe_allow_html=True)

        for res in results:
            bg = SENTIMENT_COLORS.get(res["sentiment"], "#1b1f2a")
            border = SENTIMENT_BORDER.get(res["sentiment"], "#444")
            emoji = SENTIMENT_EMOJI.get(res["sentiment"], "")

            st.markdown(
                f"""
                <div class="post-card" style="border-left:6px solid {border}; background-color:{bg};">
                    <h4>{res['title']}</h4>
                    <p class="post-meta">⬆️ {res['score']} &nbsp;|&nbsp; 💬 {res['num_comments']} &nbsp;|&nbsp;
                        <span style="color:{border}; font-weight:700;">{emoji} {res['sentiment']}</span>
                    </p>
                    <a class="post-link" href="{res['url']}" target="_blank" style="color:#5fb4ff;">🔗 Read Post</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("⚠️ No posts found. Try another subreddit.")
else:
    st.info("👈 Set your subreddit and options in the sidebar, then click **Run Analysis** to begin.")

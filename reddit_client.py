"""
Reddit API client setup using PRAW.
"""
import praw
import streamlit as st

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
)


@st.cache_resource
def get_reddit_client() -> praw.Reddit:
    """Create (and cache) a single PRAW Reddit instance for the app session."""
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME or None,
        password=REDDIT_PASSWORD or None,
    )


def fetch_posts(subreddit_name: str, num_posts: int = 15):
    """Fetch hot posts from a subreddit as raw PRAW submission objects."""
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)
    return list(subreddit.hot(limit=num_posts))

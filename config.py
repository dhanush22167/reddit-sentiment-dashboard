"""
Configuration loader.

All secrets are read from environment variables (via a local, gitignored
.env file) — never hardcoded in source. Copy .env.example to .env and
fill in your own values before running the app.
"""
import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "windows:reddit-sentiment-dashboard:1.0")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")


def credentials_present() -> bool:
    """Quick check so the UI can show a friendly setup message instead of crashing."""
    return bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

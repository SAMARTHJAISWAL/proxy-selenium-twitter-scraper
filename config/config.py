"""All configuration comes from environment variables (optionally via a .env file).

Copy .env.example to .env and fill it in. Nothing secret is stored in code.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.getenv("MONGO_DB", "twitter_trends")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "trending_topics")

    # Proxy as host:port, e.g. us-ca.proxymesh.com:31280. Chrome's --proxy-server flag cannot
    # carry a username/password, so use ProxyMesh "IP authentication" (whitelist your IP in the
    # ProxyMesh dashboard). Leave empty to connect directly.
    PROXY_SERVER = os.getenv("PROXY_SERVER", "")
    # URL used through the browser to record which egress IP the run used.
    IP_CHECK_URL = os.getenv("IP_CHECK_URL", "https://api.ipify.org?format=json")

    HEADLESS = _bool("HEADLESS", False)
    WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "20"))

    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8000"))
    FLASK_DEBUG = _bool("FLASK_DEBUG", False)

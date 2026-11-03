from flask import Flask

from app.routes import main


def create_app(scraper=None) -> Flask:
    """Create the Flask app. ``scraper`` can be injected (tests use a fake)."""
    app = Flask(__name__)
    if scraper is None:
        from src.scraper import TwitterScraper

        scraper = TwitterScraper()
    app.extensions["trend_scraper"] = scraper
    app.register_blueprint(main)
    return app

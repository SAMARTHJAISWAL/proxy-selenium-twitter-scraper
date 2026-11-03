import logging

from flask import Blueprint, current_app, jsonify, render_template

main = Blueprint("main", __name__)
log = logging.getLogger(__name__)


def _serialize(record: dict) -> dict:
    out = dict(record)
    if hasattr(out.get("datetime"), "isoformat"):
        out["datetime"] = out["datetime"].isoformat()
    return out


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/scrape")
def scrape():
    scraper = current_app.extensions["trend_scraper"]
    try:
        record = scraper.get_trends()
    except Exception as exc:  # surface the reason to the page instead of a bare 500
        log.exception("Scrape failed")
        return jsonify({"error": str(exc)}), 502
    return jsonify(_serialize(record))

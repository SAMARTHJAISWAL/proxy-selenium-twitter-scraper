from datetime import datetime, timezone

from app import create_app
from src.parsing import build_record


class FakeScraper:
    def __init__(self, fail=False):
        self.fail = fail

    def get_trends(self):
        if self.fail:
            raise RuntimeError("login blocked")
        return build_record(["<b>x</b>", "y"], "203.0.113.7", now=datetime(2024, 1, 1, tzinfo=timezone.utc))


def test_index_renders():
    client = create_app(FakeScraper()).test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"run the script" in res.data


def test_scrape_returns_record():
    client = create_app(FakeScraper()).test_client()
    data = client.get("/scrape").get_json()
    assert data["nameoftrend1"] == "<b>x</b>"
    assert data["nameoftrend3"] == "N/A"
    assert data["datetime"].startswith("2024-01-01T00:00:00")
    assert data["ip_address"] == "203.0.113.7"


def test_scrape_error_is_reported():
    client = create_app(FakeScraper(fail=True)).test_client()
    res = client.get("/scrape")
    assert res.status_code == 502
    assert res.get_json() == {"error": "login blocked"}

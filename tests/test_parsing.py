from datetime import datetime, timezone

import pytest

from src.parsing import build_record, is_metadata, parse_ip, pick_trend_name


@pytest.mark.parametrize("text", ["8,548 posts", "1,085 posts", "47K posts", "12.5K Tweets",
                                  "Trending in India", "Sports · Trending", "Only on X · Trending",
                                  "Trending", "123", "·", ""])
def test_metadata_lines(text):
    assert is_metadata(text)


@pytest.mark.parametrize("text", ["#IndVsAus", "Manmohan Singh", "Boxing Day", "2024 Wrapped"])
def test_trend_names_are_not_metadata(text):
    assert not is_metadata(text)


def test_pick_trend_name_skips_category_and_post_count():
    # Regression: the old parser returned "8,548 posts" as the trend name.
    assert pick_trend_name(["Trending in India", "#Pushpa2", "8,548 posts"]) == "#Pushpa2"
    assert pick_trend_name(["1", "·", "Politics · Trending", "Manmohan Singh", "47K posts"]) == "Manmohan Singh"


def test_pick_trend_name_none_when_only_metadata():
    assert pick_trend_name(["Trending in India", "8,548 posts"]) is None


def test_build_record_pads_to_five():
    now = datetime(2024, 12, 27, tzinfo=timezone.utc)
    rec = build_record(["a", "b"], "1.2.3.4", now=now)
    assert [rec[f"nameoftrend{i}"] for i in range(1, 6)] == ["a", "b", "N/A", "N/A", "N/A"]
    assert rec["ip_address"] == "1.2.3.4"
    assert rec["datetime"] == now
    assert len(rec["_id"]) == 36


def test_build_record_truncates():
    rec = build_record(list("abcdefg"), "x")
    assert rec["nameoftrend5"] == "e" and "nameoftrend6" not in rec


@pytest.mark.parametrize("body,ip", [('{"ip":"203.0.113.7"}', "203.0.113.7"),
                                     ("203.0.113.8\n", "203.0.113.8"),
                                     ("<html>nope</html>", "unknown")])
def test_parse_ip(body, ip):
    assert parse_ip(body) == ip

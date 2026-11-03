"""Pure helpers for turning scraped text into a trend record (no Selenium, no network)."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Iterable, Optional

TOP_N = 5

# Lines in a trend cell that are metadata, not the trend name.
_POST_COUNT = re.compile(r"^[\d.,]+\s*[KkMm]?\s*(posts?|tweets?)$", re.IGNORECASE)
_NUMBER = re.compile(r"^[\d.,]+\s*[KkMm]?$")


def is_metadata(text: str) -> bool:
    t = text.strip()
    if not t or t == "·":
        return True
    lower = t.lower()
    return bool(
        _POST_COUNT.match(t)
        or _NUMBER.match(t)
        or lower.startswith("trending in ")
        or lower in {"trending", "trending worldwide", "show more", "more"}
        or lower.endswith("· trending")
        or lower.startswith("trending with")
    )


def pick_trend_name(texts: Iterable[str]) -> Optional[str]:
    """Return the trend name from the text lines of one ``[data-testid="trend"]`` cell.

    A cell typically reads: "Trending in India" / "<name>" / "8,548 posts".
    Hashtags are valid trend names and are kept.
    """
    for text in texts:
        if text and not is_metadata(text):
            return text.strip()
    return None


def build_record(trends: list[str], ip_address: str, now: Optional[datetime] = None) -> dict:
    """Build the document stored in MongoDB and returned to the web page."""
    padded = (list(trends) + ["N/A"] * TOP_N)[:TOP_N]
    record = {"_id": str(uuid.uuid4())}
    for i, name in enumerate(padded, start=1):
        record[f"nameoftrend{i}"] = name
    record["datetime"] = now or datetime.now(timezone.utc)
    record["ip_address"] = ip_address
    return record


def parse_ip(body: str) -> str:
    """Extract an IP from an ipify-style JSON body or a plain-text body."""
    body = body.strip()
    try:
        data = json.loads(body)
        if isinstance(data, dict) and data.get("ip"):
            return str(data["ip"])
    except ValueError:
        pass
    match = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b|\b[0-9a-fA-F:]{3,39}:[0-9a-fA-F]{1,4}\b", body)
    return match.group(0) if match else "unknown"

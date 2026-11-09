# Proxy Selenium Twitter Scraper

A small Flask app that drives Chrome with Selenium to log in to X (formerly Twitter), read the top
5 entries on the Explore → Trending tab, record which IP address the browser used (optionally
through a proxy such as ProxyMesh), store the result in MongoDB, and show it on a web page.

> **Status:** the code has not been run against the live site since this cleanup (Nov 2026).
> X changes its markup and login flow often and may require extra verification steps (email/phone
> confirmation, captcha) that this scraper does not automate. Automated access may also conflict
> with X's Terms of Service, so use it only with your own account and at your own risk.

## Features

- One-click web page (`/`) that calls `/scrape` and shows the 5 trends, the time, the IP used and
  the stored JSON record.
- Selenium + Chrome. Selenium Manager downloads a matching chromedriver automatically, so you do
  not need to install one.
- Optional proxy through the `PROXY_SERVER` env var. The egress IP is read through the browser
  (via `IP_CHECK_URL`), so the stored IP is the proxy's IP when a proxy is set.
- Results stored in MongoDB (`twitter_trends.trending_topics` by default).
- CLI mode: `python -m src.scraper [--no-save]`.
- All configuration comes from environment variables. No credentials are kept in code.

## Tech stack

Python 3.12, Flask 3, Selenium 4, PyMongo 4, python-dotenv, pytest.

## Prerequisites

- Python 3.10+ (tested with 3.12)
- Google Chrome
- MongoDB reachable at `MONGO_URI` (only needed when saving results)
- An X account
- Optional: a proxy. For ProxyMesh, use **IP authentication** (whitelist your IP in the ProxyMesh
  dashboard), because Chrome's `--proxy-server` flag cannot carry a username and password.

## Setup

```bash
git clone https://github.com/SAMARTHJAISWAL/proxy-selenium-twitter-scraper.git
cd proxy-selenium-twitter-scraper
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt     # or requirements.txt without pytest
cp .env.example .env                    # then fill in TWITTER_USERNAME / TWITTER_PASSWORD etc.
```

Configuration (`.env`):

| Variable | Default | Purpose |
|---|---|---|
| `TWITTER_USERNAME`, `TWITTER_PASSWORD` | (required) | X login |
| `MONGO_URI` / `MONGO_DB` / `MONGO_COLLECTION` | `mongodb://localhost:27017/` / `twitter_trends` / `trending_topics` | storage |
| `PROXY_SERVER` | empty (direct) | `host:port` of the proxy |
| `IP_CHECK_URL` | `https://api.ipify.org?format=json` | records the egress IP |
| `HEADLESS` | `false` | run Chrome headless |
| `WAIT_SECONDS` | `20` | Selenium explicit wait timeout |
| `FLASK_HOST` / `FLASK_PORT` / `FLASK_DEBUG` | `127.0.0.1` / `8000` / `false` | web server |

## Running

```bash
python run.py            # open http://127.0.0.1:8000 and click the button
# or, without the web UI:
python -m src.scraper --no-save
```

## Tests

```bash
python -m pytest -q
```

The tests cover the trend-text parsing, the record format, IP parsing, and the Flask routes, using
a fake scraper. They need no network, browser or MongoDB. GitHub Actions runs them on every push
and pull request.

## Project structure

```
run.py                 starts the Flask app
app/__init__.py        create_app() (a scraper can be injected for tests)
app/routes.py          "/" page and "/scrape" JSON endpoint (502 + {"error": ...} on failure)
app/templates/         single-page UI (no jQuery; trend text is inserted as text, not HTML)
config/config.py       reads all settings from environment / .env
src/scraper.py         Selenium driver setup, login, trend extraction, CLI
src/parsing.py         pure helpers: pick trend names, build the record, parse the IP
src/database.py        MongoDB wrapper
tests/                 pytest suite
images/sample-run-screenshots.pdf   screenshots of an earlier run (Dec 2024)
```

## Limitations

- The scraper depends on X's current HTML (`[data-testid="trend"]`) and login form selectors.
- It does not handle 2FA, email/phone challenges or captchas.
- Proxy authentication with a username and password is not supported. Use IP-whitelisted proxies.
- The screenshots in `images/` come from the old parser, which wrongly showed post counts
  (for example "8,548 posts") instead of trend names. `src/parsing.py` fixes this.

## Licence

[MIT](LICENSE) © 2024–2026 Samarth Jaiswal

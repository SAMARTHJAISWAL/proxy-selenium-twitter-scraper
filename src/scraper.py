"""Selenium scraper for the top trends on X (formerly Twitter)."""
from __future__ import annotations

import logging
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config
from src.parsing import TOP_N, build_record, parse_ip, pick_trend_name

log = logging.getLogger(__name__)

LOGIN_URL = "https://x.com/i/flow/login"
EXPLORE_TRENDING_URL = "https://x.com/explore/tabs/trending"


class ScrapeError(RuntimeError):
    pass


class TwitterScraper:
    def __init__(self, config: type[Config] = Config, database=None):
        self.config = config
        self._database = database

    @property
    def database(self):
        # Created on first use so importing the app never needs MongoDB.
        if self._database is None:
            from src.database import Database

            self._database = Database()
        return self._database

    def setup_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        if self.config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        if self.config.PROXY_SERVER:
            options.add_argument(f"--proxy-server={self.config.PROXY_SERVER}")
        # Selenium >= 4.6 downloads a matching chromedriver itself (Selenium Manager).
        return webdriver.Chrome(options=options)

    def current_ip(self, driver) -> str:
        """Egress IP as seen by the browser, i.e. through the proxy if one is set."""
        try:
            driver.get(self.config.IP_CHECK_URL)
            return parse_ip(driver.find_element(By.TAG_NAME, "body").text)
        except WebDriverException as exc:
            log.warning("Could not determine IP: %s", exc)
            return "unknown"

    def login(self, driver) -> None:
        if not self.config.TWITTER_USERNAME or not self.config.TWITTER_PASSWORD:
            raise ScrapeError("TWITTER_USERNAME and TWITTER_PASSWORD must be set (see .env.example)")
        wait = WebDriverWait(driver, self.config.WAIT_SECONDS)
        driver.get(LOGIN_URL)

        username = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
        username.send_keys(self.config.TWITTER_USERNAME, Keys.RETURN)

        password = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        password.send_keys(self.config.TWITTER_PASSWORD, Keys.RETURN)

        try:
            wait.until(lambda d: "/home" in d.current_url)
        except WebDriverException as exc:
            # X often inserts extra steps (email/phone confirmation, captcha) that this
            # scraper does not automate.
            raise ScrapeError(f"Login did not reach the home timeline (stuck at {driver.current_url})") from exc

    def read_trends(self, driver) -> list[str]:
        driver.get(EXPLORE_TRENDING_URL)
        wait = WebDriverWait(driver, self.config.WAIT_SECONDS)
        cells = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="trend"]')))
        names: list[str] = []
        for cell in cells:
            name = pick_trend_name(cell.text.splitlines())
            if name and name not in names:
                names.append(name)
            if len(names) == TOP_N:
                break
        return names

    def get_trends(self, save: bool = True) -> dict:
        driver = self.setup_driver()
        try:
            ip_address = self.current_ip(driver)
            self.login(driver)
            trends = self.read_trends(driver)
            if not trends:
                raise ScrapeError("No trends found; the page structure may have changed")
            record = build_record(trends, ip_address)
            if save:
                self.database.insert_trends(record)
            return record
        finally:
            driver.quit()


def main(argv: Optional[list[str]] = None) -> None:
    """CLI: ``python -m src.scraper [--no-save]``."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape the top 5 trends on X")
    parser.add_argument("--no-save", action="store_true", help="do not write to MongoDB")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    record = TwitterScraper().get_trends(save=not args.no_save)
    for i in range(1, TOP_N + 1):
        print(f"{i}. {record[f'nameoftrend{i}']}")
    print("IP:", record["ip_address"])


if __name__ == "__main__":
    main()

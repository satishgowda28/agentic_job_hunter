from playwright.sync_api import Page

from agents.site_scrapers.base_scraper import ScrapedJD

from .base_scraper import BaseSiteScraper


class HiristScraper(BaseSiteScraper):
    @property
    def domain(self) -> str:
        return "www.hirist.com"

    def is_active(self, page: Page) -> bool:
        return False

    def extract_jd(self, url: str, page: Page) -> ScrapedJD | None:
        return None

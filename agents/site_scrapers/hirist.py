from abc import abstractmethod

from playwright.sync_api import Page

from agents.site_scrapers.base_scraper import ScrapedJD

from .base_scraper import BaseSiteScraper


class HiristScraper(BaseSiteScraper):
    @property
    def domain(self) -> str:
        return "hirist.com"

    # @abstractmethod
    # def is_active(self, page: Page) -> bool:
    #     return False

    # @abstractmethod
    # def extract_jd(self, page: Page) -> ScrapedJD | None:
    #     return None

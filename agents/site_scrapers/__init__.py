from urllib.parse import urlparse

from playwright.sync_api import Page

from .hirist import HiristScraper
from .linkedin import LinkedinScraper

_scraper = [LinkedinScraper(), HiristScraper()]

SCRAPER_REGISTRY = {scraper.domain: scraper for scraper in _scraper}


def get_scraper(url: str):
    parsed = urlparse(url)
    site_url = parsed.netloc
    return SCRAPER_REGISTRY.get(site_url)

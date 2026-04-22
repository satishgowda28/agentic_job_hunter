from .hirist import HiristScraper
from .linkedin import LinkedinScraper

_scraper = [LinkedinScraper()]

SCRAPER_REGISTRY = {scraper.domain: scraper for scraper in _scraper}


def get_scraper(url: str):
    pass

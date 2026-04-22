from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Page


@dataclass
class ScrapedJD:
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    jd_text: str = ""
    screenshot_path: Optional[str] = None
    is_active: bool = True


class BaseSiteScraper(ABC):
    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain this scraper handles (e.g., 'linkedin.com')."""
        pass

    # @abstractmethod
    # def is_active(self, page: Page) -> bool:
    #     """Check if the job posting is still active on the page."""
    #     pass

    @abstractmethod
    def extract_jd(self, url: str, page: Page) -> Optional[ScrapedJD]:
        """Extract job details from the page's DOM."""
        pass

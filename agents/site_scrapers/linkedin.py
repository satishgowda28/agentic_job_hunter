from playwright.sync_api import Page

from agents.site_scrapers.base_scraper import ScrapedJD

from .base_scraper import BaseSiteScraper


class LinkedinScraper(BaseSiteScraper):
    @property
    def domain(self) -> str:
        return "linkedin.com"

    # @abstractmethod
    # def is_active(self, page: Page) -> bool:
    #     return False

    def extract_jd(self, url: str, page: Page) -> ScrapedJD | None:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # job_data = page.locator(".decorated-job-posting__details").inner_text()
        # print(job_data)
        # page.screenshot(full_page=True, path="linkeding.png")
        return ScrapedJD(
            company="",
            is_active=False,
            url=url,
            jd_text="",
            location="",
            title="",
            screenshot_path="",
        )

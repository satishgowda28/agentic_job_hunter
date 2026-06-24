import logging

from playwright.sync_api import Page

from agents.types import ScrapedJD

from .base_scraper import BaseSiteScraper, SelectorRule


class HiristScraper(BaseSiteScraper):
    @property
    def domain(self) -> str:
        return "www.hirist.tech"

    def is_active(self, page: Page) -> bool:
        try:
            desc_container = page.locator(
                "div.details-container[data-testid='job-description-container']"
            )
            button = desc_container.get_by_role("button", name="Apply")
            if button.is_visible():
                return True
            else:
                return False
        except Exception as err:
            print(f"{err}")
        return False

    def extract_jd(self, url: str, page: Page) -> ScrapedJD | None:
        try:
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_selector("h1.MuiTypography-root", timeout=15000)
        except Exception as err:
            logging.debug(f"palywrite failed to open the page {url}")
            return None
        try:
            is_active = self.is_active(page)
            config = {
                "company": SelectorRule("span[data-testid='company-name']"),
                "job_location": SelectorRule("span[data-testid='company-location']"),
                "job_title": SelectorRule("h1.MuiTypography-root"),
                "job_data": SelectorRule(
                    "div.details-container[data-testid='job-description-container']"
                ),
            }
            extracted = self._extract_generic_data(page, config)
            path = None
            if len(extracted["job_data"]) < 500:
                data_from_image = None
                data_from_image, path = self._screenshot_fallback(
                    extracted["company"], page
                )
                return ScrapedJD(
                    company=data_from_image.get("company", ""),
                    is_active=data_from_image.get("is_active", False),
                    url=url,
                    jd_text=data_from_image.get("jd_text", ""),
                    location=data_from_image.get("location", ""),
                    title=data_from_image.get("title", ""),
                    screenshot_path=path,
                )
            return ScrapedJD(
                company=extracted["company"],
                is_active=is_active,
                url=url,
                jd_text=extracted["job_data"],
                location=extracted["job_location"],
                title=extracted["job_title"],
                screenshot_path=path,
            )

        except Exception as err:
            logging.exception(f"DOM extraction failed for {url}")
            data_from_image = None
            data_from_image, path = self._screenshot_fallback("unknown2", page)
            return ScrapedJD(
                company=data_from_image.get("company", ""),
                is_active=data_from_image.get("is_active", False),
                url=url,
                jd_text=data_from_image.get("jd_text", ""),
                location=data_from_image.get("location", ""),
                title=data_from_image.get("title", ""),
                screenshot_path=path,
            )

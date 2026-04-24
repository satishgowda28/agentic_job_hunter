from playwright.sync_api import Page

from agents.site_scrapers.base_scraper import ScrapedJD

from .base_scraper import BaseSiteScraper


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
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            is_active = self.is_active(page)
            company = page.locator("span[data-testid='company-name']").inner_text()

            job_location = page.locator(
                "span[data-testid='company-location']"
            ).inner_text()
            job_title = page.locator("h1.MuiTypography-root").inner_text()
            job_data = page.locator(
                "div.details-container[data-testid='job-description-container']"
            ).inner_text()
            path = None
            if len(job_data) < 500:
                data_from_image = None
                data_from_image, path = self._screenshot_fallback(company, page)
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
                company=company,
                is_active=is_active,
                url=url,
                jd_text=job_data,
                location=job_location,
                title=job_title,
                screenshot_path=path,
            )

        except Exception as err:
            print("FAILED extract_jd")
            print(f"{err}")
            return None

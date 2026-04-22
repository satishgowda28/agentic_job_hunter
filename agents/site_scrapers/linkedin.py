from playwright.sync_api import Page

from agents.site_scrapers.base_scraper import ScrapedJD

from .base_scraper import BaseSiteScraper


class LinkedinScraper(BaseSiteScraper):
    @property
    def domain(self) -> str:
        return "linkedin.com"

    def is_active(self, page: Page) -> bool:
        try:
            cta_container = page.locator(".top-card-layout__cta-container")
            inner_text = cta_container.inner_text().strip()
            if inner_text:
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
            company = page.locator(".topcard__org-name-link").inner_text()
            job_data = page.locator(".decorated-job-posting__details").inner_text()
            job_location = page.locator(
                "span.topcard__flavor.topcard__flavor--bullet"
            ).inner_text()
            job_title = page.locator("h1.top-card-layout__title").inner_text()
            path = None
            data_from_image = None
            if len(job_data) < 500:
                page.locator("button.show-more-less-html__button").click()
                page.wait_for_timeout(1000)
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
            print(f"{err}")
            return None

from urllib.parse import unquote, urlparse, urlunparse

from agents.types import JobInfo

from .base_parser import BaseJobParser

LINKEDIN_STR = "https://www.linkedin.com/comm/jobs/view/"


class LinkedInParser(BaseJobParser):
    @property
    def sender_email(self) -> str:
        return "jobalerts-noreply@linkedin.com"

    def parse_job(self, subject: str, body: str, raw_links: list[str]) -> list[JobInfo]:
        jobs = []
        job_links = self._parse_links(raw_links)
        for link in job_links:
            jobs.append(JobInfo(source="linkedin_alert", url=link))

        return jobs

    def _parse_subject(self, subject):
        pass

    def _parse_links(self, raw_links) -> list[str]:
        linksList = set()
        for link in raw_links:
            link = unquote(link)
            if LINKEDIN_STR in link:
                parsed = urlparse(link)
                components = (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path.replace("comm/jobs/view/", "jobs/view/"),
                    "",
                    "",
                    "",
                )
                linksList.add(urlunparse(components))
        return list(linksList)

import re
from email.utils import parseaddr
from enum import Enum
from typing import TypedDict
from urllib.parse import unquote, urlparse

from .base_parser import BaseJobParser, JobInfo

HIRIST_STR = "https://www.hirist.tech/j/"


class ParsedSubject(TypedDict):
    company: str | None
    job_title: str | None
    experience: str | None


class EmailClassification(Enum):
    HIRIST_DIGEST = "hirist_digest"
    HIRIST_SINGLE = "hirist_single"
    LINKEDIN_ALERT = "linkedin_alert"


HIRIST_DIGEST_SUBJECT = [
    "Top Tech",
    "Top IT/Tech",
    "Matching Jobs",
    "Top Matching Jobs",
    "10+",
]


class HiristParser(BaseJobParser):
    @property
    def sender_email(self) -> str:
        return "info@hirist.tech"

    def parse_job(self, subject: str, body: str, raw_links: list[str]) -> list[JobInfo]:
        jobs = []
        job_details = self._parse_subject(subject)
        jobs_links = self._parse_links(raw_links)
        for link in jobs_links:
            jobs.append(
                JobInfo(
                    source=self._classify_source(
                        subject
                    ),  # "hirist_single", "hirist_digest", "linkedin_alert"
                    url=link,
                    subject=subject,
                    company=job_details["company"] or "",
                    role=job_details["job_title"] or "",
                    experience=job_details["experience"] or "",
                )
            )
        return jobs

    def _classify_source(self, email_subject) -> str:
        # sender_name, email = parseaddr(email_sender)
        for subTxt in HIRIST_DIGEST_SUBJECT:
            if subTxt in email_subject:
                return EmailClassification.HIRIST_DIGEST.value
        return EmailClassification.HIRIST_SINGLE.value

    # TODO: - Line 66 — split("-") is fragile: a subject like Acme Corp - Senior Engineer - (5-8 yrs) splits into 3 parts and you only look at [1]. Consider split("-", 1) or regex on the whole subject.
    def _parse_subject(self, email_subject) -> ParsedSubject:
        splt_subject_text = email_subject.split("-")
        pattern = r"^(.*?)\s*\(\s*(\d+\s*-\s*\d+\s*(?:yrs?|years?))\s*\)"
        if len(splt_subject_text) > 1:
            company = splt_subject_text[0]
            match = re.search(pattern, splt_subject_text[1], re.IGNORECASE)
            if match:
                job_title = match.group(1)
                experience = match.group(2)
                return {
                    "company": company,
                    "job_title": job_title,
                    "experience": experience,
                }
            return {"company": company, "job_title": None, "experience": None}
        else:
            match = re.search(pattern, splt_subject_text[0], re.IGNORECASE)
            if match:
                job_title = match.group(1)
                experience = match.group(2)
                return {
                    "company": None,
                    "job_title": job_title,
                    "experience": experience,
                }
        return {"company": None, "job_title": None, "experience": None}

    def _parse_links(self, raw_links) -> list[str]:
        linksList = set()
        for link in raw_links:
            link = unquote(link)
            if HIRIST_STR in link:
                parsed = urlparse(link)
                match = re.search(r"(https?://.*)", parsed.path)
                if match:
                    linksList.add(match.group(1))
        return list(linksList)

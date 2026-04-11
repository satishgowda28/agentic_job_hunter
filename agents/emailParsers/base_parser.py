from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class JobInfo:
    source: str  # "hirist_single", "hirist_digest", "linkedin_alert"
    url: str
    subject: str = ""
    company: str = ""
    role: str = ""
    experience: str = ""


class BaseJobParser(ABC):
    @property
    @abstractmethod
    def sender_email(self) -> str:
        """The email address this parser handles."""
        pass

    @abstractmethod
    def parse_job(self, subject: str, body: str, raw_links: list[str]) -> list[JobInfo]:
        """Takes raw email data and returns standardized JobInfo objects."""
        pass

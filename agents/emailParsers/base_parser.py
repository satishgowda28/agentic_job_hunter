from abc import ABC, abstractmethod

from agents.types import JobInfo


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

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


@dataclass
class JobInfo:
    source: str  # "hirist_single", "hirist_digest", "linkedin_alert"
    url: str
    subject: str = ""
    company: str = ""
    role: str = ""
    experience: str = ""


@dataclass
class ScrapedJD:
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    jd_text: str = ""
    screenshot_path: Optional[str] = None
    is_active: bool = True


class JobStatus(str, Enum):
    SHORTLISTED = "Shortlisted"
    REVIEWMANUALLY = "Review Manually"
    SKIPPED = "Skipped"


class Legitimacy(BaseModel):
    requirements_sane: bool
    tech_specific: bool
    contradictions: bool
    tier: Literal["high", "caution", "suspicious"]
    reason: str


class MatchReport(BaseModel):
    role_fit: int
    seniority_match: int
    location_match: int
    matched_skills: list
    gaps: list
    reasoning: str


class JobFitReport(MatchReport):
    composite: int  # 0-100
    status: JobStatus


@dataclass
class ScoringResult:
    job_fit_report: JobFitReport
    legitimacy_data: Legitimacy

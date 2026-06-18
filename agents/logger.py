import logging
import os
from datetime import date

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from agents.auth import google_init
from agents.types import JobInfo, JobStatus, LogData, ScoringResult, ScrapedJD

load_dotenv()
sheet_id = os.getenv("SPREADSHEET_ID")
RANGE_NAME = "Job hunter!A2:ZZ"


def log_job(
    job_status: JobStatus,
    job_info: JobInfo | None = None,
    scraped_jd: ScrapedJD | None = None,
    scoring_result: ScoringResult | None = None,
    resume_path: str = "",
):
    creds = google_init()
    try:
        service = build("sheets", "v4", credentials=creds)
        data_row = build_row(
            job_status, job_info, scraped_jd, scoring_result, resume_path
        )
        data_to_log = []
        if data_row:
            data_to_log = [
                data_row.date,
                data_row.company,
                data_row.role,
                data_row.score or "",
                (", ".join(data_row.matched_skills) if data_row.matched_skills else ""),
                data_row.gaps or "",
                data_row.jd_url,
                data_row.screenshot or "",
                data_row.tailored_resume or "",
                data_row.status.value,
                data_row.filter_reason or "",
                data_row.applied,
                data_row.notes,
            ]
            insert_row(service, data_to_log)

    except HttpError as err:
        print(err)


def build_row(
    job_status: JobStatus,
    job_info: JobInfo | None = None,
    scraped_jd: ScrapedJD | None = None,
    scoring_result: ScoringResult | None = None,
    resume_path: str = "",
) -> LogData | None:
    today = date.today().strftime("%Y-%m-%d")
    match job_status:
        case JobStatus.SHORTLISTED:
            if not scraped_jd or not scoring_result:
                logging.error(
                    "Missing scraped_jd or scoring_result for SHORTLISTED job."
                )
                return None

            report = scoring_result.job_fit_report
            return LogData(
                date=today,
                company=scraped_jd.company or (job_info.company if job_info else ""),
                role=scraped_jd.title
                or (job_info.role if job_info else ""),  # Note: ScrapedJD uses 'title'
                jd_url=scraped_jd.url,
                status=job_status,
                applied="No",
                notes=scoring_result.legitimacy_data.reason,
                score=f"{report.composite}%",
                matched_skills=report.matched_skills,
                gaps=(
                    ", ".join(report.gaps) if report.gaps else ""
                ),  # Convert list[str] to comma-separated str
                screenshot=scraped_jd.screenshot_path,
                tailored_resume=resume_path or None,
            )
        # SCENARIO 2 & 3: Scraped and Scored, but not an immediate Yes
        case JobStatus.REVIEW_MANUALLY | JobStatus.SKIPPED:
            if not scraped_jd or not scoring_result:
                logging.error(
                    f"Missing scraped_jd or scoring_result for {job_status.name} job."
                )
                return None

            report = scoring_result.job_fit_report
            legitimacy = scoring_result.legitimacy_data

            return LogData(
                date=today,
                company=scraped_jd.company or (job_info.company if job_info else ""),
                role=scraped_jd.title or (job_info.role if job_info else ""),
                jd_url=scraped_jd.url,
                status=job_status,
                applied="No",
                notes=report.reasoning,
                score=f"{report.composite}%",
                matched_skills=report.matched_skills,
                gaps=", ".join(report.gaps) if report.gaps else None,
                screenshot=scraped_jd.screenshot_path,
                # Route the specific failure reason into your new filter_reason column
                filter_reason=(
                    legitimacy.reason
                    if legitimacy.tier != "high"
                    else "Low composite score"
                ),
            )

        # SCENARIO 4 & 5: Early Rejections (No scrape, no score)
        case JobStatus.FILTERED | JobStatus.BLACKLISTED:
            if not job_info:
                logging.error(f"Missing job_info for {job_status.name} job.")
                return None

            return LogData(
                date=today,
                company=job_info.company,
                role=job_info.role,
                jd_url=job_info.url,
                status=job_status,
                applied="No",
                notes="Rejected before scraping phase.",
                filter_reason="Matched blacklisted keyword or failed pre-filter criteria.",
            )
        case JobStatus.SCRAPE_FAILED:
            if not job_info:
                logging.error(f"Missing job_info for {job_status.name} job.")
                return None

            return LogData(
                date=today,
                company=job_info.company,
                role=job_info.role,
                jd_url=job_info.url,
                status=job_status,
                applied="No",
                notes="Scraping failed",
            )
        case JobStatus.SUSPICIOUS:
            if not job_info:
                logging.error(f"Missing job_info for {job_status.name} job.")
                return None

            return LogData(
                date=today,
                company=job_info.company,
                role=job_info.role,
                jd_url=job_info.url,
                status=job_status,
                applied="No",
                notes="The Job posting was suspicous",
            )

        # SAFETY NET
        case _:
            logging.warning(f"Unhandled JobStatus encountered: {job_status}")
            return None


def insert_row(service, data: list[str]) -> bool:
    try:
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=sheet_id,
                range=RANGE_NAME,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [data]},
            )
        )
        response = request.execute()
        updated_range = response.get("updates", {}).get("updatedRange", "Unknown Range")
        return True
    except HttpError as err:
        raise err


if __name__ == "__main__":
    from agents.types import (
        JobFitReport,
        JobInfo,
        JobStatus,
        Legitimacy,
        ScoringResult,
        ScrapedJD,
    )

    test_jd = ScrapedJD(
        url="https://razorpay.com/jobs/senior-frontend",
        title="Senior Frontend Engineer",
        company="Razorpay",
        location="Bengaluru",
        jd_text="React, Next.js, TypeScript...",
        screenshot_path=None,
    )

    test_fit = JobFitReport(
        role_fit=90,
        seniority_match=85,
        location_match=100,
        matched_skills=["React", "Next.js", "TypeScript"],
        gaps=["Go"],
        reasoning="Strong frontend match. Go is preferred but not required.",
        composite=89,
        status=JobStatus.SHORTLISTED,
    )

    test_legitimacy = Legitimacy(
        requirements_sane=True,
        tech_specific=True,
        contradictions=False,
        tier="high",
        reason="Legit posting with clear tech stack.",
    )

    test_scoring = ScoringResult(
        job_fit_report=test_fit,
        legitimacy_data=test_legitimacy,
    )

    log_job(
        job_status=JobStatus.SHORTLISTED,
        scraped_jd=test_jd,
        scoring_result=test_scoring,
    )

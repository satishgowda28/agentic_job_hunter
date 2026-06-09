from agents.gmail_reader import read_job_emails
from agents.jd_scraper import scrape_jd
from agents.logger import log_job
from agents.match_scorer import score_job
from agents.resume_tailor import tailor_resume
from agents.types import JobStatus


def run():
    jobs = read_job_emails()

    for job in jobs:
        try:
            jd = scrape_jd(job.url)
            if jd is None:
                log_job(
                    job_status=JobStatus.SKIPPED,
                    job_info=job,
                    scraped_jd=jd,
                )
                continue
            scoring_result = score_job(jd)
            if scoring_result is None:
                log_job(
                    job_status=JobStatus.SKIPPED,
                    job_info=job,
                    scraped_jd=jd,
                )
                continue
            job_status = scoring_result.job_fit_report.status
            if job_status == JobStatus.SHORTLISTED:
                resume_path = tailor_resume(jd, scoring_result)
                log_job(
                    job_status=job_status,
                    job_info=job,
                    scraped_jd=jd,
                    scoring_result=scoring_result,
                    resume_path=resume_path or "",
                )

            if job_status in (JobStatus.REVIEW_MANUALLY, JobStatus.SKIPPED):
                log_job(
                    job_status=job_status,
                    job_info=job,
                    scraped_jd=jd,
                    scoring_result=scoring_result,
                )
        except Exception as err:
            print(f"Error processing job: {err}")

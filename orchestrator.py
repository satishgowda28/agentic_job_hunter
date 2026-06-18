from agents.gmail_reader import read_job_emails
from agents.jd_scraper import scrape_jd
from agents.logger import log_job
from agents.match_scorer import score_job
from agents.notifier import send_summary
from agents.resume_tailor import tailor_resume
from agents.types import JobStatus


def run():
    jobs = read_job_emails()
    scrapping_failed = 0
    shortlisted = 0
    review = 0
    skipped = 0
    errors = 0
    errorStr = ""

    for job in jobs:
        try:
            jd = scrape_jd(job.url)
            if jd is None:
                log_job(
                    job_status=JobStatus.SCRAPE_FAILED,
                    job_info=job,
                )
                scrapping_failed += 1
                continue
            scoring_result = score_job(jd)
            if scoring_result is None:
                log_job(
                    job_status=JobStatus.SUSPICIOUS,
                    job_info=job,
                    scraped_jd=jd,
                )
                skipped += 1
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
                shortlisted += 1

            if job_status in (JobStatus.REVIEW_MANUALLY, JobStatus.SKIPPED):
                log_job(
                    job_status=job_status,
                    job_info=job,
                    scraped_jd=jd,
                    scoring_result=scoring_result,
                )
                if job_status == JobStatus.REVIEW_MANUALLY:
                    review += 1
                if job_status == JobStatus.SKIPPED:
                    skipped += 1
        except Exception as err:
            print(f"Error processing job: {err}")
            errors += 1
            errorStr += f"\n ${err} \n"
    summary = f"""\
            Here is the summary,
            
            Failed to Scrape: {scrapping_failed}\n
            Shortlisted: {shortlisted}\n
            To Reviewd Manually: {review}\n
            Skipped: {skipped}\n
            Errors : {errors}
            
            Errors Details: {errorStr}
            """
    send_summary(summary)
    return summary


if __name__ == "__main__":
    print(run())

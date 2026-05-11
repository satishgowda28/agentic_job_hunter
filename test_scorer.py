from agents.types import ScrapedJD, ScoringResult, JobFitReport, JobStatus, Legitimacy
from agents.resume_tailor import tailor_resume

jd = ScrapedJD(
    url="https://example.com",
    title="Senior Frontend Engineer",
    company="Razorpay",
    location="Bengaluru",
    jd_text="We need React, Next.js, TypeScript expert...",
)

fit = JobFitReport(
    role_fit=88,
    seniority_match=85,
    location_match=100,
    matched_skills=["React", "Next.js", "TypeScript"],
    gaps=["Go preferred"],
    reasoning="Strong frontend match.",
    composite=87,
    status=JobStatus.SHORTLISTED,
)

legitimacy = Legitimacy(
    requirements_sane=True,
    tech_specific=True,
    contradictions=False,
    tier="high",
    reason="Looks real",
)

result = ScoringResult(job_fit_report=fit, legitimacy_data=legitimacy)
print("Scoring result done")
print("Scoring result done")
file_name = tailor_resume(jd, result)
print(file_name)

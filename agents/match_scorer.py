import os

from anthropic import Anthropic

from agents.types import (
    JobFitReport,
    JobStatus,
    Legitimacy,
    MatchReport,
    ScoringResult,
    ScrapedJD,
)
from dotenv import load_dotenv

from utils import parsers

load_dotenv()

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def score_job(jd: ScrapedJD | None) -> ScoringResult | None:
    if jd is None:
        return None
    message = job_posting_analysis(jd)
    job_legitimacy_data: Legitimacy | None = parsers.extract_and_validate(
        message, Legitimacy
    )
    if job_legitimacy_data is not None:
        if job_legitimacy_data.tier == "suspicious":
            return None
        elif job_legitimacy_data.tier == "caution":
            print(f"loggin will come here {job_legitimacy_data.reason}")
        else:
            print("process it with sonnet")
            job_fit_report = job_composite(jd)
            if job_fit_report:
                return ScoringResult(
                    legitimacy_data=job_legitimacy_data, job_fit_report=job_fit_report
                )
    print(job_legitimacy_data)


def job_posting_analysis(jd: ScrapedJD):
    message = ai_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        You are a job posting analyst.

                        Analyze this job description and assess its legitimacy.

                        Check three things:

                        1. **Requirements realism** - Is this a real external job posting? (not spam, not internal transfer, not gibberish)
                        2. **Tech specificity** - Does JD name actual technologies? (not just "web development skills")
                        3. **Contradictions** - Does JD contradict itself? (e.g. "Senior" + "0–2 years exp")

                        Derive tier using this priority order:

                        1. if contradictions == true → tier = "suspicious" (stop, do not check further)
                        2. else if requirements_sane == false OR tech_specific == false → tier = "caution"
                        3. else → tier = "high"

                        Return ONLY valid JSON. No markdown. No ```json. No explanation. Raw JSON only:
                        {{
                            "requirements_sane": bool,
                            "tech_specific": bool,
                            "contradictions": bool,
                            "tier": "high|caution|suspicious",
                            "reason": one line only
                        }}

                        **Job Description:** - {jd.jd_text}
                        **Job Title:** - {jd.title}
                        """,
                    }
                ],
            }
        ],
    )
    return message


def job_composite(jd: ScrapedJD) -> JobFitReport | None:
    with open("config/profile.md", "r", encoding="utf-8") as f:
        profile_data = f.read()
        message = ai_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
                            You are a job posting analyst.

                            **profile:** - {profile_data}
                            
                            Analyze this job description and my profile and help to score the following points.

                            All the sores should be ranged between 0-100

                            3 axis that need to be score:

                            1. **role_fit** - does the stack mentioned in the JD matches my stack in my profile by how much?
                            2. **seniority_match** - experience in the JD matches my experience level by how much?
                            3. **location_match** - i have some work location preference does the JD matches and by how much

                            provide the score in the range is of 0-100

                            With the scores also mention these points too:
                            **matched_skills** - what are the skill that matches my profile e.g: ["react", 'next']
                            **gaps** - what skills do i lack e.g.["react", 'next']
                            **reasoning** - 2-3 sentences explaining why this score — what matched well, what's missing
                            
                            Return ONLY valid JSON, no markdown fences:
                            {{
                                "role_fit": int,
                                "seniority_match": int,
                                "location_match": int,
                                "matched_skills": list,
                                "gaps": list,
                                "reasoning": string
                            }}

                            **Job Description:** - {jd.jd_text}
                            **Job Title:** - {jd.title}
                            **company:** - {jd.company}
                                                    """,
                        }
                    ],
                }
            ],
        )
        match_report: MatchReport | None = parsers.extract_and_validate(
            message, MatchReport
        )
        if match_report is not None:
            score = calculate_composite_score(match_report)
            status = JobStatus.SKIPPED
            if score >= 80:
                status = JobStatus.SHORTLISTED
            elif score >= 60:
                status = JobStatus.REVIEWMANUALLY

            return JobFitReport(
                **match_report.model_dump(),
                composite=score,
                status=status,
            )
        else:
            return None


def calculate_composite_score(mr: MatchReport) -> int:
    composite = int(
        (mr.role_fit * 0.5) + (mr.seniority_match * 0.3) + (mr.location_match * 0.2)
    )
    return composite

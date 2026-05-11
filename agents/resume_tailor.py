import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

from agents.types import ScoringResult, ScrapedJD

import os

load_dotenv()

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def tailor_resume(jd: ScrapedJD, scoring_result: ScoringResult):
    try:
        with (
            open("resumes/base_resume.md", "r", encoding="utf-8") as br,
            open("resumes/template.tex", "r", encoding="utf-8") as tmpl,
        ):
            base_resume = br.read()
            template = tmpl.read()
            resume_output = ai_client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""
                                You are a Professional Resume Writer, specialized in crafting, editing, and formatting resumes, CVs based on job descriptions and skills

                                **Base Resume :** - {base_resume}

                                Please analyse base resume, the Job description and score of the job description and my resume relations
                                and want you fill the resume template

                                The scoring input will include the following:
                                **matched_skills** — it tells exactly what skill to emphasize on
                                **gaps** — it will tell what's missing (don't fabricate, but can de-emphasize)
                                **reasoning**: it give the analysis on the why this particular job fits
                                **seniority_match**: it shows the candidates experience and jd requirement, rage 0-100
                                **composite**: - composite score in percentage
                                **role_fit**: - how well the role fits the base resume in the range 0-100

                                ## Instruction

                                - Summary: rewrite to mirror JD language
                                - Skills: reorder most relevant first
                                - Aza bullets: pick best 5-6, reframe to match JD vocabulary
                                - Other roles: trim weak bullets
                                important : Never add facts, skills, or experience not present in the base resume. Only reframe, reorder, trim.

                                template for the resume is provided
                                **Resume template :** - {template}

                                ### instruction to fill the template

                                - there are place holder e.g: %%SKILLS_LANGUAGES%%, %%AZA_BULLETS%%, %%WHITEHAT_BULLETS%%,
                                I want this placeholder to be filled with refactored or reframed information
                                - I want you to fill these place holders
                                - Return ONLY the filled LaTeX. No explanation, no markdown fences.

                                ## Required information / data

                                **matched_skills** — {scoring_result.job_fit_report.matched_skills} list
                                **gaps** — {scoring_result.job_fit_report.gaps} - list
                                **reasoning** - {scoring_result.job_fit_report.reasoning} str
                                **seniority_match** - {scoring_result.job_fit_report.seniority_match} int
                                **composite** - {scoring_result.job_fit_report.composite} int
                                **role_fit** - {scoring_result.job_fit_report.role_fit} int
                                **Job Description:** - {jd.jd_text}
                                **Job Title:** - {jd.title}
                                **company:** - {jd.company}

                                """,
                            }
                        ],
                    }
                ],
            )
            custom_resume = None
            for block in resume_output.content:
                if block.type == "text":
                    custom_resume = block.text
            if custom_resume:
                os.makedirs("output/tailored", exist_ok=True)
                date = datetime.date.today().strftime("%d%m%y")
                file_name = f"output/tailored/{jd.company}_{date}.tex"
                with open(file_name, "w") as tex:
                    tex.write(custom_resume)
                    print(f"saved to {jd.company}_{date}.tex")
                return file_name
            pass
    except Exception as err:
        # TODO: log will come, when log func is created
        print(err)

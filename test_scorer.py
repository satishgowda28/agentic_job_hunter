from dotenv import load_dotenv

load_dotenv()

from agents.match_scorer import score_job
from agents.types import ScrapedJD

fake_jd = ScrapedJD(
    url="https://example.com",
    title="Senior Frontend Engineer",
    company="Razorpay",
    location="Bengaluru",
    jd_text="""
      We are looking for a Senior Frontend Engineer with 5+ years experience.
      Must know React, Next.js, TypeScript, and GraphQL.
      You will lead frontend architecture decisions.
      """,
)

result = score_job(fake_jd)
print(result)

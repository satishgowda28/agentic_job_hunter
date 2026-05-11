# Phase 5 — Resume Tailor

## Status
DONE. Branch: `phase5_resume_tailor`

## Files
- `resumes/base_resume.md` — full reviewed resume
- `resumes/template.tex` — LaTeX template with placeholders
- `agents/resume_tailor.py` — complete. Reads base resume + template, calls Sonnet, saves to `output/tailored/<company>_<date>.tex`, returns file path.

## Next Step
PDF compilation — `.tex` → `.pdf` via `pdflatex` or Playwright

---

## Tailoring Strategy — Level 3 (Full)

Not MVP — this system will be used for real job applications.

| What | How |
|---|---|
| Summary | Rewritten to mirror JD language and priorities |
| Skills | Reordered — most relevant to JD first |
| Aza bullets | Select best 5-6, reframe language to match JD vocabulary |
| Other roles | Select most relevant bullets, trim weak ones |

**Hard rule: never add facts not in `base_resume.md`. Only reframe, reorder, trim.**

---

## Sonnet Inputs

- `base_resume.md` — full content
- `jd_text`, `jd_title`, `jd_company` — from `ScrapedJD`
- `matched_skills`, `gaps`, `reasoning` — from `ScoringResult` (so Sonnet knows exactly what matched)

## Sonnet Output

Filled `template.tex` with all placeholders replaced:
- `%%SUMMARY%%`
- `%%SKILLS_LANGUAGES%%`, `%%SKILLS_FRAMEWORKS%%`, `%%SKILLS_ARCHITECTURE%%`, `%%SKILLS_API%%`, `%%SKILLS_DEVOPS%%`, `%%SKILLS_DOMAINS%%`, `%%SKILLS_LEARNING%%`
- `%%AZA_BULLETS%%`
- `%%WHITEHAT_BULLETS%%`
- `%%UNIFYND_BULLETS%%`
- `%%STYLABS_BULLETS%%`

## Output Path

`output/tailored/<company>_<date>.tex` → compiled to PDF

## Only Runs When

`ScoringResult.job_fit_report.composite >= 80` (Shortlisted)

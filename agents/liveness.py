import re

HARD_EXPIRED = [
    r"job (is )?no longer available",
    r"position has been filled",
    r"this job has expired",
    r"no longer accepting applications",
    r"job (listing )?not found",
]
LISTING_PAGE = [r"\d+\s+jobs?\s+found", r"search for jobs page is loaded"]
APPLY_SIGNALS = [
    r"\bapply\b",
    r"easy apply",
    r"submit application",
    r"start application",
]


def classify_liveness(status, body_text, controls):
    if status in (404, 410):
        return "expired"
    if any(re.search(p, body_text, re.I) for p in HARD_EXPIRED):
        return "expired"
    if any(re.search(p, c, re.I) for c in controls for p in APPLY_SIGNALS):
        return "active"
    if any(re.search(p, body_text, re.I) for p in LISTING_PAGE):
        return "expired"
    if len(body_text.strip()) < 300:
        return "expired"
    return "uncertain"

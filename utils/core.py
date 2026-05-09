import json
import re


def extract_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return json.loads(match.group(1))
    return json.loads(text.strip())

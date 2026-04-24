import base64
import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import PIL.Image
from anthropic import Anthropic
from dotenv import load_dotenv
from playwright.sync_api import Page

load_dotenv()

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class ScrapedJD:
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    jd_text: str = ""
    screenshot_path: Optional[str] = None
    is_active: bool = True


class BaseSiteScraper(ABC):
    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain this scraper handles (e.g., 'linkedin.com')."""
        pass

    @abstractmethod
    def is_active(self, page: Page) -> bool:
        """Check if the job posting is still active on the page."""
        pass

    @abstractmethod
    def extract_jd(self, url: str, page: Page) -> Optional[ScrapedJD]:
        """Extract job details from the page's DOM."""
        pass

    def _check_liveness(self, page: Page):
        pass

    def _screenshot_fallback(
        self, company: str, page: Page
    ) -> tuple[Dict[str, Any], str]:
        now = datetime.now()
        date_ddmmyy = now.strftime("%d%m%y")
        path = f"output/screenshots/{company}_{date_ddmmyy}.jpg"
        page.screenshot(full_page=True, path=path)
        image = PIL.Image.open(path)
        image = image.convert("L")
        # image.thumbnail((800, 800))
        image.save(path, format="JPEG", quality=20)
        data = self._dataExtractor(path)
        return ({}, path)

    def _dataExtractor(self, path: str):
        with open(path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            message = ai_client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": """You are an expert data extraction bot. Your task is to analyze the provided image of a job posting and extract the key information into a structured JSON format.

                                Analyze the image and extract the following fields. If a specific piece of information is not mentioned in the image, use `null` for that field. Do not invent or infer information that is not explicitly visible.
                                
                                Do not use markdown code fences.

                                Expected JSON Schema:
                                {
                                "title": "string",
                                "company": "string",
                                "location": "string (e.g., City, State, or 'Remote')",
                                "jd_text": "string",
                                "is_active": "boolean (e.g job application is active or not, look for apply button or text)"
                                }

                                RULES:
                                1. Output ONLY valid JSON.
                                2. Do NOT wrap the JSON in markdown formatting blocks (e.g., no ```json).
                                3. Do NOT include any conversational text, greetings, or explanations before or after the JSON.
                                4. Ensure all keys and string values are enclosed in double quotes.

                                Begin extraction now:""",
                            },
                        ],
                    }
                ],
            )
            json_data = None
            for block in message.content:
                if block.type == "text":
                    json_data = self._extract_json(block.text)
            if json_data is not None:
                return json_data
            else:
                return {}

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return json.loads(match.group(1))
        return json.loads(text.strip())

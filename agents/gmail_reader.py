import base64
import math
import os
import pickle
import re
from ast import Pass
from dataclasses import dataclass
from datetime import datetime
from email.utils import parseaddr
from enum import Enum
from urllib.parse import unquote, urlparse, urlunparse

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.pickle"


@dataclass
class JobInfo:
    source: str  # "hirist_single", "hirist_digest", "linkedin_alert"
    url: str
    subject: str = ""
    company: str = ""
    role: str = ""
    experience: str = ""


class EmailAddr(Enum):
    HIRIST = "info@hirist.tech"
    LINKEDIND = "jobalerts-noreply@linkedin.com"


# "hirist_single", "hirist_digest", "linkedin_alert", or "unknown"
class EmailClassification(Enum):
    HIRIST_DIGEST = "hirist_digest"
    HIRIST_SIGNLE = "hirist_single"
    LINKEDIN_ALERT = "linkedin_alert"


HIRIST_DIGEST_SUBJECT = [
    "Top Tech",
    "Top IT/Tech",
    "Matching Jobs",
    "Top Matching Jobs",
    "Matching Jobs",
    "10+",
]

HIRIST_STR = "https://www.hirist.tech/j/"
LINKEDIN_STR = "https://www.linkedin.com/comm/jobs/view/"


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "_creds/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def get_email_body(email_payload):
    body = ""
    links = []

    if "parts" in email_payload:
        html_part = None
        text_part = None
        for part in email_payload["parts"]:
            if part["mimeType"] == "text/html":
                html_part = part["body"].get("data", "")
            elif part["mimeType"] == "text/plain":
                text_part = part["body"].get("data", "")
        if html_part is not None:
            html = base64.urlsafe_b64decode(html_part).decode("utf-8")
            parsedHtml = BeautifulSoup(html, "html.parser")
            body = parsedHtml.get_text()
            allLiks = parsedHtml.find_all("a", href=True)
            for link in allLiks:
                links.append(link.get("href"))
            return body.strip(), links
        elif text_part is not None:
            body = base64.urlsafe_b64decode(text_part).decode("utf-8")
            url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
            allLiks = re.findall(url_pattern, body)
            for link in allLiks:
                links.append(link)
            return body.strip(), links
        else:
            return "", []
    else:
        data = email_payload["body"].get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8")

    return body.strip(), links


def classify_email(email_sender, email_subject):
    sender_name, email = parseaddr(email_sender)
    match email:
        case EmailAddr.HIRIST.value:
            for subTxt in HIRIST_DIGEST_SUBJECT:
                if subTxt in email_subject:
                    return EmailClassification.HIRIST_DIGEST
            return EmailClassification.HIRIST_SIGNLE
        case EmailAddr.LINKEDIND.value:
            return EmailClassification.LINKEDIN_ALERT
        case _:
            return "unknown"


def decode_hirist_links(raw_links):
    linksList = []
    for link in raw_links:
        link = unquote(link)
        if HIRIST_STR in link:
            parsed = urlparse(link)
            match = re.search(r"(https?://.*)", parsed.path)
            if match:
                linksList.append(match.group(1))
    return linksList


def parse_hirist_subject(email_subject):
    splt_subject_text = email_subject.split("-")
    pattern = r"^(.*?)\s*\(\s*(\d+\s*-\s*\d+\s*(?:yrs?|years?))\s*\)"
    if len(splt_subject_text) > 1:
        company = splt_subject_text[0]
        match = re.search(pattern, splt_subject_text[1], re.IGNORECASE)
        if match:
            job_title = match.group(1)
            experience = match.group(2)
            return {
                "company": company,
                "job_title": job_title,
                "experience": experience,
            }
        return {"company": company}
    else:
        match = re.search(pattern, splt_subject_text[0], re.IGNORECASE)
        if match:
            job_title = match.group(1)
            experience = match.group(2)
            return {"job_title": job_title, "experience": experience}
    return None


def filter_linkedin_links(raw_links):
    linksList = []
    for link in raw_links:
        link = unquote(link)
        if LINKEDIN_STR in link:
            link = unquote(link)
            parsed = urlparse(link)
            components = (parsed.scheme, parsed.netloc, parsed.path, "", "", "")
            linksList.append(urlunparse(components))
    return linksList


def read_job_emails():
    service = get_gmail_service()
    today = datetime.now().strftime("%Y/%m/%d")
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            # q=f"label:jobs_agents",
            maxResults=10,
            q=f"from:jobalerts-noreply@linkedin.com",
        )
        .execute()
    )

    messages = results.get("messages", [])
    print(f"Found {len(messages)} emails in Jobs label")

    for msg in messages:  # first 5 only for now
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()

        headers = txt["payload"]["headers"]
        payload = txt["payload"]
        body, links = get_email_body(txt["payload"])
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        sender_name, email = parseaddr(sender)
        with open("email_bodt.txt", "a") as txt:
            txt.write("\n=-=-=-=-=")
            txt.write(f"\nFrom: {sender}")
            txt.write(f"\nSubject: {subject}")
            # txt.write(f"\nBody: {body}")
            txt.write(f"\nPAyload:\n")
            txt.write(f"{payload}\n\n")
            # for link in links:
            #     link = unquote(link)
            #     parsed = urlparse(link)
            #     components = (parsed.scheme, parsed.netloc, parsed.path, "", "", "")
            #     txt.write(f"\n${urlunparse(components)}\n\n")
            #     # if HIRIST_STR in link:
            #     #     parsed = urlparse(link)
            #     #     match = re.search(r"(https?://.*)", parsed.path)
            #     #     if match:
            #     #         extracted_lnk = match.group(1)
            #     #         txt.write(f"\n${extracted_lnk}")
        # if creds and creds.expire
    print("DONE :)")


if __name__ == "__main__":
    read_job_emails()

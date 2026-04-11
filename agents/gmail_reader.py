import base64
import logging
import os
import pickle
import re
from datetime import datetime
from email.utils import parseaddr

from bs4 import BeautifulSoup
from emailParsers import get_parser
from google.auth.transport.requests import Request

# from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.pickle"

logging.basicConfig(
    filename="app.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


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


def read_job_emails():
    service = get_gmail_service()
    today = datetime.now().strftime("%Y/%m/%d")
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            q=f"label:jobs_agents after:{today}",
        )
        .execute()
    )

    messages = results.get("messages", [])
    print(f"Found {len(messages)} emails in Jobs label")

    for msg in messages:
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()

        headers = txt["payload"]["headers"]
        payload = txt["payload"]
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        sender_name, email = parseaddr(sender)
        parser = get_parser(email)
        with open("email_body.txt", "a") as body_txt:
            body_txt.write("\n=-=-=-=-=")
            body_txt.write(f"\nFrom: {sender}")
            body_txt.write(f"\nSubject: {subject}")
            if parser:
                body, raw_links = get_email_body(txt["payload"])
                # parse_job(self, subject: str, body: str, raw_links: list[str])
                extracted_jobs = parser.parse_job(subject, body, raw_links)
                for job in extracted_jobs:
                    if job is not None:
                        body_txt.write(
                            f"\nFound Job: {job.role} at {job.company} -> {job.url}"
                        )
            else:
                logging.warning(f"parser not for {sender_name} - {email}")

    print("DONE :)")


if __name__ == "__main__":
    read_job_emails()

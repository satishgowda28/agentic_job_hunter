import base64
import os
import pickle
import re
from datetime import datetime

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# from

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.pickle"


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
        for part in email_payload["parts"]:
            print(f"-=-=-=-=-={part["mimeType"]}=-=-=-=-=-")
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                body = base64.urlsafe_b64decode(data).decode("utf-8")
                url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
                allLiks = re.findall(url_pattern, body)
                for link in allLiks:
                    links.append(link)
            elif part["mimeType"] == "text/html":
                data = part["body"].get("data", "")
                html = base64.urlsafe_b64decode(data).decode("utf-8")
                parsedHtml = BeautifulSoup(html, "html.parser")
                # body = parsedHtml.get_text()
                allLiks = parsedHtml.find_all("a", href=True)
                for link in allLiks:
                    links.append(link.get("href"))

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
            # q=f"label:jobs_agents after:{today}",
            q=f"from:jobalerts-noreply@linkedin.com after:{today}",
        )
        .execute()
    )

    messages = results.get("messages", [])
    print(f"Found {len(messages)} emails in Jobs label")

    for msg in messages:  # first 5 only for now
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()

        headers = txt["payload"]["headers"]
        body, links = get_email_body(txt["payload"])
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        print("=-=-=-=-=")
        print(f"\nFrom: {sender}")
        print(f"Subject: {subject}")
        print(f"links:")
        for link in links:
            print(f"\n${link}")
        # if creds and creds.expire


if __name__ == "__main__":
    read_job_emails()

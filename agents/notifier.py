import base64
from datetime import date
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from agents.auth import google_init


def send_summary(summary: str):
    creds = google_init()
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(summary)

        message["To"] = "satishgowda28@gmail.com"
        message["From"] = "satishgowda28@gmail.com"
        message["Subject"] = f"Job Scraper {date.today().strftime("%Y-%m-%d")}"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


if __name__ == "__main__":
    print(send_summary("Hello Word"))

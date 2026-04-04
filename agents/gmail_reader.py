import os
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# from 

SCOPES= ['https://www.googleapis.com/auth/gmail.readonly']
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
      flow = InstalledAppFlow.from_client_secrets_file("_creds/credentials.json",SCOPES)
      creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "wb") as token:
      pickle.dump(creds, token)
  return build("gmail", "v1", credentials=creds)

def read_job_emails():
  service = get_gmail_service()
  
  results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='label:jobs_agents',
        maxResults=10
    ).execute()
  
  messages = results.get("messages", [])
  print(f"Found {len(messages)} emails in Jobs label")
  
  for msg in messages[:5]:  # first 5 only for now
    txt = service.users().messages().get(
        userId='me', 
        id=msg['id']
    ).execute()
    
    headers = txt['payload']['headers']
    print()
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    
    print(f"\nFrom: {sender}")
    print(f"Subject: {subject}")
    # if creds and creds.expire

if __name__ == '__main__':
  read_job_emails()
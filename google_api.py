import os
# Google Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

def connect(api,version):
    CLIENT_FILE = "credentials.json"
    SCOPES = ["https://www.googleapis.com/auth/books","https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/drive"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json",SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE,SCOPES)
            creds = flow.run_local_server(port=2048)
        with open("token.json",'w') as token:
            token.write(creds.to_json())

    try:
        service = build(api,version,credentials=creds)
    
    except HttpError as err:
        logger.error(err)
    return service

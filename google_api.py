import os
# Google Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json

logger = logging.getLogger(__name__)

def connect(api,version):
    CLIENT_FILE = "credentials.json"
    SCOPES = ["https://www.googleapis.com/auth/books","https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/drive"]
    creds = None

    if "API_TOKEN" in os.environ:
        token_data = {
                "token":os.getenv('API_TOKEN'),
                "refresh_token":os.getenv('REFRESH_TOKEN'),
                "token_uri":os.getenv('TOKEN_URI'),
                "client_id":os.getenv('CLIENT_ID'),
                "client_secret":os.getenv('CLIENT_SECRET'),
                "scopes":SCOPES,
                "expiry":os.getenv('EXPIRY')
                }
        logger.info("Found Google API token")
        creds = Credentials.from_authorized_user_info(token_data,SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            creds_json = json.loads(creds.to_json())
            os.environ['API_TOKEN']= str(creds_json['token'])
            os.environ['REFRESH_TOKEN']= str(creds_json['refresh_token'])
            os.environ['EXPIRY']= str(creds_json['expiry'])
        else:
            logger.info("Couldn't found API token, starting browser authentication")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE,SCOPES)
            creds = flow.run_local_server(port=2048)
            creds_json = json.loads(creds.to_json())
            with open(".env", "a") as f:
                f.write(f"API_TOKEN={creds_json['token']}\n")
                f.write(f"REFRESH_TOKEN={creds_json['refresh_token']}\n")
                f.write(f"TOKEN_URI={creds_json['token_uri']}\n")
                f.write(f"CLIENT_ID={creds_json['client_id']}\n")
                f.write(f"CLIENT_SECRET={creds_json['client_secret']}\n")
                f.write(f"EXPIRY={creds_json['expiry']}\n")
                f.write("NOTION_KEY=\n")
                f.write("NOTION_DATABASE_ID=\n")
                f.write("DRIVE_FOLDER_ID=\n")
                f.write("IMAGE_HOST_KEY=\n")
                f.write("TIME_OFFSET=")
            logger.info("API token credentials written to '.env' file")
            os.remove(CLIENT_FILE)
            quit()

    try:
        service = build(api,version,credentials=creds)
        return service
    
    except HttpError as err:
        logger.error(err)

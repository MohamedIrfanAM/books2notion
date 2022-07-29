import google_api
import json
import logging

logger = logging.getLogger(__name__)

def ids():
    drive = google_api.connect("drive","v3")

    secret_file = open('secrets.json') 
    secret_data = json.load(secret_file) 

    folderID = secret_data["folder_id"]
    query = f"parents = '{folderID}'"
    fields= "files(id,modifiedTime)"

    response = drive.files().list(q=query,fields=fields).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive.files().list(q=query,pageToken=nextPageToken).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')
    
    logger.info(f"listing docs under folderID - {folderID}")
    id_list = []
    for file in files:
        file_info = {
            "docs_id":file["id"],
            "modified_time":file["modifiedTime"]
        }
        id_list.append(file_info)
    logger.info("finished listing docs")
    return id_list


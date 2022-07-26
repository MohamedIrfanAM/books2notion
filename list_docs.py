import google_api
import json

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
    
    id_list = []
    for file in files:
        file_info = {
            "docs_id":file["id"],
            "modified_time":file["modifiedTime"]
        }
        id_list.append(file_info)
    return id_list


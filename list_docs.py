import google_api
import json

def ids():
    drive = google_api.connect("drive","v3")

    secret_file = open('secrets.json') 
    secret_data = json.load(secret_file) 

    folderID = secret_data["folder_id"]
    query = f"parents = '{folderID}'"

    response = drive.files().list(q=query).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive.files().list(q=query,pageToken=nextPageToken).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')
    
    id_list = []
    for file in files:
        id_list.append(file['id'])
    return id_list

